---
id: nasdaq-data-link
name: Nasdaq Data Link
domain: finance-markets
description: Nasdaq-operated marketplace and REST API delivering financial, economic, and alternative time-series and tables data (formerly Quandl), spanning free public-domain datasets and ~400+ premium vendor databases.
homepage_url: https://data.nasdaq.com/
docs_url: https://docs.data.nasdaq.com/
type:
  - rest-api
  - bulk-download
  - dataset-dump
auth_required: api-key-free
cost: freemium
license: nasdaq-data-link-mixed-vendor-terms
rate_limit: "anonymous: 20 calls / 10 min and 50 calls / day; authenticated free tier: 300 calls / 10 sec, 2,000 calls / 10 min, 50,000 calls / day per published Quandl/Nasdaq limits"
bulk_available: true
frequency: varies by dataset (intraday, daily, weekly, monthly, quarterly, annual)
lag: varies by dataset (real-time for premium feeds; end-of-day for most free/legacy series; many legacy free datasets such as WIKI are frozen and no longer updated)
geography: [global]
join_keys:
  - TICKER
  - ISIN
  - CUSIP
  - ISO_3
  - DATE
primary_keys:
  - NASDAQ_DATA_LINK_DATABASE_CODE
  - NASDAQ_DATA_LINK_DATASET_CODE
  - NASDAQ_DATA_LINK_VENDOR_CODE
  - NASDAQ_DATA_LINK_DATATABLE_CODE
join_key_fields:
  - join_key: DATE
    fields: [dataset_data.column_names, dataset_data.data, dataset.column_names, dataset.data, dataset.start_date, dataset.end_date, dataset.newest_available_date, dataset.oldest_available_date]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/stefanoamorelli/nasdaq-data-link-mcp
  - pypi.org/project/nasdaq-data-link-mcp-os
mcp_notes: >
  Community MCP (MIT, PyPI nasdaq-data-link-mcp-os, Python 3.13+) wraps the
  official Nasdaq/data-link-python SDK and exposes 5 generic tools that work
  against any database code (WIKI, WORLDBANK, E360, RTAT, NFN, etc.). Requires
  NASDAQ_DATA_LINK_API_KEY. Not affiliated with Nasdaq, Inc.
agent_use_cases:
  - end-of-day equity price history
  - macro and World Bank indicator lookup
  - retail trading activity (RTAT) tracking
  - mutual fund and ETF reference data
  - alternative-data dataset discovery
access_test:
  command: "curl -sf 'https://data.nasdaq.com/api/v3/datasets/WIKI/FB/data.json?limit=1&api_key=${NASDAQ_DATA_LINK_API_KEY}'"
  expected_status: 200
  expected_fields: [dataset_data]
last_verified: 2026-06-08
build_priority: medium
notes: "access_test not yet executed; requires ${NASDAQ_DATA_LINK_API_KEY}. Anonymous test against the same endpoint returned HTTP 403 from Incapsula bot protection, so reachability needs to be re-verified with a real key."
---

# Nasdaq Data Link

## Why this source matters

Nasdaq Data Link is the rebrand of Quandl after Nasdaq acquired it in 2018. It is a single REST API and marketplace for financial, economic, and alternative datasets, organised as `database_code/dataset_code` pairs (e.g. `WIKI/AAPL`, `WORLDBANK/WLD_NY_GDP_MKTP_CD`, `OPEC/ORB`). The free tier still hosts widely-cited public datasets (World Bank indicators, OPEC reference basket, legacy WIKI end-of-day US equities, FRED mirror, OECD), while the majority of the catalogue is premium vendor-curated data (Nasdaq RTAT, Equities 360, Nasdaq Fund Network, alternative datasets from third parties) sold a la carte. For agents it is a useful second-stop after FRED for macro and a low-friction way to reach Nasdaq's own retail-trading and fund-network datasets without negotiating vendor contracts directly. Secondary domain: `consumer-signal` via RTAT and other alt-data feeds.

## Agent use cases

- end-of-day equity price history
- macro and World Bank indicator lookup
- retail trading activity (RTAT) tracking
- mutual fund and ETF reference data
- alternative-data dataset discovery

## Join strategy

Nasdaq Data Link is a federation of vendor databases rather than a single normalised schema, so canonical join keys are dataset-dependent. The common ones exposed across the catalogue:

- `TICKER` for equity-style datasets (WIKI, EOD, SHARADAR/SEP, Equities 360). Tickers are not point-in-time corrected outside the premium SHARADAR products, so a delisted or re-used ticker can return stale or wrong rows.
- `CUSIP` and `ISIN` for security-reference datasets (Equities 360, Nasdaq Fund Network, some vendor feeds). Coverage varies per database; check the per-database documentation page on data.nasdaq.com.
- `ISO_3` for country-keyed macro data (WORLDBANK, OECD, IMF mirrors).
- `DATE` is universal: every observation is timestamped, and date filtering (`start_date`, `end_date`, `collapse`, `transform`) is a first-class API parameter.

