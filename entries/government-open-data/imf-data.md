---
id: imf-data
name: IMF Data
domain: government-open-data
entry_kind: mixed
description: The IMF's official statistics portal, macroeconomic and financial time series across datasets like IFS, Balance of Payments, Direction of Trade, Government Finance, CPI, and Financial Soundness, served over an SDMX 2.1 / 3.0 REST API.
homepage_url: https://data.imf.org/
docs_url: https://data.imf.org/en/Resource-Pages/IMF-API
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: IMF-Data-Terms
rate_limit: "no published per-key limit; anonymous public endpoint, throttles on abusive volume"
bulk_available: true
frequency: "varies by dataset (monthly, quarterly, annual)"
lag: "weeks-to-months for most macro series; some financial series near-real-time"
geography: [global]
join_keys:
  - ISO_2
  - ISO_3
  - ISO_4217
  - DATE
primary_keys:
  - IMF_DATAFLOW_ID
  - IMF_INDICATOR_CODE
  - IMF_SERIES_KEY
join_key_fields:
  - join_key: ISO_2
    fields: [REF_AREA, COUNTERPART_AREA]
  - join_key: ISO_3
    fields: [COUNTRY]
  - join_key: ISO_4217
    fields: [CURRENCY, COUNTERPART_CURRENCY]
  - join_key: DATE
    fields: [TIME_PERIOD]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/c-cf/imf-data-mcp
mcp_notes: >
  c-cf/imf-data-mcp (v0.2.0+) wraps the current data.imf.org SDMX API via the
  imfp library; earlier versions targeted the decommissioned dataservices.imf.org
  JSON endpoint. Connector must abstract SDMX dataflow/DSD discovery, series-key
  construction, and codelist resolution.
agent_use_cases:
  - country macro lookup
  - cross-country indicator comparison
  - exchange-rate and balance-of-payments time series
  - bilateral trade flow lookup (Direction of Trade)
  - government finance and fiscal statistics
access_test:
  command: "curl -sf 'https://sdmxcentral.imf.org/ws/public/sdmxapi/rest/dataflow/IMF'"
  expected_status: 200
  expected_fields: ["mes:Structure", "str:Dataflows", "str:Dataflow"]
last_verified: 2026-07-02
build_priority: medium
pit_reconstructable: false
revisions_possible: true
---

# IMF Data

## Why this source matters

The IMF's data portal is the canonical source for cross-country macroeconomic and financial statistics: International Financial Statistics (IFS), Balance of Payments (BOP/BPM6), Direction of Trade Statistics (DOTS), Government Finance Statistics (GFS), Consumer Price Index (CPI), and Financial Soundness Indicators (FSI), among 40+ dataflows. It sits alongside World Bank Open Data and OECD as one of the three pillars of global macro statistics, and it is the authoritative source for exchange rates, reserves, and bilateral trade flows that the World Bank does not publish natively. Secondary domain is `finance-markets` (exchange rates, reserves, financial soundness). Data is served over a standards-compliant SDMX 2.1 (SDMX-REST 1.x) and SDMX 3.0 API, no key required.

## Agent use cases

- country macro lookup
- cross-country indicator comparison
- exchange-rate and balance-of-payments time series
- bilateral trade flow lookup (Direction of Trade)
- government finance and fiscal statistics

## Join strategy

IMF datasets are SDMX time series keyed by dimensions that carry canonical country and currency codes. The `REF_AREA` dimension (codelist `CL_AREA`) uses ISO 3166-1 alpha-2 country codes (`US`, `GB`, `JP`) alongside IMF-specific aggregate codes (`1A`, `1C`, ...); bilateral datasets (DOTS, BOP) add a `COUNTERPART_AREA` dimension in the same form, so join on `ISO_2`. Some dataflows expose a `COUNTRY` dimension backed by `CL_COUNTRY_ISO3` (ISO 3166-1 alpha-3), giving `ISO_3` directly. Currency dimensions (`CURRENCY`, `COUNTERPART_CURRENCY`, codelist `CL_CURRENCY`) carry ISO 4217 codes, so `ISO_4217`. `TIME_PERIOD` carries the ISO 8601 period, mapping to `DATE`. Aggregates and IMF regional groupings do not map onto ISO; treat them as source-internal.

