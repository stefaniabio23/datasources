---
id: census-building-permits
name: Census Building Permits Survey (BPS)
domain: government-open-data
entry_kind: panel
description: Monthly and annual counts of new privately-owned residential building permits authorized in the US, reported at national, state, CBSA, county, and place levels.
homepage_url: https://www.census.gov/construction/bps/
docs_url: https://www.census.gov/construction/bps/how_the_data_are_collected.html
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: none published (static file downloads)
bulk_available: true
frequency: monthly (plus year-to-date and annual releases)
lag: "monthly data released on the 17th workday of the following month; annual data lags ~5 months"
geography: [USA]
release_lag_days: 45
revisions_possible: true
pit_reconstructable: false
structure: panel
join_keys:
  - FIPS
  - DATE
primary_keys:
  - CBSA_CODE
  - CENSUS_PLACE_FIPS
join_key_fields:
  - join_key: FIPS
    fields: ["FIPS State Code", "FIPS County Code", "6-Digit ID (Census place code)"]
  - join_key: DATE
    fields: ["Survey Date (YYYYMM)", "Year", "Month"]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - housing supply tracking
  - local construction activity by county or metro
  - leading indicator for residential real estate
  - regional economic monitoring
access_test:
  command: "curl -sfI 'https://www2.census.gov/econ/bps/County/co2023a.txt'"
  expected_status: 200
last_verified: 2026-07-07
build_priority: medium
notes: "No official Census Data API for BPS; access is static bulk files under www2.census.gov/econ/bps/ plus Excel current-data downloads. access_test runs a HEAD against a stable annual county file."
---

# Census Building Permits Survey (BPS)

## Why this source matters

The Building Permits Survey, run by the US Census Bureau, is the authoritative count of new privately-owned residential building permits authorized by permit-issuing jurisdictions. Census collects voluntary monthly data from the jurisdictions that issue ~99% of US permits, imputes the remainder from annual submissions, and seasonally adjusts the result. Permits are a standard leading indicator for residential construction and regional housing supply, and the survey is one of the few Census products published at county and place granularity every month. It sits in `government-open-data`; the underlying content is also a `finance-markets` / real-estate leading indicator.

## Agent use cases

- housing supply tracking
- local construction activity by county or metro
- leading indicator for residential real estate
- regional economic monitoring

## Join strategy

BPS is a geography-by-time panel. The canonical join keys it exposes are `FIPS` (state and county codes carry each row's location; place files add a 6-digit Census place code) and `DATE` (survey month `YYYYMM` plus year and month columns). Join BPS to any FIPS-keyed county/state series (BLS QCEW, ACS, HUD, Zillow county aggregates) on `FIPS` + `DATE`.

CBSA (Core-Based Statistical Area) codes are the other primary geographic identifier the CBSA-level files carry, but there is no canonical `CBSA_CODE` key in the registry yet. It is flagged in `## Review notes` as a new-key candidate. Census place FIPS codes are held in `primary_keys` as source-native; they are a subspace of the broader `FIPS` scheme rather than a distinct canonical key.

## Access notes

There is no official Census Data API for BPS (unlike ACS/decennial, it is absent from `census.gov/data/developers/data-sets.html`). Two access paths:

- **Current Excel downloads** (2019-present, US / Region / State / CBSA), e.g. `https://www.census.gov/construction/bps/permitsbyusreg_cust.xls`, refreshed on the 17th workday each month.
- **Bulk fixed-width / delimited text files** under `https://www2.census.gov/econ/bps/` in `State/`, `County/`, `Place/`, `Metro/` subdirectories, named by geography + year + period (e.g. `County/co2023a.txt` for 2023 annual). Historical coverage runs back to 1995 (CSV/ASCII) and 1960 for US/region time series.

Fixed-width files need a column layout spec (documented per-directory); parse by position, not delimiter, for the older ASCII files. Values are revised in later releases, so pin the file vintage when reproducibility matters. No auth, no published rate limit; be polite with static-file requests.

## MCP / connector notes

No MCP exists. Low shared-audience value (housing/construction niche), so a dedicated connector is low priority. A useful surface would abstract over the file layout: `get_permits(geo_level, geo_id, period)` returning normalized rows, plus a `latest_release()` freshness check against the current Excel file. The connector must own the fixed-width column maps per subdirectory and the seasonally-adjusted vs not-adjusted distinction, and should expose the survey-date and revision flags so callers can handle restated values.

## Review notes

Potential new join key for review: `CBSA_CODE`
  Entity type: us_geography (Core-Based Statistical Area, OMB/Census metro + micropolitan areas)
  Pattern: `^[0-9]{5}$` (5-digit CBSA code)
  Other datasets that would use it: BLS metro employment, HUD, Zillow/Redfin metro series, ACS metro tables, FRED metro series. Broad cross-source utility; strong candidate for the geography section of `schema/join-keys.yaml`.

License is US federal work (Title 13), public domain; recorded as `US-Government-Public-Domain` (existing canonical short name, no new value needed).
