from __future__ import annotations

from titlemcp_platform_iasworld import AuditorSearchMode, DetailProfile, IasWorldSiteConfig

# The table of Ohio county auditor sites that run the Tyler iasWorld platform.
# Adding a county is a config entry here (plus a fixture-backed contract test and
# a sample) — the scraping/canonical logic lives in titlemcp-platform-iasworld.
#
# Counties confirmed on iasWorld but not yet enabled (need a captured fixture):
# Montgomery, Stark, Butler, Lucas, Summit, Lake. See
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

# Summit County (Fiscal Office) runs iasWorld Public Access, but instead of the
# separate address/owner/parid search pages it serves a single unified
# "realprop" search — confirmed live: the only reachable search link is
# search/commonsearch.aspx?mode=realprop and the footer reads "Powered by
# iasWorld Public Access". commonsearch.aspx is the same ASP.NET handler for
# every mode; the platform client GETs the realprop form, carries forward all of
# its hidden inputs, and overlays the standard inp* fields, so routing every
# search mode to "realprop" via mode_map is a config-only change — no new
# scraper. The unified page also uses the split Public Access datalet layout, so
# detail_profile=PUBLIC_ACCESS (same as Clermont).
#
# NEEDS-VERIFICATION: the live realprop search FORM could not be captured (the
# site was returning a maintenance/disclaimer page during recon), so the jur
# district code (defaulted to "000"), parcel format (defaulted alphanumeric, the
# safe superset), and the realprop form field names are unconfirmed against live
# data. See docs/OHIO_AUDITOR_EXPANSION.md for the open items before enabling.
SUMMIT = IasWorldSiteConfig(
    source_id="us-oh-summit-auditor",
    county="Summit County",
    state="OH",
    name="Summit County, Ohio Fiscal Office Property Search",
    base_url="https://propertyaccess.summitoh.net/",
    district_code="000",
    # realprop is a unified search replacing the per-mode pages, so every search
    # mode resolves to mode=realprop on commonsearch.aspx.
    mode_map={
        AuditorSearchMode.ADDRESS: "realprop",
        AuditorSearchMode.OWNER: "realprop",
        AuditorSearchMode.PARCEL_ID: "realprop",
    },
    # Alphanumeric is the safe superset until live parcels are captured: it
    # preserves any letters/dots a numeric-only compaction would silently drop.
    numeric_parcel_ids=False,
    detail_profile=DetailProfile.PUBLIC_ACCESS,
    owner="Summit County Fiscal Office",
    priority=230,
)

OH_IASWORLD_SITES: list[IasWorldSiteConfig] = [
    FRANKLIN,
    CLERMONT,
    SUMMIT,
]
