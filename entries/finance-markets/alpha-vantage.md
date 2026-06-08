---
id: alpha-vantage
name: Alpha Vantage
domain: finance-markets
entry_kind: time-series
description: Realtime and historical market data API covering global equities, FX, crypto, commodities, technical indicators, fundamentals, and macroeconomic series, accessed by ticker symbol with a single query endpoint.
homepage_url: https://www.alphavantage.co/
docs_url: https://www.alphavantage.co/documentation/
type:
  - rest-api
auth_required: api-key-free
cost: freemium
license: Alpha-Vantage-Proprietary
rate_limit: "25 requests per day on the free tier; premium tiers scale to 75-1200 req/min"
bulk_available: false
frequency: "intraday (1/5/15/30/60 min), daily, weekly, monthly depending on endpoint"
lag: "end-of-day for free US equities; realtime and 15-minute delayed feeds gated behind premium (NASDAQ-licensed)"
geography: [global]
join_keys:
  - TICKER
  - ISO_3
  - DATE
primary_keys:
  - ALPHAVANTAGE_FUNCTION
  - ALPHAVANTAGE_SYMBOL
join_key_fields:
  - join_key: TICKER
    fields:
      - Symbol
      - "Meta Data.2. Symbol"
      - "Meta Data.2. Digital Currency Code"
  - join_key: ISO_3
    fields:
      - Country
      - "Meta Data.3. From Symbol"
      - "Meta Data.4. To Symbol"
      - "Realtime Currency Exchange Rate.1. From_Currency Code"
      - "Realtime Currency Exchange Rate.3. To_Currency Code"
  - join_key: DATE
    fields:
      - LatestQuarter
      - "Meta Data.3. Last Refreshed"
      - "Meta Data.5. Last Refreshed"
      - "Time Series (Daily).<date-key>"
      - "Time Series FX (Daily).<date-key>"
      - "data[].date"
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/alphavantage/alpha_vantage_mcp
  - github.com/berlinbra/alpha-vantage-mcp
  - github.com/matteoantoci/mcp-alphavantage
mcp_notes: >
  Vendor-affiliated alphavantage/alpha_vantage_mcp (~166 stars) is the most
  mature, plus several community Python/TypeScript implementations. All wrap the
  single /query endpoint and require ALPHAVANTAGE_API_KEY. Connector should
  abstract over the ~70 function names (TIME_SERIES_DAILY, FX_INTRADAY, CRYPTO_*,
  technical indicators, fundamentals).
agent_use_cases:
  - end-of-day equity price retrieval
  - FX and crypto price lookup
  - technical-indicator computation
  - company fundamentals fetch
  - macro indicator lookup
access_test:
  command: "curl -sf 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=${ALPHAVANTAGE_API_KEY:-demo}'"
  expected_status: 200
  expected_fields: ["Meta Data", "Time Series (Daily)"]
last_verified: 2026-06-08
build_priority: medium
---

# Alpha Vantage

## Why this source matters

Alpha Vantage is a Y Combinator-backed financial-data API offering one of the lowest-friction paths to market data for agent use. A single `https://www.alphavantage.co/query` endpoint, keyed by `function=` and `symbol=`, covers global equities (US plus tickers on LON, TRT, DEX, FRK, BSE, and others), foreign exchange, cryptocurrencies, commodities (WTI, Brent, gold, copper, etc.), 50+ technical indicators, company fundamentals (overview, income statement, balance sheet, cash flow, earnings), and US macro indicators (real GDP, CPI, treasury yields, federal funds rate, unemployment). Free tier is generous on coverage but tight on volume (25 req/day); premium tiers unlock realtime and intraday US equity data which is NASDAQ-licensed. Practical role in the directory: cheapest single-endpoint substitute for Bloomberg / Refinitiv on end-of-day OHLCV and basic fundamentals, paired with FRED for deeper macro and OpenFIGI for instrument identifier mapping.

## Agent use cases

- end-of-day equity price retrieval
- FX and crypto price lookup
- technical-indicator computation
- company fundamentals fetch
- macro indicator lookup

## Join strategy

