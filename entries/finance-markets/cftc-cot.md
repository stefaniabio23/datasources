---
id: cftc-cot
name: CFTC Commitments of Traders
domain: finance-markets
entry_kind: time-series
description: Weekly breakdown of open interest in US futures and options markets by trader category, published by the CFTC.
homepage_url: https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
docs_url: https://dev.socrata.com/foundry/publicreporting.cftc.gov/6dca-aqww
type:
  - rest-api
  - socrata
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "Socrata SODA app-token-optional; no token = shared throttle, fine for normal query volumes"
bulk_available: true
frequency: weekly
lag: "3 days: positions as of Tuesday close, released the following Friday 3:30pm ET"
geography: [US]
structure: panel
pit_reconstructable: true
revisions_possible: false
release_lag_days: 3
join_keys:
  - DATE
primary_keys:
  - CFTC_CONTRACT_MARKET_CODE
  - CFTC_COMMODITY_CODE
  - CFTC_MARKET_CODE
  - CFTC_REGION_CODE
join_key_fields:
  - join_key: DATE
    fields: [report_date_as_yyyy_mm_dd]
mcp_status: api-direct-sufficient
agent_use_cases:
  - positioning analysis by trader category
  - commercial vs speculative sentiment tracking
  - open-interest concentration monitoring
  - futures-market crowding signals
  - weekly positioning time series
access_test:
  command: "curl -sf 'https://publicreporting.cftc.gov/resource/jun7-fc8e.json?$limit=1'"
  expected_status: 200
  expected_fields: [cftc_contract_market_code, report_date_as_yyyy_mm_dd, commodity_name, open_interest_all]
last_verified: 2026-07-02
build_priority: medium
---

# CFTC Commitments of Traders

## Why this source matters

The Commitments of Traders (COT) report is the US Commodity Futures Trading Commission's weekly breakdown of open interest in every futures and options market with 20+ reportable traders, split by trader category. It is the canonical public window into who holds futures positions: commercial hedgers vs non-commercial speculators (Legacy), or the finer Producer / Swap Dealer / Managed Money / Other split (Disaggregated) and Dealer / Asset Manager / Leveraged Funds / Other split for financial futures (TFF). Positions are measured at Tuesday close and published Friday 3:30pm ET. Legacy history runs back to 1986; Disaggregated and TFF to June 2006; the Supplemental (index-trader) series to 2006-2007. Since October 2022 the CFTC serves all of this from a Socrata Public Reporting Environment at `publicreporting.cftc.gov` with a clean SODA API and bulk downloads. This is a finance-markets source with heavy overlap into consumer-signal / sentiment workflows.

## Agent use cases

- positioning analysis by trader category
- commercial vs speculative sentiment tracking
- open-interest concentration monitoring
- futures-market crowding signals
- weekly positioning time series

## Join strategy

The only registry-canonical join key COT exposes is `DATE` (`report_date_as_yyyy_mm_dd`, the Tuesday as-of date; also carried textually as `yyyy_report_week_ww`). Everything else that identifies a row is CFTC-internal: `CFTC_CONTRACT_MARKET_CODE` (6-digit code per contract market, e.g. `001612` for CBOT HRW Wheat), `CFTC_COMMODITY_CODE`, `CFTC_MARKET_CODE` (exchange, e.g. `CBT`), and `CFTC_REGION_CODE`. These live in `primary_keys`. There is no clean canonical bridge from a CFTC contract-market code to an exchange ticker or ISIN, mapping to `TICKER`/`FIGI` requires a hand-maintained crosswalk, so agents should join COT to price data via a lookup table keyed on `CFTC_CONTRACT_MARKET_CODE` plus `market_and_exchange_names`, then to prices on `DATE`. The CFTC contract-market code is a plausible new canonical key (see Review notes); it is stable and reused across all COT report variants and the OFR Hedge Fund Monitor.

## Access notes

Hit the Socrata SODA endpoint first: `https://publicreporting.cftc.gov/resource/<dataset-id>.json`. Dataset IDs: Legacy Futures-Only `6dca-aqww`, Legacy Combined `jun7-fc8e`, plus separate IDs for Disaggregated, TFF, and Supplemental (browse from the story at `publicreporting.cftc.gov/stories/s/r4w3-av2u`). Standard SODA query params apply (`$where`, `$select`, `$limit`, `$order`, `$offset`); no auth token is required, though registering a free app token raises the shared throttle. For full history prefer the per-report bulk exports (`.csv`/`.txt`/zip) linked from the COT and Historical-Compressed pages, or the legacy fixed-name text feeds under `cftc.gov/dea/newcot/` (e.g. `f_disagg.txt`, `FinFutWk.txt`). Data is never restated after publication, so a naive `$where=report_date_as_yyyy_mm_dd>...` incremental pull is point-in-time safe.

## MCP / connector notes

No dedicated MCP found; the closest third-party tooling is an Apify COT scraper. The source is a vanilla Socrata deployment, so a generic Socrata/SODA MCP already covers it and `api-direct-sufficient` is the right call. If a COT-specific connector is built, the useful surface is: `list_markets` (distinct `cftc_contract_market_code` + `market_and_exchange_names`), `get_positions(market_code, report=legacy|disagg|tff, from, to)`, and `latest_release`. The connector must abstract over the five report variants (Legacy / Disaggregated / TFF / Supplemental, each in Futures-Only and Combined forms) and normalise the differing column sets between them.

## Review notes

Potential new join key for review: CFTC_CONTRACT_MARKET_CODE
  Entity type: futures_contract_market
  Pattern: `^[0-9]{6}$` (source pads/space-trims; e.g. "001612")
  Other datasets that would use it: all CFTC COT report variants, OFR Hedge Fund Monitor (financialresearch.gov) which republishes CFTC TFF data. A related `CFTC_COMMODITY_CODE` (3-digit) groups markets by commodity and could be a second candidate.

License is a US federal work (17 USC 105), mapped to `US-Government-Public-Domain`. CFTC publishes no individual-trader identities and does not retroactively revise released figures.
