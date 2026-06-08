---
id: fred
name: FRED (Federal Reserve Economic Data)
domain: finance-markets
description: Aggregated economic and financial time-series database (~800K series) maintained by the Federal Reserve Bank of St. Louis, covering US macro indicators plus international data from BIS, OECD, World Bank, and others.
homepage_url: https://fred.stlouisfed.org/
docs_url: https://fred.stlouisfed.org/docs/api/fred/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free
license: FRED-Mixed-Source-Terms
rate_limit: "120 requests per 60 seconds per API key (per FRED API documentation)"
bulk_available: true
frequency: varies by series (daily, weekly, monthly, quarterly, annual)
lag: "varies by series; same-day for daily market data, 1-2 months for monthly BLS/BEA releases"
geography: [USA, global]
join_keys:
  - DATE
  - ISO_3
primary_keys:
  - FRED_SERIES_ID
  - FRED_CATEGORY_ID
  - FRED_RELEASE_ID
  - FRED_SOURCE_ID
  - FRED_TAG_NAME
join_key_fields:
  - join_key: DATE
    fields: [observations.date, observations.realtime_start, observations.realtime_end, seriess.observation_start, seriess.observation_end, seriess.last_updated, seriess.realtime_start, seriess.realtime_end]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/stefanoamorelli/fred-mcp-server
  - github.com/kablewy/fred-mcp-server
  - github.com/shanehull/fred-mcp
  - github.com/zachspar/fred-mcp
mcp_notes: >
  Multiple community MCPs exist; stefanoamorelli/fred-mcp-server (~100 stars,
  npm + Docker, Smithery-installable) is the most mature. All wrap the official
  REST API and require a free FRED_API_KEY. No official Federal Reserve MCP.
agent_use_cases:
  - macroeconomic indicator lookup
  - interest-rate and yield-curve retrieval
  - inflation and CPI tracking
  - cross-country comparison
  - time-series for backtesting and feature engineering
access_test:
  command: "curl -sf 'https://api.stlouisfed.org/fred/series?series_id=GNPCA&api_key=${FRED_API_KEY}&file_type=json'"
  expected_status: 200
  expected_fields: [seriess]
last_verified: 2026-06-08
build_priority: medium
notes: "access_test not yet executed; requires ${FRED_API_KEY}. Endpoint reachability confirmed: api.stlouisfed.org returns HTTP 400 with explicit api_key error when key is omitted."
---

# FRED (Federal Reserve Economic Data)

## Why this source matters

FRED is the Federal Reserve Bank of St. Louis's aggregated economic and financial time-series database, ~800,000 series pulled from ~100+ source agencies (BLS, BEA, Census, Treasury, OECD, World Bank, BIS, Eurostat, IMF, S&P). For agents doing macro analysis, FRED is the single REST endpoint that replaces hand-stitching dozens of statistical-agency APIs. The same source covers `government-open-data` as a secondary domain because much of the catalogue is repackaged US federal statistics.

## Agent use cases

- macroeconomic indicator lookup
- interest-rate and yield-curve retrieval
- inflation and CPI tracking
- cross-country comparison
- time-series for backtesting and feature engineering

## Join strategy

FRED's primary join surface is `DATE` (every observation is timestamped, frequencies range from daily to annual) and `ISO_3` for cross-country series. International data is filed under three-letter country codes inside series IDs and category tags.

FRED-internal IDs (`FRED_SERIES_ID` like `GDP`, `UNRATE`, `DGS10`; `FRED_CATEGORY_ID`; `FRED_RELEASE_ID`; `FRED_SOURCE_ID`) are intentionally outside the canonical registry; use them for direct FRED lookups, not cross-source joins. Series IDs are stable and widely cited in academic papers and financial blogs, so an agent can usually find the right ID by name search.

There are no ticker, CUSIP, ISIN, CIK, NDC, or trial-ID joins. FRED is time-series-of-numbers only; pair with OpenFIGI / SEC EDGAR for instrument or issuer joins, and with the underlying statistical agencies (BLS API, BEA API) when you need finer-grained dimensions than FRED publishes.

Potential new join key for review: `FRED_SERIES_ID`. Pattern: `^[A-Z0-9]+$` (e.g. `GDP`, `UNRATE`, `DGS10`, `CPIAUCSL`). Other datasets that would use it: ALFRED (FRED's vintage-aware sibling), GeoFRED, FRASER, and most quant-finance tutorials/notebooks reference these IDs verbatim. Worth adding if cross-referencing FRED series across multiple entries becomes useful.

## Access notes

**Auth:** free API key from `https://fred.stlouisfed.org/docs/api/api_key.html`. Pass as `?api_key=<key>` query parameter. Same key works across FRED, ALFRED, and GeoFRED endpoints.

**Rate limit:** 120 requests per 60 seconds per key. Generous for interactive use; bulk pulls should respect the window or use the bulk download.

**Bulk:** the FRED catalogue is downloadable as ZIP archives by category at `https://fred.stlouisfed.org/categories` (the bulk pages export full series histories as CSV). Faster than paginating the API for whole-category pulls.

**License gotcha:** FRED's own metadata and aggregation are free to use with attribution, but a meaningful subset of series comes from third-party providers (BIS, S&P/Case-Shiller, ICE BofA, Haver Analytics) that impose redistribution restrictions documented per-series on the series page. An agent redistributing FRED data downstream should check the `notes` field on each series before republishing. US federal-government source data (BLS, BEA, Census) is in the public domain under 17 USC 105.

**ALFRED:** vintage-aware sister database at `https://alfred.stlouisfed.org/` exposes the as-of-date snapshots needed for backtesting (avoids look-ahead bias from revised series). Same API key.

## MCP / connector notes

`mcp-exists` with several community implementations on GitHub. Most mature is `stefanoamorelli/fred-mcp-server` (~100 stars, npm package `fred-mcp-server`, Smithery-installable, Docker image, version 1.0.2). Exposes `fred_browse`, `fred_search`, `fred_get_series` with date-range and transformation options (percent change, log, aggregation). Requires `FRED_API_KEY` env var. Explicitly community, not affiliated with the Fed.

Other community options: `kablewy/fred-mcp-server`, `shanehull/fred-mcp` (claims full API coverage including categories, releases, sources, tags, GeoFRED), `zachspar/fred-mcp` (Python, built on `fred-py-api`). No official Federal Reserve MCP.

Gaps a hardened connector should address: ALFRED vintage queries (most existing MCPs cover FRED only), automatic series-ID disambiguation from natural-language names, batch series fetch with rate-limit-aware throttling, and surfacing the per-series redistribution notes so downstream agents don't accidentally republish restricted vendor data.

## Review notes

- License field `FRED-Mixed-Source-Terms` is not in the SCHEMA.md known-canonical list. Proposed because no single SPDX or existing canonical name fits: FRED itself is free-with-attribution, US-agency source data is `US-Government-Public-Domain`, but BIS/S&P/ICE/Haver series carry vendor-specific restrictions documented per-series. Alternatives: split into two entries (FRED-public-domain subset vs FRED-restricted-vendor subset) or add `FRED-Mixed-Source-Terms` to SCHEMA.md § License conventions.
- Potential new join key `FRED_SERIES_ID` flagged in Join strategy above. Low urgency until a second FRED-family entry (ALFRED, GeoFRED) lands.
- Rate limit (120 req / 60 sec) is cited from common community documentation; the official FRED docs page returned 403 to WebFetch so this should be re-verified manually before publication.
- `access_test` constructed but not executed; requires `${FRED_API_KEY}`. Endpoint host reachability confirmed (HTTP 400 with `api_key not set` error when key omitted).
