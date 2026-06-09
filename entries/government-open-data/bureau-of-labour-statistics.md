---
id: bureau-of-labour-statistics
name: Bureau of Labor Statistics (BLS) Public Data API
domain: government-open-data
entry_kind: mixed
description: US Bureau of Labor Statistics Public Data API and bulk flat files covering employment, unemployment, wages, prices (CPI/PPI), productivity, job openings, and compensation across dozens of survey programs.
homepage_url: https://www.bls.gov/data/
docs_url: https://www.bls.gov/developers/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free
license: US-Government-Public-Domain
rate_limit: "v2 with registered API key: 500 queries/day, up to 50 series per query, 20-year span; v2 without key: 25 queries/day, up to 25 series, 10-year span"
bulk_available: true
frequency: monthly for most series; weekly/quarterly/annual underlying cadence varies by survey
lag: "typically 1-6 weeks after reference period (e.g. Employment Situation released first Friday of following month; CPI mid-month)"
geography: [USA]
join_keys:
  - DATE
  - US_STATE_CODE
  - FIPS
primary_keys:
  - BLS_SERIES_ID
  - BLS_SURVEY_ABBREVIATION
join_key_fields:
  - join_key: DATE
    fields: [Results.series.data.year, Results.series.data.period, Results.series.data.periodName]
  - join_key: US_STATE_CODE
    fields: [Results.series.catalog.area, Results.series.catalog.state]
  - join_key: FIPS
    fields: [Results.series.catalog.area_code]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cyanheads/bls-labor-mcp-server
  - github.com/larasrinath/bls_mcp
  - github.com/shawndrake2/mcp-bls
  - github.com/pipeworx-io/mcp-bls
  - github.com/kovashikawa/bls_mcp
  - github.com/RakeemRanger/bls-mcp
mcp_notes: >
  Multiple community MCPs exist; cyanheads/bls-labor-mcp-server exposes 7 tools
  (list_surveys, search_series, get_series, get_latest, plus optional DuckDB
  dataframe ops). All wrap the v2 REST API; registered key recommended for the
  500/day quota. No official BLS-maintained MCP.
agent_use_cases:
  - unemployment-rate and labour-force lookup
  - inflation tracking via CPI and PPI series
  - state and metro-area employment panels
  - wage and compensation benchmarking
  - job-openings and labour-turnover (JOLTS) monitoring
access_test:
  command: "curl -sf -X POST -H 'Content-Type: application/json' -d '{\"seriesid\":[\"LNS14000000\"]}' https://api.bls.gov/publicAPI/v2/timeseries/data/"
  expected_status: 200
  expected_fields: [status, Results.series]
last_verified: 2026-06-09
build_priority: medium
notes: "access_test executed successfully without API key (anonymous tier returns status=REQUEST_SUCCEEDED for series LNS14000000, the seasonally adjusted civilian unemployment rate). Registered key recommended for production use."
---

# Bureau of Labor Statistics (BLS) Public Data API

## Why this source matters

The Bureau of Labor Statistics is the principal US federal statistical agency for labour-market and price data. Its Public Data API v2 exposes hundreds of survey programs as queryable time series, including the Current Population Survey (CPS), Current Employment Statistics (CES), Local Area Unemployment Statistics (LAUS), Consumer Price Index (CPI), Producer Price Index (PPI), Job Openings and Labor Turnover Survey (JOLTS), Occupational Employment and Wage Statistics (OEWS), National Compensation Survey (NCS), and productivity series. For agents doing US macro analysis, BLS is the primary source rather than a downstream aggregator: FRED, Trading Economics, and similar dashboards republish BLS releases on a lag. Secondary domain coverage: `finance-markets` (CPI and PPI feed inflation forecasting), `consumer-signal` (real earnings, consumer-expenditure surveys).

## Agent use cases

- unemployment-rate and labour-force lookup
- inflation tracking via CPI and PPI series
- state and metro-area employment panels
- wage and compensation benchmarking
- job-openings and labour-turnover (JOLTS) monitoring

## Join strategy

Every BLS observation is timestamped, so `DATE` is the universal join axis (year + period code; period names like `M01`-`M12` for months, `Q01`-`Q05` for quarters, `A01` for annual). Geographic series carry `US_STATE_CODE` and `FIPS` codes in the area dimension of LAUS, OEWS, QCEW, and CES state/metro releases.

BLS-internal identifiers (`BLS_SERIES_ID` and the two-letter `BLS_SURVEY_ABBREVIATION` prefix) are the load-bearing keys for actually fetching data but are intentionally outside the canonical join registry. Series IDs are deterministic concatenations of survey + area + industry + data-type codes, for example `LNS14000000` (seasonally-adjusted civilian unemployment rate from CPS), `CUUR0000SA0` (CPI-U All Items, US city average, not seasonally adjusted), `WPUFD4` (PPI Final Demand), `CES0000000001` (total nonfarm employment from CES), `LAUCN040010000000005` (Autauga County AL unemployment rate from LAUS). Survey abbreviations: `LN`/`LU` (CPS), `CE` (CES), `LA` (LAUS), `EN` (QCEW), `CU`/`CW` (CPI), `WP`/`PC` (PPI), `JT` (JOLTS), `OE` (OEWS), `CI` (ECI), `PR` (Productivity).

