---
id: oecd-data
name: OECD Data Explorer
domain: government-open-data
entry_kind: mixed
description: OECD's flagship data portal exposing 1,500+ statistical dataflows across 38 member countries via a public SDMX 2.1 REST API, with CSV/Excel downloads and a browsable web UI.
homepage_url: https://data-explorer.oecd.org/
docs_url: https://gitlab.algobank.oecd.org/public-documentation/dotstat-migration
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: OECD-Terms-and-Conditions
rate_limit: "no published per-key limit; anonymous; subject to fair-use throttling"
bulk_available: true
frequency: "varies by dataflow (annual, quarterly, monthly)"
lag: "weeks-to-years depending on dataflow"
geography: [global]
join_keys:
  - ISO_3
  - ISO_2
  - ISO_4217
primary_keys:
  - OECD_DATAFLOW_ID
  - OECD_AGENCY_ID
  - OECD_DSD_ID
join_key_fields:
  - join_key: ISO_3
    fields: [REF_AREA, COUNTERPART_AREA, REPORTING_COUNTRY]
  - join_key: ISO_2
    fields: [REF_AREA]
  - join_key: ISO_4217
    fields: [CURRENCY, UNIT_MEASURE]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cyanheads/oecd-mcp-server
  - github.com/isakskogstad/OECD-MCP
  - github.com/pipeworx-io/mcp-oecd
mcp_notes: >
  Multiple community MCPs wrap the SDMX 2.1 REST surface at
  sdmx.oecd.org/public/rest. cyanheads/oecd-mcp-server exposes
  dataflow search, dimension resolution, and observation queries with a
  DuckDB spillover for large pulls. No official OECD-published MCP yet.
agent_use_cases:
  - cross-country macro and social indicator comparison
  - long-run time series for GDP, trade, employment, education
  - dataflow discovery by department or keyword
  - tax and revenue statistics lookup
  - PISA, education, and skills outcome retrieval
access_test:
  command: "curl -sf 'https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I/all/?format=jsondata&dimensionAtObservation=AllDimensions&lastNObservations=1'"
  expected_status: 200
  expected_fields: [meta, data.dataSets, data.structures]
last_verified: 2026-06-09
build_priority: medium
---

# OECD Data Explorer

## Why this source matters

OECD Data Explorer is the OECD's unified statistical front door, replacing the legacy OECD.Stat portal in 2024. It exposes more than 1,500 dataflows spanning national accounts, trade, taxation, employment, education (PISA), health, environment, productivity, and inequality across the 38 OECD member countries plus selected partner economies. The portal runs on the .Stat Suite (dotstat) platform and serves data through a public SDMX 2.1 REST API at `sdmx.oecd.org/public/rest` with no auth and no per-key rate limit. For any agent answering cross-country questions about economic, social, or fiscal indicators in advanced economies, OECD sits next to the World Bank and IMF as a primary reference. Pairs naturally with World Bank Open Data (broader country coverage) and FRED (US-deep time series).

## Agent use cases

- cross-country macro and social indicator comparison
- long-run time series for GDP, trade, employment, education
- dataflow discovery by department or keyword
- tax and revenue statistics lookup
- PISA, education, and skills outcome retrieval

## Join strategy

OECD reports country-level series under the SDMX `REF_AREA` dimension, which uses ISO 3166-1 alpha-3 codes (`USA`, `GBR`, `JPN`) for member countries and OECD-defined area codes for aggregates (`OECD`, `EU27_2020`, `G7`, `WLD`). The alpha-3 form is the canonical join key for cross-source country joins; some legacy dataflows still expose alpha-2 codes. Currency-denominated series carry ISO 4217 codes in the `CURRENCY` or `UNIT_MEASURE` dimensions.

OECD-internal identifiers that are not in the canonical registry but matter inside the API:

- `OECD_AGENCY_ID` (e.g. `OECD.SDD.NAD` national accounts, `OECD.ELS` employment and social affairs, `OECD.CTP` taxation, `OECD.EDU` education) is the OECD department that maintains a dataflow.
- `OECD_DSD_ID` is the data structure definition identifier; pairs with `OECD_DATAFLOW_ID` in the canonical `{agency},{dsd}@{dataflow}` reference form (e.g. `OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I`).
- `OECD_DATAFLOW_ID` is the dataflow code (the `DF_*` suffix) that identifies one queryable series family. Treat it as the source's primary key for time series.

