---
id: finnhub-stock-api
name: Finnhub Stock API
domain: finance-markets
entry_kind: time-series
description: Multi-asset market data API covering global equities, FX, crypto, company fundamentals, estimates, alternative data, and economic indicators behind a single REST endpoint plus WebSocket streaming, with a generous free tier the provider markets as real-time.
homepage_url: https://finnhub.io/
docs_url: https://finnhub.io/docs/api
type:
  - rest-api
auth_required: api-key-free
cost: freemium
license: Finnhub-Terms-of-Service
rate_limit: "60 API calls/minute on the free tier; 30 calls/second hard cap across all paid plans per ToS"
bulk_available: false
frequency: real-time on US equities (free) and global equities on premium; intraday and daily candles
lag: "real-time for US trades on the free tier per provider claim; non-US realtime gated behind premium per-exchange licences"
geography: [global, USA]
join_keys:
  - TICKER
  - ISIN
  - CUSIP
  - FIGI
  - CIK
  - LEI
  - ISO_3
  - ISO_4217
  - DATE
primary_keys:
  - FINNHUB_SYMBOL
  - FINNHUB_FILING_ID
join_key_fields:
  - join_key: TICKER
    fields:
      - symbol
      - displaySymbol
      - ticker
  - join_key: ISIN
    fields:
      - isin
  - join_key: CUSIP
    fields:
      - cusip
  - join_key: FIGI
    fields:
      - figi
      - shareClassFIGI
  - join_key: CIK
    fields:
      - cik
  - join_key: LEI
    fields:
      - lei
  - join_key: ISO_3
    fields:
      - country
  - join_key: ISO_4217
    fields:
      - currency
  - join_key: DATE
    fields:
      - ipo
      - filedDate
      - acceptedDate
      - period
      - date
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/SalZaki/finnhub-mcp
  - github.com/aloewright/finnhub-mcp
  - github.com/jackdark425/aigroup-finnhub-mcp
