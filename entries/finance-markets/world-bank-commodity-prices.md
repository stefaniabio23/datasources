---
id: world-bank-commodity-prices
name: World Bank Commodity Prices (Pink Sheet)
domain: finance-markets
entry_kind: time-series
description: World Bank's monthly Pink Sheet of global commodity price benchmarks across energy, agriculture, fertilizers, metals, and precious metals, published as Excel workbooks with full monthly history back to 1960 and annual aggregates.
homepage_url: https://www.worldbank.org/en/research/commodity-markets
docs_url: https://www.worldbank.org/en/research/commodity-markets
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "none; static Excel and PDF downloads"
bulk_available: true
frequency: monthly
lag: "approximately one month (June 2026 release dated 2026-06-02 covers May 2026 prices)"
geography: [global]
join_keys:
  - DATE
  - ISO_4217
primary_keys:
  - WB_COMMODITY_CODE
join_key_fields:
  - join_key: DATE
    fields: ["Monthly Prices.Date", "Annual Prices.Year"]
  - join_key: ISO_4217
    fields: ["units (price columns labeled in $/bbl, $/mt, $/kg, c/lb, etc., all USD)"]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No dedicated MCP. The whole surface is two Excel files plus a monthly PDF at
  stable URLs. A thin MCP wrapping pandas.read_excel against the monthly and
  annual workbooks (resolve_commodity, get_series, latest_print) covers every
  realistic use. Low value because the upstream cadence is monthly and the file
  is tiny enough to cache locally per release.
agent_use_cases:
  - commodity price time series for backtest and feature engineering
  - cross-commodity index lookup (energy, non-energy, agriculture, metals)
  - inflation-adjusted commodity benchmark series
  - monthly commodity forecast input
  - sanity-check commodity print against vendor feeds
access_test:
  command: "curl -sfI 'https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx'"
  expected_status: 200
  expected_fields: []
last_verified: 2026-06-09
build_priority: low
notes: >
  Distinct from the world-bank-open-data entry (which covers the /v2 Indicators
  API for development statistics). Pink Sheet is its own data product under the
  Prospects Group, distributed only as Excel and PDF; not exposed via the
  Indicators API or the Data360 MCP.
---

# World Bank Commodity Prices (Pink Sheet)

## Why this source matters

The Pink Sheet is the World Bank Prospects Group's monthly bulletin of global commodity price benchmarks, the canonical free reference series for crude oil (Brent, WTI, Dubai), natural gas (US Henry Hub, Europe TTF-equivalent, LNG Japan), coal, agricultural commodities (grains, oils, beverages, raw materials), fertilizers, base metals, and precious metals. The monthly Excel workbook carries history back to 1960 for many series and is widely cited as the reference for long-run real commodity prices. For agents doing macro, inflation, or commodity-exposed asset analysis, this is the long-horizon companion to higher-frequency vendor feeds. Secondary domain is `government-open-data`; this entry sits in `finance-markets` because the use case is commodity price retrieval, not development statistics. Distinct from `world-bank-open-data` which wraps the /v2 Indicators API.

## Agent use cases

- commodity price time series for backtest and feature engineering
- cross-commodity index lookup (energy, non-energy, agriculture, metals)
- inflation-adjusted commodity benchmark series
- monthly commodity forecast input
- sanity-check commodity print against vendor feeds

## Join strategy

The exposed canonical join keys are `DATE` (every observation is a calendar month or year) and `ISO_4217` implicitly via the USD denomination on every price column (the Pink Sheet quotes prices in USD with mixed units: $/bbl for crude, $/mt for metals and grains, c/lb for some agriculturals, $/kg for precious metals; the unit string is in the column header, the currency is always USD).

The source-internal handle is the World Bank commodity code in the header row of the Monthly Prices sheet (e.g. `CRUDE_BRENT`, `CRUDE_DUBAI`, `CRUDE_WTI`, `NGAS_US`, `iNATGAS`, `COAL_AUS`, `MAIZE`, `WHEAT_US_HRW`, `SOYBEANS`, `COFFEE_ARABIC`, `GOLD`, `SILVER`, `COPPER`, `ALUMINUM`, `iAGRICULTURE`, `iENERGY`, `iNONENERGY`). These codes are stable across releases but not in the canonical join-key registry; see Review notes for a proposal.

