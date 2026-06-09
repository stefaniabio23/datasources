---
id: trading-economics-commodities
name: Trading Economics Commodities
domain: finance-markets
entry_kind: time-series
description: Live and historical prices, forecasts, and metadata for ~100 commodities (energy, metals, agricultural, industrial, livestock, electricity, carbon) accessed via the Trading Economics markets API and web tables.
homepage_url: https://tradingeconomics.com/commodities
docs_url: https://docs.tradingeconomics.com/
type:
  - rest-api
  - web-ui
auth_required: api-key-paid
cost: paid
license: Trading-Economics-Proprietary
rate_limit: "trial accounts capped at 100,000 data points and 100 requests; paid tier limits are contract-specific and not published"
bulk_available: false
frequency: "intraday quotes during market hours; end-of-day snapshots; historical series go back decades for major contracts"
lag: "minutes for major futures during exchange hours; end-of-day for smaller contracts and physical benchmarks"
geography: [global]
join_keys:
  - DATE
  - ISO_4217
primary_keys:
  - TE_SYMBOL
  - TE_TICKER
join_key_fields:
  - join_key: DATE
    fields: [Date, LastUpdate]
  - join_key: ISO_4217
    fields: [Unit]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/slekrem/MacroPulseMCP
mcp_notes: >
  One community MCP (slekrem/MacroPulseMCP, .NET 9.0, 0 stars at last check)
  wraps the Trading Economics API including a MarketsTools surface that covers
  commodity prices. Auth via the TradingEconomics:ApiKey config slot; defaults
  to the guest:guest evaluation key which is rate-capped. A second community
  MCP (gavinHuang/trading_economics_calendar_mcp) covers the economic calendar
  only and does not expose commodity quotes.
agent_use_cases:
  - live commodity price snapshot across energy, metals, and agriculture
  - historical commodity price series for backtesting
  - commodity-group sector comparison (Energy vs Metals vs Agricultural)
  - currency- and country-specific contracts (CNY/T eggs, EUR carbon permits)
  - macro-correlation studies pairing commodities with FX and macro indicators
access_test:
  command: "curl -sf 'https://api.tradingeconomics.com/markets/commodities?c=${TRADINGECONOMICS_KEY}&f=json'"
  expected_status: 200
  expected_fields: [Symbol, Ticker, Name, Last, Group, Unit, Date, DailyChange, DailyPercentualChange]
last_verified: 2026-06-09
build_priority: low
notes: "access_test not yet executed; requires ${TRADINGECONOMICS_KEY}. The legacy guest:guest key on /markets/commodities returns HTTP 410 Gone as of 2026-06-09, so a paid or trial key is now required end-to-end."
---

# Trading Economics Commodities

## Why this source matters

Trading Economics is a Lisbon-based market-data vendor that publishes a wide, agent-friendly cross-section of commodity prices in one place: WTI and Brent crude, natural gas (Henry Hub and TTF), gasoline, heating oil, coal, gold, silver, copper, steel, lithium, iron ore, platinum, cobalt, aluminium, tin, zinc, nickel, soybeans, wheat, lumber, palm oil, coffee, cotton, sugar, cocoa, feeder and live cattle, lean hogs, salmon, the CRB and GSCI indices, EU carbon permits, and European day-ahead electricity prices. The pull is breadth, not depth: a single API gives an agent one row per commodity with last price, daily change, weekly/monthly/year-to-date/year-over-year performance, unit, and the underlying exchange ticker, then a historical endpoint for the time series. Useful when an agent needs a quick cross-sector commodity snapshot without wiring up ICE, CME, LME, NYMEX, and SHFE feeds separately. Trade-off: free programmatic access is effectively gone (the legacy `guest:guest` key now returns HTTP 410), and the data is vendor-licenced with redistribution restrictions, so this is a paid-API entry for production use.

## Agent use cases

- live commodity price snapshot across energy, metals, and agriculture
- historical commodity price series for backtesting
- commodity-group sector comparison (Energy vs Metals vs Agricultural)
- currency- and country-specific contracts (CNY/T eggs, EUR carbon permits)
- macro-correlation studies pairing commodities with FX and macro indicators

## Join strategy

Trading Economics keys commodities by its own `Symbol` (e.g. `DCE:COM` for Dalian eggs) and a shorter `Ticker` field. Neither maps cleanly onto a canonical join key, neither is in the registry. Cross-source joins on this dataset rely on `DATE` for time alignment and on `ISO_4217` parsed out of the `Unit` field (`USD/BBL`, `EUR/MWh`, `CNY/T`) when joining priced commodities to FX series.

Source-internal IDs that belong in YAML `primary_keys`: `TE_SYMBOL` (vendor-specific concatenation, exchange-prefixed) and `TE_TICKER` (short form, frequently overlapping with the exchange-native futures code but not guaranteed). Group/Country/Unit live in the response as strings and stay in the body, not the YAML.

