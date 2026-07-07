---
id: eurostat-prodcom
name: Eurostat PRODCOM
domain: government-open-data
entry_kind: panel
description: EU statistics on the physical and value volume of manufactured goods sold, exported, and imported, by 8-digit product code, country, and year.
homepage_url: https://ec.europa.eu/eurostat/web/prodcom
docs_url: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines/api-statistics
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "no documented request-rate cap; a single extraction is limited to 5,000,000 data points (HTTP 413 otherwise)"
bulk_available: true
frequency: annual
lag: "reference-year data first disseminated ~6-18 months after year-end, then revised in later cycles"
geography: [EU, EFTA]
join_keys:
  - ISO_2
  - DATE
primary_keys:
  - PRODCOM_CODE
  - NACE_REV2_CODE
  - EUROSTAT_DATASET_CODE
join_key_fields:
  - join_key: ISO_2
    fields: [reporter]
  - join_key: DATE
    fields: [time]
mcp_status: mcp-exists
mcp_maturity: experimental
mcp_package:
  - "github.com/ano-kuhanathan/eurostat-mcp"
mcp_notes: >
  Single-author community server (MIT, ~7 stars, single commit) covering all of Eurostat, including
  the SDMX 2.1 Comext API that serves PRODCOM DS-prefixed datasets. Exposes search_datasets,
  query_eurostat_data, get_dataset_info, get_available_values, export_to_csv. DS-prefixed extractions
  need aggressive filtering to stay under the 5M-point cap.
mcp_command:
  - "uv --directory /path/to/eurostat-mcp run server.py"
agent_use_cases:
  - manufacturing-output lookup by product
  - industry supply-and-demand analysis (production + trade)
  - apparent-consumption estimation (production + imports - exports)
  - cross-country product-market sizing
  - NACE-sector production trends
access_test:
  command: "curl -sf 'https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-059358?format=JSON&lang=EN&time=2023&product=08111250&reporter=DE'"
  expected_status: 200
  expected_fields: [label, value, dimension, updated, source]
last_verified: 2026-07-03
build_priority: medium
structure: panel
pit_reconstructable: false
revisions_possible: true
---

# Eurostat PRODCOM

## Why this source matters

PRODCOM ("PRODuction COMmunautaire") is Eurostat's official statistics on the production of manufactured goods by enterprises in the EU, covering mining, quarrying, manufacturing, and materials recovery (NACE sections B, C, and part of E). Each observation is keyed by an 8-digit PRODCOM product code, a reporting country, an indicator (sold-production value/volume, exports, imports), and a reference year. It is the authoritative source for what the EU physically makes: volumes and euro values per product, harmonised across member states, and the only pan-EU product-level production series linkable to trade flows. Run by Eurostat within the European Statistical System. Secondary relevance: `finance-markets` (industry sizing / apparent consumption) given the embedded export/import indicators drawn from Comext.

## Agent use cases

- manufacturing-output lookup by product
- industry supply-and-demand analysis (production + trade)
- apparent-consumption estimation (production + imports - exports)
- cross-country product-market sizing
- NACE-sector production trends

## Join strategy

Canonical keys this source exposes: `ISO_2` (the `reporter` dimension) and `DATE` (the annual `time` dimension, `YYYY`). Pair on `ISO_2` + `DATE` with any country-year EU source (Eurostat national accounts, Comext trade, business demography) for supply-chain and market-sizing work.

Caveat on the country key: `reporter` uses Eurostat's GEONOM code list, which is alpha-2 and mostly ISO 3166-1 alpha-2 but deviates (e.g. `EL` for Greece, `UK` for the United Kingdom, plus EU aggregates like `EU27_2020`). Map to `ISO_2`/`ISO_3` with those exceptions handled, and drop aggregate codes before a country-level join.

