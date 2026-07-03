---
id: sec-form4
name: SEC Form 4 Insider Transactions (EDGAR)
domain: finance-markets
entry_kind: event-stream
description: Section 16 insider transaction reports (Forms 3/4/5) filed to SEC EDGAR, reporting officer, director, and 10%-owner trades in a company's securities.
homepage_url: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
docs_url: https://www.sec.gov/os/accessing-edgar-data
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "10 req/sec per IP; a descriptive User-Agent header with contact email is mandatory or requests return 403"
bulk_available: true
frequency: "continuous (filings accepted through the trading day); official flat-file data sets refreshed quarterly"
lag: "Form 4 due within 2 business days of the transaction; appears in EDGAR near-instantly on acceptance"
geography: [USA]
join_keys:
  - CIK
  - TICKER
primary_keys:
  - SEC_ACCESSION_NUMBER
join_key_fields:
  - join_key: CIK
    fields: [cik, issuerCik, rptOwnerCik]
  - join_key: TICKER
    fields: [tickers, issuerTradingSymbol]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/stefanoamorelli/sec-edgar-mcp"
  - "sec-edgar-mcp (pip)"
mcp_command:
  - "docker run -i --rm -e SEC_EDGAR_USER_AGENT='Name (you@example.com)' stefanoamorelli/sec-edgar-mcp:latest"
  - "pip install sec-edgar-mcp; python -m sec_edgar_mcp.server (set SEC_EDGAR_USER_AGENT)"
mcp_notes: >
  Community server (AGPL-3.0) wrapping edgartools; exposes Form 3/4/5 insider-trading
  tools plus CIK lookup, filing retrieval, and XBRL financials. Requires SEC_EDGAR_USER_AGENT.
agent_use_cases:
  - insider buy/sell monitoring
  - section-16 ownership tracking
  - executive transaction signals
  - cluster-buying detection
  - cik-to-ticker resolution
access_test:
  command: "curl -sf -H \"User-Agent: ${SEC_EDGAR_USER_AGENT}\" 'https://data.sec.gov/submissions/CIK0000320193.json'"
  expected_status: 200
  expected_fields: [cik, name, tickers, filings]
last_verified: 2026-07-02
structure: event-log
pit_reconstructable: true
revisions_possible: false
release_lag_days: 2
build_priority: medium
---

# SEC Form 4 Insider Transactions (EDGAR)

## Why this source matters

Forms 3, 4, and 5 are the Section 16 filings that corporate insiders (officers, directors, and beneficial owners of more than 10% of a class of equity) must file with the SEC when they acquire or dispose of the company's securities. Form 4, the change-of-ownership report, is the highest-signal of the three: it names who traded, the transaction date, code, share count, and price, filed within two business days. EDGAR serves this data through free, no-key REST endpoints (`data.sec.gov` submissions JSON, the `www.sec.gov/Archives` filing store, and the `efts.sec.gov` full-text search API) plus quarterly flat-file bulk data sets extracted from the ownership XML. This is a `finance-markets` source (insider-trade signals) that is also a `corporate-registry` source: every filing carries the issuer's canonical SEC identifiers.

## Agent use cases

- insider buy/sell monitoring
- section-16 ownership tracking
- executive transaction signals
- cluster-buying detection
- cik-to-ticker resolution

## Join strategy

Each Form 4 carries two SEC Central Index Keys: the issuer (`issuerCik`) and the reporting insider (`rptOwnerCik`). Both are `CIK` values under the canonical registry; SEC mints a CIK for companies and individuals alike, so an insider is joined on the same key as a company. The issuer's `issuerTradingSymbol` gives `TICKER`, and the `data.sec.gov/submissions` endpoint additionally exposes `cik` and `tickers` for CIK-to-ticker resolution. Pair with any CIK- or ticker-keyed source (SEC EDGAR company filings, market-price feeds, corporate-registry entries) to attach trades to fundamentals and price action.

The SEC accession number (`SEC_ACCESSION_NUMBER`, form `0001234567-YY-NNNNNN`) uniquely identifies each filing and is the source-native primary key; it is flagged below as a candidate canonical key because every EDGAR-derived dataset references it.

## Access notes

Hit `https://data.sec.gov/submissions/CIK##########.json` (10-digit zero-padded CIK) first; it lists every filing for an entity with a parallel-array `filings.recent` block where `form` selects the `4`, `3`, and `5` rows. Resolve a ticker to a CIK via `https://www.sec.gov/files/company_tickers.json`. The structured transaction detail lives in each filing's `form4.xml` under `https://www.sec.gov/Archives/edgar/data/<cik>/<accession-no-dashes>/form4.xml` (`issuerCik`, `issuerTradingSymbol`, `rptOwnerCik`, `rptOwnerName`, plus `nonDerivativeTransaction` / `derivativeTransaction` blocks). Full-text discovery is `https://efts.sec.gov/LATEST/search-index?q=<term>&forms=4`. Every request needs a descriptive `User-Agent` header with a contact email or SEC returns 403; keep under 10 req/sec. For historical analysis, prefer the quarterly Insider Transactions Data Sets (flattened TSV) at `https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets` over paginating the API.

## MCP / connector notes

Community MCP exists: `stefanoamorelli/sec-edgar-mcp` (AGPL-3.0, pip `sec-edgar-mcp`, Docker image), which wraps the `edgartools` library and exposes Form 3/4/5 insider-trading tools alongside CIK lookup, filing retrieval, and XBRL financials. It requires the `SEC_EDGAR_USER_AGENT` env var. Known gaps: AGPL licensing constrains commercial embedding, and the insider tools return per-filing views rather than a normalized cross-issuer transaction stream. A purpose-built connector could add a `get_insider_transactions(cik|ticker, since)` surface that flattens the XML into typed rows (owner, code, shares, price, post-transaction holdings) and streams the quarterly bulk sets for backfill.

## Review notes

Potential new join key for review: SEC_ACCESSION_NUMBER
  Entity type: sec_filing
  Pattern: "^[0-9]{10}-[0-9]{2}-[0-9]{6}$"
  Other datasets that would use it: all SEC EDGAR sources (company filings, 8-K/10-K, Financial Statement Data Sets, full-text search) key on this same accession number.

Insider identity: the reporting owner is carried as `rptOwnerCik`, which is an ordinary `CIK`, so it maps to the existing canonical key rather than a new one. If the registry later wants to distinguish issuer CIKs from individual/insider CIKs (different entity_type), that would be a schema refinement, not an invented key; noted here rather than added.

License: SEC filings are US federal works in the public domain (17 USC 105); mapped to `US-Government-Public-Domain`. No new short name needed.