Alpha Vantage is keyed almost entirely by `TICKER`: US symbols (`IBM`, `MSFT`, `AAPL`), suffixed international symbols (`TSCO.LON`, `SHOP.TRT`, `MBG.DEX`), and a small set of index pseudo-tickers (`DJI`, `SPX`, `COMP`, `VIX`). Currency pairs use ISO-4217 alpha codes (`USD`, `EUR`, `JPY`) which map onto `ISO_3` for the issuing country join when needed. Every observation carries a `DATE`.

Alpha-Vantage-internal identifiers (function names like `TIME_SERIES_DAILY_ADJUSTED`, `FX_DAILY`, `DIGITAL_CURRENCY_DAILY`, `OVERVIEW`, `EARNINGS`, `CPI`, `REAL_GDP`) belong in query construction, not in cross-source joins. No CUSIP, ISIN, FIGI, or CIK joins are exposed by the public response payloads; pair with OpenFIGI for `TICKER` ↔ `FIGI`/`ISIN`/`CUSIP` mapping and with SEC EDGAR for `TICKER` ↔ `CIK` mapping when joining onto filings or fundamentals at the legal-entity level.

## Access notes

**Auth:** free API key from `https://www.alphavantage.co/support/#api-key`, passed as `?apikey=<key>` query parameter. The literal string `apikey=demo` works for a handful of pre-cached requests (IBM time series, demo crypto and FX queries) and is the easiest way to smoke-test the endpoint without signup.

**Rate limit:** 25 requests per day on the free tier, refreshed at UTC midnight. Premium tiers run from 75 req/min ($49.99/mo) up to 1200 req/min, with the higher tiers also unlocking realtime and 15-minute delayed US equity data. The free tier is genuinely free with lifetime access; no credit card needed.

**Output:** JSON by default, CSV available on most endpoints via `&datatype=csv`. Response shapes are nested objects keyed by numbered strings (`"1. open"`, `"2. high"`, ...) which need flattening before downstream analytical use. The TOS asks open-source wrappers to preserve the JSON/CSV response structure verbatim, so connectors should normalise at the consumer layer rather than rewriting the payload.

**Bulk:** no bulk download surface. For whole-universe historical loads, Alpha Vantage is not the right tool; use Sharadar, Polygon flat files, or scrape-and-cache an OpenFIGI-keyed universe through paid tiers.

**Realtime gating:** realtime and 15-min delayed US equity data is premium-only because of NASDAQ / FINRA / SEC redistribution rules. End-of-day data on free tier is fine for most agent backtesting use cases.

## MCP / connector notes

`mcp-exists`. The vendor-affiliated `alphavantage/alpha_vantage_mcp` (~166 stars, Python, recently updated) is the most active option and the safest default. Community alternatives include `berlinbra/alpha-vantage-mcp` (~97 stars, Python) and `matteoantoci/mcp-alphavantage` (TypeScript). All wrap the single `/query` endpoint and require `ALPHAVANTAGE_API_KEY` from the environment.

Gaps a hardened connector should address: rate-limit-aware queueing so a 25-req/day budget isn't blown on a single agent loop, automatic ticker-suffix disambiguation for international symbols, normalisation of the numbered-key JSON response shape, paging or batching across the ~70 `function=` values without forcing the caller to memorise them, and clear surfacing of the free-vs-premium gating so a request for intraday US data fails fast rather than returning a stub.

## Review notes

- License `Alpha-Vantage-Proprietary` is not in the SCHEMA.md known-canonical list. Alpha Vantage's TOS is a vendor licence rather than an SPDX-listed open licence: free for personal and some commercial use under defined criteria, with redistribution and bulk-republication restricted. Worth adding to SCHEMA.md § License conventions if other vendor-licenced commercial APIs (Polygon, Twelve Data, IEX Cloud) are catalogued later, or splitting into per-vendor canonical names.
- `access_test` executed successfully against the live endpoint using `apikey=demo` (HTTP 200, full `Meta Data` and `Time Series (Daily)` payload returned for IBM, last refreshed 2026-06-05). Re-running with a real `${ALPHAVANTAGE_API_KEY}` is recommended for revalidation; the demo key only works for a small whitelist of pre-cached queries.
- Free-tier rate limit (25 req/day) was lowered from older published figures (5 req/min, 500 req/day) and is now the binding constraint for free use. Worth re-checking before publication in case the vendor changes the cap again.
- No bulk-download surface; if the registry later adopts a `bulk_available` audit rule, Alpha Vantage will correctly fail it.
