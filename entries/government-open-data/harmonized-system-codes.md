---
id: harmonized-system-codes
name: Harmonized System Codes
domain: government-open-data
entry_kind: reference-table
description: Hierarchical lookup of the World Customs Organization Harmonized System (HS) classification, mirrored as public-domain CSV on DataHub from the UN Comtrade nomenclature endpoint.
homepage_url: https://datahub.io/core/harmonized-system
docs_url: https://github.com/datasets/harmonized-system
type:
  - bulk-download
auth_required: none
cost: free
license: ODC-PDDL-1.0
rate_limit: "none documented; static CSV behind Cloudflare R2"
bulk_available: true
frequency: irregular
lag: "tracks WCO nomenclature revisions (every 5 years); DataHub snapshot is version 2022.0"
geography: [global]
join_keys: []
primary_keys:
  - HS_CODE
  - HS_SECTION
join_key_fields: []
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Static reference table; no server needed. A connector would only be useful as
  part of a broader trade-data MCP (UN Comtrade, Census USA Trade) that maps
  HS codes to human descriptions and walks the parent/child hierarchy.
agent_use_cases:
  - decode HS codes from customs filings
  - walk product taxonomy (section -> 2-digit -> 4-digit -> 6-digit)
  - join trade-volume datasets to human-readable product names
  - normalise commodity descriptions across trade sources
access_test:
  command: "curl -sfL 'https://datahub.io/core/harmonized-system/r/harmonized-system.csv' | head -5"
  expected_status: 200
  expected_fields: [section, hscode, description, parent, level]
last_verified: 2026-06-09
build_priority: low
notes: >
  Two CSV resources: sections.csv (21 sections, top-level groupings) and
  harmonized-system.csv (~5k rows covering 2-, 4-, and 6-digit HS codes).
  Snapshot is HS-2022 nomenclature.
---

# Harmonized System Codes

## Why this source matters

The Harmonized System is the WCO-administered classification used by 200+ customs authorities to code traded goods at 2-, 4-, and 6-digit levels. It underpins every import/export filing, tariff schedule, and trade-statistics table on the planet (UN Comtrade, USITC DataWeb, Eurostat Comext, US Census USA Trade). The DataHub mirror packages the 2022 nomenclature as a public-domain CSV with a clean parent/child column, so an agent can decode an HS code, walk up to its section, or join trade-volume tables to human-readable product names without scraping the WCO PDF or registering for UN Comtrade.

## Agent use cases

- decode HS codes from customs filings
- walk product taxonomy (section to 2-digit to 4-digit to 6-digit)
- join trade-volume datasets to human-readable product names
- normalise commodity descriptions across trade sources

## Join strategy

This is a reference table; it has no canonical join keys from the registry. Its value is the source-internal `HS_CODE` (and the `HS_SECTION` Roman numeral grouping), which is the primary identifier other trade datasets reference. Pair with: UN Comtrade (trade flows by HS code), US Census USA Trade Online (US imports/exports by HS), Eurostat Comext (EU intra/extra trade by HS), USITC HTS (US tariff schedule). When joining to those sources, agents must match on bare HS code strings and may need to truncate (their dataset's 10-digit HTS to this dataset's 6-digit HS) since national customs authorities extend HS with extra digits.

`HS_CODE` is a strong candidate for the canonical join-key registry. See Review notes.

## Access notes

Single bulk download. No API, no auth, no rate limit. The canonical URL `https://datahub.io/core/harmonized-system/r/harmonized-system.csv` returns a 301 to `/_r/-/data/harmonized-system.csv`, which 302s to `r2.datahub.io` (Cloudflare R2). Use `curl -sfL` to follow redirects; final response is `text/csv`, ~850 kB.

The sister file `https://datahub.io/core/harmonized-system/r/sections.csv` (~2 kB) lists the 21 top-level sections (I through XXI) with their human-readable names.

Freshness check: the DataHub `datapackage.json` carries a `version` field (currently `2022.0`); compare against WCO's most recent nomenclature edition (HS-2027 is the next scheduled revision). The upstream GitHub repo at `github.com/datasets/harmonized-system` is the place to watch for snapshot updates.

## MCP / connector notes

No MCP and no real need for one in isolation: an agent that needs HS code lookups can load the 850 kB CSV once and treat it as an in-memory lookup. The right MCP surface is a broader trade-data connector that combines this lookup table with UN Comtrade flow queries and USITC HTS tariff queries, exposing `lookup_hs_code`, `walk_hs_hierarchy`, and `get_trade_flows_for_hs`. Building an MCP just for the static lookup is low-value.

## Review notes

Potential new join key for review: `HS_CODE`
  Entity type: traded_product_classification
  Pattern: `^[0-9]{2,6}$` (2-, 4-, or 6-digit; national customs authorities extend with extra digits)
  Other datasets that would use it: UN Comtrade, US Census USA Trade, Eurostat Comext, USITC HTS, WITS (World Integrated Trade Solution), customs declarations data in any country

HS-2022 nomenclature is the snapshot here; if Stephanie wants HS-2017 or earlier (relevant for joining to historical trade flows that were filed under prior revisions), DataHub does not publish the older snapshots and the agent would need WCO's PDFs or a third-party mirror.
