---
id: ici-fund-flows
name: ICI Fund Flows
domain: finance-markets
entry_kind: time-series
description: Investment Company Institute weekly and monthly estimates of US mutual fund and ETF flows, money market fund assets, and related fund-industry statistics.
homepage_url: https://www.ici.org/research/statistics
docs_url: https://www.ici.org/research/stats/flows
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: ICI-Terms-of-Use
rate_limit: "unknown; static XLS files, no published limit"
bulk_available: true
frequency: "weekly (long-term flows, ETF flows, money market assets); monthly and quarterly for other series"
lag: "flows for a week ended are released the following Wednesday (~7 days)"
geography: [USA]
join_keys:
  - DATE
join_key_fields:
  - join_key: DATE
    fields: [Date]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - track weekly fund flow trends
  - money market fund asset monitoring
  - equity-vs-bond risk-appetite signal
  - retail fund demand proxy
access_test:
  command: "curl -sfI 'https://www.ici.org/flows_data_2026.xls'"
  expected_status: 200
last_verified: 2026-07-02
structure: time-series
pit_reconstructable: false
revisions_possible: true
release_lag_days: 7
build_priority: low
---

# ICI Fund Flows

## Why this source matters

The Investment Company Institute (ICI) is the US trade association for regulated funds (mutual funds, ETFs, closed-end funds, UITs), and its statistics division publishes the most widely cited estimates of US fund flows and industry assets. Its members hold the large majority of US open-end fund assets, so its weekly estimated long-term mutual fund flows (derived from data covering ~98% of industry assets), weekly combined ETF and long-term flows, and weekly money market fund assets are treated as the industry benchmark for retail and institutional fund demand. Flows are broken down by asset class and fund type (equity domestic/world, hybrid, bond taxable/municipal, plus large/mid/small cap and developed/emerging market sub-splits). The broader statistics hub also carries monthly Trends in Mutual Fund Investing, monthly ETF data, quarterly retirement market data (IRA/401k), and the quarterly worldwide open-end fund market, making this a multi-dataset provider even though every series is time-series shaped. Data is distributed as downloadable XLS summary files rather than an API.

## Agent use cases

- track weekly fund flow trends
- money market fund asset monitoring
- equity-vs-bond risk-appetite signal
- retail fund demand proxy

## Join strategy

The only canonical join key this source exposes is `DATE` (week-ended or month-end, ISO 8601). Every series is a time series keyed on that date column, so ICI flows join cleanly to macro and market series that also expose `DATE` (FRED macro series, CBOE VIX, equity index levels). The second axis, asset class / fund type (equity, hybrid, bond, taxable vs municipal, domestic vs world, money market), is a categorical dimension inside each file and is not a canonical join key in the registry; it is flagged below as a new-key candidate. There are no source-minted entity identifiers in the public summary files (the data is aggregated by fund category, not per-fund), so `primary_keys` is empty. Money market fund asset totals also feed the Federal Reserve Financial Accounts (Z.1), which surface via FRED (e.g. `BOGZ1FA634090073Q`), giving an indirect bridge to `finance-markets` macro sources.

## Access notes

No auth and no API. Fetch the current-year summary workbooks directly:

- Long-term mutual fund flows: `https://www.ici.org/flows_data_2026.xls`
- Money market fund assets: `https://www.ici.org/mm_summary_data_2026.xls`

Both return HTTP 200 as `application/vnd.ms-excel`. The public files carry recent history (weekly flows back several years; money market assets last ~20 weeks plus historical). Full member-level detail requires ICI membership or a nonmember statistical subscription. Estimates are revised as more complete data arrives, so values are `revisions_possible: true` and the source is not point-in-time reconstructable. The HTML release pages under `/research/stats/flows` and `/research/stats/mmf` render the same numbers for quick reads. A licensed, cleaned mirror of several ICI series is also sold through Nasdaq Data Link (publisher ICI, e.g. database ICI2); prefer the free XLS for the public summary series.

## MCP / connector notes

No MCP exists. Narrow analyst audience and only a handful of XLS files, so low build priority. A connector would fetch the year-stamped XLS files, parse the multi-header Excel layout (category rows, week-ended columns, dollar amounts in millions plus percent-of-assets), normalise to long format (date, asset_class, fund_type, flow_usd_millions), and expose `get_weekly_flows`, `get_money_market_assets`, and `get_historical_flows`. The tricky part is the Excel layout (merged header cells, footnote rows, year-rollover filename change each January) rather than transport.

## Review notes

- **License short name not yet canonical.** ICI requires a permission request form to reproduce or redistribute its materials; there is no SPDX license. Used placeholder short name `ICI-Terms-of-Use` for the `license` field. Candidate for the canonical license short-name list in SCHEMA.md; Stephanie to confirm wording. Redistribution/commercial use likely needs ICI permission, so treat as restricted despite `cost: free`.
- **Potential new join key for review:** `FUND_ASSET_CLASS`
  - Entity type: fund_category (equity / hybrid / bond / money-market, with domestic-vs-world and taxable-vs-municipal sub-splits)
  - Pattern: controlled vocabulary, not an identifier regex
  - Other datasets that would use it: any fund/ETF flow or holdings source that segments by asset class (SEC N-CEN/N-PORT-derived aggregates, Nasdaq Data Link ICI mirror). No standard code system exists across sources, so this may be better modeled as a shared enum than a join key.
- **Homepage URL note:** the supplied target `https://www.ici.org/research/stats` returns 404 (redirects to a dead node). Used the canonical statistics landing `https://www.ici.org/research/statistics` (reached via `/statistics`) as `homepage_url` and the flows release page as `docs_url`.
- **access_test** was constructed and executed: `curl -sfI` on the flows XLS returned HTTP 200 (`application/vnd.ms-excel`). No JSON fields to assert (binary XLS), so `expected_fields` omitted.
