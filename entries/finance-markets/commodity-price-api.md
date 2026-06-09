---
id: commodity-price-api
name: CommodityPriceAPI
domain: finance-markets
entry_kind: time-series
description: Commercial REST API for real-time and historical prices on 130+ commodities (precious metals, energy, agricultural, soft commodities) with quote-currency conversion across 175+ currencies and daily history back to 1990.
homepage_url: https://commoditypriceapi.com/
docs_url: https://commoditypriceapi.com/#documentation
type:
  - rest-api
auth_required: api-key-free
cost: freemium
license: CommodityPriceAPI-Proprietary
rate_limit: "10 requests/minute on free and Lite tiers; no documented per-minute cap on Plus and Premium. Monthly call quotas vary by plan (Lite 2,000; Plus 10,000; Premium 50,000)."
bulk_available: false
frequency: "60-second refresh on Plus and Premium; 10-minute delay on Lite. Monthly-only commodities deliver closing rate only."
lag: "60 seconds (paid Plus/Premium); 10 minutes (Lite); historical series complete to prior trading day"
geography: [global]
join_keys:
  - DATE
  - ISO_4217
primary_keys:
  - COMMODITY_PRICE_API_SYMBOL
join_key_fields:
  - join_key: DATE
    fields: [date, timestamp, startDate, endDate, "rates.<date>"]
  - join_key: ISO_4217
    fields: [quote, "metaData.quote"]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No MCP found on GitHub, npm, or PyPI as of 2026-06-09. Wrapping the six v2
  endpoints (usage, symbols, rates/latest, rates/historical, rates/time-series,
  rates/fluctuation) is straightforward but the upstream license forbids
  redistribution and most cross-source commodity workflows can be served by
  free sources (World Bank Pink Sheet for monthly benchmarks, FRED for
  validated US energy series, EIA for native US data). Low-value tag reflects
  the narrow audience that needs paid 60-second commodity refresh and accepts
  the no-redistribute terms.
agent_use_cases:
  - real-time commodity price snapshot across metals, energy, agricultural
  - historical commodity rate lookup back to 1990 for backtesting
  - currency-converted commodity prices in non-USD quote currencies
  - fluctuation/change metrics over arbitrary date ranges
  - sanity-check commodity prints against vendor or exchange feeds
access_test:
  command: "curl -sf 'https://api.commoditypriceapi.com/v2/symbols?apiKey=${COMMODITY_PRICE_API_KEY}'"
  expected_status: 200
  expected_fields: [success, symbols]
last_verified: 2026-06-09
build_priority: low
notes: "access_test not yet executed; requires ${COMMODITY_PRICE_API_KEY}. Vendor advertises an unlimited free trial without credit card, but Terms of Service classify all access as licensed-not-sold and prohibit redistribution; treat as commercial-licensed regardless of cost tier."
---

# CommodityPriceAPI

## Why this source matters

CommodityPriceAPI is a small commercial vendor publishing a JSON REST API for spot and historical commodity prices across 130+ commodities, with USD as the default numeraire and 175+ quote currencies available on paid tiers. Coverage spans precious metals (gold XAU, silver XAG), energy (WTI crude, Brent, natural gas, uranium, electricity), agricultural (coffee, wheat, soybeans, corn, butter), and softs (cocoa, cotton, sugar). Historical daily and monthly series go back to 1990-01-01. The shape is the same flat "one row per commodity, latest or as-of date" pattern Trading Economics offers, with a cleaner single-vendor scope. The free trial does not require a credit card, which makes it useful for prototyping agent workflows that need a commodity rate without standing up a paid Trading Economics or Polygon plan. Production use is paid-only in practice (the free trial is bounded by call quotas and a 10-minute delay), and the Terms of Service prohibit redistribution to third parties, so output cannot be cached and republished, only consumed inside the calling agent.

## Agent use cases

- real-time commodity price snapshot across metals, energy, agricultural
- historical commodity rate lookup back to 1990 for backtesting
- currency-converted commodity prices in non-USD quote currencies
- fluctuation/change metrics over arbitrary date ranges
- sanity-check commodity prints against vendor or exchange feeds

## Join strategy

Two canonical join keys exposed: `DATE` (every observation is dated; the `historical`, `time-series`, and `fluctuation` endpoints all carry ISO YYYY-MM-DD dates and the `latest` endpoint carries a Unix timestamp) and `ISO_4217` via the `quote` parameter (the quote currency code is echoed back in the `metaData` object on each rate response).

The source-internal handle is the commodity symbol used in the `symbols` query parameter (`XAU` for gold, `XAG` for silver, `WTIOIL` for WTI crude, plus 127+ others enumerated by the `/v2/symbols` endpoint). These ticker-style codes are vendor-specific: gold and silver follow ISO 4217-style precious-metal codes (XAU, XAG) which overlap with FX conventions, but the energy and agricultural symbols (`WTIOIL`, `BRENTOIL`, etc.) are bespoke. Store as `COMMODITY_PRICE_API_SYMBOL` in primary_keys.

No country, instrument, or issuer joins. Pair with:

- `world-bank-commodity-prices` (cross-validate the Pink Sheet's monthly print against this API's daily history).
- `fred` (cross-check WTI, Brent, gold, copper against the St. Louis Fed mirrors).
- `eia-open-data` (replace this source for US energy use cases; EIA is free, native, and not licence-restricted).
- `trading-economics-commodities` (broader symbol universe but harder paid tier and similar redistribution restrictions).
- Alpha Vantage or any FX source on `ISO_4217` when joining quote-currency-converted prices into a common numeraire.

