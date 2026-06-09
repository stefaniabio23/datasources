---
id: predscope-prediction-market-data
name: PredScope Prediction Market Data
domain: finance-markets
entry_kind: event-stream
description: Free, no-auth REST API exposing live and resolved Polymarket prediction-market odds, volumes, and outcomes, refreshed every 10 minutes.
homepage_url: https://predscope.com/
docs_url: https://predscope.com/api/
type:
  - rest-api
auth_required: none
cost: free
license: unknown
rate_limit: "no documented quota; CORS open from any domain"
bulk_available: false
frequency: "10 minutes"
lag: "near-real-time (10-minute refresh from upstream Polymarket Gamma API)"
geography: [global]
join_keys:
  - DATE
  - URL
primary_keys:
  - PREDSCOPE_MARKET_SLUG
join_key_fields:
  - join_key: DATE
    fields: [meta.generated_at, events.end_date]
  - join_key: URL
    fields: [markets.url, events.url]
mcp_status: mcp-needed-low-value
mcp_notes: >
  No connector found. A thin MCP wrapper would add little over the two flat JSON
  endpoints since there is no pagination, auth, or query parameter to abstract.
  Real value would come from a Polymarket-direct connector covering the full market
  universe, order book, and historical price series, with PredScope used only as a
  cached top-100 fallback.
agent_use_cases:
  - prediction-market odds snapshot
  - political event probability tracking
  - sports and crypto market sentiment
  - resolved-market backtesting and accuracy research
  - category-level event monitoring
access_test:
  command: "curl -sf 'https://predscope.com/api/markets.json'"
  expected_status: 200
  expected_fields: [meta.source, meta.total_markets, markets]
last_verified: 2026-06-09
build_priority: low
notes: >
  Top-100-only on the live endpoint; full universe lives upstream at Polymarket's
  Gamma API. PredScope ownership and legal entity are not disclosed on the site.
---

# PredScope Prediction Market Data

## Why this source matters

PredScope is a free analytics layer over Polymarket's Gamma API that serves two pre-built JSON snapshots (top-100 active markets and recently resolved events) with no API key, no pagination, and CORS open to any origin. It refreshes every 10 minutes and covers Politics, Crypto, Sports, Geopolitics, and Economy categories. For agents that want a quick read of crowd-priced probabilities on near-term events without standing up the full Polymarket integration, it is the lowest-friction path. The site is unaffiliated with Polymarket and asks for attribution when published.

Secondary domain: `consumer-signal`. Prediction-market odds function as a crowd-sourced expectation series alongside Google Trends and Wikipedia Pageviews, and a forecasting agent will want them in the same pull as search-interest and news-volume signals.

## Agent use cases

- prediction-market odds snapshot
- political event probability tracking
- sports and crypto market sentiment
- resolved-market backtesting and accuracy research
- category-level event monitoring

## Join strategy

PredScope is identifier-poor. The native handle for a market is a Polymarket-style URL slug (`world-cup-winner`, `peru-presidential-election-winner`); outcomes are addressed by free-text title and a probability in `[0, 1]`. Categories are free-form lowercase tags (`politics`, `sports`, `crypto`, `geopolitics`, `economy`, `culture`).

Of the canonical registry, only `DATE` (from `meta.generated_at` and resolved `events.end_date`) and `URL` (from `markets.url` / `events.url`, which point at PredScope's own event pages and round-trip to Polymarket via the shared slug) apply cleanly. There is no ticker, ISIN, FIGI, or stable cross-source entity ID for the underlying event.

Pair with GDELT or NewsAPI on the event timestamp to attribute odds moves to news flow, with Google Trends on category keywords for attention-vs-probability divergence, and with the upstream Polymarket Gamma API when full market depth, order book, or historical price series are required.

The Polymarket market slug is a strong candidate for cross-source joining once a Polymarket-direct entry exists; flagged for review below.

## Access notes

**Start at:** `https://predscope.com/api/markets.json` for live markets, `https://predscope.com/api/resolved.json` for resolved events, `https://predscope.com/api/openapi.json` for the OpenAPI 3.0.3 spec.

**Auth:** None. No API key, no account, CORS-enabled.

**Rate limits:** Not documented. The endpoints are static JSON snapshots regenerated every 10 minutes, so polling faster than the refresh cadence wastes calls.

**Coverage gotcha:** The live endpoint returns only the top 100 markets by activity. For the long tail of the ~thousands of active Polymarket markets, hit the upstream Gamma API directly (`https://gamma-api.polymarket.com/markets`).

**License nuance:** No explicit licence published. The docs ask users to credit PredScope when publishing analysis. Underlying data is sourced from Polymarket and any redistribution should respect Polymarket's own terms. Treat as `unknown` until clarified.

**Freshness check:** `meta.generated_at` in the response payload, or the "Updated [timestamp] UTC" footer on the homepage.

## MCP / connector notes

No MCP found in `modelcontextprotocol/servers`, npm, or PyPI as of last verify. Building a PredScope-specific connector adds little value: there are two flat endpoints, no auth, no pagination, no query parameters, and the response shape is small enough to fit in a single tool call.

The high-value connector in this space targets Polymarket directly, exposing the full market universe, individual market detail, order book depth, historical price series, and resolution metadata. PredScope's snapshots would be a useful cache fallback inside that connector rather than its own surface. Suggested surface for a Polymarket MCP (out of scope for this entry): `list_markets`, `get_market`, `get_orderbook`, `get_price_history`, `list_resolved`, `search_markets`.

## Review notes

- License field is `unknown`; site publishes no explicit licence string, only an attribution ask. Flagging for human review and possible follow-up with the operator.
- Owner and legal entity for PredScope are not disclosed on the homepage, about page, or API docs. Flagging in case Stephanie wants to drop the entry if provenance can't be confirmed.
- This entry covers a third-party reseller of Polymarket data. A direct `polymarket-gamma-api` entry would be higher-value and would let this entry be downgraded to a cache fallback note. Suggested as the next entry to add.
- Potential new join key for review: `POLYMARKET_MARKET_SLUG`
  - Entity type: prediction_market
  - Pattern: kebab-case URL-safe string (e.g. `world-cup-winner`, `peru-presidential-election-winner`)
  - Other datasets that would use it: Polymarket Gamma API direct, Kalshi (separate slug scheme), Manifold Markets, PredictIt; useful once two or more prediction-market sources are catalogued.
- `access_test` executed at last_verified date: `curl -sf https://predscope.com/api/markets.json` returned 200 with `meta.total_markets: 579` and a `markets` array.