Aggregate area codes (`OECD`, `EU27_2020`, `G7`, `EA19`) do not map onto ISO 3166; treat them as source-internal.

## Access notes

**Base URL:** `https://sdmx.oecd.org/public/rest/`. The web UI at `data-explorer.oecd.org` is a browsable Angular front-end over the same API.

**Discovery path:** start with `/dataflow/all/all/latest?detail=allstubs` to enumerate dataflows, then `/datastructure/{agency}/{dsd_id}` to inspect dimensions, then `/data/{agency},{dsd_id}@{dataflow_id}/{key}` to fetch observations. The `key` is a dot-separated list of dimension values, with empty slots wildcarded (e.g. `USA.A....` for the USA, annual, all other dimensions).

**Formats:** SDMX-ML (default) and SDMX-JSON via `?format=jsondata`. For tabular work pass `?format=csvfile` to get a flat CSV. `dimensionAtObservation=AllDimensions` flattens the response into one observation per row.

**Time filters:** `?startPeriod=2000&endPeriod=2023` for ranges, `?lastNObservations=1` for the most recent value.

**Bulk:** the UI offers per-dataflow CSV and Excel exports. There is no single canonical bulk archive across all OECD dataflows; for heavy use, script the SDMX-JSON endpoint with paging.

**Gotchas:**

- Dataflow identifiers are versioned (e.g. `1.0`, `1.4`); the `@latest` shortcut is reliable, but pinning a version is safer for reproducible queries.
- The legacy `stats.oecd.org` SDMX-JSON endpoint is being retired as part of the dotstat migration; new code should target `sdmx.oecd.org/public/rest`.
- Sparse cells return `null`; ask for `lastNObservations` rather than a fixed year when a value is required.
- Some dataflows mix ISO 3166 alpha-3 codes with OECD aggregates in the same `REF_AREA` dimension; filter explicitly when you only want sovereign countries.
- License attribution is required per OECD terms: cite the OECD dataflow and link back to data-explorer.oecd.org.

## MCP / connector notes

Multiple community MCPs exist; none official from OECD. The most active is `cyanheads/oecd-mcp-server` (TypeScript, keyless, wraps SDMX 2.1 REST), exposing `oecd_list_agencies`, `oecd_search_datasets`, `oecd_get_dataset_info`, `oecd_get_dimension_values`, `oecd_query_dataset`, and a DuckDB spillover for large pulls. Alternatives include `isakskogstad/OECD-MCP` and `pipeworx-io/mcp-oecd`. The right MCP surface is dataflow search, dimension resolution (codes to labels), observation queries with time-window and country filters, and a streaming or staging path for multi-country time-series that exceed an LLM context window.

## Review notes

- License recorded as `OECD-Terms-and-Conditions` (kebab-case short name). OECD's terms permit free use with attribution and source citation; redistribution and commercial reuse are generally allowed but not under an SPDX-coded licence. Worth a separate PR to confirm canonical short-name or to add an explicit entry to SCHEMA.md's known-cases list.
- Potential new join keys for review:
  - `OECD_DATAFLOW_ID`, entity type `statistical_dataflow`, pattern `^DF_[A-Z0-9_]+$`. Other datasets that would use it: only OECD-internal; narrow utility, skip unless other dotstat-based sources land (UNESCO UIS, ILOSTAT, Eurostat use sibling SDMX surfaces with their own dataflow namespaces).
  - `SDMX_DATAFLOW_REF`, a generalised canonical form `{agency},{dsd}@{dataflow}` would be useful across all SDMX sources (OECD, Eurostat, ECB, IMF, ILO, UNESCO UIS). Worth registering if 3+ SDMX entries land.
- `entry_kind: mixed` per SCHEMA.md's explicit treatment of OECD; sub-dataflows are not modelled here.
- Access test executed against the SDD.NAD national-accounts dataflow; returned 200 with valid SDMX-JSON envelope.
