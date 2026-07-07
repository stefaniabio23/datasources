---
id: bts-faf
name: BTS Freight Analysis Framework (FAF)
domain: government-open-data
entry_kind: panel
description: US origin-destination freight flow estimates by commodity, mode, and FAF zone, in tons, value, and ton-miles across historical, base, and forecast years.
homepage_url: https://www.bts.gov/faf
docs_url: https://faf.ornl.gov/faf5/
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "none documented; static file downloads"
bulk_available: true
frequency: "annual provisional updates; new base year roughly every 5 years, aligned to the Commodity Flow Survey"
lag: "base year trails the reference year by 2-4 years; annual provisional estimates trail by ~1 year"
geography: [USA]
join_keys:
  - DATE
primary_keys:
  - FAF_ZONE
  - SCTG2
  - DMS_MODE
join_key_fields:
  - join_key: DATE
    fields: [tons_2017, tons_2022, value_2022, tmiles_2022]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - freight flow lookup by commodity and mode
  - domestic origin-destination tonnage and value estimates
  - modal share analysis (truck, rail, water, air, pipeline)
  - long-range freight demand forecasts to 2050
  - commodity-level trade gateway analysis
access_test:
  command: "curl -sfI -A 'Mozilla/5.0' 'https://faf.ornl.gov/faf5/data/download_files/FAF5.7.1_State.zip' -o /dev/null -w '%{http_code}'"
  expected_status: 200
last_verified: 2026-07-03
structure: panel
pit_reconstructable: false
revisions_possible: true
build_priority: low
---

# BTS Freight Analysis Framework (FAF)

## Why this source matters

FAF is the authoritative public estimate of freight moving on the US transportation system, produced by Oak Ridge National Laboratory for the Bureau of Transportation Statistics and the Federal Highway Administration. It integrates the Commodity Flow Survey with trade, agriculture, and other sources into a single origin-destination matrix: for each pair of FAF zones, each SCTG commodity group, and each transport mode, it reports tonnage (thousand tons), value (million dollars), and ton-miles (million ton-miles). FAF5 covers historical years (1997-2012), a 2017 base year with annual provisional estimates through 2024, and mid/high/low forecasts out to 2050. It is the standard reference class for US domestic freight demand and modal share. Secondary relevance to `finance-markets` (commodity and logistics demand signals) and `geospatial` (FAF zone and CFS metro-area shapefiles).

## Agent use cases

- freight flow lookup by commodity and mode
- domestic origin-destination tonnage and value estimates
- modal share analysis (truck, rail, water, air, pipeline)
- long-range freight demand forecasts to 2050
- commodity-level trade gateway analysis

## Join strategy

The only canonical registry key FAF exposes is `DATE`: every measure is published as year-suffixed columns (`tons_2022`, `value_2022`, `tmiles_2022`, plus historical and forecast years), so the year is the join axis for stitching FAF against macro or trade time series.

FAF's other three dimensions are source-native codes with no canonical registry key today, so they stay in `primary_keys`: `FAF_ZONE` (the origin/destination `dms_orig`, `dms_dest`, `fr_orig`, `fr_dest` fields; ~132 domestic regions plus international gateways), `SCTG2` (2-digit Standard Classification of Transported Goods commodity group in `sctg2`), and `DMS_MODE` (mode code in `dms_mode`: 1 truck, 2 rail, 3 water, 4 air, 5 multiple modes and mail, 6 pipeline, 7 other/unknown). These three are flagged as new-key candidates below; SCTG in particular is shared by the Commodity Flow Survey and Census trade data, so it has clear cross-source utility.

The experimental county-level product (`bts.gov/faf/county`) disaggregates flows to US county FIPS codes, so `FIPS` is genuinely present there. It is left out of `join_keys` because the exact county-file column names were not verified from published docs; confirm against `FAF5_metadata.xlsx` before adding.

## Access notes

Primary path is bulk download, not an API. Grab the regional or state CSV/zip from the FAF5 data page (`faf.ornl.gov/faf5/`); the state file (`FAF5.7.1_State.zip`, ~150-330 MB depending on forecast bands) carries origin-destination tonnage and value by commodity and mode. Field definitions live in `FAF5_metadata.xlsx`. The Data Tabulation Tool (`faf.ornl.gov/faf5/dtt_total.aspx`) is a web-UI for custom summary tables without downloading the full matrix. No auth, no rate limit, static files. Check freshness by comparing the version string on the data page (currently FAF5.7.1) against your local copy; version bumps re-estimate prior years, so treat values as revisable rather than point-in-time stable. FAF zone and CFS metro-area shapefiles are bundled for mapping.

## MCP / connector notes

No MCP exists. A connector would wrap the bulk state/regional files into a queryable interface: `get_flow(origin_zone, dest_zone, sctg, mode, year)`, `modal_share(zone, year)`, `commodity_totals(sctg, year)`, `forecast(zone_pair, sctg, year)`, plus a zone/commodity/mode code lookup. The tricky parts are abstracting the year-suffixed wide-column layout into tidy long form, resolving FAF zone codes to names and geographies, and reconciling the regional vs state vs experimental county products. Low build priority: narrow audience within this registry (few freight entries) and the data is a static annual file rather than a live feed.

## Review notes

Potential new join keys for review:

Potential new join key for review: SCTG_CODE
  Entity type: commodity_classification
  Pattern: 2-digit Standard Classification of Transported Goods code, "01".."43" (FAF uses 2-digit sctg2; CFS also publishes 3/4-digit)
  Other datasets that would use it: Census Commodity Flow Survey, Census USA Trade / USATrade, USDA freight statistics

Potential new join key for review: FAF_ZONE
  Entity type: us_freight_region
  Pattern: 3-digit FAF region code (~132 domestic zones plus international gateway codes); maps to state FIPS + CFS metro areas
  Other datasets that would use it: Commodity Flow Survey, other FAF-derived freight models

Potential new join key for review: FAF_MODE
  Entity type: transport_mode
  Pattern: single-digit domestic mode code (1 truck, 2 rail, 3 water, 4 air, 5 multiple modes and mail, 6 pipeline, 7 other/unknown)
  Other datasets that would use it: Commodity Flow Survey, BTS modal statistics

The experimental county-level product exposes `FIPS` (a canonical registry key) but exact county-file column names were not verified; confirm against `FAF5_metadata.xlsx` before adding `FIPS` to `join_keys`. License is US federal public-domain work under 17 USC 105 (`US-Government-Public-Domain`); ORNL produces it under contract to FHWA/BTS, which does not change the public-domain status.
