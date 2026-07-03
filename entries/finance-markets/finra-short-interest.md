---
id: finra-short-interest
name: FINRA Equity Short Interest
domain: finance-markets
entry_kind: panel
description: Bi-monthly consolidated short interest positions FINRA collects for all exchange-listed and OTC equity securities under Rule 4560.
homepage_url: https://www.finra.org/finra-data/browse-catalog/equity-short-interest/data
docs_url: https://developer.finra.org/docs
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free-non-commercial
license: FINRA-Data-Terms
rate_limit: "1,200 req/min per IP (sync); 20 req/min per dataset per account (async)"
bulk_available: true
frequency: "twice monthly (mid-month and end-of-month settlement dates)"
lag: "published ~8 business days after each settlement date"
geography: [USA]
join_keys:
  - TICKER
  - DATE
primary_keys:
  - FINRA_SHORT_INTEREST_KEY
join_key_fields:
  - join_key: TICKER
    fields: [symbolCode]
  - join_key: DATE
    fields: [settlementDate]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/cmaurer/finra-mcp-server"
mcp_notes: >
  Community MCP wraps the FINRA Query API (OAuth2, token caching, pagination) and ships a
  curated dataset catalog including consolidatedShortInterest. Convenience tools map symbol,
  CUSIP, date range, and CRD number onto the query shape. Auth is only needed for gated
  datasets; consolidatedShortInterest is queryable unauthenticated.
agent_use_cases:
  - short-squeeze screening
  - days-to-cover ranking
  - short-interest trend tracking
  - crowded-short detection
access_test:
  command: "curl -sf 'https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest?limit=1'"
  expected_status: 200
  expected_fields: [symbolCode, settlementDate, currentShortPositionQuantity, daysToCoverQuantity]
last_verified: 2026-07-02
build_priority: medium
structure: panel
pit_reconstructable: false
revisions_possible: true
release_lag_days: 8
---

# FINRA Equity Short Interest

## Why this source matters

FINRA (Financial Industry Regulatory Authority) collects short interest positions from member firms twice a month under Rule 4560 and publishes a consolidated file covering all exchange-listed and OTC equity securities. Each record carries current and prior short shares, average daily volume, days-to-cover, and percent change per symbol per settlement date. This is the authoritative, free US short interest series, the same data vendors resell. It is the primary public signal for short-squeeze screens, crowded-short detection, and days-to-cover trend work, and it sits in the `finance-markets` domain alongside price and volume feeds.

## Agent use cases

- short-squeeze screening
- days-to-cover ranking
- short-interest trend tracking
- crowded-short detection

## Join strategy

The dataset exposes `TICKER` (`symbolCode`) and `DATE` (`settlementDate`) as canonical join keys, so it joins directly to price, volume, and reference-master sources keyed on ticker plus date. There is no source-minted stable row id; a record is uniquely identified by the composite of `symbolCode` + `settlementDate` (captured as `FINRA_SHORT_INTEREST_KEY` in `primary_keys`). `CUSIP` is NOT present in the consolidated short interest payload; the community MCP's CUSIP argument maps onto other FINRA datasets (TRACE bonds), not this one. To bridge to `CUSIP` or `ISIN`, first resolve the ticker through a security master. Pair with a daily OHLCV feed to compute utilization and squeeze metrics, and with SEC EDGAR (`CIK`) for issuer-level context.

## Access notes

Hit the Query API first: `GET https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest`. This dataset returns records unauthenticated (verified 200), defaulting to CSV; send `Accept: application/json` for JSON. Filter with the FINRA query grammar (POST body or `limit`/`offset` query params) on `settlementDate` and `symbolCode`; the API returns one rolling year. Older periods are pipe-delimited text archives under the OTC Data portal (`otce.finra.org/otce/EquityShortInterest`). The broader Developer Center uses OAuth2 (API Console credentials, FIP bearer tokens) for gated Equity datasets, but short interest itself does not require it. Watch the `revisionFlag` field: firms restate positions, so a settlement date can be re-published.

## MCP / connector notes

A community MCP server exists (`github.com/cmaurer/finra-mcp-server`) exposing the FINRA Query API as tools, with OAuth2 handling, token caching, pagination, and a bundled dataset catalog (TRACE, OTC weekly/monthly summaries, consolidated short interest, Reg SHO daily volume, threshold list, firm profile). It offers convenience tools that map symbol, CUSIP, date range, and CRD number onto the underlying query shape. Known gap: it treats CUSIP as a universal argument, but short interest is symbol-keyed only, so a caller passing CUSIP for short interest will need ticker resolution upstream.

## Review notes

- License short name `FINRA-Data-Terms` is NOT yet in SCHEMA.md's known-license list. FINRA Data is published for non-commercial use under the FINRA Data terms of use (no SPDX code exists). Flagging for Stephanie to canonicalize or rename.
- Join-key hint `CUSIP` was supplied but the consolidatedShortInterest payload does not carry it (fields are `symbolCode`, `issueName`, exchange/market codes, and share counts only). Not added to `join_keys` to avoid a false edge. If FINRA adds CUSIP to the file, revisit.
- No new canonical join keys proposed; `TICKER` and `DATE` both already exist in `schema/join-keys.yaml`.
</content>
</invoke>