## Access notes

**Base URL:** `https://api.commoditypriceapi.com/v2`. Six endpoints: `/usage`, `/symbols`, `/rates/latest`, `/rates/historical`, `/rates/time-series`, `/rates/fluctuation`. Output is JSON with `success` (boolean) and `metaData` envelope fields plus a `rates` object keyed by symbol or date.

**Auth:** API key per request, supplied either as `?apiKey=<key>` query string or `x-api-key: <key>` header. Sign up at `https://commoditypriceapi.com/auth/signup`, no credit card required for the trial. Keys are managed from the account dashboard.

**Plans and quotas (as advertised 2026-06-09):**

- Free trial: unlimited duration, no credit card, default quote currency only, 10-minute refresh, 10 req/min.
- Lite ($15.99/month): 2,000 calls/month, 10-minute refresh, 5 symbols/request, default quote currency only, 10 req/min.
- Plus ($34.99/month): 10,000 calls/month, 60-second refresh, 10 symbols/request, custom quote currency (175+).
- Premium ($149.99/month): 50,000 calls/month, 60-second refresh, unlimited symbols, custom quote currency.

**Endpoint shapes:**

- `/v2/rates/latest?symbols=XAU,XAG,WTIOIL&quote=USD` returns `{success, timestamp, rates: {XAU: <number>, ...}, metaData}`.
- `/v2/rates/historical?symbols=XAU&date=2024-01-15` returns OHLC fields `{date, open, high, low, close}` per symbol.
- `/v2/rates/time-series?symbols=XAU&startDate=2024-01-01&endDate=2024-06-30` returns rates keyed by date; **maximum 1-year window per call** so multi-year pulls must paginate.
- `/v2/rates/fluctuation?symbols=XAU&startDate=...&endDate=...` returns `{startRate, endRate, change, changePercent}` per symbol.
- If a requested historical date has no quote, the API returns the most recent prior rate with its own date attached.

**Error codes:** `400 VALIDATION_ERROR`, `401 API_KEY_NOT_FOUND`, `402 PAYMENT_REQUIRED` (trial expired), `403 LIMIT_REACHED` (quota), `404 USER_NOT_FOUND` / `SYMBOL_NOT_FOUND` / `QUOTE_NOT_FOUND`, `429 TOO_MANY_REQUESTS`, `500 SERVER_ERROR`.

**Bulk:** no bulk download. The `/v2/symbols` endpoint returns the full commodity universe in one call, the `/rates/time-series` endpoint is the only batch path for history and is capped at one-year windows.

**License:** vendor-proprietary (`https://commoditypriceapi.com/terms`). The Terms classify use as "licensed, not sold" with explicit prohibitions on redistribution, resale, sublicensing, and use to build a competing commodity-price API. Internal/business-reference use is permitted within the calling application. No attribution string is required. Treat output as a closed dataset for production agents and never persist it to a public artefact without re-licensing.

## MCP / connector notes

No MCP exists as of 2026-06-09 (no matching repositories on GitHub or npm, no PyPI package). A purpose-built MCP would be thin: `list_symbols()` (cached daily, returns the 130+ commodity catalogue), `get_latest(symbols, quote)`, `get_historical(symbols, date, quote)`, `get_time_series(symbols, start_date, end_date, quote)` (must internally paginate when the requested span exceeds 365 days), and `get_fluctuation(symbols, start_date, end_date, quote)`. The connector must abstract the dual auth mechanism (query-param vs header), surface the `402 PAYMENT_REQUIRED` and `403 LIMIT_REACHED` quota-exhaustion states as typed errors, and cache responses tightly given the small free-tier quota. Filed `mcp-needed-low-value` because cheaper or free alternatives (World Bank Pink Sheet, FRED, EIA) cover most agent commodity workflows, and the proprietary licence rules out building a public connector that caches and republishes the data.

## Review notes

- License `CommodityPriceAPI-Proprietary` is not in SCHEMA.md's canonical short-name list. Same shape as the `Trading-Economics-Proprietary` placeholder in `trading-economics-commodities.md`. A generic `Vendor-Proprietary` family or a `Proprietary-No-Redistribution` short name would cover this entry and any other commercial finance vendor; defer to a schema PR.
- Potential new join key for review: `COMMODITY_PRICE_API_SYMBOL` is vendor-internal and not registry-worthy. The broader question (raised in `trading-economics-commodities.md`'s review notes) is whether a `COMMODITY_SYMBOL` canonical key covering ISO precious-metal codes (XAU, XAG) plus exchange-native commodity codes is worth registering once a third commodity-pricing source lands in the directory. Three sources now exist (Trading Economics, World Bank Pink Sheet, CommodityPriceAPI), so this is closer to actionable; flag for a separate schema PR.
- `access_test` is constructed but not executed; requires `${COMMODITY_PRICE_API_KEY}` from a registered account. The endpoint is the cheapest stable read (`/v2/symbols`, returns the catalogue, counts as a single request against the quota).
- `entry_kind: time-series` fits the historical and time-series endpoints; the `/rates/latest` endpoint is registry-shaped (one row per symbol, latest value) but the load-bearing agent use is the time series.
- Vendor identity ("who runs it") is not disclosed on the marketing pages beyond the blog author (Ejaz Ahmed) and an unverified company name "CommodityPriceAPI". Domain registrant and corporate entity are unknown; recorded as such rather than guessed.
