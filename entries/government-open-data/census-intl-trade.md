---
id: census-intl-trade
name: US Census International Trade API
domain: government-open-data
entry_kind: panel
description: Monthly US import and export statistics by commodity, country, district, port, and state, from the Census Bureau's foreign-trade program.
homepage_url: https://www.census.gov/data/developers/data-sets/international-trade.html
docs_url: https://www.census.gov/foreign-trade/reference/guides/Guide_to_International_Trade_Datasets.pdf
type:
  - rest-api
  - web-ui
auth_required: api-key-free
cost: free
license: US-Government-Public-Domain
rate_limit: "no key: 500 queries/day per IP; with free key: effectively unlimited for normal use"
bulk_available: false
frequency: monthly
lag: "~35 days after the reference month (FT-900 release day); annual revisions each April"
release_lag_days: 35
revisions_possible: true
pit_reconstructable: false
structure: panel
geography: [USA]
join_keys:
  - DATE
primary_keys:
  - E_COMMODITY
  - I_COMMODITY
  - CTY_CODE
  - PORT
  - DISTRICT
  - STATE
join_key_fields:
  - join_key: DATE
    fields: [time, YEAR, MONTH]
mcp_status: mcp-exists
mcp_maturity: official
mcp_package:
  - "github.com/uscensusbureau/us-census-bureau-data-api-mcp"
mcp_notes: >
  Official Census Bureau Data API MCP covers the whole api.census.gov surface, including
  the timeseries/intltrade endpoints. General-purpose; no trade-specific tooling for
  Schedule-C country codes or HS-level rollups.
agent_use_cases:
  - trade-flow lookup by HS commodity
  - import/export values by trading partner
  - port- and district-level trade volumes
  - supply-chain and tariff-exposure analysis
  - monthly trade-balance time series
access_test:
  command: "curl -sf 'https://api.census.gov/data/timeseries/intltrade/exports/hs?get=CTY_CODE,CTY_NAME,ALL_VAL_MO,E_COMMODITY&YEAR=2013&MONTH=12&COMM_LVL=HS2&E_COMMODITY=01&key=${CENSUS_API_KEY}'"
  expected_status: 200
  expected_fields: [CTY_CODE, CTY_NAME, ALL_VAL_MO, E_COMMODITY]
last_verified: 2026-07-03
build_priority: medium
notes: "access_test not executed; requires ${CENSUS_API_KEY}. Endpoint returns 302 -> Missing Key page without a valid key."
---

# US Census International Trade API

## Why this source matters

The Census Bureau's foreign-trade program is the authoritative source for official US merchandise trade statistics, the same numbers behind the monthly FT-900 trade-balance release. The International Trade API exposes monthly import and export values, quantities, and shipping-mode breakdowns from January 2013 to present, sliced by commodity classification (Harmonized System, NAICS, SITC, End-use, USDA, Advanced Technology), by trading-partner country, and by US district, port, and state. For an agent doing supply-chain, tariff-exposure, or macro trade-balance work, this is the primary US customs-based trade dataset, free and machine-readable. It sits in `government-open-data` but is equally useful for `finance-markets` macro analysis.

## Agent use cases

- trade-flow lookup by HS commodity
- import/export values by trading partner
- port- and district-level trade volumes
- supply-chain and tariff-exposure analysis
- monthly trade-balance time series

## Join strategy

The only canonical join key this source cleanly exposes is `DATE` (via `time`, plus `YEAR` + `MONTH`), so it joins to other monthly time series on the reporting month.

Every other identifier here is Census-native and does not map to a registry key without a crosswalk. `E_COMMODITY` / `I_COMMODITY` are Harmonized System codes (2/4/6/10 character), but there is no canonical `HS_CODE` in the registry yet (flagged below). `CTY_CODE` is a 4-character Census Schedule C country code, NOT ISO 3166; joining to `ISO_2` / `ISO_3` sources requires the Census country-code-to-ISO crosswalk. `PORT` (4-char Schedule D), `DISTRICT` (2-char), and `STATE` are Census foreign-trade geography codes, also non-standard. Treat all of these as `primary_keys` for source-internal filtering, not cross-source joins, until a crosswalk or new canonical key exists.

## Access notes

Base URLs: `https://api.census.gov/data/timeseries/intltrade/exports/{type}` and `.../imports/{type}`, where `{type}` is one of `hs`, `naics`, `enduse`, `sitc`, `usda`, `hitech`, `statehs`, `statenaics`, `porths` (imports adds `porths`/`district` variants). Hit `exports/hs` first with a `get=` variable list plus `YEAR`, `MONTH`, and a `COMM_LVL` filter (`HS2`/`HS4`/`HS6`/`HS10`).

A free API key is required: without one the endpoint 302-redirects to a "Missing Key" page. Sign up at `https://api.census.gov/data/key_signup.html` and pass it as `&key=...`. Per-endpoint variable lists live at `.../variables.html`; valid code values at `.../{var}.json`. The interactive query builder at `census.gov/foreign-trade/api_tool.html` is the fastest way to discover valid parameter combinations. No bulk snapshot; page through the API by month and commodity level.

## MCP / connector notes

The official `github.com/uscensusbureau/us-census-bureau-data-api-mcp` server wraps the entire Census Data API, so the intltrade timeseries endpoints are reachable through it. It is general-purpose: it does not abstract over Schedule-C/Schedule-D code vocabularies, HS-level rollups, or the exports-vs-imports variable-name asymmetry (`E_COMMODITY` vs `I_COMMODITY`, `ALL_VAL_MO` vs `GEN_VAL_MO`). A trade-focused connector would add: HS/country/port code resolution, a Census-to-ISO country crosswalk, and monthly-series pagination helpers.

## Review notes

Potential new join key for review: HS_CODE
  Entity type: traded_commodity
  Pattern: `^[0-9]{2}([0-9]{2}([0-9]{2}([0-9]{4})?)?)?$` (2/4/6/8/10-digit Harmonized System code)
  Other datasets that would use it: UN Comtrade, USA Trade Online, USITC DataWeb, EU Eurostat Comext, and any customs/tariff dataset. High cross-source utility for trade analysis.

Census `CTY_CODE` is a 4-character Schedule C country code, not ISO. If a Census-country-to-ISO crosswalk is added elsewhere in the registry, this source could then expose `ISO_2`/`ISO_3` transitively. Flagged rather than mapped to avoid a false ISO join.

License recorded as `US-Government-Public-Domain` (17 USC 105); confirm no residual redistribution nuance in the Census API Terms of Service.
