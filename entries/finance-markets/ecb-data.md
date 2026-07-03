---
id: ecb-data
name: ECB Data Portal (SDMX API)
domain: finance-markets
entry_kind: time-series
description: European Central Bank statistical warehouse (exchange rates, interest rates, monetary aggregates, balance of payments) served as time series via an SDMX 2.1 REST API.
homepage_url: https://data.ecb.europa.eu/
docs_url: https://data.ecb.europa.eu/help/api/overview
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: ESCB-Free-Reuse
rate_limit: "no published hard limit; fair-use, gzip/compression encouraged for large pulls"
bulk_available: true
frequency: "varies by dataflow (daily for EXR to quarterly for BOP/GFS)"
lag: "varies by dataflow; daily reference rates published ~16:00 CET same day"
geography: [euro-area, EU, global]
join_keys:
  - ISO_4217
  - ISO_2
  - DATE
primary_keys:
  - ECB_DATAFLOW_ID
  - ECB_SERIES_KEY
join_key_fields:
  - join_key: ISO_4217
    fields: [CURRENCY, CURRENCY_DENOM]
  - join_key: ISO_2
    fields: [REF_AREA, COUNTERPART_AREA]
  - join_key: DATE
    fields: [TIME_PERIOD]
mcp_status: mcp-needed-high-value
agent_use_cases:
  - euro exchange-rate lookup
  - policy and market interest-rate series
  - monetary aggregate retrieval
  - balance-of-payments panels
  - macro time-series joins by currency and country
access_test:
  command: "curl -sf 'https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=1&format=jsondata'"
  expected_status: 200
  expected_fields: [header, dataSets, structure]
last_verified: 2026-07-02
build_priority: medium
---

# ECB Data Portal (SDMX API)

## Why this source matters

The European Central Bank publishes the Eurosystem's official statistics (daily euro foreign-exchange reference rates, ECB policy and money-market interest rates, monetary aggregates, bank balance-sheet items, balance of payments, government finance, securities and inflation series) through the ECB Data Portal. Programmatic access is a SDMX 2.1 RESTful web service at `https://data-api.ecb.europa.eu/service`. It is the authoritative free source for euro-area macro and monetary time series, the counterpart to the US Fed's FRED. Secondary domain: government-open-data (it is an EU-institution open-data publisher).

## Agent use cases

- euro exchange-rate lookup
- policy and market interest-rate series
- monetary aggregate retrieval
- balance-of-payments panels
- macro time-series joins by currency and country

## Join strategy

ECB series are addressed by an SDMX series key, an ordered dot-delimited tuple of dimension values whose positions are defined per dataflow (e.g. `EXR` key `D.USD.EUR.SP00.A` = FREQ.CURRENCY.CURRENCY_DENOM.EXR_TYPE.EXR_SUFFIX). The registry-canonical join keys the payloads expose are `ISO_4217` (the `CURRENCY` / `CURRENCY_DENOM` dimensions), `ISO_2` (the `REF_AREA` / `COUNTERPART_AREA` dimensions), and `DATE` (the `TIME_PERIOD` observation dimension). Which dimensions are present depends on the dataflow; `EXR` carries currencies, most macro dataflows carry a reference area.

Source-internal identifiers, the dataflow id (`EXR`, `BSI`, `ICP`, `MIR`, `BOP`, `IRS`, `GFS`) and the full series key, live in `primary_keys`; use them for direct ECB lookups, not cross-source joins. Pair with FRED and OECD for cross-central-bank macro joins on `ISO_4217` + `DATE`, and with Eurostat on `ISO_2` + `DATE`.

Caveat: the ECB `CL_AREA` reference-area codelist is mostly ISO 3166 alpha-2 but includes non-ISO aggregate codes (`U2` euro area, `I8`, `B0`, etc.); those rows will not join cleanly to a strict ISO_2 registry and need filtering.

## Access notes

Base entry point: `https://data-api.ecb.europa.eu/service`. Data resource path is `data/{flowRef}/{key}?{params}`; e.g. the euro/USD daily reference rate is `data/EXR/D.USD.EUR.SP00.A`. Discover structure via `dataflow/ECB/{flow}`, `datastructure/`, and `codelist/` endpoints. Formats are negotiated by `Accept` header or `?format=` (`genericdata`/`structurespecificdata` SDMX-ML, `jsondata` SDMX-JSON, `csvdata` CSV). Useful params: `startPeriod`, `endPeriod`, `updatedAfter`, `firstNObservations`, `lastNObservations`, `detail`. No API key or account required; the portal also offers full-dataset CSV bulk downloads. No hard published rate limit, but the ECB asks callers to enable gzip and avoid hammering; wide wildcard series requests can return very large payloads.

## MCP / connector notes

No known ECB or generic-SDMX MCP server. High value: any agent doing euro-area macro, FX, or rates work wants this, and the same connector would serve other SDMX providers (Eurostat, OECD, BIS, IMF) with only an endpoint swap. Suggested surface: `search_dataflows`, `get_dataflow_structure` (return dimension ids + codelists so the caller can build a key), `get_series` (flowRef + key + period window), `get_latest_observation`, `list_codelist`. The connector must abstract over the positional dot-key syntax (let callers pass named dimension filters), reshape SDMX-JSON's dimension-index arrays into flat `{date, value}` records, and cap/paginate wildcard queries.

## Review notes

- New license short name candidate: `ESCB-Free-Reuse`. The ESCB subscribes to a policy of free access and free reuse of publicly released statistics on the condition that the ECB/ESCB is cited as the source; third-party data embedded in ECB releases needs the originator's permission. No SPDX code exists. Recommend adding `ESCB-Free-Reuse` to the canonical license short-name list (analogous to `ECDC-Public-Data`).
- `ISO_2` mapping is approximate: the `CL_AREA` codelist mixes ISO 3166 alpha-2 with ECB aggregate area codes (`U2`, `I8`, etc.). Flagged for the join-graph so consumers filter aggregates before joining to strict-ISO sources.
- Dataflow ids and series keys are source-native and central-bank-specific, kept in `primary_keys`; no new canonical join key proposed.
