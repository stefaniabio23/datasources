---
id: nppes-npi
name: NPPES NPI Registry
domain: healthcare-claims
entry_kind: registry
description: Public registry of every US healthcare provider's National Provider Identifier (NPI), with taxonomy, practice addresses, and other identifiers.
homepage_url: https://npiregistry.cms.hhs.gov/
docs_url: https://npiregistry.cms.hhs.gov/api-page
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "no documented hard cap; 200 results/request max, skip paginates to 1000 (1200-record ceiling per query)"
bulk_available: true
frequency: "weekly (bulk dissemination); full-replacement file monthly, incremental weekly"
lag: "providers self-report changes; new NPIs and updates appear within days"
geography: [USA]
join_keys:
  - NPI
  - ZCTA
  - US_STATE_CODE
primary_keys:
  - NPI
join_key_fields:
  - join_key: NPI
    fields: [number]
  - join_key: ZCTA
    fields: [addresses.postal_code]
  - join_key: US_STATE_CODE
    fields: [addresses.state, taxonomies.state]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/eliotk/npi-registry-mcp-server"
  - "mcp-healthcare (npm)"
mcp_command:
  - "npx -y npi-registry-mcp-server"
mcp_notes: >
  Community MCPs wrap the public Read API (search by name, org, NPI, location).
  Suggested surface: search_providers, get_provider_by_npi, filter_by_taxonomy,
  filter_by_state. No auth needed; MCP should paginate via skip and cap result pulls.
agent_use_cases:
  - resolve provider name to NPI
  - look up provider taxonomy / specialty
  - geocode providers by ZIP and state
  - enrich claims rows with provider metadata
  - build provider directories
access_test:
  command: "curl -sf 'https://npiregistry.cms.hhs.gov/api/?version=2.1&number=1245319599'"
  expected_status: 200
  expected_fields: [result_count, results, number, enumeration_type, taxonomies, addresses]
last_verified: 2026-07-02
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: true
build_priority: medium
---

# NPPES NPI Registry

## Why this source matters

The National Plan and Provider Enumeration System (NPPES), run by the Centers for Medicare & Medicaid Services (CMS), assigns and publishes the National Provider Identifier (NPI): a 10-digit number carried by every US healthcare provider (type-1 individuals and type-2 organizations). The registry is the canonical crosswalk between a provider's name, NPI, NUCC taxonomy (specialty), and practice/mailing addresses. It is the join backbone for almost anything provider-level in US healthcare: Medicare/Medicaid claims, Part D prescribing, Open Payments, quality reporting. Data is FOIA-disclosable and released into the public domain via both a no-auth REST API and a monthly bulk dissemination file.

## Agent use cases

- resolve provider name to NPI
- look up provider taxonomy / specialty
- geocode providers by ZIP and state
- enrich claims rows with provider metadata
- build provider directories

## Join strategy

The registry mints `NPI` (canonical, in the `number` field) as both its primary key and a cross-source join key: CMS claims, Open Payments, and NPPES-derived provider directories all key on it. Practice/mailing `addresses` expose `US_STATE_CODE` (`addresses.state`) and a ZIP (`addresses.postal_code`) that maps to `ZCTA`, though the field is often returned as ZIP+4 (nine digits, e.g. `237082111`); truncate to the 5-digit prefix before joining to Census `ZCTA` tables, and note the ZIP-to-ZCTA mapping is approximate (ZIPs are delivery routes, ZCTAs are Census tabulation areas).

The high-value identifier this registry carries but the canonical registry does not is the NUCC **provider taxonomy code** (`taxonomies[].code`, e.g. `207Q00000X` = Family Medicine). It is flagged below as a new-key candidate. Pair NPPES with CMS claims/prescribing datasets (join on `NPI`) and with Census demographics (join on `ZCTA`) for geographic provider analysis.

## Access notes

Hit the Read API first: `https://npiregistry.cms.hhs.gov/api/?version=2.1&number=<NPI>` for a single record, or swap in name/taxonomy/location parameters for search. The `version=2.1` parameter is required or the request 400s. No auth, no API key. Per-request `limit` maxes at 200 and `skip` paginates to 1000, so a single query surfaces at most 1200 records; for anything larger use the bulk file. The monthly full-replacement + weekly incremental dissemination CSVs live at `download.cms.gov/nppes/NPI_Files.html` (roughly 9 GB unzipped, ~8M+ providers) and are the right tool for whole-registry pulls or offline joins. The bulk file's field layout differs from the JSON API (flat columns vs nested `taxonomies`/`addresses` arrays); reconcile before merging the two.

## MCP / connector notes

Community MCP servers exist: `eliotk/npi-registry-mcp-server` (search by provider name, organization, NPI, and location) and `mcp-healthcare` (bundles NPI with ICD-10, NDC, DEA tools). Both wrap the public no-auth Read API. Maturity is community, not official; gaps include no bulk-file ingestion and thin taxonomy-code filtering. A connector should expose `search_providers`, `get_provider_by_npi`, `filter_by_taxonomy`, `filter_by_state`, paginate transparently over `skip`, and normalize the ZIP+4 postal_code to a 5-digit key.

## Review notes

Potential new join key for review: `NUCC_TAXONOMY_CODE`
  Entity type: provider_taxonomy (healthcare provider specialty/type)
  Pattern: `^[0-9]{3}[A-Z0-9]{6}X$` (10-char NUCC Health Care Provider Taxonomy code, e.g. `207Q00000X`, `208D00000X`)
  Other datasets that would use it: CMS Medicare provider/utilization data, Medicaid provider files, health-plan network directories, NUCC taxonomy reference table.

`ZCTA` is mapped here to `addresses.postal_code`, which the API returns as ZIP or ZIP+4, not a true Census ZCTA. The join is approximate (5-digit prefix). Flagging in case a stricter `ZIP_CODE` canonical key is preferred over reusing `ZCTA` for raw provider ZIPs.
