---
id: census-m3
name: Census M3 (Manufacturers' Shipments, Inventories & Orders)
domain: government-open-data
entry_kind: time-series
description: US Census Bureau monthly survey of manufacturers' value of shipments, new orders, unfilled orders, and inventories, by NAICS-based industry category, served via the Economic Indicators time series API.
homepage_url: https://www.census.gov/manufacturing/m3
docs_url: https://www.census.gov/data/developers/data-sets/economic-indicators.html
type:
  - rest-api
  - bulk-download
auth_required: api-key-free
cost: free
license: US-Government-Public-Domain
rate_limit: "free API key required for all data queries; no published per-key cap (fair-use). Metadata endpoints (variables.json, etc.) are keyless."
bulk_available: true
frequency: monthly
lag: "advance report ~4 weeks after the reference month; full report ~1 week after the advance; both revised in subsequent months"
geography: [USA]
join_keys:
  - DATE
primary_keys:
  - M3_CATEGORY_CODE
  - M3_DATA_TYPE_CODE
join_key_fields:
  - join_key: DATE
    fields: [time]
mcp_status: mcp-exists
mcp_maturity: official
mcp_package:
  - "github.com/uscensusbureau/us-census-bureau-data-api-mcp"
  - "github.com/cyanheads/census-mcp-server"
mcp_notes: >
  Official Census Bureau Data API MCP wraps the whole Census Data API, including
  the eits/m3 timeseries endpoint, so no M3-specific connector is needed. Gap: it
  is a generic Census-API surface, not an economic-indicator helper, so an agent
  must still know M3 category_code / data_type_code vocabulary to build a query.
agent_use_cases:
  - manufacturing demand nowcasting
  - durable-goods new-orders tracking
  - inventory-to-shipments ratio analysis
  - industrial macro context for markets
  - point-in-time indicator retrieval
access_test:
  command: "curl -sf 'https://api.census.gov/data/timeseries/eits/m3?get=cell_value,category_code,data_type_code,seasonally_adj,time&category_code=MTM&data_type_code=NO&time=2024&key=${CENSUS_API_KEY}'"
  expected_status: 200
  expected_fields: [cell_value, category_code, data_type_code, seasonally_adj, time]
last_verified: 2026-07-03
build_priority: medium
notes: "access_test not executed; requires a free ${CENSUS_API_KEY}. Host reachability confirmed: keyless data query 302-redirects to /data/missing_key.html, and the keyless metadata endpoint api.census.gov/data/timeseries/eits/m3/variables.json returns HTTP 200 with the 13-variable schema."
structure: time-series
pit_reconstructable: false
revisions_possible: true
release_lag_days: 34
---

# Census M3 (Manufacturers' Shipments, Inventories & Orders)

## Why this source matters

The M3 survey is the US Census Bureau's monthly read on the domestic manufacturing sector: value of shipments, new orders (net of cancellations), end-of-month unfilled orders (backlog), and total, materials, work-in-process, and finished-goods inventories. It is the primary source behind the closely watched "durable goods orders" and "factory orders" headlines, so it is a leading indicator for industrial demand and a standing input to nowcasting and business-cycle work. One free Census API key exposes the full series as JSON over HTTPS, in both seasonally adjusted and not-adjusted forms, back to 1992. Secondary domain: finance-markets, since new-orders and inventory-to-shipments prints move rate expectations and industrial equities.

## Agent use cases

- manufacturing demand nowcasting
- durable-goods new-orders tracking
- inventory-to-shipments ratio analysis
- industrial macro context for markets
- point-in-time indicator retrieval

## Join strategy

Only one canonical join key is exposed: `DATE`, carried by the `time` field in ISO-8601 form (monthly, `YYYY-MM`). Use it to align M3 with any other time series (FRED, BEA, BLS, EIA) on a common calendar spine.

Everything else that identifies an M3 cell is source-internal and lives in `primary_keys`. `M3_CATEGORY_CODE` (the API `category_code`, labelled "Industry list", e.g. `MTM` total manufacturing, plus durable and nondurable NAICS-based groupings) and `M3_DATA_TYPE_CODE` (the API `data_type_code`, e.g. `VS` value of shipments, `NO` new orders, `UO` unfilled orders, `TI` total inventories) together with `seasonally_adj` pin a single series. These are M3-native codes, not cross-source identifiers, so they stay out of `join_keys`.

The `category_code` values are Census M3 industry groupings derived from NAICS but published under M3's own code list, not raw NAICS strings. A canonical NAICS key would let M3 join to Census County Business Patterns / Economic Census, BLS QCEW, and BEA GDP-by-industry, but it would require a documented M3-category-to-NAICS crosswalk, so it is flagged in Review notes rather than mapped. See Review notes.

## Access notes

Base endpoint: `https://api.census.gov/data/timeseries/eits/m3`. A free API key (request at `https://api.census.gov/data/key_signup.html`) is now required for every data query; a keyless data request 302-redirects to `/data/missing_key.html`. Discover the vocabulary from the keyless metadata endpoints first: `.../m3/variables.json` (13 variables including `cell_value`, `category_code`, `data_type_code`, `seasonally_adj`, `error_data`, `time`), `.../m3/examples.html`, and `.../m3/geography.html` (US national only). A typical pull passes `get=cell_value,category_code,data_type_code,seasonally_adj,time` plus filters on `category_code`, `data_type_code`, and `time`. No published per-key rate cap; batch by time range rather than looping one month at a time.

For bulk or human use, the M3 site publishes monthly press-release PDFs from 1992 to present and Excel/CSV data files (including detailed nondurable-industry files from the June 2025 advance release onward). The API is the right surface for programmatic access; the site downloads are for full-report tables and documentation. The same series are also mirrored in FRED under the Census M3 release.

## MCP / connector notes

Covered by the official `uscensusbureau/us-census-bureau-data-api-mcp` server, which wraps the entire Census Data API (including `timeseries/eits/m3`) and pulls some metadata into a local Postgres for search; community servers such as `cyanheads/census-mcp-server` offer similar coverage. Known gap: these are generic Census-API surfaces, so the agent still supplies M3-specific `category_code` / `data_type_code` values. A thin economic-indicator helper (resolve human labels to M3 codes, expose `get_series(indicator, category, seasonally_adj, from, to)`, and abstract the always-key requirement) would remove that friction, but is low incremental value given the official MCP already reaches the endpoint.

## Review notes

Potential new join key for review: NAICS_CODE
  Entity type: industry_classification
  Pattern: ^[0-9]{2,6}$ (2-6 digit North American Industry Classification System)
  Other datasets that would use it: Census County Business Patterns, Census Economic Census, BLS QCEW, BEA GDP-by-industry, SEC EDGAR (SIC crosswalk). M3 publishes its own `category_code` industry groupings derived from NAICS, so a canonical NAICS key would require a documented M3-category-to-NAICS crosswalk before mapping. Same candidate was flagged on the `bea` entry; consolidate into one PR if adopted.

License: M3 statistics are US federal works in the public domain (mapped to `US-Government-Public-Domain`). The Census Data API terms request attribution to the U.S. Census Bureau and prohibit altering data precision; no redistribution restriction. Short name already used elsewhere in the registry.