Industry dimensions in CES, QCEW, and OEWS use NAICS codes; occupations in OEWS and NCS use SOC codes. Neither NAICS nor SOC is currently in `schema/join-keys.yaml` (see Review notes).

Common pairings: FRED republishes the headline BLS series with the same DATE axis; Census Bureau ACS for demographic context behind labour-force figures; BEA NIPA for income aggregates that complement BLS earnings; EIA for energy-input cross-checks on PPI. State-level joins to ACS or Census economic series via `US_STATE_CODE` / `FIPS`.

## Access notes

**Auth.** Registration at `https://data.bls.gov/registrationEngine/` produces a free v2 API key. Pass via `"registrationkey"` field in the JSON POST body. The API is also reachable anonymously (no key) at a reduced quota.

**Rate limits.** Registered v2: 500 queries/day, up to 50 series per query, 20-year span per series, with optional `catalog`, `calculations`, `annualaverage`, and `aspects` flags. Anonymous v2: 25 queries/day, up to 25 series per query, 10-year span, no optional flags. Limits are per IP for anonymous and per key for registered. v1 endpoint (`/publicAPI/v1/timeseries/data/`) is still live with a 10-series / 10-year cap and no auth.

**Request shape.** All multi-series and parameterised queries are POST against `https://api.bls.gov/publicAPI/v2/timeseries/data/` with a JSON body: `{"seriesid": ["LNS14000000"], "startyear": "2020", "endyear": "2026", "registrationkey": "..."}`. Single-series GET shortcut: `https://api.bls.gov/publicAPI/v2/timeseries/data/<SERIES_ID>` returns the most recent three years.

**Bulk.** Flat-file tab-separated dumps at `https://download.bls.gov/pub/time.series/<survey>/` (e.g. `/ln/` for CPS, `/cu/` for CPI, `/ce/` for CES, `/la/` for LAUS). Each survey directory carries a `<survey>.txt` README plus a `<survey>.series` file (series catalog), `<survey>.data.*` files (observations partitioned by series subset), and dimension lookup tables. The download host enforces a strict browser-style User-Agent; requests with default `curl`/`python-requests` UAs are 403'd by Akamai. Bulk is the only sensible path for full-history multi-million-row pulls; the API is for targeted lookups.

**License.** Public domain under 17 USC 105. BLS asks for citation as the data source but imposes no redistribution restrictions.

**Gotchas.** Series IDs are positional concatenations of fixed-width segment codes; an off-by-one in the area or industry segment silently returns no data rather than an error. Some surveys have both seasonally-adjusted and not-seasonally-adjusted variants under different ID prefixes (`LNS` vs `LNU` for CPS). Discontinued series persist in the catalog. Periods of government appropriations lapse leave gaps with footnote codes rather than zeros.

## MCP / connector notes

`mcp-exists` with at least six community MCP servers. Most feature-complete is `cyanheads/bls-labor-mcp-server`, which exposes `bls_list_surveys`, `bls_search_series`, `bls_get_series` (up to 50 series), `bls_get_latest`, plus optional DuckDB-backed `bls_dataframe_query` for SQL over fetched results. `larasrinath/bls_mcp` mirrors the core surface with a popular-series helper. None are official BLS releases; all are early-stage (single-digit stars).

A hardened connector should abstract over: series-ID construction from natural-language survey + geography + industry queries (the positional-code scheme is the main friction); registered vs anonymous quota switching; the API-vs-bulk decision (anything over a few years times a few dozen series is faster via flat files); footnote-code interpretation (especially the appropriation-lapse and revision footnotes that the raw response only flags by single-character codes).

## Review notes

- Potential new join key for review: `NAICS`. Entity type: `industry_classification`. Pattern: `^[0-9]{2,6}$` (2-6 digit hierarchy). Other datasets that would use it: BLS CES/QCEW/OEWS industry dimensions, Census Bureau Economic Census and County Business Patterns, BEA industry accounts, SEC EDGAR SIC-to-NAICS mappings. High cross-source utility for US industry-level joins.
- Potential new join key for review: `SOC_CODE`. Entity type: `occupation_classification`. Pattern: `^[0-9]{2}-[0-9]{4}$`. Other datasets that would use it: BLS OEWS/NCS, O*NET occupational database, Census ACS occupation tabulations.
- Potential new join key for review: `BLS_SERIES_ID`. Entity type: `bls_time_series`. Pattern: `^[A-Z]{2}[A-Z0-9]+$`. Cross-source utility is real because FRED, Haver, and academic papers cite BLS series IDs verbatim; same situation flagged in the FRED entry for `FRED_SERIES_ID`. Worth adding if a second BLS-family entry (e.g. QCEW standalone) lands.
- `access_test` executed successfully against the anonymous v2 endpoint with HTTP 200 and `status: REQUEST_SUCCEEDED`; quota will exhaust at 25 queries/day from the executing IP without a registration key.
- BLS website pages (`/data/`, `/developers/`, `/help/`) return 403 to WebFetch and to non-browser curl due to Akamai bot protection; figures here cross-referenced from community MCP READMEs that wrap the same documented API. Worth re-verifying the rate-limit and span figures from official BLS documentation manually before publication.
