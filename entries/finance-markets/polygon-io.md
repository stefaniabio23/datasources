---
id: polygon-io
name: Polygon.io
domain: finance-markets
entry_kind: time-series
description: Multi-asset market data API covering US stocks, options, indices, forex, crypto, and futures with REST, WebSocket, and S3 flat-file delivery.
homepage_url: https://polygon.io/
docs_url: https://polygon.io/docs
type:
  - rest-api
  - bulk-download
auth_required: api-key-free
cost: freemium
license: Polygon-Terms-of-Service
rate_limit: "5 req/min on Basic free tier; unlimited on paid Stocks Starter and above"
bulk_available: true
frequency: real-time on paid tiers; 15-min delayed on free tier
lag: "end-of-day flat files post overnight; reference data refreshed daily"
geography: [USA, global]
join_keys:
  - TICKER
  - FIGI
  - ISIN
  - CUSIP
  - CIK
  - DATE
primary_keys:
  - POLYGON_TICKER
  - OPRA_OPTION_SYMBOL
join_key_fields:
  - join_key: TICKER
    fields: [results.ticker, ticker, T]
  - join_key: FIGI
    fields: [results.composite_figi, results.share_class_figi]
  - join_key: CIK
    fields: [results.cik]
  - join_key: DATE
    fields: [results.list_date, results.delisted_utc, t, from, to]
mcp_status: mcp-exists
mcp_maturity: official
mcp_package:
  - github.com/polygon-io/mcp_polygon
  - github.com/NimbleBrainInc/mcp-massive
mcp_notes: >
  Official Python MCP server from Polygon.io covers most REST endpoints. Community wrappers
  add focused surfaces (news-only, options-Greeks). Connector should abstract pagination,
  ticker normalisation (OPRA option symbols vs OCC), and tier-aware rate limiting.
agent_use_cases:
  - intraday OHLC bars
  - options chain pulls
  - corporate actions lookup
  - real-time quote and trade streaming
  - ticker reference and exchange metadata
access_test:
  command: "curl -sf 'https://api.polygon.io/v3/reference/tickers?ticker=AAPL&apiKey=${POLYGON_API_KEY}'"
  expected_status: 200
  expected_fields: [results, status, request_id]
last_verified: 2026-06-08
build_priority: medium
notes: >
  Polygon.io rebranded to "Massive" in 2026; landing-page domain (polygon.io) now redirects to
  massive.com. The api.polygon.io endpoint remains the documented API host as of last verify.
  access_test not yet executed; requires ${POLYGON_API_KEY}.
---

# Polygon.io

## Why this source matters

Polygon.io (rebranded to Massive in 2026) is a commercial market-data vendor that consolidates US equity, options, index, forex, crypto, and futures feeds behind a single REST + WebSocket + S3 flat-file API. Sourced from direct exchange feeds (CTA/UTP for stocks, OPRA for options, CME/CBOT/COMEX/NYMEX for futures), it is one of the cleaner non-Bloomberg ways for an agent to pull tick-level historical data without negotiating per-exchange licences. Free tier covers 15-minute delayed equity data for exploration; paid tiers unlock real-time, options, and full historical depth.

## Agent use cases

- intraday OHLC bars
- options chain pulls
- corporate actions lookup
- real-time quote and trade streaming
- ticker reference and exchange metadata

## Join strategy

Polygon exposes `TICKER` everywhere (its primary lookup key), plus `FIGI`, `ISIN`, `CUSIP`, and `CIK` on the ticker-details endpoint for cross-source joins to SEC EDGAR, OpenFIGI, and global security databases. `DATE` aligns bar and corporate-action timestamps across vendors.

Polygon-internal IDs (`POLYGON_TICKER_ID`, OPRA option symbols like `O:SPY230327P00390000`) are intentionally outside the canonical registry; option symbols carry the underlying ticker, expiry, and strike inline, so parse them rather than treating the whole string as a join key.

Pair with OpenFIGI for ISIN/CUSIP-to-FIGI mapping when stitching global portfolios; pair with SEC EDGAR (via CIK) for fundamentals and filings; pair with GDELT or Benzinga news (bundled on higher Polygon tiers) for event-study workflows.

## Access notes

**Start at:** `https://api.polygon.io/v3/reference/tickers` for the ticker universe, then `https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}` for OHLC bars.

**Auth:** API key in `?apiKey=...` query param or `Authorization: Bearer ...` header. Sign up at polygon.io for a free key; paid tiers unlock real-time and full options/futures coverage.

**Rate limits:** Basic free tier caps at 5 requests/min and 15-minute-delayed equities. Stocks Starter and above are unlimited request-rate but tier-restricted by asset class and historical depth. Bulk historical pulls should use S3 flat files (`s3://flatfiles.polygon.io/...`) rather than paginating REST.

**License nuance:** Polygon-Terms-of-Service governs use. Real-time exchange data carries display-vs-non-display redistribution restrictions imposed by CTA/UTP/OPRA; verify your use case against the per-exchange agreement before redistributing or showing to external users. End-of-day data is generally redistributable on paid tiers; check current terms for specifics.

## MCP / connector notes

Official MCP server: `github.com/polygon-io/mcp_polygon` (Python) covers most REST endpoints. Several community wrappers exist (`pipeworx-io/mcp-polygon-io`, `kevinkda/polygon-news-mcp` for news-only, `theknight2/polygon-mcp-server` for options Greeks). The official server is the right default; community forks are useful when you want a trimmed surface.

Known gaps the connector should abstract: cursor-based pagination (`next_url`), option-symbol parsing (OPRA format), tier-aware rate-limit backoff, and bulk-vs-REST routing for multi-year historical pulls.

## Review notes

- License field uses non-SPDX `Polygon-Terms-of-Service` short name; flagging for canonical-list review (similar pattern to `GDELT-Open-Data`).
- Polygon.io is mid-rebrand to Massive (massive.com). Landing page redirects; `api.polygon.io` API host still works per docs. Re-verify host and any URL drift on next pass.
- access_test constructed but not executed (requires `${POLYGON_API_KEY}`).
- Potential new join key for review: `OPRA_OPTION_SYMBOL`
  - Entity type: us_listed_option_contract
  - Pattern: `^O:[A-Z]+[0-9]{6}[CP][0-9]{8}$` (underlying + YYMMDD expiry + C/P + strike*1000 zero-padded)
  - Other datasets that would use it: CBOE DataShop, Bloomberg OPRA feed, IVolatility, ORATS.
