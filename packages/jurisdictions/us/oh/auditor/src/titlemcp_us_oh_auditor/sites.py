from __future__ import annotations

from titlemcp_platform_iasworld import DetailProfile, IasWorldSiteConfig

# The table of Ohio county auditor sites that run the Tyler iasWorld platform.
# Adding a county is a config entry here (plus a fixture-backed contract test and
# a sample) — the scraping/canonical logic lives in titlemcp-platform-iasworld.
#
# Counties confirmed on iasWorld but not yet enabled (need a captured fixture):
# Montgomery, Stark, Lucas, Summit, Lake. See
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

# Butler runs the same iasWorld stack: commonsearch.aspx (mode=owner/address/parid)
# and Datalet.aspx, "Powered by iasWorld Public Access" (Tyler). The jur district
# code 000 was confirmed from a live Datalet.aspx URL. Its parcels are 14-character
# alphanumeric tokens (e.g. "A0000001"), so numeric_parcel_ids=False like Clermont.
# Re-verified live (an owner search returned result rows): the datalet detail uses
# the Public Access split layout with numbered labels ("Owner 1", "Address 1"), so
# detail_profile=PUBLIC_ACCESS like Clermont — not the CLASSIC default.
BUTLER = IasWorldSiteConfig(
    source_id="us-oh-butler-auditor",
    county="Butler County",
    state="OH",
    name="Butler County, Ohio Auditor Property Search",
    base_url="https://propertysearch.bcohio.gov/",
    district_code="000",
    numeric_parcel_ids=False,
    detail_profile=DetailProfile.PUBLIC_ACCESS,
    owner="Butler County Auditor",
    priority=230,
)

OH_IASWORLD_SITES: list[IasWorldSiteConfig] = [
    FRANKLIN,
    CLERMONT,
    BUTLER,
]
