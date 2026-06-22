---
id: cboe-volatility-index-vix
name: CBOE Volatility Index (VIX)
domain: finance-markets
entry_kind: time-series
description: Daily OHLC time series of the CBOE Volatility Index (VIX) from January 1990 to present, mirrored from the official CBOE CSV by DataHub's Core dataset pipeline.
homepage_url: https://datahub.io/core/finance-vix
docs_url: https://github.com/datasets/finance-vix
type:
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: ODC-PDDL-1.0
rate_limit: "none; static CSV download"
bulk_available: true
frequency: "approximately every 4 hours via DataHub Core pipeline; upstream CBOE file updates each US trading day"
lag: "same-day for the upstream CBOE CSV; up to ~4 hours for the DataHub mirror"
geography: [USA]
join_keys:
  - DATE
join_key_fields:
  - join_key: DATE
    fields: [DATE, Date]
primary_keys:
  - DATE
mcp_status: api-direct-sufficient
mcp_maturity: none
mcp_notes: >
  Two CSV files at stable URLs (DataHub mirror + GitHub raw + upstream CBOE),
  no auth, no rate limit. curl plus a CSV parser covers the whole surface;
  an MCP wrapper would add little beyond what a generic CSV / time-series MCP
  already provides.
agent_use_cases:
  - retrieve VIX daily OHLC history for backtesting
  - track market-implied volatility regime
  - feature-engineer a fear-gauge signal for cross-asset models
  - join VIX closes to equity or macro series by trading date
  - monthly close lookup for regime-switching analysis
access_test:
  command: "curl -sfI 'https://raw.githubusercontent.com/datasets/finance-vix/master/data/vix-daily.csv'"
  expected_status: 200
  expected_fields: [DATE, OPEN, HIGH, LOW, CLOSE]
last_verified: 2026-06-09
build_priority: low
notes: >
  Pre-2004 OHLC rows carry identical open / high / low / close values because
  CBOE only published the daily close before mid-June 2004. Treat the
  intraday range as unavailable before 2004-06-11.
---

# CBOE Volatility Index (VIX)

## Why this source matters

The VIX is the canonical market-implied volatility index for the S&P 500, published by Cboe Global Markets and widely used as a fear-gauge regressor in macro and cross-asset models. DataHub's Core pipeline mirrors the official CBOE daily CSV (`cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`) onto a stable HTTPS URL plus a GitHub repo, refreshes every ~4 hours, and derives a monthly file from the daily series. The whole surface is two CSVs and a `datapackage.json`. Pick this entry over hitting CBOE directly when an agent wants a single stable URL, the derived monthly view, or a JSON metadata description; pick the upstream CBOE URL when freshness matters more than convenience.

## Agent use cases

- retrieve VIX daily OHLC history for backtesting
- track market-implied volatility regime
- feature-engineer a fear-gauge signal for cross-asset models
- join VIX closes to equity or macro series by trading date
- monthly close lookup for regime-switching analysis

## Join strategy

The only canonical join key exposed is `DATE` (column `DATE` in `vix-daily.csv`, `Date` in `vix-monthly.csv`). The VIX has no ticker, ISIN, CUSIP, or FIGI in the conventional sense because it is a calculated index, not a tradable security; downstream agents typically join VIX closes to equity index series (`^GSPC`, `SPY`) or macro series (FRED `DGS10`, `VIXCLS`) by trading date.

Useful pairings:

- FRED series `VIXCLS` for the same daily-close series with the same `DATE` join, when the agent already has a `FRED_API_KEY` and wants a unified macro pull.
- `sp500-companies-financials` (this directory) + Alpha Vantage / Polygon / yfinance for the underlying S&P 500 universe whose options drive the VIX calculation.
- Any of the equity-market time-series sources for cross-asset regimes keyed on `DATE`.

There is no source-side ticker column; the implicit ticker is `VIX` (or `^VIX` on Yahoo) but the dataset does not carry it as a field, so this entry does not claim `TICKER` as a join key.

## Access notes

**Auth:** none. **Cost:** free. **Rate limit:** none (static CSV).

**Stable URLs.** Three live targets, in descending order of mirror-distance from the source:

- Upstream CBOE: `https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`. Same-day fresh, columns `DATE,OPEN,HIGH,LOW,CLOSE`. Use when freshness matters.
- DataHub R-link: `https://datahub.io/core/finance-vix/_r/-/data/vix-daily.csv`. Returns HTTP 302 to a signed R2 CDN URL; up to ~4 hours behind upstream. Convenient for the matching `vix-monthly.csv` and the `datapackage.json` metadata.
- GitHub raw: `https://raw.githubusercontent.com/datasets/finance-vix/master/data/vix-daily.csv` returns 200 directly and is the simplest programmatic target for the DataHub-shaped CSV.

The `main` branch path on GitHub returns 404; use `master`. The DataHub `_r/-/data/` path follows a 302 redirect, so `curl -L` is required to actually fetch bytes; the `-I` form returns 302 as expected.

**Pre-2004 caveat.** Rows dated before 2004-06-11 have OPEN = HIGH = LOW = CLOSE because CBOE only published the daily closing print at the time. Backtests that depend on intraday range or true-range volatility should drop or mark pre-2004 rows.

**Freshness verification.** Hit the upstream CBOE URL and check the last row's `DATE` against the most recent US trading day. The DataHub mirror's lag is bounded by its ~4-hour cron.

## MCP / connector notes

No dedicated MCP exists for the VIX or CBOE volatility indices, and none is needed for this entry. Two CSV files at stable URLs over plain HTTPS, no auth, no rate limit. A generic CSV-or-time-series MCP plus `curl` covers every realistic agent use case. If an agent wants the VIX as part of a broader volatility / options surface (VVIX, SKEW, term-structure futures), the right MCP target is a CBOE options-data wrapper or a market-data MCP that already covers indices (Alpha Vantage `VIX`, FRED `VIXCLS`), not a single-series VIX connector.

## Review notes

- License `ODC-PDDL-1.0` is a valid SPDX identifier but is not on the explicit example list in SCHEMA.md. Same flag as `sp500-companies-financials` (the other DataHub Core entry).
- DataHub's repo claims public-domain status by inference because CBOE's historical-data page carries no explicit licence statement. An agent redistributing this dataset commercially should verify CBOE's current terms directly rather than relying on the DataHub maintainer's good-faith call.
- `access_test` runs against the GitHub raw URL (`master` branch) rather than the DataHub R-link because the latter returns 302 and would require `curl -L` to validate the eventual 200. Returned 200 at last verification.
- No new canonical join keys proposed. `DATE` covers the only cross-source join surface this dataset exposes.
