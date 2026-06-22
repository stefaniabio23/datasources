---
id: sp500-companies-financials
name: S&P 500 Companies Financials
domain: finance-markets
entry_kind: reference-table
description: Static CSV roster of the 500 S&P 500 constituents with sector, ticker, SEC filings link, and a snapshot of common per-share valuation metrics.
homepage_url: https://datahub.io/core/s-and-p-500-companies-financials
docs_url: https://github.com/datasets/s-and-p-500-companies-financials
type:
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: ODC-PDDL-1.0
rate_limit: "none; static CSV download"
bulk_available: true
frequency: ad-hoc (script-triggered; constituents refreshed Feb 2026, financials refreshed Jun 2026)
lag: "unknown; refresh is run-on-demand against Wikipedia + Yahoo Finance"
geography: [USA]
join_keys:
  - TICKER
join_key_fields:
  - join_key: TICKER
    fields: [Symbol]
primary_keys:
  - Symbol
mcp_status: api-direct-sufficient
mcp_maturity: none
mcp_notes: >
  Three CSVs at stable URLs, no auth, no rate limit. Curl + a CSV parser covers the
  whole surface; an MCP wrapper would add little. Pair with a live-pricing MCP
  (Alpha Vantage, Polygon, yfinance) for fresh quotes.
agent_use_cases:
  - resolve S&P 500 ticker list for a backtest universe
  - join company ticker to GICS sector for sector-neutral analysis
  - look up SEC EDGAR filings URL by ticker
  - sanity-check ticker spelling against a curated list
access_test:
  command: "curl -sfI 'https://raw.githubusercontent.com/datasets/s-and-p-500-companies-financials/master/data/constituents-financials.csv'"
  expected_status: 200
  expected_fields: [Symbol, Name, Sector, Price, "Market Cap", "SEC Filings"]
last_verified: 2026-06-09
build_priority: low
notes: >
  Financial metrics columns (Price, P/E, Market Cap, EBITDA, etc.) are a snapshot
  taken at the last manual refresh, not a live feed. Treat the financials columns
  as illustrative; pull live quotes from a market-data API for anything
  decision-relevant.
---

# S&P 500 Companies Financials

## Why this source matters

DataHub's "Core" curated CSV of the 500 S&P 500 index constituents, scraped from Wikipedia's index page and Yahoo Finance via `yfinance`. The interesting column is the static roster of ticker, company name, and GICS sector, plus a SEC EDGAR filings URL per company. The valuation snapshot (Price, P/E, EBITDA, Market Cap, Dividend Yield, 52-week range, Price/Sales, Price/Book) is bundled in but is only as fresh as the last manual refresh, so treat it as illustrative rather than market data. Three files: `constituents.csv` (ticker + name + sector), `constituents-financials.csv` (the above + metrics + SEC URL), and `scatter-data.csv` (a derived view filtered to positive P/E ratios under 100, with Market Cap in billions).

## Agent use cases

- resolve S&P 500 ticker list for a backtest universe
- join company ticker to GICS sector for sector-neutral analysis
- look up SEC EDGAR filings URL by ticker
- sanity-check ticker spelling against a curated list

## Join strategy

The only canonical join key exposed is `TICKER` (column `Symbol`). The embedded SEC EDGAR filings URL contains a `CIK=<TICKER>` query parameter but resolves to the ticker, not a raw CIK integer, so this entry does not claim `CIK` as a join key. Pair with SEC EDGAR (for actual `CIK`-keyed filings), OpenFIGI (for `FIGI`/`ISIN`/`CUSIP` cross-walks), Alpha Vantage / Polygon / FRED / yfinance (for live prices and time series), and Wikidata (for `WIKIDATA_QID` company identifiers) to expand the join graph.

GICS sector is exposed as a free-text label in the `Sector` column, not as a canonical industry code. The directory currently has no canonical `GICS_SECTOR` join key; see Review notes.

## Access notes

No auth, no rate limit, no API. Three CSV files at stable URLs on both datahub.io and the upstream GitHub repo `datasets/s-and-p-500-companies-financials`. The DataHub R-link (`datahub.io/core/.../_r/-/data/<file>.csv`) currently returns HTTP 302 to a signed CDN URL; the GitHub raw URL (`raw.githubusercontent.com/datasets/s-and-p-500-companies-financials/master/data/<file>.csv`) returns 200 directly and is the safer programmatic target.

Refresh is run-on-demand via the scripts in the repo's `scripts/` directory; there is no published cadence. Constituents file was last refreshed 2026-02-09, financials 2026-06-09. To verify freshness, check the latest commit date for `data/constituents-financials.csv` in the GitHub repo.

## MCP / connector notes

No MCP exists and none is needed. The whole surface is three CSVs at stable URLs; `curl` plus any CSV parser covers every use case. The valuation columns are stale anyway, so the high-value behaviour, joining the constituent roster to a live-quote source, belongs in whichever market-data MCP an agent is already using (Alpha Vantage, Polygon, yfinance).

## Review notes

- License `ODC-PDDL-1.0` is not on the explicit SPDX example list in SCHEMA.md but is a valid SPDX identifier; flagged for confirmation.
- Potential new join key for review: `GICS_SECTOR` (or `GICS_CODE` for the 8-digit numeric form). Entity type: industry_classification. Pattern: free-text sector label as exposed here (e.g. "Information Technology", "Industrial Conglomerates"), or `^[0-9]{2,8}$` for the canonical numeric GICS code. Other datasets that would use it: most equity-market and corporate-fundamentals sources (Polygon, Alpha Vantage, SEC EDGAR, yfinance) tag securities with GICS or a near-equivalent sector classification.
- Potential entry_kind ambiguity: this is a small curated lookup of ~500 rows, so `reference-table` fits better than `registry`, but a case could be made for `registry` since each row is one canonical company. Chose `reference-table` because the file is a static snapshot of the index membership, not a live entity directory.
