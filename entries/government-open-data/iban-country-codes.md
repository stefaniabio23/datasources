---
id: iban-country-codes
name: IBAN Country Codes
domain: government-open-data
entry_kind: reference-table
description: HTML lookup table of ISO 3166-1 country codes (alpha-2, alpha-3, numeric) keyed by country name, republished by iban.com.
homepage_url: https://www.iban.com/country-codes
docs_url: https://www.iban.com/country-codes
type:
  - web-ui
  - scraper-required
auth_required: none
cost: free
license: iban-com-terms
bulk_available: false
frequency: irregular
rate_limit: "site-wide 15 req/sec per IP; a single table scrape is well inside that"
lag: "static reference; updated when the ISO 3166-1 country-code registry changes"
geography: [global]
join_keys:
  - ISO_2
  - ISO_3
primary_keys:
  - ISO_3166_NUMERIC
join_key_fields:
  - join_key: ISO_2
    fields: [alpha-2-code]
  - join_key: ISO_3
    fields: [alpha-3-code]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Narrow lookup-table use. A connector would scrape the single HTML table once and expose
  lookup_by_alpha2, lookup_by_alpha3, lookup_by_numeric, lookup_by_country. Most agents are
  better served by the ISO 3166 list from the ISO Online Browsing Platform or a packaged
  ISO-codes library (pycountry, iso-3166).
agent_use_cases:
  - country-code lookup
  - alpha-2 to alpha-3 translation
  - numeric-to-alpha ISO 3166 translation
  - reference-table seeding for country joins
access_test:
  command: "curl -sf 'https://www.iban.com/country-codes' | grep -c 'USA'"
  expected_status: 200
  expected_fields: [country, alpha-2-code, alpha-3-code, numeric]
last_verified: 2026-06-09
build_priority: low
notes: "Data is the ISO 3166-1 standard; iban.com republishes with database-rights claim. For redistribution, source from the ISO Online Browsing Platform or pycountry instead."
---

# IBAN Country Codes

## Why this source matters

A single HTML table on iban.com listing every country with its ISO 3166-1 alpha-2 code (US, GB, FR), alpha-3 code (USA, GBR, FRA), and numeric code (840, 826, 250). Useful as a quick lookup or seed table when an agent needs to translate between country names and ISO country codes without pulling the full ISO 3166-1 list from the ISO Online Browsing Platform (which sits behind a registration wall for full XML access). iban.com is a commercial banking-data vendor (IBAN/BIC validation, sort code lookup, Bank Suite APIs) and republishes the ISO 3166-1 list as a free reference page. The underlying data is the ISO standard, not iban.com's own; iban.com asserts database rights over the compilation.

## Agent use cases

- country-code lookup
- alpha-2 to alpha-3 translation
- numeric-to-alpha ISO 3166 translation
- reference-table seeding for country joins

## Join strategy

Exposes `ISO_2` (two-letter alpha-2 code) and `ISO_3` (three-letter alpha-3 code) for every country. These are the two canonical country join keys in the registry; pair with any source that emits a country code in either form (OpenAlex affiliations, World Bank indicators, FRED international series, GDELT actors, WHO surveillance, ECDC, OECD, openFDA country fields). The source-internal numeric form (840, 826, 250) is recorded in `primary_keys` as `ISO_3166_NUMERIC`; the registry covers only the alpha forms, so numeric-to-alpha translation has to happen at parse time.

The country column is plain English country names, not a registry key. Name-to-code lookup is straightforward against this table for canonical ISO names; for non-canonical aliases ("Burma" vs "Myanmar", "Czech Republic" vs "Czechia") prefer `pycountry` which carries the alias index.

## Access notes

No API for the country-codes table. The page is server-rendered HTML; a one-shot `curl` returns the full table, no JS execution required. Scrape with BeautifulSoup or a simple regex over the `<tr>` rows.

iban.com's terms restrict redistribution of "Licensed Material" (the BIC/IBAN/bank-directory data). The ISO 3166-1 list itself is public-standard reference data and the terms language around redistribution targets the commercial banking feeds; treat the country-codes page as a convenience republish rather than a redistribution-licensed feed. For any production pipeline shipping the list onward, source from the ISO 3166 Maintenance Agency (iso.org/iso-3166-country-codes.html) or use the `pycountry` Python package, both of which carry the authoritative list with full subdivision and historic-code coverage.

Rate limit: site-wide 15 req/sec per IP applies. A single scrape is well inside that.

## MCP / connector notes

No MCP, low value. The table is ~250 rows and rarely changes (a handful of edits per year at most); a connector adds little over a one-time scrape into a static CSV. If built, expose `lookup_by_alpha2(code)`, `lookup_by_alpha3(code)`, `lookup_by_numeric(num)`, `lookup_by_country(name)`. The MCP should abstract over (a) the page format changing, (b) preference for ISO authoritative source vs iban republish, (c) ISO 3166-1 vs deprecated/transitional codes.

## Review notes

- Potential new join key for review: `ISO_3166_NUMERIC`
  - Entity type: country (numeric form of ISO 3166-1)
  - Pattern: `^[0-9]{3}$`
  - Other datasets that would use it: UN Comtrade, IMF DOTS, some WHO surveillance payloads, ISO 3166 XML feed, SWIFT message standards
  - Currently captured only in `primary_keys`; promote to canonical join key if a second source in the directory exposes it.
- License field uses `iban-com-terms` (kebab-case short name), matching the sibling `iban-currency-codes` entry. Add to the known-cases list in SCHEMA.md if the vendor-terms tag stays in use, or remap to a more generic vendor-terms identifier.
- Country column is free-text English names. Most rows match the canonical ISO short name, but a few aliases drift from ISO usage; for production name resolution prefer `pycountry`.
