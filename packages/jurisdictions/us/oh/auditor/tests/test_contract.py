from __future__ import annotations

# ruff: noqa: E501
import asyncio
import tomllib
import types
import unittest
from pathlib import Path

from titlemcp_us_oh_auditor.adapters import OhioCountyAuditorAdapter
from titlemcp_us_oh_auditor.manifest import capability_manifest
from titlemcp_us_oh_auditor.plugin import OhioAuditorPlugin
from titlemcp_us_oh_auditor.sites import (
    CLERMONT,
    FRANKLIN,
    LUCAS,
    MONTGOMERY,
    OH_IASWORLD_SITES,
    STARK,
)
from titlemcp_us_oh_auditor.toolsets import OhioAuditorToolset

from title_mcp.domain.models import Jurisdiction, WorkflowKind
from title_mcp.sources import SourceKind, SourceQuery, SourceResultStatus
from title_mcp.sources.registry import SourceConnectorRegistry
from titlemcp_platform_iasworld import (
    AuditorSearchMode,
    DetailProfile,
    IasWorldAuditorClient,
    IasWorldAuditorParcelDetail,
    IasWorldAuditorSearchHit,
    IasWorldAuditorSearchQuery,
    IasWorldAuditorSearchResponse,
    build_auditor_source_connector,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class OhioAuditorContractTests(unittest.TestCase):
    def test_manifest_matches_package_readiness_file(self) -> None:
        manifest = capability_manifest()
        with (PACKAGE_ROOT / "titlemcp-capability.toml").open("rb") as readiness_file:
            readiness = tomllib.load(readiness_file)

        self.assertEqual(manifest.capability_id, readiness["capability"]["capability_id"])
        self.assertEqual(manifest.package_name, readiness["capability"]["package_name"])
        self.assertEqual(manifest.version, readiness["capability"]["version"])

    def test_sites_table_includes_franklin(self) -> None:
        self.assertIn(FRANKLIN, OH_IASWORLD_SITES)
        self.assertEqual(FRANKLIN.source_id, "us-oh-franklin-auditor")
        self.assertEqual(FRANKLIN.district_code, "025")
        self.assertEqual(
            FRANKLIN.base_url,
            "https://property.franklincountyauditor.com/_web/",
        )
        self.assertTrue(FRANKLIN.numeric_parcel_ids)

    def test_sites_table_includes_clermont_with_alphanumeric_parcels(self) -> None:
        # A second county: config entry only, plus the one alphanumeric-parcel knob.
        self.assertIn(CLERMONT, OH_IASWORLD_SITES)
        self.assertEqual(CLERMONT.source_id, "us-oh-clermont-auditor")
        self.assertEqual(CLERMONT.district_code, "000")
        self.assertFalse(CLERMONT.numeric_parcel_ids)
        self.assertEqual(CLERMONT.tool_name, "clermont_county_auditor_search")

    def test_sites_table_includes_montgomery_with_alphanumeric_parcels(self) -> None:
        # Montgomery: a bare-domain base_url (no /_web/ prefix) and an alphanumeric
        # primary Parcel ID ("A01 00107 0001"), so numeric_parcel_ids=False. jur=000
        # and the alphanumeric parcels were both confirmed against the live site.
        self.assertIn(MONTGOMERY, OH_IASWORLD_SITES)
        self.assertEqual(MONTGOMERY.source_id, "us-oh-montgomery-auditor")
        self.assertEqual(MONTGOMERY.district_code, "000")
        self.assertEqual(MONTGOMERY.base_url, "https://www.mcrealestate.org/")
        self.assertFalse(MONTGOMERY.numeric_parcel_ids)
        self.assertTrue(MONTGOMERY.preserve_parcel_whitespace)
        self.assertEqual(MONTGOMERY.tool_name, "montgomery_county_auditor_search")

    def test_sites_table_includes_lucas_with_path_prefix_base_url(self) -> None:
        # Lucas (AREIS branding) is another config-only county. Its base_url is a
        # path prefix (.../lucascare/) rather than a bare domain or /_web/ stack;
        # the config preserves the trailing slash so search/ and Datalets/ resolve.
        self.assertIn(LUCAS, OH_IASWORLD_SITES)
        self.assertEqual(LUCAS.source_id, "us-oh-lucas-auditor")
        self.assertEqual(LUCAS.district_code, "048")
        self.assertEqual(LUCAS.base_url, "https://icare.co.lucas.oh.us/lucascare/")
        self.assertTrue(LUCAS.numeric_parcel_ids)
        self.assertEqual(LUCAS.tool_name, "lucas_county_auditor_search")
        self.assertEqual(
            LUCAS.search_url(AuditorSearchMode.PARCEL_ID),
            "https://icare.co.lucas.oh.us/lucascare/search/commonsearch.aspx?mode=parid",
        )

    def test_sites_table_includes_stark_with_realprop_only_search(self) -> None:
        # Stark is a bare-domain base_url like Montgomery, but it does NOT serve
        # the classic mode=parid / mode=address searches at all (both redirect to
        # /main/accesserror.aspx). Everything routes through its unified
        # "realprop" Basic Search form, whose inputs are named inpNo/inpOwner1.
        # All verified against the live site.
        self.assertIn(STARK, OH_IASWORLD_SITES)
        self.assertEqual(STARK.source_id, "us-oh-stark-auditor")
        self.assertEqual(STARK.district_code, "000")
        self.assertEqual(STARK.base_url, "https://realestate.starkcountyohio.gov/")
        self.assertEqual(STARK.tool_name, "stark_county_auditor_search")
        # Parcels are numeric ("99000001"), so the default is kept deliberately.
        self.assertTrue(STARK.numeric_parcel_ids)
        self.assertFalse(STARK.preserve_parcel_whitespace)
        # The datalet uses the numbered Public Access layout, not CLASSIC.
        self.assertEqual(STARK.detail_profile, DetailProfile.PUBLIC_ACCESS)
        for mode in AuditorSearchMode:
            self.assertEqual(
                STARK.search_url(mode),
                "https://realestate.starkcountyohio.gov/search/commonsearch.aspx?mode=realprop",
            )

    def test_stark_search_form_uses_realprop_field_names(self) -> None:
        # The unified realprop form renames the address-number and owner inputs.
        client = IasWorldAuditorClient(STARK)

        self.assertEqual(
            client._apply_field_overrides({"inpNumber": "100", "inpStreet": "EXAMPLE"}),
            {"inpNo": "100", "inpStreet": "EXAMPLE"},
        )
        self.assertEqual(
            client._apply_field_overrides({"inpOwner": "DOE JANE A"}),
            {"inpOwner1": "DOE JANE A"},
        )
        # The parcel field is shared across iasWorld forms and is never renamed.
        self.assertEqual(
            client._apply_field_overrides({"inpParid": "99000001"}),
            {"inpParid": "99000001"},
        )

    def test_stark_fixtures_parse_into_canonical_record(self) -> None:
        # Fixture-backed end-to-end parse: synthetic realprop results grid plus a
        # synthetic Public Access datalet, served through a fake opener.
        client = IasWorldAuditorClient(STARK, opener=_StarkFixtureOpener())
        connector = build_auditor_source_connector(STARK, client=client)

        result = asyncio.run(
            connector.query(
                SourceQuery(
                    jurisdiction=STARK.jurisdiction,
                    kind=SourceKind.TAX_AUTHORITY,
                    criteria={"mode": "owner", "owner_name": "DOE JANE A"},
                )
            )
        )

        self.assertEqual(result.status, SourceResultStatus.SUCCEEDED)
        self.assertTrue(result.requires_human_review)
        record = result.records[0]
        self.assertEqual(record["schema_name"], "title_mcp.property_assessment_record")
        self.assertEqual(record["source"]["source_id"], "us-oh-stark-auditor")
        self.assertEqual(record["jurisdiction"]["county"], "Stark County")
        # jur=000 comes from the datalet's hdJur input, not from a guess.
        self.assertEqual(record["parcel"]["tax_authority_jurisdiction"], "000")
        self.assertEqual(record["parcel"]["parcel_number"], "99000001")
        # Numbered "Owner 1" label resolves only under the PUBLIC_ACCESS profile.
        self.assertEqual(record["ownership"]["owners"], ["DOE JANE A"])
        self.assertEqual(record["property"]["property_class"], "R - RESIDENTIAL")
        self.assertEqual(
            record["property"]["legal_description_lines"][0],
            "EXAMPLE SUBDIVISION LOT 1",
        )

    def test_stark_owner_search_posts_realprop_field_names(self) -> None:
        # Proves the rename reaches the wire rather than only the helper.
        opener = _StarkFixtureOpener()
        client = IasWorldAuditorClient(STARK, opener=opener)

        client.search(
            IasWorldAuditorSearchQuery(
                mode=AuditorSearchMode.OWNER,
                owner_name="DOE JANE A",
                include_details=False,
            )
        )

        self.assertTrue(opener.post_bodies, "expected at least one POST")
        self.assertIn("inpOwner1=", opener.post_bodies[0])
        self.assertNotIn("inpOwner=", opener.post_bodies[0])

    def test_stark_empty_results_report_no_records(self) -> None:
        # Missing/empty path: a results page with no rows must not raise.
        client = IasWorldAuditorClient(STARK, opener=_StarkFixtureOpener(search_html="<table></table>"))
        connector = build_auditor_source_connector(STARK, client=client)

        result = asyncio.run(
            connector.query(
                SourceQuery(
                    jurisdiction=STARK.jurisdiction,
                    kind=SourceKind.TAX_AUTHORITY,
                    criteria={"mode": "owner", "owner_name": "NOBODY MATCHES THIS"},
                )
            )
        )

        self.assertIn(
            result.status,
            {SourceResultStatus.SUCCEEDED, SourceResultStatus.NO_RESULTS},
        )
        self.assertFalse(result.records)

    def test_adapter_supports_ohio_tax_certificate(self) -> None:
        adapter = OhioCountyAuditorAdapter()

        self.assertTrue(
            adapter.supports(Jurisdiction(country="US", state="OH", county="Franklin County"))
        )
        self.assertFalse(
            adapter.supports(Jurisdiction(country="US", state="CA", county="Los Angeles County"))
        )
        self.assertIn(WorkflowKind.TAX_CERTIFICATE, adapter.workflow_kinds)

    def test_plugin_registers_one_source_per_county(self) -> None:
        registry = SourceConnectorRegistry()
        context = types.SimpleNamespace(sources=registry)

        OhioAuditorPlugin().register(context)

        for site in OH_IASWORLD_SITES:
            connector = registry.get(site.source_id)
            self.assertIsNotNone(connector)
            self.assertTrue(
                connector.supports(site.jurisdiction, SourceKind.TAX_AUTHORITY)
            )

    def test_toolset_registers_tool_per_county(self) -> None:
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        OhioAuditorToolset().register(mcp, types.SimpleNamespace())

        tools = asyncio.run(mcp.list_tools())
        tool_names = {tool.name for tool in tools}
        for site in OH_IASWORLD_SITES:
            self.assertIn(site.tool_name, tool_names)
        self.assertIn("franklin_county_auditor_search", tool_names)

    def test_source_query_returns_canonical_record(self) -> None:
        connector = build_auditor_source_connector(FRANKLIN, client=_FakeClient())

        result = asyncio.run(
            connector.query(
                SourceQuery(
                    jurisdiction=FRANKLIN.jurisdiction,
                    kind=SourceKind.TAX_AUTHORITY,
                    criteria={"mode": "parid", "parcel_id": "010-000123-00"},
                )
            )
        )

        self.assertEqual(result.status, SourceResultStatus.SUCCEEDED)
        self.assertTrue(result.requires_human_review)
        record = result.records[0]
        self.assertEqual(record["schema_name"], "title_mcp.property_assessment_record")
        self.assertEqual(record["source"]["source_id"], "us-oh-franklin-auditor")
        self.assertEqual(record["parcel"]["parcel_id"], "010-000123-00")
        self.assertEqual(record["tax_status"]["property_class"], "R - Residential")

    def test_missing_address_fields_report_failure_not_exception(self) -> None:
        # Address mode with no street should be caught and surfaced as FAILED.
        connector = build_auditor_source_connector(FRANKLIN, client=_FailingClient())

        result = asyncio.run(
            connector.query(
                SourceQuery(
                    jurisdiction=FRANKLIN.jurisdiction,
                    kind=SourceKind.TAX_AUTHORITY,
                    criteria={"mode": "address"},
                )
            )
        )

        self.assertEqual(result.status, SourceResultStatus.FAILED)
        self.assertTrue(result.warnings)


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class _FixtureResponse:
    def __init__(self, body: str, url: str) -> None:
        self._body = body.encode("utf-8")
        self._url = url

    def read(self) -> bytes:
        return self._body

    def geturl(self) -> str:
        return self._url

    def __enter__(self) -> _FixtureResponse:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class _StarkFixtureOpener:
    """Serves the synthetic Stark fixtures instead of touching the network.

    GETs of ``Datalets/`` return the datalet fixture, any other GET returns an
    empty search form, and POSTs (the search submission) return the results
    fixture while recording the encoded body.
    """

    def __init__(self, search_html: str | None = None) -> None:
        if search_html is None:
            search_html = (FIXTURES / "stark_search_results.html").read_text(encoding="utf-8")
        self._search_html = search_html
        self._detail_html = (FIXTURES / "stark_datalet.html").read_text(encoding="utf-8")
        self.post_bodies: list[str] = []

    def open(self, request: object, timeout: float | None = None) -> _FixtureResponse:
        url = getattr(request, "full_url", "https://realestate.starkcountyohio.gov/")
        data = getattr(request, "data", None)
        if data is None:
            if "Datalet" in url:
                return _FixtureResponse(self._detail_html, url)
            return _FixtureResponse("<form></form>", url)
        self.post_bodies.append(data.decode("utf-8"))
        return _FixtureResponse(self._search_html, url)


class _FakeClient:
    def search(self, query: IasWorldAuditorSearchQuery) -> IasWorldAuditorSearchResponse:
        return IasWorldAuditorSearchResponse(
            query=query,
            search_url="https://example.test/search",
            search_mode=AuditorSearchMode.PARCEL_ID,
            result_count=1,
            results=[
                IasWorldAuditorSearchHit(
                    parcel_id="010-000123-00",
                    parcel_number="01000012300",
                    address="100 EXAMPLE AVE",
                    owner="DOE JANE A",
                )
            ],
            details=[
                IasWorldAuditorParcelDetail(
                    parcel_id="010-000123-00",
                    parcel_number="01000012300",
                    owners=["DOE JANE A"],
                    site_property_address="100 EXAMPLE AVE",
                    tax_status={"Property Class": "R - Residential"},
                )
            ],
        )


class _FailingClient:
    def search(self, query: IasWorldAuditorSearchQuery) -> IasWorldAuditorSearchResponse:
        raise RuntimeError("Address searches require street_name or address.")


if __name__ == "__main__":
    unittest.main()
