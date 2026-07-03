---
id: financial-modeling-prep
name: Financial Modeling Prep
domain: finance-markets
entry_kind: mixed
description: Commercial financial-data API covering company fundamentals, financial statements, real-time and historical prices, ETFs, forex, crypto, commodities, and macro-economic series.
homepage_url: https://site.financialmodelingprep.com/
docs_url: https://site.financialmodelingprep.com/developer/docs
type:
  - rest-api
  - bulk-download
auth_required: api-key-free
cost: freemium
license: proprietary
rate_limit: "250 req/day on the free tier; higher tiers scale to hundreds of req/sec"
bulk_available: true
frequency: "real-time to daily depending on plan and endpoint"
lag: "real-time quotes on paid tiers; end-of-day on the free tier"
geography: [global]
join_keys:
  - TICKER
  - CIK
  - ISIN
  - CUSIP
  - ISO_4217
  - DATE
join_key_fields:
  - join_key: TICKER
    fields: [symbol]
  - join_key: CIK
    fields: [cik]
  - join_key: ISIN
    fields: [isin]
  - join_key: CUSIP
    fields: [cusip]
  - join_key: ISO_4217
    fields: [currency]
  - join_key: DATE
    fields: [date]
mcp_status: mcp-exists
mcp_maturity: official
mcp_package:
  - "https://site.financialmodelingprep.com/developer/docs/mcp-server"
  - "financial-modeling-prep-mcp-server (npm)"
  - "github.com/imbenrabi/Financial-Modeling-Prep-MCP-Server"
mcp_command:
  - "npx financial-modeling-prep-mcp-server --fmp-token=$FMP_API_KEY"
mcp_notes: >
  FMP ships an official hosted MCP server plus multiple community implementations.
  The imbenrabi community server (Apache-2.0) exposes 250+ tools across 24 categories.
  All require an FMP API key via --fmp-token or FMP_ACCESS_TOKEN.
agent_use_cases:
  - financial statement retrieval
  - company fundamentals lookup
  - stock price history
  - valuation and ratio analysis
  - ticker-to-CIK/ISIN resolution
access_test:
  command: "curl -sf 'https://financialmodelingprep.com/stable/profile?symbol=AAPL&apikey=${FMP_API_KEY}'"
  expected_status: 200
  expected_fields: [symbol, cik, isin, cusip, currency, companyName]
last_verified: 2026-07-02
revisions_possible: true
pit_reconstructable: false
build_priority: medium
notes: "access_test not yet executed; requires ${FMP_API_KEY} (the public demo key is rejected as of 2026-07)."
---

# Financial Modeling Prep

## Why this source matters

Financial Modeling Prep (FMP) is a commercial financial-data provider offering a single REST API over company profiles, standardized financial statements (income / balance / cash-flow), valuation ratios, real-time and historical equity prices, plus ETFs, forex, crypto, commodities, and macro-economic series. Fundamentals are serialized from SEC filings, so US-company records carry the SEC CIK alongside the trading symbol, ISIN, and CUSIP. For an agent it is a one-key substitute for stitching together SEC EDGAR, an exchange price feed, and a reference-data vendor; the free tier (250 req/day) is enough for point lookups, and paid tiers cover bulk and high-frequency use. Secondary domain: `corporate-registry`, via CIK-keyed company records sourced from SEC filings.

## Agent use cases

- financial statement retrieval
- company fundamentals lookup
- stock price history
- valuation and ratio analysis
- ticker-to-CIK/ISIN resolution

## Join strategy

FMP's company profile is a natural resolver hub: it returns `TICKER` (`symbol`), `CIK`, `ISIN`, and `CUSIP` on the same record, so an agent can pivot from any one identifier to the others. `ISO_4217` (`currency`) tags every statement and quote, and `DATE` keys every row of historical prices and periodic statements for time-series joins. Pair with SEC EDGAR on `CIK` for primary filings and XBRL facts, with any ISIN/CUSIP-keyed security master for cross-listing coverage, and with a macro source (FRED) on `DATE` + `ISO_4217`. FMP does not mint its own opaque entity IDs; it identifies entities by exchange ticker, so `TICKER` doubles as its practical primary key.

## Access notes

Base URL is `https://financialmodelingprep.com/stable/`; append `?apikey=YOUR_KEY` (or `&apikey=`) to every request. Start with `GET /stable/profile?symbol=AAPL` to confirm the key and inspect the identifier fields. A free key (email only, no card) grants 250 requests/day across nearly all endpoints; legacy `/api/v3/` paths still work for existing subscribers but new integrations should target `/stable/`. Bulk CSV downloads and real-time/websocket feeds are gated behind paid plans. The old shared `apikey=demo` credential is now rejected (401), so an executable check needs a real key.

## MCP / connector notes

MCP exists and is mature. FMP publishes an official hosted MCP server (`/developer/docs/mcp-server`) that wraps its REST surface into ~250 tools across 24 categories (stocks, ETFs, crypto, forex, commodities, economics). Multiple community servers also exist, notably `financial-modeling-prep-mcp-server` (npm, `github.com/imbenrabi/...`, Apache-2.0) and `cdtait/fmp-mcp-server`. Run the community one with `npx financial-modeling-prep-mcp-server --fmp-token=$FMP_API_KEY`; all variants need an FMP key. A connector should abstract the free-tier daily quota (250 req/day), the `/stable/` vs `/api/v3/` split, and response trimming, since raw statement payloads are large.

## Review notes

- License short name `proprietary` is not yet in SCHEMA.md's known-license list. FMP data is under a commercial Terms of Service with redistribution restrictions (paid tiers required for redistribution/commercial use); flagging `proprietary` as a candidate canonical short name for review.
- All six `join_keys` (`TICKER`, `CIK`, `ISIN`, `CUSIP`, `ISO_4217`, `DATE`) already exist in `schema/join-keys.yaml`; none invented. No new join-key candidates.