Nasdaq-internal IDs (`DATABASE_CODE` / `DATASET_CODE` pairs like `WIKI/AAPL`, `WORLDBANK/WLD_NY_GDP_MKTP_CD`, `RTAT/RTAT10`) are intentionally outside the canonical registry; use them for direct Nasdaq Data Link lookups, not cross-source joins. For instrument-level joins across providers, pair with OpenFIGI (FIGI) and SEC EDGAR (CIK).

## Access notes

**Auth:** free API key from a Nasdaq Data Link account at `https://data.nasdaq.com/account/profile`. Pass as `?api_key=<key>` query parameter. The same key authenticates the REST API, the Python (`Nasdaq/data-link-python`) and R (`Nasdaq/data-link-r`) SDKs, and the Excel add-in.

**Anonymous use:** technically allowed for free datasets but capped at 20 calls / 10 min and 50 calls / day and gated by Incapsula bot protection, which returns HTTP 403 to plain `curl`. Use a key for any non-trivial work.

**Two API surfaces:** Time-series API (`/api/v3/datasets/{database_code}/{dataset_code}/data.{json|csv|xml}`) for legacy Quandl-style time series, and Tables API (`/api/v3/datatables/{vendor_code}/{datatable_code}.{json|csv}`) for the newer wide-format datasets including most premium products. Endpoint shape, filters, and pagination differ between the two.

**Bulk:** premium subscribers can pull whole databases as zipped CSV (`?download_type=full`) or incremental deltas (`?download_type=partial`); free datasets do not expose bulk download.

**Streaming / real-time:** separate Nasdaq Cloud Data Service (NCDS) SDKs (`Nasdaq/NasdaqCloudDataService-SDK-Python` / `-Java`) for exchange feeds, not part of the REST API.

**Freshness gotchas:** the once-flagship free `WIKI` end-of-day US equities dataset has been frozen since 2018 and is not a current price source despite being the most-cited example in tutorials. `OPEC/ORB`, `WORLDBANK/*`, and `OECD/*` are still maintained. Always check the dataset's `newest_available_date` in the metadata endpoint before treating it as live.

**Rate limit:** documented free-tier limits are 300 calls / 10 sec, 2,000 calls / 10 min, and 50,000 calls / day per key (per long-standing Quandl docs carried over to Nasdaq Data Link). Premium subscriptions raise these.

## MCP / connector notes

`mcp-exists`. `stefanoamorelli/nasdaq-data-link-mcp` (MIT, PyPI `nasdaq-data-link-mcp-os`, Python 3.13+, community, not affiliated with Nasdaq) wraps the official `Nasdaq/data-link-python` SDK and exposes 5 generic tools that work against any database code: dataset search, dataset/datatable fetch with date filters, metadata lookup, and format export. Demonstrated against WIKI, WORLDBANK, E360, RTAT, and NFN in the README. Requires `NASDAQ_DATA_LINK_API_KEY`.

Gaps a hardened connector should address: routing between the two API surfaces (time-series vs tables) automatically based on database code, surfacing per-dataset premium-vs-free status and `newest_available_date` to avoid silently returning frozen series like WIKI, batching large pulls through the premium bulk-download endpoint instead of paginating, and exposing the per-vendor licensing notes alongside results so downstream agents do not redistribute restricted vendor data.

## Review notes

- License field `nasdaq-data-link-mixed-vendor-terms` is not in the SCHEMA.md known-canonical list. Proposed because no single SPDX code fits: Nasdaq Data Link itself is a marketplace, not a publisher, and licensing is per-database. Free datasets carry source-specific terms (World Bank: CC-BY-4.0; OPEC: source attribution; legacy WIKI: public-domain crowd-sourced); premium datasets carry vendor-specific subscriber agreements that typically forbid redistribution. Alternatives: split entries per major sub-database, or add `nasdaq-data-link-mixed-vendor-terms` to SCHEMA.md § License conventions. Worth raising before further finance-markets entries with similar marketplace shape (Refinitiv, Bloomberg Enterprise) land.
- Rate-limit numbers carried over from long-standing Quandl documentation; `docs.data.nasdaq.com` rate-limit page was not fetchable from this run. Re-verify against the official docs page before publication.
- `access_test` constructed but not executed; requires `${NASDAQ_DATA_LINK_API_KEY}`. Anonymous probe against the same endpoint returned HTTP 403 from Incapsula bot protection (not a routing failure, the host is reachable; the WAF blocks unauthenticated SDK-less traffic).
- Coverage of `CUSIP` / `ISIN` join keys is asserted at the catalogue level (Equities 360, Nasdaq Fund Network databases document both) but is not uniform across every database; an agent should not assume every Nasdaq Data Link result row carries them.