Source-internal identifiers, useful inside the IMF but not for cross-source joins: `IMF_DATAFLOW_ID` (the dataset code, e.g. `IFS`, `BOP6`, `DOTS`, `CPI`, `GFS`), `IMF_INDICATOR_CODE` (the `INDICATOR` dimension value from `CL_INDICATOR`), and the fully-qualified dot-delimited `IMF_SERIES_KEY`. The IMF indicator codes are dataflow-scoped and do not currently have a canonical registry key, flagged below for review (parallels `WB_INDICATOR_CODE` in the World Bank entry).

## Access notes

**Base URL (SDMX 2.1 / SDMX-REST 1.x):** `https://sdmxcentral.imf.org/ws/public/sdmxapi/rest`. Discover datasets with `/dataflow/IMF`, fetch a dataset's structure (dimensions + codelists) with `/datastructure/IMF/{DSD_ID}`, then pull data with `/data/{FLOW_REF}/{KEY}` where `KEY` is the dot-delimited series key (e.g. frequency.area.indicator). Codelists resolve via `/codelist/IMF/{CL_ID}` (e.g. `CL_AREA/2.0.0`, `CL_COUNTRY_ISO3`, `CL_CURRENCY`, `CL_INDICATOR`).

**SDMX 3.0 (SDMX-REST 2.x):** the newer surface is advertised at `https://api.imf.org/external/sdmx/3.0`; endpoint paths differ from 2.1 and the exact routes are still stabilising, so the 2.1 `sdmxcentral` base is the reliable default for now.

Responses default to SDMX-ML (XML). Request JSON with `Accept: application/vnd.sdmx.data+json` on data queries where supported. The legacy `dataservices.imf.org/REST/SDMX_JSON.svc` JSON API was decommissioned in 2025, do not build against it.

**Gotchas:**

- Series keys are positional and dataflow-specific; you must read the DSD before constructing a query. Wrong-order dimensions return empty results, not errors.
- The same economic concept can carry different indicator codes across dataflows; there is no global indicator vocabulary.
- Country coverage and code form differ by dataset (`CL_AREA` alpha-2 vs `CL_COUNTRY_ISO3` alpha-3); check the DSD's `REF_AREA`/`COUNTRY` dimension before joining.
- SDMX-ML is verbose; for large pulls prefer the JSON accept header or the bulk SDMX structure/data downloads.

## MCP / connector notes

Community MCP exists: `c-cf/imf-data-mcp` (Python, built on the `imfp` library, targets the current `data.imf.org` SDMX API). v0.2.0 is a breaking migration off the decommissioned `dataservices.imf.org` endpoint. No official IMF MCP. A good connector surface: `list_dataflows`, `get_dataflow_structure` (returns dimensions + codelists), `search_indicators`, `get_series` (accepts dataflow + partial key with named dimensions), `resolve_codelist`. The hard part the MCP must abstract is SDMX series-key construction: agents should pass named dimension filters, not positional dot-keys.

## Review notes

- License: IMF statistical data is governed by the IMF's "Special Terms and Conditions" for data (attribution to "International Monetary Fund" required; reuse and derivative works permitted; standalone resale must disclose the data is free from the IMF; provided "as is"). No SPDX code exists. Proposed canonical short name `IMF-Data-Terms` (new, not yet in SCHEMA.md § License conventions), flagged for Stephanie to confirm/register. Note a tension between the 2015 open data re-use terms (permit commercial reuse) and the current imf.org copyright page (directs commercial reuse to copyright@imf.org); resolve before publishing a firm commercial-use claim.
- Potential new join key for review: `IMF_INDICATOR_CODE`
  - Entity type: `macroeconomic_indicator`
  - Pattern: dataflow-scoped short codes (no single stable regex; drawn from `CL_INDICATOR` and dataflow-specific codelists)
  - Other datasets that would use it: overlaps conceptually with `WB_INDICATOR_CODE` (World Bank) and OECD indicator codes; worth a shared "statistical indicator" key only if the directory standardises one across World Bank / OECD / IMF. Skip if kept source-internal.
- `join_keys` includes `ISO_2`, `ISO_4217`, and `DATE` beyond the `ISO_3` hint given, because the SDMX codelists genuinely expose all four (verified against `CL_AREA`, `CL_COUNTRY_ISO3`, `CL_CURRENCY`). Which country-code form applies is per-dataflow.
