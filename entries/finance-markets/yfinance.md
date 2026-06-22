---
id: yfinance
name: yfinance
domain: finance-markets
entry_kind: time-series
description: Unofficial Python wrapper around Yahoo Finance's undocumented JSON endpoints for historical OHLCV prices, fundamentals, options chains, dividends, splits, and corporate actions.
homepage_url: https://pypi.org/project/yfinance/
docs_url: https://ranaroussi.github.io/yfinance/
type:
  - unofficial-api
auth_required: none
cost: free
license: Apache-2.0
rate_limit: "unspecified; Yahoo throttles aggressively on the underlying endpoints and returns HTTP 429 under load. Community guidance: keep concurrent calls low (<5/sec), back off on 429, cache responses."
bulk_available: false
frequency: continuous
lag: "real-time for end-of-day prices; intraday quotes delayed 15 min for most exchanges"
geography: [global]
join_keys:
  - TICKER
  - ISIN
primary_keys:
  - YAHOO_SYMBOL
  - TICKER
join_key_fields:
  - join_key: TICKER
    fields: [chart.result.meta.symbol, info.symbol, ticker]
  - join_key: ISIN
    fields: [isin]
mcp_status: fragile-unofficial
mcp_maturity: none
mcp_notes: >
  No official MCP. yfinance itself is a fragile wrapper around undocumented Yahoo
  endpoints that break every few months. A connector should expose narrow surfaces
  (get_history, get_info, get_financials, get_options, search_ticker) and pin a
  known-working yfinance version. Surface upstream breakage explicitly rather than
  retrying silently.
agent_use_cases:
  - historical OHLCV pulls for equities and ETFs
  - dividend and split history
  - fundamentals snapshot (income statement, balance sheet, cash flow)
  - options chain retrieval
  - quick ticker-to-company-name lookup
access_test:
  command: "curl -sf -A 'Mozilla/5.0' 'https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=5d'"
  expected_status: 200
  expected_fields: [chart, result, meta, symbol, timestamp]
last_verified: 2026-06-08
build_priority: low
notes: "Yahoo Finance terms restrict use to personal/research; commercial or redistribution use violates terms. Library breaks several times a year when Yahoo changes endpoints."
---

# yfinance

## Why this source matters

yfinance is the de facto free Python interface to Yahoo Finance, maintained by Ran Aroussi under Apache-2.0. It wraps Yahoo's undocumented `query1/query2.finance.yahoo.com` JSON endpoints to deliver historical OHLCV, dividends, splits, fundamentals (income statement, balance sheet, cash flow), options chains, holders, analyst recommendations, sector and industry data, and a simple ticker search. For agents that need free equity and ETF data without a paid market-data vendor, it is usually the first thing reached for. The trade-off is structural: Yahoo's terms restrict use to personal research, the endpoints are undocumented and change without notice, and Yahoo throttles aggressively, the library breaks several times a year and recovers via community patches.

## Agent use cases

- historical OHLCV pulls for equities and ETFs
- dividend and split history
- fundamentals snapshot (income statement, balance sheet, cash flow)
- options chain retrieval
- quick ticker-to-company-name lookup

## Join strategy

yfinance is keyed on `TICKER`, with Yahoo's exchange-suffix convention (`AAPL` for NASDAQ, `RIO.L` for LSE, `7203.T` for Tokyo). `Ticker.isin` exposes the security's `ISIN` when Yahoo has it, which is the only stable cross-source key the library emits, treat it as best-effort and verify against OpenFIGI for anything load-bearing. Currency, exchange code, and `quoteType` (EQUITY, ETF, INDEX, CURRENCY, FUTURE, CRYPTOCURRENCY) live in `Ticker.info` but are Yahoo-internal strings, not registry keys.

Recommended pairing: resolve any incoming `TICKER` to `FIGI` and `ISIN` via OpenFIGI before joining yfinance pulls to other finance sources, Yahoo's ticker namespace collides across exchanges and changes after corporate actions. For US issuers, pair with SEC EDGAR on `CIK` for canonical filings.

## Access notes

Install via `pip install yfinance`. No API key, no signup. The library calls Yahoo's `query1.finance.yahoo.com/v8/finance/chart/{symbol}` for prices and `/v10/finance/quoteSummary/{symbol}` for fundamentals, both undocumented and subject to silent schema changes.

Throttling is the dominant gotcha. Yahoo returns HTTP 429 under modest load and bans IPs that hammer the endpoints. Keep concurrent requests under five per second, add backoff on 429, and cache historical pulls aggressively (history is immutable). Bulk downloads of more than a few hundred tickers should run sequentially with sleep between calls, not via `download(tickers=[...])` with high concurrency.

Yahoo's terms restrict use to personal and research purposes. Commercial use, redistribution, or storing the data in a product that competes with Yahoo violates the terms. The library's own README states explicitly that it is not affiliated with or endorsed by Yahoo.

Verify freshness by checking the release date on PyPI (`pip index versions yfinance`) and skimming the GitHub issues tab for "broken" or "429" reports before relying on the library in production.

## MCP / connector notes

No MCP exists. A connector for yfinance is low-priority because the underlying source is fragile (`fragile-unofficial`), but if built, it should expose a narrow surface: `get_history(ticker, start, end, interval)`, `get_info(ticker)`, `get_financials(ticker, statement)`, `get_options(ticker, expiry)`, `search_ticker(query)`. The connector must pin a known-working yfinance version, surface upstream breakage as a distinct error (not retry silently), and ideally cache responses on disk keyed by `(ticker, endpoint, date)`. For any agent doing serious financial work, the better long-term move is to route through a paid vendor with a stable contract (Polygon, IEX Cloud, Alpaca) rather than wrap yfinance.

## Review notes

License nuance: the yfinance library code is Apache-2.0, but the data it returns is governed by Yahoo's terms of service, which restrict use to personal and research purposes. The `license: Apache-2.0` field captures the library; the data restriction is documented in `notes` and `## Access notes`. Flag for review whether the directory should add a separate field for "data license vs tooling license" when the two diverge, this pattern recurs with any unofficial wrapper (pytrends, snscrape).
