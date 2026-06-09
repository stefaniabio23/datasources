---
id: iban-currency-codes
name: IBAN Currency Codes
domain: government-open-data
entry_kind: reference-table
description: HTML lookup table of ISO 4217 currency codes (alphabetic and numeric) keyed by country/territory, republished by iban.com.
homepage_url: https://www.iban.com/currency-codes
docs_url: https://www.iban.com/currency-codes
type:
  - web-ui
  - scraper-required
auth_required: none
cost: free
license: iban-com-terms
bulk_available: false
frequency: irregular
lag: "table dated 2026-01-09 at last verification"
geography: [global]
join_keys:
  - ISO_4217
primary_keys:
  - ISO_4217_ALPHA
  - ISO_4217_NUMERIC
join_key_fields:
  - join_key: ISO_4217
    fields: [code]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Narrow lookup-table use. A connector would scrape the single HTML table once and expose
  lookup_by_alpha, lookup_by_numeric, list_by_country. Most agents are better served by the
  ISO 4217 list from the SIX maintenance agency or a packaged ISO-codes library.
agent_use_cases:
  - currency-code lookup
  - mapping country to local currency
  - numeric-to-alpha ISO 4217 translation
  - reference-table seeding for FX pipelines
access_test:
  command: "curl -sf 'https://www.iban.com/currency-codes' | grep -c 'USD'"
  expected_status: 200
  expected_fields: [country, currency, code, number]
last_verified: 2026-06-09
build_priority: low
notes: "Data is the ISO 4217 standard; iban.com republishes with database-rights claim. For redistribution, source from the SIX maintenance agency XML feed instead."
---

# IBAN Currency Codes

## Why this source matters

A single HTML table on iban.com listing every country/territory with its local currency, the ISO 4217 alphabetic code (USD, EUR, GBP), and the ISO 4217 numeric code (840, 978, 826). Useful as a quick lookup or seed table when an agent needs to translate between country names and currency codes without pulling the full ISO 4217 list from the SIX maintenance agency. iban.com is a commercial banking-data vendor (IBAN/BIC validation, sort code lookup, Bank Suite APIs) and republishes the ISO 4217 list as a free reference page. The underlying data is the ISO standard, not iban.com's own; iban.com asserts database rights over the compilation.

## Agent use cases

- currency-code lookup
- mapping country to local currency
- numeric-to-alpha ISO 4217 translation
- reference-table seeding for FX pipelines

## Join strategy

Exposes `ISO_4217` (three-letter alphabetic code). The table prints country names, not ISO_2 codes, so the country column is not a join key; an agent that needs a country-code join must map "United States" to `US` / `USA` externally. Pair with any source that emits currency codes: FRED, Alpha Vantage, World Bank, Polygon, Nasdaq Data Link, Wise/Revolut FX feeds. The source-internal `ISO_4217_NUMERIC` (840, 978) is recorded in `primary_keys`; the registry covers only the alphabetic form, so numeric-to-alpha translation has to happen at parse time.

The country column is plain English country names, not ISO codes. If the use case is a clean `ISO_3`/`ISO_2` join, prefer the SIX ISO 4217 XML feed or `pycountry` instead, both of which expose ISO codes natively.

## Access notes

No API for the currency-codes table. The page is server-rendered HTML; a one-shot `curl` returns the full table, no JS execution required. Scrape with BeautifulSoup or a simple regex over the `<tr>` rows.

iban.com's terms restrict redistribution of "Licensed Material" (the BIC/IBAN/bank-directory data). The ISO 4217 list itself is public-standard reference data and the terms language around redistribution targets the commercial banking feeds; treat the currency-codes page as a convenience republish rather than a redistribution-licensed feed. For any production pipeline shipping the list onward, source from the ISO 4217 maintenance agency (SIX, currency-iso.org) which publishes an authoritative XML list.

Rate limit: site-wide 15 req/sec per IP applies. A single scrape is well inside that.

## MCP / connector notes

No MCP, low value. The table is ~180 rows and rarely changes; a connector adds little over a one-time scrape into a static CSV. If built, expose `lookup_by_alpha(code)`, `lookup_by_numeric(num)`, `lookup_by_country(name)`. The MCP should abstract over (a) the page format changing, (b) preference for ISO authoritative source vs iban republish.

## Review notes

- Potential new join key for review: `ISO_4217_NUMERIC`
  - Entity type: currency (numeric form of ISO 4217)
  - Pattern: `^[0-9]{3}$`
  - Other datasets that would use it: ISO 4217 XML feed (SIX), SWIFT message standards, ECB reference rates (some payloads use numeric), bank ledger systems
  - Currently captured only in `primary_keys`; promote to canonical join key if a second source in the directory exposes it.
- License field uses `iban-com-terms` (kebab-case short name); add to the known-cases list in SCHEMA.md if accepted, or remap to a more generic vendor-terms tag.
- Country column is free-text English names, not ISO codes. `ISO_2` is not exposed by the source and was dropped from `join_keys`; an agent needing a country-code join must apply a name-to-code mapping step (`pycountry`, ISO 3166 lookup) externally.
