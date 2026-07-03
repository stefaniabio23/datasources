---
id: simfin
name: SimFin
domain: finance-markets
entry_kind: panel
description: Standardised company fundamentals (income statement, balance sheet, cash flow), daily share prices, and derived ratios for ~5,000 mostly-US public companies via REST API and bulk CSV.
homepage_url: https://www.simfin.com/
docs_url: https://simfin.readthedocs.io/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: freemium
license: proprietary
rate_limit: "credit-based; free tier ~500 high-speed credits/month, paid tiers 5K-30K"
bulk_available: true
frequency: daily
lag: "free-tier data delayed ~12 months; paid (SimFin+) near-current after filing"
geography: [USA, global]
join_keys:
  - TICKER
  - DATE
primary_keys:
  - SIMFIN_ID
join_key_fields:
  - join_key: TICKER
    fields: [ticker, Ticker]
  - join_key: DATE
    fields: [Report Date, Publish Date, Date]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "https://mcp.mcpbundles.com/bundle/simfin"
mcp_notes: >
  Third-party hosted MCP via MCPBundles (not SimFin-official). ~4 tools:
  get_companies, get_company_data, get_filings, get_financial_statements.
  Auth handled by the bundle host; wraps the SimFin API key.
agent_use_cases:
  - fundamental data retrieval
  - financial-ratio screening
  - cross-company financial comparison
  - backtesting on point-in-time fundamentals
  - ticker-to-financials lookup
access_test:
  command: "curl -sf -H \"Authorization: ${SIMFIN_API_KEY}\" 'https://backend.simfin.com/api/v3/companies/list?ticker=AAPL'"
  expected_status: 200
  expected_fields: [ticker, name, id]
last_verified: 2026-07-02
build_priority: medium
structure: panel
pit_reconstructable: false
revisions_possible: true
notes: "access_test not executed; requires ${SIMFIN_API_KEY}. Unauthenticated call to the v3 endpoint returns 401, confirming the route exists."
---

# SimFin

## Why this source matters

SimFin (SimFin Analytics GmbH, Halle, Germany) is a low-cost financial-data platform offering standardised company fundamentals, income statement, balance sheet, and cash-flow line items, plus daily share prices and 7,000+ derived daily ratios, going back roughly 20 years. Coverage is ~5,000 companies, heavily US-weighted with expanding European and Asian coverage. The pitch for an agent is standardisation and price: it re-maps heterogeneous filings into a consistent schema and exposes it through a clean REST API, a Python package, an Excel plugin, and ZIP-compressed bulk CSV, with a genuinely usable free tier (12-month-delayed data). It sits primarily in finance-markets; because the underlying data derives from SEC and other regulatory filings, it overlaps corporate-registry for company-fundamentals use.

## Agent use cases

- fundamental data retrieval
- financial-ratio screening
- cross-company financial comparison
- backtesting on point-in-time fundamentals
- ticker-to-financials lookup

## Join strategy

SimFin exposes `TICKER` as the primary cross-source join key for public equities, and `DATE` (report date / publish date / price date, ISO 8601) as the temporal axis, so a SimFin pull panel-joins naturally against any ticker-and-date financial or price source. Pair with SEC EDGAR (CIK-keyed filings) for primary-source verification, and with a ticker-to-CIK or ticker-to-ISIN crosswalk when joining into identifier-keyed universes. SimFin's own `SIMFIN_ID` (integer, `primary_keys`) uniquely identifies a company inside SimFin and is required as a parameter for most API calls; it is source-internal, not a cross-source key. SimFin's `IndustryId` is likewise internal (not a canonical SIC/NAICS code). See Review notes on possible ISIN exposure.

## Access notes

Register free at simfin.com for an API key; the key authenticates both the REST API and the Python package. Start with the v3 backend, e.g. `https://backend.simfin.com/api/v3/companies/list?ticker=AAPL` with an `Authorization` header carrying the key (an unauthenticated call returns 401). Rate limiting is credit-based, not requests-per-second: the free tier gets ~500 high-speed credits/month, paid SimFin+ tiers 5,000-30,000. For anything beyond a few companies, prefer the bulk download (single CSV per dataset, ZIP-compressed) over paginating the API. Freshness caveat: free-tier data is delayed ~12 months; only paid SimFin+ subscriptions get near-current fundamentals. Redistribution is restricted, SimFin's terms require deleting downloaded data on subscription cancellation, so treat bulk pulls as license-bound, not open data.

## MCP / connector notes

A third-party hosted MCP exists via MCPBundles (`https://mcp.mcpbundles.com/bundle/simfin`), exposing roughly four tools: get_companies, get_company_data, get_filings, get_financial_statements. It is not SimFin-official and is a managed hosted endpoint rather than an installable package; it wraps the user's SimFin API key. A first-party or self-hostable connector would ideally surface: company search (ticker/name to SIMFIN_ID), financial-statement fetch (statement type + period), price history, and ratio/derived-metric fetch, and must abstract over the credit budget and the free-vs-SimFin+ data-delay boundary so agents do not silently retrieve 12-month-stale data.

## Review notes

License: SimFin data is proprietary with no SPDX identifier; `license: proprietary` is used as a placeholder short name. If the registry standardises on a canonical short name for restricted commercial-data terms (redistribution-prohibited, delete-on-cancel), this entry should adopt it. Flagging for human confirmation.

Possible additional canonical join key: SimFin's Companies dataset historically included an `ISIN` column (a registry key, `ISIN`) and, for US names, may map to `CIK`. I could not confirm current presence from the public docs, so I did not add `ISIN`/`CIK` to `join_keys`. If confirmed in the live companies dataset, both should be added (they already exist in the registry, no new key needed).
