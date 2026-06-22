from __future__ import annotations

from titlemcp_platform_iasworld import AuditorSearchMode, DetailProfile, IasWorldSiteConfig

# The table of Ohio county auditor sites that run the Tyler iasWorld platform.
# Adding a county is a config entry here (plus a fixture-backed contract test and
# a sample) — the scraping/canonical logic lives in titlemcp-platform-iasworld.
#
# Counties confirmed on iasWorld but not yet enabled (need a captured fixture):
# Montgomery, Stark, Butler, Lucas. See
# docs/OHIO_AUDITOR_EXPANSION.md for the rollout order and platform recon.

FRANKLIN = IasWorldSiteConfig(
    source_id="us-oh-franklin-auditor",
    county="Franklin County",
    state="OH",
    name="Franklin County, Ohio Auditor Property Search",
    base_url="https://property.franklincountyauditor.com/_web/",
    district_code="025",
    owner="Franklin County Auditor",
    priority=230,
)

# Clermont is the same iasWorld /_web/ stack as Franklin, but two things differ,
# both confirmed against live data: parcels are alphanumeric ("100200C003D") so
# numeric_parcel_ids=False, and its datalet detail uses the "Public Access" split
# section layout (Parcel/Owner/Tax Mailing/Legal/Taxes Charged) rather than
# Franklin's combined-Owner layout. Both are handled by config — no new scraper.
CLERMONT = IasWorldSiteConfig(
    source_id="us-oh-clermont-auditor",
    county="Clermont County",
    state="OH",
    name="Clermont County, Ohio Auditor Property Search",
    base_url="https://www.clermontauditorrealestate.org/_web/",
    district_code="000",
    numeric_parcel_ids=False,
    detail_profile=DetailProfile.PUBLIC_ACCESS,
    owner="Clermont County Auditor",
    priority=230,
)

# Lake County's auditor site runs iasWorld (the page identifies as iasWorld) but
# serves a single unified "realprop" Basic Search form for parcel, owner, AND
# address — there is no separate address/owner search page. Verified live: jur
# "000", alphanumeric parcels ("16A0010000010", token "000:02A0010000050:2026"),
# and the standard tr.SearchResults / parcel-token result rows the shared parser
# already handles. Two knobs make it work:
#   - mode_map routes every search mode to the realprop URL, and
#   - form_field_overrides renames the two POST fields whose names differ on the
#     realprop form: address number inpNumber->inpNo, owner inpOwner->inpOwner1
#     (parcel inpParid and street inpStreet are unchanged).
# Its datalet detail layout is a THIRD variant (sections "Owner Name and Mailing
# Address", "Legal Description Information", "Appraised (Market - 100%) Value",
# "Taxes Due") that neither the CLASSIC nor PUBLIC_ACCESS profile fully parses, so
# search + the header-derived canonical fields (parcel, owner, site address,
# token) populate, but deep detail extraction (legal/taxes/valuation) is a known
# follow-up: a LAKE DetailProfile. Lake is therefore NEEDS-VERIFICATION, not fully
# enabled. CLASSIC is the safe default until that profile lands. See
# docs/OHIO_AUDITOR_EXPANSION.md.
LAKE = IasWorldSiteConfig(
    source_id="us-oh-lake-auditor",
    county="Lake County",
    state="OH",
    name="Lake County, Ohio Auditor Property Search",
    base_url="https://auditor.lakecountyohio.gov/",
    district_code="000",
    numeric_parcel_ids=False,
    mode_map={
        AuditorSearchMode.ADDRESS: "realprop",
        AuditorSearchMode.OWNER: "realprop",
        AuditorSearchMode.PARCEL_ID: "realprop",
    },
    form_field_overrides={"inpNumber": "inpNo", "inpOwner": "inpOwner1"},
    owner="Lake County Auditor",
    priority=230,
)

# Summit County (Fiscal Office) runs iasWorld Public Access and, like Lake, serves
# a single unified "realprop" search (no separate per-mode pages) whose form
# renames two POST fields. All confirmed against live data: behind the
# Disclaimer.aspx gate the realprop form fields are inpNo (address number, classic
# inpNumber) and inpOwner1 (owner, classic inpOwner) while inpParid/inpStreet are
# unchanged, and a live owner search via inpOwner1 returned tr.SearchResults rows
# with jur "000" parcel tokens ("000:0100111:2025", numeric parcels). So the same
# two knobs as Lake apply — mode_map routes every mode to realprop, and
# form_field_overrides renames inpNumber->inpNo / inpOwner->inpOwner1 (the shared
# platform knob introduced with Lake). numeric_parcel_ids=False keeps the
# alphanumeric-safe superset even though the sampled parcels were numeric.
# Its datalet detail page is the same THIRD layout variant as Lake (Appraised
# (Market - 100%) Value / Taxes Due sections) that neither CLASSIC nor
# PUBLIC_ACCESS fully parses, so search + header-derived canonical fields populate
# but deep detail extraction is the same LAKE-DetailProfile follow-up. Summit is
# therefore SEARCH-VERIFIED but NEEDS-VERIFICATION on detail; CLASSIC (the default)
# is the safe layout until that profile lands.
SUMMIT = IasWorldSiteConfig(
    source_id="us-oh-summit-auditor",
    county="Summit County",
    state="OH",
    name="Summit County, Ohio Fiscal Office Property Search",
    base_url="https://propertyaccess.summitoh.net/",
    district_code="000",
    numeric_parcel_ids=False,
    mode_map={
        AuditorSearchMode.ADDRESS: "realprop",
        AuditorSearchMode.OWNER: "realprop",
        AuditorSearchMode.PARCEL_ID: "realprop",
    },
    form_field_overrides={"inpNumber": "inpNo", "inpOwner": "inpOwner1"},
    owner="Summit County Fiscal Office",
    priority=230,
)

OH_IASWORLD_SITES: list[IasWorldSiteConfig] = [
    FRANKLIN,
    CLERMONT,
    LAKE,
    SUMMIT,
]
