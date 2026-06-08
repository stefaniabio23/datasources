---
id: world-bank-open-data
name: World Bank Open Data
domain: government-open-data
description: World Bank's free catalogue of global development statistics covering 16,000+ indicators across 200+ economies, with REST API, bulk downloads, and an official MCP for the newer Data360 platform.
homepage_url: https://data.worldbank.org/
docs_url: https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "no published per-key limit; anonymous; backs off on abusive volume"
bulk_available: true
frequency: "varies by indicator (annual, quarterly, monthly)"
lag: "months-to-years (most macro indicators publish 6-18 months after period end)"
geography: [global]
join_keys:
  - ISO_2
  - ISO_3
primary_keys:
  - WB_INDICATOR_CODE
  - WB_TOPIC_ID
  - WB_SOURCE_ID
  - WB_INCOMELEVEL
  - WB_LENDINGTYPE
  - WB_REGION_CODE
join_key_fields:
  - join_key: ISO_2
    fields: [country.id, iso2Code]
  - join_key: ISO_3
    fields: [countryiso3code, id]
mcp_status: mcp-exists
mcp_maturity: official
mcp_package:
  - github.com/worldbank/data360-mcp
  - github.com/cyanheads/worldbank-mcp-server
  - github.com/bhayanak/worldbank-mcp-server
mcp_notes: >
  Official worldbank/data360-mcp targets the newer Data360 platform
  (data360api.worldbank.org), not the classic /v2 Indicators API. Community
  MCPs (cyanheads, bhayanak) wrap the classic v2 endpoint. Both surfaces
  share most indicator codes.
agent_use_cases:
  - country macro lookup
  - cross-country indicator comparison
  - long-run time series for GDP, population, poverty
  - development indicator search by topic
  - economy classification (income group, region)
access_test:
  command: "curl -sf 'https://api.worldbank.org/v2/country/BR/indicator/NY.GDP.MKTP.CD?date=2022&format=json'"
  expected_status: 200
  expected_fields: [indicator, country, countryiso3code, date, value]
last_verified: 2026-06-08
build_priority: medium
---

# World Bank Open Data

## Why this source matters

The World Bank's open-data catalogue is the de facto reference for global development statistics: 16,000+ indicators across 200+ economies, with multi-decade time series (most series start 1960). Topics span economy (GDP, trade, debt), people (education, health, gender), planet (climate, environment), infrastructure, and digital access. CC-BY-4.0, no auth, free REST API plus bulk downloads. For any agent answering "how is country X doing on metric Y over time?", this is the canonical hub. Pairs naturally with IMF, OECD, and UN data sources.

## Agent use cases

- country macro lookup
- cross-country indicator comparison
- long-run time series for GDP, population, poverty
- development indicator search by topic
- economy classification (income group, region)

## Join strategy

World Bank uses both `ISO_2` (default in API paths, e.g. `/country/BR/`) and `ISO_3` (returned as `countryiso3code` in responses). Either works as a join key onto other country-level sources.

World-Bank-internal identifiers that are not in the canonical registry but matter inside the API:

- `WB_INDICATOR_CODE` (e.g. `NY.GDP.MKTP.CD`, `SP.POP.TOTL`, `SI.POV.DDAY`) — the indicator dotted-namespace. Stable across decades; treat as the source's primary key for time series.
- `WB_TOPIC_ID`, `WB_SOURCE_ID`, `WB_INCOMELEVEL`, `WB_LENDINGTYPE`, `WB_REGION_CODE` — taxonomies used for filtering. Use them for slicing inside World Bank, not for cross-source joins.

For aggregates (regions, income groups, lending categories), the API returns World-Bank-defined codes (`WLD`, `EAS`, `LIC`, `HIC`) that do not map cleanly onto ISO; treat those as source-internal.

## Access notes

**Base URL:** `https://api.worldbank.org/v2/`. Default response format is XML; always append `?format=json` for agent use. JSON-stat (`?format=jsonstat`) is available if you need a tighter shape for time-series.

**Path style:** two forms work, e.g. `/country/br/indicator/NY.GDP.MKTP.CD` or `/country?incomeLevel=LIC`. The path form is more common in examples.

**Pagination:** `per_page` defaults to 50; bump to 1000 for indicator scans. Use `page=N` for further pages. Total count is returned in the metadata envelope (first element of the JSON array).

**Time filters:** `?date=2000:2023` for ranges, `?mrv=5` for most-recent-N, `?mrnev=5` for most-recent-non-empty. `mrnev` is the right default for sparse indicators.

**Multi-entity queries:** semicolon-delimited, e.g. `/country/us;br;cn/indicator/SP.POP.TOTL;NY.GDP.MKTP.CD`.

**Bulk:** entire indicator series available as CSV/Excel/XML from `https://databank.worldbank.org/` (DataBank) and `https://datacatalog.worldbank.org/` (Data Catalog). Use bulk when scanning >100K observations; the API is fast enough for everything smaller.

**Gotchas:**

- No sorting in the API; results come back in default order (usually alphabetical by entity).
- Many indicators are sparse: ask for `mrnev` rather than a fixed year if you need a value, not a NULL.
- Indicator codes are stable but occasionally retired; check `sourceNote` and `lastupdated` metadata for staleness.
- Third-party datasets surfaced in the Data Catalog may have stricter licences than CC-BY-4.0; the umbrella terms only cover World-Bank-owned datasets.
- License attribution string per terms: "The World Bank: Dataset name: Data source (if known)".

## MCP / connector notes

Official MCP exists: `worldbank/data360-mcp` (Python, official, active development; no formal release yet). Exposes `data360_search_indicators`, `data360_get_data`, `data360_get_metadata`, `data360_get_disaggregation`, `data360_find_codelist_value`, `data360_list_indicators`. Crucially, it targets the newer Data360 unified platform (`data360api.worldbank.org`), not the classic `api.worldbank.org/v2` Indicators API. Most popular indicators exist in both surfaces with the same codes; agents needing legacy series should test both.

Community MCPs (`cyanheads/worldbank-mcp-server`, `bhayanak/worldbank-mcp-server`) wrap the classic v2 endpoint and may be a better fit when you need exact parity with `data.worldbank.org` browsable indicators.

## Review notes

- Potential new join keys for review:
  - `WB_INDICATOR_CODE` — Entity type: `development_indicator`. Pattern: dotted ASCII (`^[A-Z]{2}\.[A-Z0-9.]+$`). Other datasets that would use it: IMF SDMX (shares some codes), OECD data, FAO data via Data360. Worth registering if more global-stats sources land in the directory.
  - `WB_TOPIC_ID` — narrow utility, skip unless other sources adopt.
- The `worldbank/data360-mcp` is the official package but targets a different (newer) API surface than `data.worldbank.org`. Flagged in MCP notes; may warrant a second entry for Data360 if it diverges meaningfully.
- License is unambiguously CC-BY-4.0 for World-Bank-owned datasets, but the Data Catalog also surfaces partner datasets under heterogeneous terms. Per-dataset license check is on the consumer.
