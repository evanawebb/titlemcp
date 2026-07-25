from __future__ import annotations

from titlemcp_platform_iasworld import AuditorSearchMode, DetailProfile, IasWorldSiteConfig

# The table of Ohio county auditor sites that run the Tyler iasWorld platform.
# Adding a county is a config entry here (plus a fixture-backed contract test and
# a sample) — the scraping/canonical logic lives in titlemcp-platform-iasworld.
#
# Counties confirmed on iasWorld but not yet enabled (need a captured fixture):
# Summit. See
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

# Montgomery is the same iasWorld stack, but its base_url is a bare domain
# (https://www.mcrealestate.org/) — the parent of search/ and Datalets/ with no
# "/_web/" prefix. Two knobs were confirmed against the live site: jur=000 (seen
# in the datalet URLs), and the primary Parcel ID is alphanumeric (example
# "A01 00000 0001") so numeric_parcel_ids=False, like Clermont. Re-verified live:
# the datalet detail is the combined-Owner CLASSIC layout (no numbered "Owner 1"/
# "Address 1" Public Access sections), so detail_profile=CLASSIC (the default) is
# correct. All knobs now confirmed against live result/datalet pages.
MONTGOMERY = IasWorldSiteConfig(
    source_id="us-oh-montgomery-auditor",
    county="Montgomery County",
    state="OH",
    name="Montgomery County, Ohio Auditor Property Search",
    base_url="https://www.mcrealestate.org/",
    district_code="000",
    numeric_parcel_ids=False,
    # Newer iasWorld build: parcels carry significant internal spaces
    # ("A01 00000 0001") the form expects verbatim. The owner/address column
    # swap is handled automatically by header detection.
    preserve_parcel_whitespace=True,
    owner="Montgomery County Auditor",
    priority=230,
)

# Lucas County serves its iasWorld site under the AREIS brand at a path-prefix
# base_url (the parent of search/ and Datalets/ is .../lucascare/), "Powered by
# iasWorld Public Access" with the standard commonsearch.aspx / inpParid stack.
# All knobs re-verified live (an owner search returned result rows): the parcel
# token is jur 048 (e.g. "048:0100000:2026"), so district_code="048" — NOT the
# 000 regional default. Parcels are numeric ("0100000"), so the default
# numeric_parcel_ids=True is kept; the datalet detail uses the combined-Owner
# CLASSIC layout (labels "Owner"/"Prior Owner", not the numbered Public Access
# sections), so detail_profile stays CLASSIC. See docs/OHIO_AUDITOR_EXPANSION.md.
LUCAS = IasWorldSiteConfig(
    source_id="us-oh-lucas-auditor",
    county="Lucas County",
    state="OH",
    name="Lucas County, Ohio Auditor Property Search (AREIS)",
    base_url="https://icare.co.lucas.oh.us/lucascare/",
    district_code="048",
    owner="Lucas County Auditor",
    priority=230,
)

# Stark serves iasWorld from a bare domain (https://realestate.starkcountyohio.gov/,
# no "/_web/" prefix) like Montgomery, behind a one-time "Agree" disclaimer page.
# Every knob below was verified against the live site (an owner search returned
# result rows and a reachable datalet):
#   * mode_map -> "realprop" for ALL THREE modes. Stark does NOT serve the classic
#     mode=parid / mode=address searches at all — both redirect to
#     /main/accesserror.aspx even with an accepted disclaimer session. It exposes a
#     single unified "Basic Search" form (mode=realprop) carrying parcel, owner,
#     address-number and street fields together, so every mode routes there. (A
#     dedicated mode=owner page also exists, but routing owner through realprop too
#     keeps one form — and one set of field names — for the whole county.)
#   * form_field_overrides: the realprop form names its inputs inpNo/inpOwner1
#     rather than the classic inpNumber/inpOwner — the same shape as Lake.
#   * district_code="000": read from the datalet's hdJur hidden input (confirming
#     the recon guess), not assumed from the regional default.
#   * numeric_parcel_ids: parcels are purely numeric ("10000006", "1000049"), so
#     the default True is correct and is kept deliberately, not by omission.
#   * detail_profile=PUBLIC_ACCESS: the datalet uses the numbered split-section
#     layout ("Owner 1", "Address 1", "Mailing Name 1", "Legal Desc 1") with no
#     combined "Owner"/"Prior Owner" CLASSIC labels. The CLASSIC default would
#     have been WRONG here.
STARK = IasWorldSiteConfig(
    source_id="us-oh-stark-auditor",
    county="Stark County",
    state="OH",
    name="Stark County, Ohio Auditor Property Search",
    base_url="https://realestate.starkcountyohio.gov/",
    district_code="000",
    mode_map={
        AuditorSearchMode.ADDRESS: "realprop",
        AuditorSearchMode.OWNER: "realprop",
        AuditorSearchMode.PARCEL_ID: "realprop",
    },
    form_field_overrides={"inpNumber": "inpNo", "inpOwner": "inpOwner1"},
    detail_profile=DetailProfile.PUBLIC_ACCESS,
    owner="Stark County Auditor",
    priority=230,
)

OH_IASWORLD_SITES: list[IasWorldSiteConfig] = [
    FRANKLIN,
    CLERMONT,
    MONTGOMERY,
    LUCAS,
    STARK,
]
