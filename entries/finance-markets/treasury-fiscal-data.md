---
id: treasury-fiscal-data
name: US Treasury Fiscal Data
domain: finance-markets
entry_kind: mixed
description: Official machine-readable home for US federal fiscal data (debt, interest rates, securities auctions, receipts, outlays, exchange rates) published by the Treasury Bureau of the Fiscal Service.
homepage_url: https://fiscaldata.treasury.gov/
docs_url: https://fiscaldata.treasury.gov/api-documentation/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "no published hard limit; fair-use IP throttling under a Right to Limit clause"
bulk_available: true
frequency: "dataset-dependent: daily (debt-to-penny), monthly, quarterly"
lag: "dataset-dependent; auctions posted around announcement/auction dates, most reports 1 day to 1 month after period close"
geography: [USA]
join_keys:
  - CUSIP
  - DATE
join_key_fields:
  - join_key: CUSIP
    fields: [cusip, corpus_cusip, announcemtd_cusip]
  - join_key: DATE
    fields: [record_date, auction_date, issue_date, maturity_date, dated_date, original_auction_date]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/QuantGeekDev/fiscal-data-mcp"
  - "github.com/jsconiers/treasury-fiscaldata-mcp"
mcp_notes: >
  Two community FastMCP/mcp-framework servers wrapping the same key-less REST API. Both are
  narrow demos; a robust connector should abstract over ~90 datasets, their per-dataset endpoint
  paths and versions (v1 vs v2), and JSON:API-style pagination.
agent_use_cases:
  - federal debt tracking
  - treasury auction lookup by CUSIP
  - average interest rate series
  - TIPS reference-CPI lookup
  - exchange-rate reference for USD conversions
access_test:
  command: "curl -sf 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?page%5Bsize%5D=1'"
  expected_status: 200
  expected_fields: [data, cusip, security_type, auction_date, issue_date, maturity_date]
last_verified: 2026-07-02
build_priority: medium
structure: time-series
pit_reconstructable: false
revisions_possible: true
release_lag_days: 1
---

# US Treasury Fiscal Data

## Why this source matters

Fiscal Data is the US Treasury Bureau of the Fiscal Service's single, machine-readable front door for federal financial data, consolidating datasets that were previously scattered across TreasuryDirect, MSPD, and legacy report pages. It covers ~90 datasets: the daily debt to the penny, average interest rates on Treasury securities, marketable securities auctions (announced and awarded), TIPS and CPI reference data, monthly Treasury statements of receipts and outlays, exchange rates for USD conversions, and more. Everything is public-domain, key-less, and served over one RESTful API with JSON, CSV, and XML output. Secondary domain is `government-open-data`; the securities-auctions and TIPS datasets are the primary reason a finance agent cares.

## Agent use cases

- federal debt tracking
- treasury auction lookup by CUSIP
- average interest rate series
- TIPS reference-CPI lookup
- exchange-rate reference for USD conversions

## Join strategy

The load-bearing canonical key is `CUSIP`: the securities-auctions and TIPS/CPI datasets key every marketable Treasury security by its CUSIP (`cusip`, plus `corpus_cusip` and `announcemtd_cusip` in the auctions payload), which joins directly to SEC filings, OpenFIGI, and any security-master keyed on CUSIP. `DATE` (ISO 8601, e.g. `record_date`, `auction_date`, `issue_date`, `maturity_date`) is the temporal join for stitching auction results, interest-rate series, and debt levels against market data.

Auction/security-type descriptors (`security_type` = Bill/Note/Bond/TIPS/FRN/CMB, `security_term`, `auction_format`) are useful filters but are NOT canonical join keys, they are flagged in Review notes as a possible controlled-vocabulary key. There is no Treasury-minted global record id exposed as a stable primary key across datasets, so joins run through CUSIP + DATE rather than a source-native surrogate.

## Access notes

No auth, no key, no cost. Base URL is `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/`; the full request is base + a dataset-specific endpoint path. Endpoints live at either `v1` or `v2`, and the version is per-dataset (auctions is `v1/accounting/od/auctions_query`; average interest rates is `v2/accounting/od/avg_interest_rates`) so check each dataset's detail page under API Quick Guide before hardcoding a version. Query params use JSON:API-style bracket syntax that must be URL-encoded in curl: `page[size]` -> `page%5Bsize%5D`, `page[number]` -> `page%5Bnumber%5D`. Also supports `fields=`, `filter=`, `sort=`, and `format=` (json default, or csv/xml). Pagination metadata and link headers are returned in the `meta`/`links` envelope. No hard rate limit is published; excessive volume can trigger IP throttling under the Right to Limit clause, so page politely for bulk pulls. CSV bulk export is available per dataset for large historical grabs.

## MCP / connector notes

Two community MCP servers exist: `QuantGeekDev/fiscal-data-mcp` (mcp-framework, focused on Treasury statements) and `jsconiers/treasury-fiscaldata-mcp` (FastMCP, broader: debt, interest, receipts/outlays, exchange rates, auctions). Both are lightweight and neither is official. A production connector should abstract over the ~90-dataset catalog, resolve the correct endpoint path and API version per dataset, handle the bracketed pagination encoding, and expose a small surface: `list_datasets`, `get_dataset` (with fields/filter/sort/pagination), plus convenience wrappers for `auctions_query`, `debt_to_penny`, and `avg_interest_rates`. The tricky part is that field schemas differ per dataset, so the connector must surface each dataset's data dictionary rather than assume a shared shape.

## Review notes

Potential new join key for review: SECURITY_TYPE (or TREASURY_SECURITY_TYPE)
  Entity type: security_class
  Pattern: small controlled vocabulary (Bill, Note, Bond, TIPS, FRN, CMB)
  Other datasets that would use it: TreasuryDirect, SEC/MSRB fixed-income feeds, FRED Treasury series. Low cross-source id value (it is a category, not a stable identifier); flagged because the prompt named auction/security types, but likely better left as a body-level filter than a canonical key.

License is US federal public domain (17 USC 105), recorded as the existing `US-Government-Public-Domain` short name; no new short name needed.
