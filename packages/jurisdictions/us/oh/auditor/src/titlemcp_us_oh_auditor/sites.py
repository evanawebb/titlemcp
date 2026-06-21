from __future__ import annotations

from titlemcp_platform_iasworld import DetailProfile, IasWorldSiteConfig

# The table of Ohio county auditor sites that run the Tyler iasWorld platform.
# Adding a county is a config entry here (plus a fixture-backed contract test and
# a sample) — the scraping/canonical logic lives in titlemcp-platform-iasworld.
#
# Counties confirmed on iasWorld but not yet enabled (need a captured fixture):
# Montgomery, Stark, Butler, Summit, Lake. See
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

# Lucas County serves its iasWorld site under the AREIS brand at a path-prefix
# base_url (the parent of search/ and Datalets/ is .../lucascare/). The platform
# was confirmed live as "Powered by iasWorld Public Access" with the standard
# commonsearch.aspx / inpParid stack. The site was in scheduled maintenance during
# recon, so three knobs could not be confirmed against live result/datalet pages
# and use the safe iasWorld defaults: district_code "000", numeric parcels, and
# the CLASSIC datalet profile. The "Public Access" footer hints the detail layout
# may be PUBLIC_ACCESS (as Clermont's is) — verify and switch when the site is
# reachable. See docs/OHIO_AUDITOR_EXPANSION.md.
LUCAS = IasWorldSiteConfig(
    source_id="us-oh-lucas-auditor",
    county="Lucas County",
    state="OH",
    name="Lucas County, Ohio Auditor Property Search (AREIS)",
    base_url="https://icare.co.lucas.oh.us/lucascare/",
    district_code="000",
    owner="Lucas County Auditor",
    priority=230,
)

OH_IASWORLD_SITES: list[IasWorldSiteConfig] = [
    FRANKLIN,
    CLERMONT,
    LUCAS,
]
