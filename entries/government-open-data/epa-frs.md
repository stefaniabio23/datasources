---
id: epa-frs
name: EPA Facility Registry Service (FRS)
domain: government-open-data
entry_kind: registry
description: US EPA master registry of facilities and sites subject to environmental regulation, each assigned a single cross-program FRS Registry ID.
homepage_url: https://www.epa.gov/frs
docs_url: https://www.epa.gov/enviro/envirofacts-data-service-api
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "no documented request cap; each request must complete within 15 minutes, paginate large pulls"
bulk_available: true
frequency: weekly
lag: "continuous to monthly refresh from contributing EPA program systems; national bulk files typically monthly, file geodatabase weekly"
geography: [USA]
structure: registry-snapshot
join_keys:
  - FIPS
  - US_STATE_CODE
  - ZCTA
  - NAICS_CODE
  - EPA_REGISTRY_ID
primary_keys:
  - FRS_REGISTRY_ID
join_key_fields:
  - join_key: FIPS
    fields: [fips_code, std_county_fips]
  - join_key: US_STATE_CODE
    fields: [state_code, std_state_code]
  - join_key: ZCTA
    fields: [postal_code, std_postal_code]
mcp_status: api-direct-sufficient
agent_use_cases:
  - environmental facility lookup
  - cross-program facility resolution
  - facility geolocation
  - industry-classified facility search
  - regulatory-interest screening
access_test:
  command: "curl -sf 'https://data.epa.gov/dmapservice/frs.frs_facility_site/registry_id/equals/110009327246/JSON'"
  expected_status: 200
  expected_fields: [registry_id, primary_name, state_code, fips_code, postal_code]
last_verified: 2026-07-03
build_priority: medium
---

# EPA Facility Registry Service (FRS)

## Why this source matters

FRS is the US Environmental Protection Agency's authoritative registry of facilities, sites, and places subject to environmental regulation. Its job is deduplication: FRS mints one FRS Registry ID (a 12-digit `110...` identifier) per real-world facility and links that ID to the many program-system records (air, water, waste, Superfund, TRI, enforcement) that describe the same place. For an agent, FRS is the crosswalk that collapses dozens of EPA program identifiers onto a single canonical facility, with name, standardised address, county FIPS, and (in the geospatial files) latitude/longitude and NAICS/SIC industry codes. Secondary relevance to `geospatial` (facility point geometry) and `corporate-registry` (facility-to-operator linkage).

## Agent use cases

- environmental facility lookup
- cross-program facility resolution
- facility geolocation
- industry-classified facility search
- regulatory-interest screening

## Join strategy

FRS exposes the standard US geographic canonical keys: `US_STATE_CODE` (`state_code`), `FIPS` (`fips_code` carries the 5-digit county FIPS, e.g. `17097`), and `ZCTA` (`postal_code`; note this is the raw USPS ZIP, which approximates but is not strictly the Census ZCTA, join with that caveat). Use these to pair FRS facilities with Census, EIA, or CDC state/county data.

FRS's real value is its own `FRS_REGISTRY_ID` (in `primary_keys`), the hub that ties together program-system identifiers via `PGM_SYS_ACRNM` + `PGM_SYS_ID` in the `frs.frs_program_facility` table (TRI IDs, NPDES permit numbers, RCRA handler IDs, CERCLIS IDs, and more). That registry ID is not yet a canonical key here; see Review notes. NAICS/SIC industry codes and lat/long coordinates are present in the geospatial bulk download and adjacent Envirofacts tables but are not canonical join keys in this registry, both are flagged below.

## Access notes

Two programmatic paths. First hit the Envirofacts Data Service REST API at `https://data.epa.gov/dmapservice/`, querying FRS tables as `frs.<table>` (e.g. `frs.frs_facility_site`, `frs.frs_program_facility`). URL grammar is `/<table>/<column>/<operator>/<value>/<first>:<last>/<format>`; default output is JSON, with CSV, Excel, XML, and Parquet available by appending the format. No auth, no API key. Each request must return within 15 minutes; paginate with the `first:last` row range for large result sets. Table joins are expressed inline, e.g. join `frs.frs_facility_site` to `frs.frs_program_facility` on `registry_id`.

For full-corpus work, use the national/state bulk downloads (combined CSV set with separate files for geospatial coordinates, industrial classifications, alternative names, contacts; plus a file geodatabase refreshed weekly) rather than paginating the API. NAICS/SIC and lat/long live in the combined CSV set and geodatabase.

## MCP / connector notes

No known EPA/Envirofacts MCP server as of 2026-07. The Envirofacts REST API is clean, no-auth, and JSON-native, so `api-direct-sufficient`: an agent can call it directly. A thin wrapper would still help by abstracting the positional URL grammar (`/<column>/<operator>/<value>/`) and the `frs.frs_program_facility` join pattern behind named tools such as `get_facility(registry_id)`, `search_facilities(state, county_fips, naics)`, and `list_program_links(registry_id)`, plus response trimming and automatic pagination under the 15-minute limit.

## Review notes

Potential new join keys for review, all three flagged by the task and confirmed present in FRS but absent from `schema/join-keys.yaml`:

Potential new join key for review: NAICS
  Entity type: industry_classification
  Pattern: `^[0-9]{2,6}$` (US/North American Industry Classification System code)
  Other datasets that would use it: Census County Business Patterns, BLS, EIA, SEC EDGAR SIC crosswalks, most US corporate-registry and government-open-data sources. Registry currently has only `SIC_UK_2007`; a US NAICS key would be broadly reused.

Potential new join key for review: FRS_REGISTRY_ID
  Entity type: regulated_facility
  Pattern: `^1[0-9]{11}$` (12-digit EPA facility identifier, `110...`)
  Other datasets that would use it: every EPA program dataset (TRI, ECHO/enforcement, NPDES/ICIS, RCRAInfo, Superfund/CERCLIS, GHGRP) resolves to the FRS Registry ID; it is the canonical cross-EPA facility hub. Strong candidate if more EPA program sources are added.

Potential new join key for review: LAT_LONG (spatial, not an identifier)
  Entity type: geographic_point
  Pattern: decimal degrees WGS84/NAD83 latitude+longitude pair
  Note: FRS geospatial files carry facility coordinates. This is a spatial-join surface, not an ID-style equality join; the registry has no coordinate key yet. Flag rather than force into an equality join_key.

License: EPA data is a US federal government work, public domain under 17 USC 105 (`US-Government-Public-Domain`). No explicit terms-of-use or redistribution restriction published on the FRS bulk-download page; attribution to EPA is customary but not required.
