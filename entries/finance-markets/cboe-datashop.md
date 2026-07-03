---
id: cboe-datashop
name: Cboe DataShop
domain: finance-markets
entry_kind: mixed
description: Cboe's commercial marketplace for historical and real-time options, equities, futures, and index market data, sold as per-day CSV files and via the Cboe All Access REST API.
homepage_url: https://datashop.cboe.com/
docs_url: https://datashop.cboe.com/documentation
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-paid
cost: paid
license: proprietary
rate_limit: "tiered points-per-month quota on the All Access API (e.g. Free Tier 500 points/day, Tier 3 1.25M points/month, Tier 4 4M points/month); overage billed per point"
bulk_available: true
frequency: "daily end-of-day files; also tick / intraday products and real-time streaming via API"
lag: "T+1 for end-of-day historical files; real-time available via All Access API on paid SIP entitlements"
geography: [USA, Europe, global]
join_keys:
  - TICKER
  - DATE
primary_keys:
  - OSI_OPTION_SYMBOL
  - OCC_ROOT_SYMBOL
join_key_fields:
  - join_key: TICKER
    fields: [underlying_symbol]
  - join_key: DATE
    fields: [quote_date, expiry]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Paid, entitlement-gated options/market-data marketplace. A connector would wrap the
  All Access REST API (auth, points-budget tracking, historical option/quote/trade
  pulls) but the paywall and per-account SIP entitlements limit the shared audience,
  so build priority is low. Suggested surface: search_products, get_option_eod_summary,
  get_option_trades, get_option_quotes, get_underlying_reference.
agent_use_cases:
  - pull full historical options chains for backtesting
  - retrieve trade-by-trade options execution detail
  - build end-of-day options open-interest and volume panels
  - reconstruct historical implied-volatility surfaces
  - source intraday quote intervals for microstructure research
access_test:
  command: "curl -sf -H \"Authorization: Bearer ${CBOE_ALL_ACCESS_TOKEN}\" 'https://api.livevol.com/v1/live/allaccess/market/option-and-underlying-quotes?root=SPY&symbol=SPY'"
  expected_status: 200
last_verified: 2026-07-02
build_priority: low
notes: >
  access_test not yet executed; requires a paid Cboe All Access subscription and
  ${CBOE_ALL_ACCESS_TOKEN}. Endpoint path is illustrative; confirm against the
  current technical reference at https://www.livevol.com/apis/technical-reference.
---

# Cboe DataShop

## Why this source matters

Cboe DataShop (operated by Cboe Exchange, Inc., built on the LiveVol platform) is the exchange's own e-commerce destination for market data. It sells deep historical and real-time coverage of US and European options, equities, ETFs, index values, and futures: trade-by-trade execution detail, end-of-day summaries, options open-interest and volume, quote intervals, and calculated analytics (implied vol, greeks). This is the authoritative first-party source for Cboe-listed options microstructure, the data a quant would otherwise reconstruct imperfectly from consolidated feeds. It is paid and entitlement-gated, which distinguishes it sharply from the free `cboe-volatility-index-vix` entry in this directory (a single derived index time series); DataShop is the underlying raw options and market-data marketplace, not a headline index. Secondary relevance to any options-derivatives or volatility-modelling workflow.

## Agent use cases

- pull full historical options chains for backtesting
- retrieve trade-by-trade options execution detail
- build end-of-day options open-interest and volume panels
- reconstruct historical implied-volatility surfaces
- source intraday quote intervals for microstructure research

## Join strategy

The two canonical join keys DataShop exposes are `TICKER` (the `underlying_symbol` column, the equity/ETF/index ticker the option is written on) and `DATE` (the `quote_date` observation date and the `expiry` contract-expiration date, both ISO-shaped). Join DataShop options panels to equity price series (`polygon-io`, `alpha-vantage`, `yfinance`), fundamentals (`sec-companyfacts`, `sp500-companies-financials`), or the VIX (`cboe-volatility-index-vix`) on `TICKER` + trading `DATE`.

The individual option contract is identified source-side by its OCC `root` symbol plus `expiry` + `strike` + `type`, or by the full 21-character OSI option symbol. These are the natural primary keys of an options dataset (`OCC_ROOT_SYMBOL`, `OSI_OPTION_SYMBOL` in `primary_keys`) but neither is in the canonical registry, so they are not claimed as `join_keys`. The OSI option symbol is a strong new-join-key candidate (it uniquely identifies a listed contract across any options vendor: Databento, OPRA, ORATS, brokerages); it is flagged in Review notes.

## Access notes

**Auth:** paid. Bulk historical products are purchased per-product on the DataShop storefront and delivered as one `.csv` file per trading day; the All Access API uses a token/entitlement tied to a paid subscription tier. **Cost:** paid, with a 14-day / limited Free Tier (500 points/day, non-SIP data) for evaluation. **Rate limit:** the API meters usage as points-per-month against your tier, with per-point overage billing; SIP (consolidated real-time) entitlements are priced separately and not bundled.

Start with the storefront product pages (`option-eod-summary`, `option-trades`, `option-quote-intervals`, `end-of-day-options-summary`) to identify the exact product and its CSV schema, then either buy the historical file set or provision the All Access API. The EOD summary CSV carries `quote_date, underlying_symbol, root, expiry, strike, type, open_interest, total_volume, open, high, low, last, last_bid_price, last_ask_price, underlying_close, series_type, product_type`. Root symbols containing a digit mark non-standard (corporate-action-adjusted) options whose deliverable differs from 100 shares; handle those separately in any chain reconstruction. Confirm the current API surface against the LiveVol technical reference before wiring endpoints.

**Freshness verification:** end-of-day files post T+1; check the latest available `quote_date` on the relevant product page or via the API against the most recent US trading day.

## MCP / connector notes

No MCP exists. A connector would wrap the Cboe All Access REST API and abstract over: token auth, the points-budget metering (so an agent does not blow its monthly quota on one wide historical pull), SIP-vs-non-SIP entitlement differences, and the per-day-file bulk delivery for historical backfills. Suggested surface: `search_products`, `get_option_eod_summary`, `get_option_trades`, `get_option_quotes`, `get_underlying_reference`. Build priority is low because the paywall and per-account entitlements keep the shared-audience overlap small; a generic paid-market-data MCP is a better home than a Cboe-specific one unless a workflow standardises on Cboe options microstructure.

## Review notes

- **New join-key candidate: `OSI_OPTION_SYMBOL`.** Entity type: option_contract. Pattern: 21-character OCC/OSI symbol (6-char underlying root, padded; YYMMDD expiry; C/P; 8-digit strike in cents), e.g. `SPY   240719C00450000`. Datasets that would use it: Databento options, OPRA, ORATS, brokerage APIs, any options-chain source. Strong cross-source key; recommend PR into `schema/join-keys.yaml`.
- **New join-key candidate (weaker): `OCC_ROOT_SYMBOL`.** Entity type: option_class. The OCC option-class root; useful but only unique in combination with expiry + strike + type, so lower priority than the full OSI symbol.
- **License:** DataShop content is commercial/proprietary with per-product redistribution restrictions; there is no SPDX code. Used the kebab short name `proprietary`, which is not on the SCHEMA.md example list. Flagging for a canonical short-name decision (e.g. `proprietary` vs `commercial-proprietary`).
- **`access_test` not executed** (requires paid subscription + `${CBOE_ALL_ACCESS_TOKEN}`); the endpoint path is illustrative and should be confirmed against the live LiveVol technical reference.
- Distinct from `cboe-volatility-index-vix` (free derived index series). No conflict; this entry is the raw options/market-data marketplace, that one is a single VIX time series.
