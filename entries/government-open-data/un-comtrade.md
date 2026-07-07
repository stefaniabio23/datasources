---
id: un-comtrade
name: UN Comtrade
domain: government-open-data
entry_kind: panel
description: Official United Nations repository of annual and monthly international merchandise (and services) trade statistics, bilateral by reporter, partner, and commodity code.
homepage_url: https://comtradeplus.un.org/
docs_url: https://comtradedeveloper.un.org/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free-with-registration
license: UN-Comtrade-Terms
rate_limit: "no token: 1 req/sec, 100 req/hr per IP; free token: 1 req/sec, 10K req/hr, 500 calls/day, up to 100K records/call"
bulk_available: true
frequency: monthly
lag: "months; countries report with variable delay, most within 3-12 months of the reference period"
geography: [global]
structure: panel
pit_reconstructable: false
revisions_possible: true
join_keys:
  - ISO_3
  - DATE
  - HS_CODE
primary_keys:
  - COMTRADE_REPORTER_M49
  - COMTRADE_PARTNER_M49
  - COMTRADE_CMD_CODE
join_key_fields:
  - join_key: ISO_3
    fields: [reporterISO, partnerISO, partner2ISO]
  - join_key: DATE
    fields: [period, refYear, refPeriodId]
mcp_status: mcp-needed-high-value
agent_use_cases:
  - bilateral trade flow lookup
  - commodity-level import/export analysis
  - supply-chain dependency mapping
  - trade balance computation
  - country trade-partner ranking
access_test:
  command: "curl -sf 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=2022&partnerCode=0&cmdCode=TOTAL&flowCode=X'"
  expected_status: 200
  expected_fields: [reporterCode, partnerCode, cmdCode, period, flowCode, primaryValue]
last_verified: 2026-07-03
build_priority: medium
---

# UN Comtrade

## Why this source matters

UN Comtrade is the United Nations Statistics Division's (UNSD) canonical repository of official international trade statistics. It holds bilateral merchandise-trade records (imports and exports) reported by ~200 countries and territories, disaggregated by trading partner and by commodity code, back to 1962, plus a growing services-trade dataset. Each record is a value (and often quantity/weight) for a reporter-partner-commodity-flow-period tuple. It is the authoritative free source for questions about who trades what with whom, and the backbone of derived products like the World Bank's WITS and the Atlas of Economic Complexity. Because trade values are aggregated from national customs authorities, it doubles as a macro-economic and a supply-chain / industrial-dependency dataset.

## Agent use cases

- bilateral trade flow lookup
- commodity-level import/export analysis
- supply-chain dependency mapping
- trade balance computation
- country trade-partner ranking

## Join strategy

Comtrade natively keys entities on UN M49 numeric country codes (`reporterCode`, `partnerCode`, `partner2Code`) and on classification-specific commodity codes (`cmdCode`). For cross-source joining it also emits ISO 3166-1 alpha-3 country codes in `reporterISO`, `partnerISO`, and `partner2ISO`, mapped here to canonical `ISO_3`. The `period` / `refYear` fields carry the reference year (or year-month for monthly data), mapped to canonical `DATE`.

The commodity code (`cmdCode`) is the most valuable cross-source key Comtrade exposes, it carries Harmonized System codes (HS, at 2/4/6-digit levels via classifications H0-H6) as well as SITC codes. There is no canonical HS key in the registry yet; see `## Review notes`.

Pair with World Bank WDI or IMF for macro context, with Open Corporates / trade-lane datasets for firm-level enrichment, and with any HS-coded product dataset once an `HS_CODE` join key exists.

## Access notes

Hit the free preview endpoint first, no key required: `https://comtradeapi.un.org/public/v1/preview/{typeCode}/{freqCode}/{clCode}` (e.g. `.../preview/C/A/HS?...`). Preview responses are capped at 500 records, enough to validate query shape. For full extracts, register on the Developer Portal (`https://comtradedeveloper.un.org/`), subscribe to the free `comtrade - v1` product for a subscription key, and call `https://comtradeapi.un.org/data/v1/get/{typeCode}/{freqCode}/{clCode}` with the key in the `Ocp-Apim-Subscription-Key` header. Query constraints: among `reporterCode`, `partnerCode`, and the period range, only one may use the catch-all `All`; the others are capped at 5 values each. Bulk file downloads are available to authenticated subscribers.

License nuance: UN Comtrade data are copyrighted by the United Nations and governed by a data-use/re-dissemination policy administered by UNSD. Non-commercial internal use is permitted; bulk re-dissemination in any form generally requires written permission from UNSD (contact comtrade@un.org). This is materially more restrictive than a Creative Commons license, treat redistribution as gated.

## MCP / connector notes

No MCP server exists. Mature client libraries do: the official `comtradeapicall` Python package (github.com/uncomtrade/comtradeapicall) and the rOpenSci `comtradr` R package, both wrap the v1 API and include M49-to-ISO3 helpers. A connector is high-value because trade data is broadly requested across macro, supply-chain, and industrial-analysis agents. Suggested MCP surface: `get_trade` (reporter/partner/commodity/flow/period), `preview_trade` (no-key 500-row sanity check), `list_reporters`, `list_commodities` (classification lookup), `convert_iso3_to_m49`. The connector must abstract over the M49-vs-ISO3 country-code duality, the classification-code zoo (H0-H6, SITC S1-S4, BEC), the one-`All`-dimension query rule, and the 500-record preview vs keyed full-data split.

## Review notes

Potential new join key for review: `HS_CODE`
  Entity type: traded_commodity
  Pattern: `^[0-9]{2,6}$` (2-, 4-, or 6-digit Harmonized System code; `TOTAL` sentinel for all-commodity aggregate)
  Other datasets that would use it: any product-level trade or tariff source (World Bank WITS, USA Trade Online, EU Comext, tariff schedules, product-classification crosswalks). This is the join-key hint flagged in the task and the single highest-value cross-source key Comtrade exposes.

New license short name flagged: `UN-Comtrade-Terms`. No SPDX code exists for the UNSD data-use policy. Used as the canonical short name here; confirm naming before merge. Nuance recorded in `## Access notes` (restricted re-dissemination, not open).

M49 numeric country codes (`reporterCode`, `partnerCode`) are treated as source-native primary keys, not registry join keys, since the source also exposes ISO_3. If a canonical `UN_M49` key is ever wanted for sources that expose only M49, it would be a separate PR.
