---
id: occ-options
name: OCC Options Volume & Open Interest
domain: finance-markets
entry_kind: time-series
description: Daily and historical US listed-options and futures volume, open interest, put/call ratios, and option series data from the Options Clearing Corporation, the central clearinghouse for all US-listed options.
homepage_url: https://www.theocc.com/market-data
docs_url: https://www.theocc.com/market-data/market-data-reports/volume-and-open-interest
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: OCC-Terms-of-Use
rate_limit: "unpublished; Cloudflare-fronted, polite per-report polling only"
bulk_available: true
frequency: daily
lag: "published the following business day (T+1) after each session"
geography: [USA]
structure: time-series
pit_reconstructable: true
revisions_possible: false
release_lag_days: 1
join_keys:
  - TICKER
  - DATE
primary_keys:
  - OCC_OPTION_SYMBOL
  - OCC_UNDERLYING_SYMBOL
join_key_fields:
  - join_key: TICKER
    fields: [symbol, underlyingSymbol]
  - join_key: DATE
    fields: [reportDate, Date]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - options volume lookup
  - open-interest tracking
  - put/call ratio signal
  - options series discovery
  - market-wide options flow context
access_test:
  command: "curl -sf -o /dev/null -w '%{http_code}' 'https://marketdata.theocc.com/daily-open-interest?reportDate=06/30/2026&action=download&format=csv'"
  expected_status: 200
  expected_fields:
    - Date
    - Calls
    - Puts
    - Total
last_verified: 2026-07-02
build_priority: low
---

# OCC Options Volume & Open Interest

## Why this source matters

The Options Clearing Corporation (OCC) is the sole central counterparty clearinghouse for every US-listed equity, index, and ETF option, clearing for 16+ exchanges. Its market-data site publishes the authoritative source-of-record for US options volume and open interest: daily volume, volume by exchange, volume by account type, put/call ratios, daily and futures open interest, monthly/weekly statistics, historical volume, and option series data. Because OCC sits at the clearing layer, its totals are the definitive market-wide numbers rather than one exchange's slice. This is a `finance-markets` source; the series-and-trading-data reports also make it a lightweight corporate-registry of option series keyed to underlying equities.

## Agent use cases

- options volume lookup
- open-interest tracking
- put/call ratio signal
- options series discovery
- market-wide options flow context

## Join strategy

Two canonical keys are exposed. `TICKER` maps to the underlying equity symbol on per-symbol reports (volume query, series search), letting agents join OCC options activity to any equity-keyed source (SEC EDGAR via ticker, price/fundamentals feeds). `DATE` (report date) makes the volume and open-interest series joinable to any daily time series.

OCC's native identifier for a specific contract is the OSI option symbol (root + expiry + call/put + strike, e.g. `AAPL  260116C00150000`), captured here as `OCC_OPTION_SYMBOL` in `primary_keys` alongside the underlying root (`OCC_UNDERLYING_SYMBOL`). The OSI symbol is a strong cross-source join candidate for options data (exchange feeds, brokerage APIs, options-analytics vendors all key on it) but is not yet in the canonical registry; flagged below for review. The headline daily-open-interest and daily-volume reports are aggregated by asset class (equity / index-other / debt / futures) and join only on `DATE`; per-`TICKER` granularity comes from the volume-query and series-search reports.

## Access notes

No auth. The programmatic host is `marketdata.theocc.com`. Each report is its own endpoint taking a `reportDate` (MM/DD/YYYY) plus `action=download&format=csv` for a CSV file, e.g. `https://marketdata.theocc.com/daily-open-interest?reportDate=06/30/2026&action=download&format=csv`. Per-symbol reports take `symbolType=U&symbol=AAPL` (series-search) or stock/index flags (volume-query). The site is Cloudflare-fronted with no published rate limit; poll politely and cache. Bulk history is available via the historical-volume-statistics and monthly/weekly reports rather than a single dump. Higher-frequency or licensed feeds (intraday, contract-level tick) route through OCC Data Sales and are paid; the public reports covered here are free. To check freshness, request the current business day's `daily-volume` report and confirm the top row matches the prior session date.

## MCP / connector notes

No MCP found (npm, PyPI, modelcontextprotocol org all empty for OCC). Audience is narrower than a broad equities feed, so low build priority, but a thin connector would help: suggested surface `get_daily_volume(date)`, `get_open_interest(date)`, `get_put_call_ratio(date)`, `volume_query(symbol, date)`, `series_search(symbol)`. The connector must abstract over (a) heterogeneous per-report CSV schemas with multi-row headers and asset-class column groups, (b) MM/DD/YYYY date formatting, (c) Cloudflare cookies/session handling, and (d) parsing thousands-separated numeric strings. Returning normalized JSON rows keyed on `DATE` and `TICKER` is the main value-add.

## Review notes

Potential new join key for review: OCC_OPTION_SYMBOL
  Entity type: listed_option_contract
  Pattern: OSI 21-char symbology, root (<=6 chars, space-padded) + YYMMDD expiry + C/P + 8-digit strike (e.g. "AAPL  260116C00150000")
  Other datasets that would use it: exchange options feeds (Cboe, Nasdaq), brokerage APIs (IBKR, Tradier), options-analytics vendors (ORATS, LiveVol), Polygon/Alpha Vantage options endpoints. Strong cross-source utility for any options dataset.

License: used canonical short name `OCC-Terms-of-Use` (no SPDX identifier exists). OCC market-data reports are published free for public viewing/download under the site Terms of Use; redistribution and commercial/real-time licensing are governed separately by OCC Data Sales. Confirm the exact short-name convention and whether a distinct paid-feed entry is warranted before merge.
