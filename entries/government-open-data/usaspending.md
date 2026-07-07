---
id: usaspending
name: USAspending.gov
domain: government-open-data
entry_kind: mixed
description: Official U.S. government record of federal spending — contracts, grants, loans, and other awards, plus agency account balances, from FY2008 to present.
homepage_url: https://www.usaspending.gov/
docs_url: https://api.usaspending.gov/docs/endpoints
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "not publicly documented; HTTP 429 returned on excessive use"
bulk_available: true
frequency: daily
lag: "FPDS contract transactions flow ~daily; agency financial (DABS) submissions are monthly/quarterly"
geography: [USA]
structure: event-log
pit_reconstructable: false
revisions_possible: true
join_keys:
  - FIPS
  - US_STATE_CODE
  - ISO_3
primary_keys:
  - USASPENDING_GENERATED_AWARD_ID
  - USASPENDING_INTERNAL_AWARD_ID
  - USASPENDING_RECIPIENT_HASH
  - PIID
  - FAIN
  - URI
join_key_fields:
  - join_key: FIPS
    fields:
      - recipient.location.county_code
      - place_of_performance.county_code
  - join_key: US_STATE_CODE
    fields:
      - recipient.location.state_code
      - place_of_performance.state_code
  - join_key: ISO_3
    fields:
      - recipient.location.country_code
      - place_of_performance.country_code
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/blencorp/capture-mcp-server"
  - "github.com/agilesix/usaspending-mcp-nextjs"
  - "github.com/jsconiers/usaspending-mcp"
mcp_notes: >
  Multiple community MCPs exist (none official). Suggested surface: search_awards,
  get_award, get_recipient, spending_by_agency, spending_by_geography, bulk_download.
  Connector must abstract the POST-body filter grammar and paginate large result sets.
agent_use_cases:
  - federal contractor diligence
  - grant recipient lookup
  - agency spending breakdown
  - award search by NAICS or PSC
  - geographic spending analysis
access_test:
  command: "curl -sf 'https://api.usaspending.gov/api/v2/references/toptier_agencies/'"
  expected_status: 200
  expected_fields: [results, toptier_code, agency_name]
last_verified: 2026-07-07
build_priority: medium
---

# USAspending.gov

## Why this source matters

USAspending.gov is the U.S. Treasury's official public record of federal spending, mandated by the DATA Act. It covers every federal award (contracts, grants, loans, direct payments, insurance) from FY2008 to present, plus agency-level account balances and obligations. Data flows in from FPDS (contracts), SAM.gov/ASP (assistance), and agency financial submissions. For an agent, this is the authoritative source for "who received federal money, from which agency, for what, and where" — federal contractor diligence, grant tracking, and agency budget analysis all resolve here. A secondary `corporate-registry` flavour exists via recipient profiles keyed on UEI, which overlap with SAM.gov and corporate-registry sources.

## Agent use cases

- federal contractor diligence
- grant recipient lookup
- agency spending breakdown
- award search by NAICS or PSC
- geographic spending analysis

## Join strategy

USAspending exposes canonical geographic join keys on both recipient location and place of performance: `US_STATE_CODE` (two-letter state), `FIPS` (three-digit county codes; pair with the state to form the full 5-digit county FIPS), and `ISO_3` (three-letter country codes on the location objects).

The high-value cross-source identifiers this source carries are NOT yet in the canonical registry and are flagged in `## Review notes`: recipient **UEI** (the SAM.gov Unique Entity Identifier, the natural bridge to SAM.gov and corporate registries), **NAICS** and **PSC** codes (industry/product classification of the work), and **CFDA / Assistance Listing** numbers (program identifier for grants). Agency **toptier/subtier codes** are source-internal spending-hierarchy keys.

Source-internal award identifiers live in `primary_keys`: `USASPENDING_GENERATED_AWARD_ID` (the URL-safe id like `CONT_IDV_TMHQ10C0040_2044`), the numeric internal award id, the recipient hash, and the upstream `PIID` (contracts) / `FAIN` and `URI` (assistance) that trace back to FPDS and the assistance systems. Use these for direct USAspending lookups, not cross-source joins, until UEI/NAICS are promoted to canonical keys.

## Access notes

REST API at `https://api.usaspending.gov/api/v2/`, no auth. Simple reference pulls are GET (`/references/toptier_agencies/`, `/awards/<generated_award_id>/`); the powerful search endpoints (`/search/spending_by_award/`, `/search/spending_by_geography/`) are POST with a JSON `filters` body. No published rate limit, but excessive use returns HTTP 429, so throttle. For large analyses use the bulk pipeline: `/api/v2/bulk_download/awards/` produces a zipped CSV, and full database snapshots plus per-award-type archives are linked from the site's Download Center. V1 endpoints are deprecated; use V2 only.

## MCP / connector notes

Several community MCP servers wrap this API (none official): `blencorp/capture-mcp-server` (joins USAspending with SAM.gov and Tango, MIT), `agilesix/usaspending-mcp-nextjs`, and `jsconiers/usaspending-mcp`, plus a FastMCP key-less server covering FY2008-present. A connector should expose `search_awards`, `get_award`, `get_recipient`, `spending_by_agency`, `spending_by_geography`, and `bulk_download`, abstracting the verbose POST filter grammar (time period, award type codes, agency tier, NAICS/PSC/CFDA arrays, location objects) and handling pagination plus the 429 backoff.

## Review notes

Potential new join keys for review (all exposed by this source, none currently in `schema/join-keys.yaml`):

- Potential new join key: `UEI`
  - Entity type: legal_entity / federal_award_recipient
  - Pattern: 12-character alphanumeric (SAM.gov Unique Entity Identifier), e.g. `ABC123DEF456`
  - Other datasets that would use it: SAM.gov, federal procurement/grant sources, corporate-registry entries. Highest-value candidate; the natural bridge from federal spending to entity registries.

- Potential new join key: `NAICS`
  - Entity type: industry_classification
  - Pattern: `^[0-9]{2,6}$` (North American Industry Classification System; the US analogue to the registry's `SIC_UK_2007`)
  - Other datasets that would use it: Census Business data, BLS, SAM.gov, any US industry-coded source.

- Potential new join key: `PSC` (Product and Service Code)
  - Entity type: product_or_service_classification
  - Pattern: 4-character alphanumeric
  - Other datasets that would use it: FPDS, SAM.gov contract data.

- Potential new join key: `CFDA` / Assistance Listing Number
  - Entity type: federal_assistance_program
  - Pattern: `^[0-9]{2}\.[0-9]{3}$`, e.g. `93.243`
  - Other datasets that would use it: SAM.gov Assistance Listings (formerly CFDA.gov), grant sources.

License: US federal work under 17 USC 105, recorded as `US-Government-Public-Domain` (already canonical in SCHEMA.md).
