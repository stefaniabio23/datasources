---
id: finra-trace
name: FINRA TRACE (Trade Reporting and Compliance Engine)
domain: finance-markets
entry_kind: event-stream
description: OTC secondary-market transaction data for US fixed income (corporate, agency, treasury, and securitized products) reported to FINRA TRACE, plus aggregate volume and market-breadth datasets.
homepage_url: https://www.finra.org/finra-data/fixed-income
docs_url: https://developer.finra.org/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: oauth
cost: freemium
license: FINRA-Fixed-Income-Data-Terms
rate_limit: "Public credential: free, capped at 10 GB download/month. Firm credential: $1,650/mo + $250 per extra 10 GB."
bulk_available: true
frequency: "real-time trade dissemination; end-of-day, weekly, and monthly aggregate datasets"
lag: "real-time for most disseminated bond trades; aggregate stats published end-of-day"
geography: [USA]
join_keys:
  - CUSIP
  - FIGI
  - DATE
primary_keys:
  - TRACE_SYMBOL
join_key_fields:
  - join_key: CUSIP
    fields: [CUSIP_ID, cusip]
  - join_key: FIGI
    fields: [BSYM_ID]
  - join_key: DATE
    fields: [tradeDate, executionDate, weekStartDate]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/cmaurer/finra-mcp-server"
mcp_notes: >
  Community MCP wraps the FINRA Query API: handles OAuth2 token exchange + caching,
  request shaping, and pagination, and ships a dataset catalog. Convenience tools map
  friendly args (CUSIP, symbol, date range) onto the underlying query shape for TRACE
  bonds and the aggregate datasets.
agent_use_cases:
  - corporate bond price and trade lookup
  - fixed income market breadth and sentiment signals
  - treasury trading-volume aggregates
  - securitized-product capped volume
  - CUSIP-to-FIGI security resolution
access_test:
  command: "TOKEN=$(curl -s -u \"${FINRA_CLIENT_ID}:${FINRA_CLIENT_SECRET}\" -X POST 'https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token?grant_type=client_credentials' | jq -r .access_token); curl -sf -H \"Authorization: Bearer $TOKEN\" -H 'Content-Type: application/json' -X POST 'https://api.finra.org/data/group/FixedIncomeMarket/name/treasuryWeeklyAggregatesMock' -d '{\"limit\":1}'"
  expected_status: 200
last_verified: 2026-07-02
build_priority: medium
structure: event-log
pit_reconstructable: false
revisions_possible: false
notes: "access_test not executed; requires ${FINRA_CLIENT_ID}/${FINRA_CLIENT_SECRET} OAuth credentials (public credential is free with registration). Unauthenticated call to the mock endpoint returned HTTP 401, confirming auth is required."
---

# FINRA TRACE (Trade Reporting and Compliance Engine)

## Why this source matters

TRACE is FINRA's mandatory OTC transaction-reporting facility for US fixed income: every broker-dealer trade in corporate bonds, agency debt, US treasuries, and securitized products (ABS, MBS, CMO, TBA) is reported and disseminated here. It is the authoritative public tape for the US bond market, the fixed-income analogue to consolidated equity trade data. An agent researching bond pricing, liquidity, dealer activity, or issue-level trade history has no better free primary source. The Developer Center exposes a REST Query API over the aggregate and market-breadth datasets (treasury daily/weekly/monthly volumes, corporate/agency/144A breadth and sentiment, capped volume), while the public Fixed Income Security lookup gives per-security real-time trade history via the web UI. Secondary domain: `corporate-registry`, since every disseminated trade carries the issuer name and security master attributes (coupon, maturity, sub-product type).

## Agent use cases

- corporate bond price and trade lookup
- fixed income market breadth and sentiment signals
- treasury trading-volume aggregates
- securitized-product capped volume
- CUSIP-to-FIGI security resolution

## Join strategy

TRACE keys every security on `CUSIP` (`CUSIP_ID`), the US/Canada standard, making it the natural join to any CUSIP-indexed source (SEC filings, holdings data, rating feeds). It also carries the Bloomberg symbology id in `BSYM_ID`, whose `BBG...` values are `FIGI`, so TRACE doubles as a CUSIP-to-FIGI crosswalk for fixed-income instruments. Trade and aggregate records are timestamped, giving `DATE` for temporal joins against macro and rates series.

The source-internal `TRACE_SYMBOL` (`SYM_CD`) is FINRA's own security symbol; use it for direct TRACE lookups, not cross-source joins (it is in `primary_keys`, not `join_keys`).

`ISIN` was suggested as a mapping but TRACE does not publish a native ISIN field; for US issues the ISIN is deterministically derivable from the CUSIP ("US" + CUSIP + check digit), so joins should route through `CUSIP`. See Review notes.

## Access notes

Programmatic access is OAuth2 client-credentials. Base64-encode `client_id:client_secret`, POST to `https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token?grant_type=client_credentials`, then send the returned token as a Bearer header to the Query API at `https://api.finra.org/data/group/FixedIncomeMarket/name/<dataset>` (POST with a JSON body of filters/limits; `...Mock` variants serve randomized data for testing). Provision credentials self-service in the API Console. A **Public** credential is free with registration and capped at 10 GB download/month; a **Firm** credential unlocks firm-specific data and higher volume at $1,650/mo + $250 per extra 10 GB. Note the free API surface is largely aggregates and breadth/sentiment; full real-time transaction-level TRACE data and historical trade files are gated behind separate paid data subscriptions, which is why `cost` is `freemium`.

License restrictions are material: data is for non-commercial personal or professional use, you must attribute FINRA as owner and source, you may not charge end users, and end users may not further redistribute. A site notice states corporate/agency/treasury trade history prior to April 2025 is currently unavailable.

Bulk file downloads exist via the Web API file-download specs (Corporate & Agency Debt, Treasury Securities, Securitized Products) for firms with the appropriate CUSIP Global Services license.

## MCP / connector notes

A community MCP server exists (`github.com/cmaurer/finra-mcp-server`). It exposes the FINRA Query API as tools, handling the OAuth2 token exchange + caching, request shaping, and pagination, and ships a local dataset catalog so a model can discover datasets before querying. Curated convenience tools map friendly arguments (CUSIP, symbol, date range) onto the query shape for TRACE bonds and the aggregate datasets. Main gaps to watch: it only reaches what the caller's credential tier permits (public credential sees aggregates/mock data, not full transaction feeds), and it must respect the 10 GB/month public cap and the no-redistribution terms.

## Review notes

- **New license short name flagged:** `FINRA-Fixed-Income-Data-Terms` is not yet in SCHEMA.md's known-cases list. Proposed for the canonical set; nuance (attribution, no end-user charging, no redistribution, non-commercial) is documented in Access notes. Human review before merge.
- **ISIN mapping not applied:** the task hint listed `ISIN` (already a canonical key) but TRACE exposes no native ISIN field. It is derivable from the CUSIP for US issues; excluded from `join_keys` to avoid asserting a payload field that does not exist. Not a new-key candidate (already registered).
- `FIGI` is carried via the `BSYM_ID` (Bloomberg symbology) field rather than an explicitly labelled FIGI field; verify field naming holds across all Fixed Income datasets, not just Corporate & Agency Debt.
- `access_test` constructed but not executed (no credentials); unauthenticated call returned HTTP 401, confirming the auth path.
