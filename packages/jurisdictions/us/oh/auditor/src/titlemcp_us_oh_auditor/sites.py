from __future__ import annotations

from titlemcp_platform_iasworld import (
    AuditorSearchMode,
    DetailProfile,
    IasWorldSiteConfig,
)

# The table of Ohio county auditor sites that run the Tyler iasWorld platform.
# Adding a county is a config entry here (plus a fixture-backed contract test and
# a sample) — the scraping/canonical logic lives in titlemcp-platform-iasworld.
#
# Counties confirmed on iasWorld but not yet enabled (need a captured fixture):
# Montgomery, Butler, Lucas, Summit, Lake. See
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

# Stark serves the iasWorld "Public Access" experience on a bare domain (no
# /_web/ prefix). Two things differ from Franklin, both confirmed against the
# live site's chrome ("Powered by iasWorld Public Access"): the basic property
# search is served under mode=realprop (a unified search like Summit/Lake, not
# the separate address/owner/parid pages), so every mode is mapped to realprop
# via mode_map; and the datalet detail uses the Public Access split-section
# layout (Parcel/Owner/Tax Mailing/Legal/Taxes Charged) so detail_profile is
# PUBLIC_ACCESS. district_code "000" is from platform recon (the live search was
# in maintenance, so the jur value and parcel format could not be re-read); the
# default numeric_parcel_ids=True is retained. All handled by config — no new
# scraper. See docs/OHIO_AUDITOR_EXPANSION.md.
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
    detail_profile=DetailProfile.PUBLIC_ACCESS,
    owner="Stark County Auditor",
    priority=230,
)

OH_IASWORLD_SITES: list[IasWorldSiteConfig] = [
    FRANKLIN,
    CLERMONT,
    STARK,
]