Recommended pairings: align time series with FRED commodity series on `DATE` for sanity-checking against St. Louis Fed methodology; align WTI/Brent and natural gas pulls with EIA Open Data petroleum and natural gas series; pair currency-quoted contracts with Alpha Vantage FX on `ISO_4217` to convert into a common numeraire. For agents that need exchange-canonical futures IDs (CME globex codes, ICE codes), Trading Economics is the wrong source, go direct to the exchange or to a paid futures vendor.

Potential new join key for review: `TE_SYMBOL` is not registry-worthy on its own (vendor-internal), but a generic `EXCHANGE_FUTURES_CODE` key covering CME globex, ICE, LME ring, and SHFE futures codes would join Trading Economics, Alpha Vantage commodities, Polygon futures, and CME's public reference data. Worth proposing if and when a second commodity source lands in the directory.

## Access notes

**Base URL:** `https://api.tradingeconomics.com`. The commodities snapshot endpoint is `/markets/commodities`, optionally constrained by group (`/markets/commodities?group=metals`). Historical series live under `/markets/historical/{symbol}` (e.g. `/markets/historical/XAUUSD:CUR`). Output format is JSON by default with `csv` and `xml` available via `&f=csv` or `&f=xml`.

**Auth:** query-string credential pair appended as `?c=<client_key>:<client_secret>`. The historically public `c=guest:guest` evaluation pair now returns HTTP 410 Gone on the commodities endpoint as of 2026-06-09, paid plans and trial accounts get their own credentials from the developer portal. The trial is fee-bearing (not free), capped at 100,000 data points and 100 requests total, and auto-converts to a paid plan if not cancelled.

**Rate limits:** trial accounts are hard-capped at 100,000 data points and 100 requests total (lifetime, not per-day). Paid-tier limits are not published and are negotiated per contract; expect per-second and per-day request caps.

**Bulk:** no public bulk download. Paid customers can subscribe to direct feeds or an Excel add-in; the registry does not catalogue those.

**Licence:** Trading Economics's terms are vendor-proprietary. Free use is restricted to personal evaluation through the trial. Redistribution, republishing, and use in derivative commercial products require a separate licence. Attribution to Trading Economics is required even for permitted display use. Treat this as a closed dataset for production agents and gate downstream artefacts on the licence terms before publishing.

**Freshness check (no API key on hand):** the web table at `https://tradingeconomics.com/commodities` carries the latest update timestamp in the page header; the API documentation at `docs.tradingeconomics.com` is the authoritative spec for endpoint shape and field names.

## MCP / connector notes

`mcp-exists` with one relevant community option: `slekrem/MacroPulseMCP` is a .NET 9.0 server that wraps the Trading Economics API and exposes thirteen tool categories including `MarketsTools` for commodity, currency, index, and bond prices. Authentication is configured via the `TradingEconomics:ApiKey` slot in `appsettings.json` and defaults to the `guest:guest` evaluation key, which is now insufficient for commodity reads. Maturity is low (no stars, single maintainer, recent activity). A hardened connector would expose `get_commodity_snapshot(group)`, `get_commodity_history(symbol, start, end, frequency)`, and `search_commodity(query)`, abstract the trial-vs-paid credential difference, surface the 410-Gone state when guest credentials are sent against gated endpoints, and cache snapshots aggressively given the request-budget caps. The second community MCP (`gavinHuang/trading_economics_calendar_mcp`) covers the economic calendar only and is not relevant to commodities.

## Review notes

- License `Trading-Economics-Proprietary` is not in the SCHEMA.md known-canonical short-name list. Adding it (or a more general `Vendor-Proprietary` family) is worth considering once a second vendor-licenced commercial finance API lands in the directory (Polygon, Twelve Data, Bloomberg Open Symbology, Refinitiv).
- Potential new canonical join key for review: `EXCHANGE_FUTURES_CODE` (entity type: futures_contract; pattern: exchange-prefixed alphanumeric, e.g. `CL`, `BZ`, `GC` on CME globex; `XAUUSD:CUR` on TE; ICE Brent `B`). Other datasets that would use it: CME public reference data, Polygon futures, exchange-native data feeds. Defer until a second commodity entry justifies the key.
- `access_test` is constructed but not executed; the registry-side `${TRADINGECONOMICS_KEY}` placeholder needs a real trial or paid key to verify. The legacy `guest:guest` route returned HTTP 410 Gone during research, the docs assert the endpoint is live, so a re-run with a real key is recommended before the next publish cycle.
- `entry_kind: time-series` fits the dominant use (price-over-time per commodity) but the snapshot endpoint also delivers a flat registry-like cross-section. Filed as `time-series` since the historical series is the load-bearing path for agent use; flag if the directory later splits the kind.