mcp_notes: >
  Several community MCP servers wrap the Finnhub REST API; none are vendor-published.
  SalZaki/finnhub-mcp (C#, SSE + STDIO transports) and aloewright/finnhub-mcp
  (TypeScript, Cloudflare Workers) are the most current as of last verify. Official
  Apache-2.0 SDKs in Python, JS, Go, Ruby, PHP, and Kotlin sit under
  github.com/Finnhub-Stock-API and are the safer build base for a hardened
  connector. Connector should abstract over the 100+ method surface, normalise
  symbol formats (US tickers vs exchange-prefixed like `MSFT.US`, `RDSA.L`), and
  expose per-method rate-limit budget.
agent_use_cases:
  - real-time US equity quote retrieval
  - company profile and fundamentals lookup
  - earnings and EPS-estimate fetch
  - insider transactions and congressional trading pulls
  - cross-source ticker-to-FIGI/ISIN/CUSIP mapping
access_test:
  command: "curl -sf 'https://finnhub.io/api/v1/quote?symbol=AAPL&token=${FINNHUB_API_KEY}'"
  expected_status: 200
  expected_fields: [c, h, l, o, pc, t]
last_verified: 2026-06-09
build_priority: medium
notes: >
  access_test constructed but not executed against a real key; live probe with
  token=demo returned HTTP 401 (Invalid API key), confirming the endpoint is
  reachable but auth-gated. Requires ${FINNHUB_API_KEY} for revalidation.
---

# Finnhub Stock API

## Why this source matters

Finnhub is a New York-based market-data vendor whose free tier is one of the few that markets a genuinely real-time US equity quote rather than the standard 15-minute delayed snapshot. A single `https://finnhub.io/api/v1/` host covers equity quotes and candles, company profiles, fundamentals, earnings and EPS estimates, insider and congressional trading, ETF and mutual-fund holdings, indices constituents, bonds, forex, crypto, and macro indicators across more than 100 documented methods. Practical role in the directory: lowest-friction substitute for paid quote feeds when an agent needs free US real-time pricing plus cross-source identifier mapping (ticker to FIGI, ISIN, CUSIP, CIK, LEI all appear on the company-profile and stock-symbols endpoints), with the caveat that the free tier is non-commercial per ToS and the provider's real-time claim hinges on US exchange licences only.

## Agent use cases

- real-time US equity quote retrieval
- company profile and fundamentals lookup
- earnings and EPS-estimate fetch
- insider transactions and congressional trading pulls
- cross-source ticker-to-FIGI/ISIN/CUSIP mapping

## Join strategy

Finnhub exposes `TICKER` everywhere as the primary lookup key, with US symbols (`AAPL`, `MSFT`) plus exchange-suffixed international symbols (`MSFT.US`, `RDSA.L`, `0700.HK`). The company-profile-2 and stock-symbols endpoints carry `FIGI`, `shareClassFIGI`, `ISIN`, `CUSIP`, and `CIK`, which makes Finnhub a usable junction table between SEC EDGAR (`CIK`), OpenFIGI (`FIGI`/`ISIN`/`CUSIP`), and GLEIF (`LEI`) without paying for Polygon or Bloomberg. `ISO_3` appears in company `country` fields and `ISO_4217` in `currency` for FX and quote responses. `DATE` aligns IPO dates, filing accepted dates, and time-series period fields.

Finnhub-internal IDs (`FINNHUB_SYMBOL` for the exchange-suffixed form, filing UUIDs returned by the SEC filings endpoint) belong in query construction, not cross-source joins.

Pair with SEC EDGAR (via CIK) for full XBRL filings, OpenFIGI for non-US instrument identifier mapping, and FRED for the macroeconomic series Finnhub returns only at summary granularity.

## Access notes

**Start at:** `https://finnhub.io/api/v1/quote?symbol=AAPL&token=<key>` for the cheapest smoke test. Then `https://finnhub.io/api/v1/stock/profile2?symbol=AAPL` for identifier mapping (returns figi, shareClassFIGI, isin, cusip, country, currency, ipo, marketCapitalization, name, ticker).

**Auth:** free API key from the dashboard at `https://finnhub.io/dashboard`, passed as `?token=<key>` query parameter or `X-Finnhub-Token: <key>` header. Email + password registration, no card needed for the free tier.

**Rate limits:** 60 API calls per minute on the free tier per the provider's published limit, with a 30-calls-per-second hard ceiling that applies across all paid plans per the Terms of Service. WebSocket streaming counts against the same budget. Quotas reset on the rolling minute.

**Free-tier coverage:** US equities marketed as real-time; non-US equities, options, futures, and most premium fundamentals are gated behind paid tiers. Live test against `token=demo` returns HTTP 401, so any verification needs a real key.

**Output:** JSON only. Symbol suffixes differ across endpoints (some accept bare `AAPL`, some require `AAPL.US`); connectors should normalise.

**License nuance:** Finnhub-Terms-of-Service. The free tier is explicitly non-commercial. Users must certify non-professional status, securities professionals registered with regulatory bodies are barred from personal plans, and redistribution requires written approval. Data must be deleted when a subscription ends. These restrictions are stricter than Alpha Vantage and matter for any agent that surfaces Finnhub data to external users or counts as a business use.

**Bulk:** no bulk-download surface; the API is the only access path. Whole-universe historical loads are not the intended use case.

## MCP / connector notes

`mcp-exists`. No vendor-published MCP; several community implementations are active:

- `github.com/SalZaki/finnhub-mcp` (C#, SSE + STDIO transports, updated 2026-06-09)
- `github.com/aloewright/finnhub-mcp` (TypeScript, Cloudflare Workers)
- `github.com/jackdark425/aigroup-finnhub-mcp` (quotes, fundamentals, signals, news, crypto)

Official Apache-2.0 client SDKs at `github.com/Finnhub-Stock-API` (Python ~1k stars, plus JS, Go, Ruby, PHP, Kotlin) are the better build base for a hardened connector than wrapping the existing MCPs.

Gaps a hardened connector should address: rate-limit-aware queueing against the 60/min budget and the 30/sec ceiling, symbol-suffix normalisation (`AAPL` vs `AAPL.US` vs `MSFT.MX`), tier-aware error mapping so a non-US realtime request fails fast rather than silently returning stale data, paging across the 100+ method surface without forcing the caller to memorise method names, and a clear flag distinguishing real-time fields from estimate/aggregate fields that Finnhub returns alongside them.

## Review notes

- License `Finnhub-Terms-of-Service` is not in the SCHEMA.md known-canonical list. Same pattern as `Polygon-Terms-of-Service` and `Alpha-Vantage-Proprietary`. Worth folding all three (and likely Twelve Data, IEX Cloud, EOD Historical) into a single `Vendor-Terms` canonical entry or splitting per-vendor when the registry crosses a threshold of vendor-licenced commercial APIs.
- access_test constructed but not executed against a real key; `?token=demo` returns HTTP 401 (Invalid API key). Requires `${FINNHUB_API_KEY}` for live revalidation.
- Free-tier "real-time" claim is provider-marketed and applies to US equities only per the available exchange licences; non-US realtime is gated behind premium. Re-verify the wording on the pricing page before publication if framing matters.
- Free tier is explicitly non-commercial per ToS (personal plans cannot be used by businesses, securities professionals barred, redistribution requires written approval). If the registry later adds a `commercial_use` field, Finnhub's free tier will need a flag distinct from genuinely-open sources like FRED.
- No bulk-download surface; if the registry later adopts a `bulk_available` audit rule, Finnhub will correctly fail it.