Source-internal identifiers (not in the canonical registry): the 8-digit **PRODCOM product code** (`product` dimension), the **NACE Rev. 2** class formed by its first four digits, the **indicators** code list, and the Eurostat **dataset code** `DS-059358` (current annual "Sold production, exports and imports" dataflow, successor to the retired `DS-056120`). The PRODCOM code structure is layered: digits 1-4 = NACE class, digits 5-6 = CPA sub-category, digits 7-8 = PRODCOM-specific. PRODCOM codes also cross-reference Combined Nomenclature (CN) trade codes. `PRODCOM_CODE`, `NACE_REV2_CODE`, and `CN_CODE` are proposed new canonical join keys below.

## Access notes

First call: the statistics API returns JSON-stat 2.0. PRODCOM is a Comext DS-prefixed dataset, so it lives on the dedicated endpoint `https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-059358`, not the standard `/api/dissemination` path. Dimensions are `freq`, `reporter`, `product`, `indicators`, `time`; filter with `&dimension=code` (e.g. `&reporter=DE&product=08111250&time=2023`). No auth, no key. A single extraction is capped at 5,000,000 data points, so unfiltered pulls return HTTP 413; always constrain at least `time` plus one of `product`/`reporter`. For large historical or full-product pulls, use the Eurostat bulk download service rather than paginating the API. Discover the current dataflow id and its data structure via the SDMX 2.1 endpoints (`/comext/dissemination/sdmx/2.1/dataflow/ESTAT/all` and `/datastructure/ESTAT/DS-059358`); dataset codes are periodically re-minted (DS-056120 is gone), so resolve the live code before hardcoding.

License: Eurostat data reuse is authorised under the Commission's reuse policy (Decision 2011/833/EU), default licence CC BY 4.0, provided the source is acknowledged. Attribute "Source: Eurostat".

## MCP / connector notes

A community MCP exists: `github.com/ano-kuhanathan/eurostat-mcp` (MIT, single author, early-stage: ~7 stars, single commit). It wraps both the SDMX 3.0 API (regular datasets) and the SDMX 2.1 Comext API (PRODCOM/trade DS-datasets) and exposes `search_datasets`, `query_eurostat_data`, `get_dataset_info`, `get_available_values`, `list_popular_datasets`, `export_to_csv`. Gaps: nascent, unversioned, no packaged release (run from a local clone via `uv`); does not abstract the 5M-point extraction cap or the GEONOM-vs-ISO country-code deviations. The underlying JSON-stat API is clean enough for direct agent use; an ideal connector would add PRODCOM/NACE/CN code resolution and automatic filter-splitting to keep extractions under the row limit.

## Review notes

Potential new join key for review: `PRODCOM_CODE`
  Entity type: manufactured_product
  Pattern: `^[0-9]{8}$` (8-digit PRODCOM list code; first 4 digits are a NACE Rev. 2 class)
  Other datasets that would use it: Eurostat Comext (via CN correspondence), national production surveys, industry-classification crosswalks.

Potential new join key for review: `NACE_REV2_CODE`
  Entity type: industry_classification
  Pattern: `^[A-Z]?[0-9]{2}(\.[0-9]{1,2})?$` (NACE Rev. 2 section/division/class; PRODCOM code digits 1-4 map to a NACE class)
  Other datasets that would use it: Eurostat SBS/national accounts, EU business demography, most EU industrial statistics. Analogous to the existing `SIC_UK_2007` key; likely high cross-source value.

Potential new join key for review: `CN_CODE`
  Entity type: traded_good_classification
  Pattern: `^[0-9]{8}$` (Combined Nomenclature 8-digit; PRODCOM codes carry a documented CN correspondence)
  Other datasets that would use it: Eurostat Comext, UN Comtrade (HS-linked), customs/trade datasets.

Country key note: the join hint proposed `ISO_3`, but the `reporter` dimension carries alpha-2 GEONOM codes (mostly ISO 3166-1 alpha-2, with `EL`/`UK` deviations and EU aggregates). Mapped to `ISO_2` as the accurate exposed key; joining to `ISO_3` sources requires the standard alpha-2 to alpha-3 lookup plus the two deviations.

License short name: used SPDX `CC-BY-4.0` per Eurostat's stated default reuse licence (Decision 2011/833/EU). No new short name needed.
