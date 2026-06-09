---
id: eia-open-data
name: EIA Open Data
domain: finance-markets
entry_kind: mixed
description: US Energy Information Administration's REST API and bulk files covering energy production, consumption, prices, and forecasts across electricity, petroleum, natural gas, coal, nuclear, and international markets.
homepage_url: https://www.eia.gov/opendata/
docs_url: https://www.eia.gov/opendata/documentation.php
type:
  - rest-api
  - bulk-download
auth_required: api-key-free
cost: free
license: US-Government-Public-Domain
rate_limit: "no published hard cap; standard practice is to keep concurrent requests modest"
bulk_available: true
frequency: twice-daily for most series; weekly/monthly/annual underlying cadence varies by route
lag: "minutes for real-time series; weeks to months for survey-driven series"
geography: [USA, global]
join_keys:
  - DATE
  - ISO_3
  - US_STATE_CODE
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Self-describing metadata API + thousands of series. A Skill-based wrapper that walks
  the route tree, inspects facets, and pulls series by id is more useful than a hand-coded
  MCP per route. Suggested surface: walk_routes, inspect, query, bulk_fetch.
agent_use_cases:
  - electricity price time series
  - natural gas storage signal monitoring
  - petroleum spot price forecasting input
  - state-level energy demand panel
  - macro energy supply/demand signal construction
last_verified: 2026-06-09
build_priority: medium
notes: Multi-dataset provider. The 11 top-level route trees are electricity, petroleum, natural-gas, coal, nuclear, total-energy, international, steo, aeo, seds, co2-emissions; agents discover sub-datasets and field schemas via the v2 metadata endpoints.
---

# EIA Open Data

## Why this source matters

EIA's open data API and bulk files cover energy production, consumption, prices, and forecasts across electricity, petroleum, natural gas, coal, nuclear, and international markets. The v2 API is hierarchical and self-describing: routes return their child routes, available facets, data columns, and frequencies, which lets the schema be discovered rather than hand-coded. For quant/backtest agents, petroleum prices, natural gas storage, electricity retail series, and STEO forecasts are workhorse signals.

11 top-level route trees and thousands of underlying series. Sub-datasets are not modeled individually in this registry; agents walk the v2 metadata endpoints to discover them.

## Agent use cases

- electricity price time series
- natural gas storage signal monitoring
- petroleum spot price forecasting input
- state-level energy demand panel
- macro energy supply/demand signal construction

## Join strategy

`DATE` (period) is universal across all sub-datasets. `ISO_3` is the country dimension on international routes. `US_STATE_CODE` (two-letter USPS code) is the state granularity on electricity/SEDS routes.

EIA-internal codes for sectors (RES, COM, IND, TRA), products (CL, GA, HO), and series IDs (RWTC, WTIPUUS, COPRPUS) are not in the canonical registry; agents fetch their definitions per-route from the v2 metadata response.

Common pairings: FRED (cross-validate WTI spot, retail electricity), World Bank Open Data (international cross-country at lower cadence), Alpha Vantage / Polygon (real-time prices against EIA spot benchmarks).

## Access notes

Get a free key at https://www.eia.gov/opendata/register.php. Pass via query string `?api_key=YOUR_KEY`. Base URL `https://api.eia.gov/v2`.

The API is hierarchical. GET a route node (e.g. `/electricity/retail-sales`) and the response includes the available facets, data columns, and frequencies. GET the `/data` sub-route to query: `/electricity/retail-sales/data?data[]=price&facets[stateid][]=CA&frequency=monthly`. Pagination via `offset` and `length` (max 5000 per page).

Bulk: zipped JSON files at https://api.eia.gov/bulk/, refreshed twice daily. Useful for full-history backfills of high-volume series.

Gotchas:

- STEO mixes historical and forecast periods on the same axis; use the metadata endpoint to find the forecast horizon per series.
- Series-level metadata (units, descriptions) is returned per row; agents should cache it per series rather than reading from every row.
- Some legacy "v1" series IDs are deprecated; the v2 route tree is canonical.
- International data uses EIA's own country aggregates ("OPEC", "EUR", "WORLD") alongside ISO-3.

## MCP / connector notes

No dedicated EIA MCP. Given the route-tree shape and the breadth of series, a Skill-based wrapper that walks the metadata tree and pulls series by id is more useful than a hand-coded MCP per route. Suggested surface: `walk_routes(prefix)`, `inspect(route)` (returns facets + data columns + frequencies), `query(route, data, facets, frequency, start, end)`, `bulk_fetch(route)`.

## Review notes

None.
