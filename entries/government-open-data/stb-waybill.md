---
id: stb-waybill
name: STB Carload Waybill Sample
domain: government-open-data
entry_kind: event-stream
description: Stratified sample of U.S. rail carload waybills (commodity, tonnage, revenue, origin/destination) collected by the Surface Transportation Board from large freight railroads.
homepage_url: https://www.stb.gov/reports-data/waybill/
docs_url: https://stb.gov/wp-content/uploads/2023-STB-Waybill-Reference-Guide.pdf
type:
  - bulk-download
  - socrata
  - rest-api
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "Socrata SODA mirror: ~1000 rows/page default; add $$app_token for higher throughput"
bulk_available: true
frequency: annual
lag: "public-use file typically released 1-2 years after the data year"
geography: [USA]
structure: event-log
join_keys: []
agent_use_cases:
  - rail commodity flow analysis
  - origin-destination freight traffic
  - freight revenue and rate analysis
  - modal-shift and productivity studies
  - STCC-coded traffic lookup
access_test:
  command: "curl -sf 'https://agtransport.usda.gov/resource/xve5-xb56.json?$limit=1'"
  expected_status: 200
  expected_fields: [stcc, numberofcarloads, freightrevenue, originbea, terminationbea]
last_verified: 2026-07-03
build_priority: low
mcp_status: mcp-needed-low-value
---

# STB Carload Waybill Sample

## Why this source matters

The Surface Transportation Board (STB) collects a stratified sample of carload waybills from every U.S. rail carrier terminating 4,500+ revenue carloads a year, the authoritative microdata behind rate cases, costing systems, productivity studies, and exemption decisions for freight rail. Each record carries commodity (STCC), billed and actual tonnage, freight revenue, car type, routing, short-line miles, and origin/termination BEA economic areas, with expansion factors to inflate the sample to population totals. Two tiers exist: a masked, freely downloadable Public Use File (annual, 1996-present) and a Confidential Version available only by written application under 49 CFR Part 1244. Governed by the STB (an independent federal agency); the Public Use File is also republished by USDA on its Agricultural Transportation Open Data Platform as a Socrata dataset. Secondary relevance to finance-markets (rail volume and revenue as an economic-activity signal).

## Agent use cases

- rail commodity flow analysis
- origin-destination freight traffic
- freight revenue and rate analysis
- modal-shift and productivity studies
- STCC-coded traffic lookup

## Join strategy

The Public Use File exposes no canonical registry join key. Its structural identifiers are all rail-industry classifications not yet in the registry: `stcc` (Standard Transportation Commodity Code, with rolled-up `stcc4`/`stcc3`/`stcc2` levels and text descriptions), and origin/termination BEA economic-area codes (`originbea`, `terminationbea`). Carrier identity, the Standard Carrier Alpha Code (SCAC) and AAR Rule 260 railroad codes, is masked out of the Public Use File and appears only in the Confidential Version. Records carry `datayear` and `waybilldate` (maps loosely to the canonical `DATE`) but there is no stable per-waybill primary key in the public file. See Review notes for proposed new keys (`STCC`, `SCAC`, `BEA_AREA`).

## Access notes

Two paths. (1) STB bulk: the Public Use File is downloadable as annual ZIP archives from the STB waybill page, each shipped with a Reference Guide documenting the fixed-width record layout; the Confidential Version requires a written request published in the Federal Register with a 14-day objection window, a signed confidentiality agreement, one-year access, and mandatory data destruction on expiry. (2) USDA Socrata mirror: the Public Use File is queryable as SODA JSON/CSV at `https://agtransport.usda.gov/resource/xve5-xb56.json` (dataset id `xve5-xb56`), no auth; standard Socrata `$where`/`$select`/`$limit`/`$offset` filtering, and an app token lifts throttling. The Socrata mirror is the fastest programmatic route for the public data; use the STB ZIPs when you need the full documented record layout or years the mirror lacks. Freight revenue may be masked in some strata; use the exact and theoretical expansion factors (`exactexpansionfactor`, `theoreticalexpansionfactor`) to scale sample rows to population estimates.

## MCP / connector notes

No source-specific MCP. The Public Use File rides on generic Socrata (SODA), so a general Socrata connector plus the dataset id covers programmatic access; the clean REST/JSON surface makes a bespoke MCP low value. A useful wrapper would abstract the two tiers (public vs confidential), decode STCC codes to descriptions, resolve BEA area codes to names, and apply expansion factors automatically so callers get population estimates rather than raw sampled rows. The Confidential Version has no API at all, it is a manual application-and-download process.

## Review notes

`join_keys` is empty: none of this source's identifiers are in the canonical registry. Three candidates for review:

Potential new join key for review: STCC
  Entity type: commodity_class (rail freight)
  Pattern: 2-7 digit Standard Transportation Commodity Code (e.g. "29121"); hierarchical (2/3/4/5-digit rollups)
  Other datasets that would use it: USDA rail grain data, BTS/Freight Analysis Framework, AAR commodity reports, other STB filings

Potential new join key for review: SCAC
  Entity type: carrier (rail/motor/ocean)
  Pattern: 2-4 uppercase alpha characters assigned by AAR (e.g. "BNSF", "UP")
  Other datasets that would use it: FMCSA/DOT carrier data, ocean/rail intermodal manifests, BTS transportation datasets; NOTE masked in this Public Use File, present only in the Confidential Version

Potential new join key for review: BEA_AREA
  Entity type: us_economic_area (BEA economic areas / regions)
  Pattern: 3-digit BEA economic-area code (e.g. "010"); used here as origin/termination geography
  Other datasets that would use it: BEA regional accounts, FAF freight zones, other economic-geography sources

License is US federal public domain (17 USC 105) for the Public Use File; the Confidential Version is access-restricted by regulation and confidentiality agreement (not a redistribution license). No new domain or enum values needed.