No country, instrument, or issuer joins. The Pink Sheet is one global benchmark print per commodity per month. Pair with:

- `fred` (cross-validate WTI, Henry Hub, gold; FRED mirrors many Pink Sheet series under codes like `PWTIUSDM`, `PNGASUSUSDM`, `PMAIZMTUSDM`).
- `eia-open-data` (higher-cadence US energy spot and storage).
- `world-bank-open-data` (country-level macro context via the /v2 Indicators API).

## Access notes

No auth, no API, no rate limit. Two Excel workbooks plus a monthly PDF at stable URLs hosted on `thedocs.worldbank.org`:

- Monthly history: `https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx`
- Annual history: `https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx`
- Current Pink Sheet PDF: `https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Pink-Sheet-<Month>-<Year>.pdf`
- ZIP archive of charts and data: `https://openknowledge.worldbank.org/bitstreams/76ad7738-f039-45cc-971a-2d5c6cf3a356/download`

The URL stem (the `74e8be41...0050012026` slug) rolls forward annually; the previous-year stem was `18675f1d...0050012025`. Agents fetching the file by hard-coded URL should also try the landing page (`https://www.worldbank.org/en/research/commodity-markets`) and parse the current download links if the stem 404s.

**Release cadence:** monthly, first Wednesday of the month, covering the prior calendar month. June 2026 release dated 2026-06-02; next release 2026-07-02.

**Workbook shape:** the Monthly file has multiple sheets (Monthly Prices, Monthly Indices, sometimes a Description sheet). Read with `pandas.read_excel(..., sheet_name='Monthly Prices', skiprows=4)` (header rows occupy the first 4-5 rows: human label, World Bank code, unit, units2). Date column is the first column.

**License attribution:** CC-BY-4.0 with the World Bank's attribution string: "The World Bank: Commodity Markets Outlook: Pink Sheet Data". Some underlying series cite third-party providers (Platts, Argus) in the methodology notes; redistribution of the World Bank's printed series is permitted, but heavy-volume redistribution of raw vendor prices may need to be checked against the third party's terms.

## MCP / connector notes

No MCP exists. The Pink Sheet is intentionally out of scope for both the official `worldbank/data360-mcp` (which targets the Data360 indicators platform) and the community World Bank MCPs (which wrap the /v2 Indicators API). A purpose-built connector would expose a small surface: `list_commodities()` (returns the stable Pink Sheet codes and human labels), `get_series(commodity, frequency='monthly', start, end)` (returns the price series with unit metadata), `latest_print()` (returns the most recent month's prices for every series), and `download_pdf(date)` (returns the dated Pink Sheet PDF for citation). The whole MCP is a thin wrapper over `pandas.read_excel` on a single cached Excel file per month, which is why it ranks as low-value: an agent that already pulls the workbook once per release has covered every realistic query.

## Review notes

- Potential new join key for review: `WB_COMMODITY_CODE`. Entity type: `commodity`. Pattern: free-form uppercase identifier from the Pink Sheet header row (`CRUDE_BRENT`, `NGAS_US`, `iNATGAS` for index series with lowercase `i` prefix, `GOLD`, `COPPER`). Other datasets that would use it: FRED (carries near-equivalent codes prefixed `P` for Pink Sheet series), IMF Primary Commodity Prices System (overlapping commodity set with its own codes), UN Comtrade (commodity-classified trade flows). Worth registering if a second commodity-benchmark source lands in the directory.
- `access_test` uses a HEAD request (`curl -sfI`) against the stable URL stem; verified HTTP 200 with `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` content type on 2026-06-09. The URL stem rolls annually; agents should fall back to parsing the landing page when the hard-coded stem 404s.
- License is CC-BY-4.0 per the World Bank's "Terms of Use for Datasets". Underlying vendor-priced series (Platts, Argus) may carry secondary terms documented in the workbook's methodology notes; this entry's license field reflects the World Bank's umbrella terms.
- Secondary domain is `government-open-data`; primary placement in `finance-markets` reflects the dominant agent use case (commodity benchmark retrieval). Mentioned in Why this source matters.
