---
id: bts-port-performance
name: BTS Port Performance Freight Statistics
domain: government-open-data
entry_kind: mixed
description: US DOT program publishing nationally-consistent throughput and capacity metrics (TEU, tonnage, dry bulk) for the largest US ports, hosted as Socrata datasets plus annual reports to Congress.
homepage_url: https://www.bts.gov/ports
docs_url: https://www.bts.gov/PPFS-Tech-Docs
type:
  - socrata
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "no hard limit unauthenticated; optional Socrata app token lifts throttling under load"
bulk_available: true
frequency: "annual report to Congress; underlying Socrata datasets refreshed monthly-to-annually by series"
lag: "months (container/tonnage source data lags observation by roughly a quarter)"
geography: [USA]
structure: time-series
revisions_possible: true
pit_reconstructable: false
join_keys:
  - DATE
primary_keys:
  - SOCRATA_DATASET_4X4
join_key_fields:
  - join_key: DATE
    fields: [port, year, month]
mcp_status: api-direct-sufficient
agent_use_cases:
  - port throughput trend analysis
  - container volume (TEU) time series
  - supply-chain congestion monitoring
  - freight tonnage ranking by port
  - dry bulk capacity lookup
access_test:
  command: "curl -sf 'https://data.bts.gov/resource/rd72-aq8r.json?$limit=2'"
  expected_status: 200
  expected_fields: [port, los_angeles_ca, port_of_ny_nj, savannah_ga]
last_verified: 2026-07-03
build_priority: low
---

# BTS Port Performance Freight Statistics

## Why this source matters

The Port Performance Freight Statistics Program (PPFSP), run by the US DOT Bureau of Transportation Statistics, is the federal government's mandated source (FAST Act, 2015) for nationally-consistent performance measures at the largest US ports by tonnage, container, and dry bulk. It reports annually to Congress on port capacity and throughput and publishes the underlying series on the BTS Data Inventory (`data.bts.gov`), a Socrata open-data portal. An agent building freight, supply-chain, or trade-flow context wants this for container volume (TEU), total and commodity-level tonnage, dry bulk, and port-capacity metrics with an authoritative US-government provenance. Secondary relevance to `finance-markets` (freight/shipping macro signals) and `geospatial` (port-of-entry locations).

## Agent use cases

- port throughput trend analysis
- container volume (TEU) time series
- supply-chain congestion monitoring
- freight tonnage ranking by port
- dry bulk capacity lookup

## Join strategy

The only canonical registry key this source exposes cleanly is `DATE` (ISO-8601 period). In the flagship Monthly TEU dataset (`rd72-aq8r`) the temporal value lives in the mislabelled `port` column (it holds dates such as `1/1/2019`); annual tables carry a `year` column instead, so `DATE` maps to `[port, year, month]` across the family.

Ports themselves are identified only by human-readable name-plus-state strings (`Los Angeles, CA`, `Port of NY & NJ`, `NWSA (Seattle & Tacoma, WA)`) rather than any coded identifier, so there is no clean port-code join key to expose. See Review notes for a proposed `US_PORT_CODE` canonical key. Each Socrata sub-dataset is uniquely addressed by its 4x4 dataset id (`rd72-aq8r`, `sn74-xpkp`, `iqfi-cuyv`, etc.), recorded here as the source-native `SOCRATA_DATASET_4X4` primary key. Pair with USACE Waterborne Commerce or Census USA Trade for coded port joins once a port-code key exists; pair on `DATE` with freight-rate and macro series.

## Access notes

Data is served through the Socrata SODA API at `https://data.bts.gov/resource/<4x4>.json`. No auth required; an optional Socrata app token (`X-App-Token` header) removes throttling under sustained load. SODA supports SoQL query params (`$select`, `$where`, `$limit`, `$order`) and pages at 50,000 rows. Key datasets: Monthly TEU (`rd72-aq8r`), Top 25 Container Ports by TEU (`sn74-xpkp`), Top 25 Ports by Total Tonnage (`iqfi-cuyv`), Top 25 Ports by Dry Bulk Tonnage (`b99s-dekj`), Port Throughput / Capacity Metrics (`8sfc-juwb`, `a54a-9hsb`). Formats: JSON, CSV, XML, RDF via the export suffix. Per-port PDF fact sheets and the annual Report to Congress (PDF) are download-only on `bts.gov/ports`. Gotcha: the wide/pivoted layout (ports as columns, dates as rows) in some datasets means you often reshape client-side, and column field names are snake_cased port names, not codes.

## MCP / connector notes

No source-specific MCP. The SODA API is a clean, widely-standardised REST surface and generic Socrata/SODA tooling already covers discovery and querying, so `api-direct-sufficient`. A connector, if built, would abstract over: catalog discovery (`api.us.socrata.com/api/catalog/v1?domains=data.bts.gov`), 4x4-to-name resolution, wide-to-long reshaping of the pivoted TEU/tonnage tables, and SoQL passthrough.

## Review notes

Potential new join key for review: `US_PORT_CODE`
  Entity type: seaport / port_of_entry
  Pattern: no single standard in this source; candidates are Census Schedule D port-of-entry codes (4-digit) or USACE port codes / UN/LOCODE. This source exposes only free-text port names, so the key would be materialised by mapping names to a coded scheme.
  Other datasets that would use it: USACE Waterborne Commerce, Census USA Trade Online, CBP/Census Schedule D port lists, AIS/vessel-port datasets.

License: Socrata metadata reports "Public Domain" for these datasets; mapped to `US-Government-Public-Domain` (federal work under 17 USC 105). No new short name introduced.

`SOCRATA_DATASET_4X4` is recorded as a source-native primary key (it identifies datasets, not row entities); not proposed for the canonical registry.
