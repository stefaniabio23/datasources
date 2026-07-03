---
id: twelve-data
name: Twelve Data
domain: finance-markets
entry_kind: time-series
description: Unified financial market-data API for real-time and historical prices across stocks, ETFs, forex, crypto, indices, and commodities, plus reference and fundamentals data.
homepage_url: https://twelvedata.com/
docs_url: https://twelvedata.com/docs
type:
  - rest-api
auth_required: api-key-free
cost: freemium
license: proprietary
rate_limit: "free (Basic) plan: 8 API credits/min, 800/day; endpoints cost 1-100 credits each; paid plans scale credits/min"
bulk_available: false
frequency: real-time (streaming ~170ms via WebSocket; REST intraday to monthly intervals)
lag: "real-time on paid tiers; free tier can be delayed for some exchanges"
geography: [global]
join_keys:
  - TICKER
  - ISIN
  - CUSIP
  - FIGI
  - ISO_4217
  - DATE
join_key_fields:
  - join_key: TICKER
    fields: [symbol, data.symbol]
  - join_key: ISIN
    fields: [isin, data.isin]
  - join_key: CUSIP
    fields: [cusip, data.cusip]
  - join_key: FIGI
    fields: [figi, data.figi]
  - join_key: ISO_4217
    fields: [meta.currency, currency]
  - join_key: DATE
    fields: [values.datetime, datetime]
mcp_status: mcp-exists
mcp_maturity: official
mcp_package:
  - "github.com/twelvedata/mcp"
mcp_command:
  - "python src/server.py (local; set TWELVE_DATA_API_KEY) or use the hosted cloud server"
mcp_notes: >
  Official vendor MCP. Exposes prices (stocks/ETFs/forex/crypto/commodities), 60+ technical
  indicators, fundamentals, earnings, dividends, movers, and SEC filings. Cloud server links
  the account API key on OAuth-style login; local server reads TWELVE_DATA_API_KEY.
agent_use_cases:
  - latest price lookup
  - historical OHLCV retrieval
  - symbol and ISIN resolution
  - forex and crypto quotes
  - technical-indicator computation
access_test:
  command: "curl -sf 'https://api.twelvedata.com/price?symbol=AAPL&apikey=${TWELVE_DATA_API_KEY}'"
  expected_status: 200
  expected_fields: [price]
last_verified: 2026-07-02
structure: time-series
build_priority: medium
---

# Twelve Data

## Why this source matters

Twelve Data is a commercial market-data provider offering a single REST + WebSocket API across ~160k stocks, 25k+ ETFs, 2k+ forex pairs, 4.8k+ crypto pairs, indices, and commodities, sourced from 250+ exchanges in 90+ countries. It fills the gap left by fragile unofficial wrappers (yfinance, pytrends): a documented, SLA-backed API with a real free tier (800 credits/day) an agent can call without scraping. Core value for agents is fast price and OHLCV retrieval plus symbol resolution (ticker to ISIN/FIGI/exchange) across asset classes from one endpoint surface.

## Agent use cases

- latest price lookup
- historical OHLCV retrieval
- symbol and ISIN resolution
- forex and crypto quotes
- technical-indicator computation

## Join strategy

Twelve Data keys instruments on `TICKER` (its native addressing, e.g. `AAPL`, `EUR/USD`, `BTC/USD`), and `symbol_search` / reference endpoints resolve to `ISIN`, `CUSIP`, and `FIGI` (ISIN and CUSIP require a data add-on; FIGI is gated to Ultra+ plans). That makes it a useful crosswalk hub: resolve a messy ticker or ISIN to a canonical security identifier, then join to SEC EDGAR (`CIK`/`TICKER`), OpenFIGI (`FIGI`), or any holdings dataset. Forex and index series expose `ISO_4217` currency codes in `meta.currency`; time-series rows carry `DATE` in `values.datetime`.

Exchange venues are identified by ISO 10383 MIC codes (`mic_code`, e.g. `XNAS`), which has no canonical key in the registry yet, see Review notes.

## Access notes

Get a free API key from the dashboard after registration; pass it as `?apikey=` or the `Authorization: apikey <key>` header. A working `apikey=demo` exists for a limited set of symbols (used for the smoke test, which returned `{"price":"308.22000"}` for AAPL). Rate limiting is credit-based, not request-based: the free Basic plan allows 8 credits/min and 800/day, and each endpoint has a documented credit weight (a plain `/price` is 1 credit; heavier reference/fundamentals calls cost more). Quota resets at 00:00 UTC. Start at `/price` or `/quote` for a single instrument, `/time_series` for history, and `/symbol_search` to resolve identifiers. No bulk download; freshness is verified by hitting `/price` live.

## MCP / connector notes

Official vendor MCP at `github.com/twelvedata/mcp`. Two deployment paths: a hosted cloud server (browser login links your account key, nothing to install) and a local Python 3.10+ server run as `python src/server.py` with `TWELVE_DATA_API_KEY` set. It exposes prices across all asset classes, 60+ technical indicators (RSI, MACD, SMA, BBANDS, ATR), fundamentals, earnings, dividends, company profiles, market movers, and SEC/EDGAR filings. Known gap: repo has no explicit LICENSE file, and credit budgets on the free tier are easy to exhaust, so a wrapper should track credit spend per call.

## Review notes

- License: no SPDX code applies. Marked `proprietary` (commercial terms of service, per-account API key, redistribution restricted). If the registry prefers a canonical short name like `Twelve-Data-Terms`, adjust on review.
- Potential new join key for review: MIC_CODE
  - Entity type: exchange_venue
  - Pattern: ISO 10383 four-letter Market Identifier Code, `^[A-Z0-9]{4}$` (e.g. XNAS, XLON)
  - Other datasets that would use it: any multi-exchange market-data or securities-reference source (OpenFIGI, LSEG/Refinitiv, exchange schedules); Twelve Data returns it as `mic_code` on symbol and exchange endpoints.
- `CUSIP` and `FIGI` are exposed only on paid add-ons / Ultra+ plans; free-tier agents will not see those fields.
