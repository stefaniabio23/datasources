---
id: e-prtr
name: E-PRTR (European Industrial Emissions Portal)
domain: government-open-data
entry_kind: mixed
description: EU-wide register of pollutant releases, waste transfers, and energy/emissions data for ~33,000 large industrial facilities across 33 European countries.
homepage_url: https://industry.eea.europa.eu/
docs_url: https://industry.eea.europa.eu/download
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "no published limit; ArcGIS REST FeatureServer standard paging (resultRecordCount / resultOffset)"
bulk_available: true
frequency: annual
lag: "1-2 years; member states report annually under Art. 7 of Regulation (EC) No 166/2006"
geography: [Europe, EU27, EFTA, Serbia, Iceland, Liechtenstein, Norway, Switzerland]
structure: panel
revisions_possible: true
join_keys:
  - ISO_2
  - NUTS
  - DATE
primary_keys:
  - EPRTR_FACILITY_ID
  - EPRTR_FACILITY_REPORT_ID
  - EPRTR_NATIONAL_ID
join_key_fields:
  - join_key: ISO_2
    fields: [CountryCode]
  - join_key: NUTS
    fields: [NUTSLevel2RegionCode]
  - join_key: DATE
    fields: [ReportingYear]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - industrial facility lookup by location
  - pollutant release and waste-transfer queries
  - parent-company emissions attribution
  - sector-level emissions aggregation
  - large-combustion-plant energy and emissions analysis
access_test:
  command: "curl -sf 'https://air.discomap.eea.europa.eu/arcgis/rest/services/Air/EprtrFacilities_Dyna_WGS84/FeatureServer/0/query?where=1%3D1&outFields=FacilityID,CountryCode,ReportingYear,NUTSLevel2RegionCode&resultRecordCount=1&f=json'"
  expected_status: 200
  expected_fields: [FacilityID, CountryCode, ReportingYear, NUTSLevel2RegionCode]
last_verified: 2026-07-07
build_priority: medium
---

# E-PRTR (European Industrial Emissions Portal)

## Why this source matters

The European Industrial Emissions Portal is the single entry point for the European Pollutant Release and Transfer Register (E-PRTR) and related industrial reporting under the Industrial Emissions Directive (2010/75/EU) and Regulation (EC) No 166/2006. It is jointly run by the European Environment Agency (EEA) and the European Commission. It holds location and administrative data for ~33,000 of the largest industrial complexes across 33 countries (EU27, Iceland, Liechtenstein, Norway, Switzerland, Serbia, and historically the UK), plus their reported releases of 91 regulated pollutants to air, water, and land, off-site waste transfers, and detailed energy-input and emissions data for large combustion plants. It is the authoritative open source for facility-level industrial emissions in Europe. Secondary relevance to `geospatial` (facilities carry point coordinates and NUTS regions) and `corporate-registry` (parent-company names attribute emissions to operators).

## Agent use cases

- industrial facility lookup by location
- pollutant release and waste-transfer queries
- parent-company emissions attribution
- sector-level emissions aggregation
- large-combustion-plant energy and emissions analysis

## Join strategy

The registry-side canonical keys this source exposes are `ISO_2` (`CountryCode`, two-letter e.g. `NO`), `NUTS` (`NUTSLevel2RegionCode`, e.g. `NO03`), and `DATE` (`ReportingYear`, year granularity). The country code is alpha-2; map to `ISO_3` when joining against sources that key on the three-letter form.

Facility identity is carried by source-native ids kept in `primary_keys`: `FacilityID` (the stable E-PRTR facility identifier), `NationalID` (member-state identifier), and `FacilityReportID` (per-report row id). The full tabular dataset (EEA SDI catalogue, ver 10.0) additionally carries an INSPIRE `inspireId` per facility and a NACE rev. 2 economic-activity code. Neither the E-PRTR facility id nor NACE is in the canonical registry yet; both are flagged in Review notes as cross-source-facility / industry-classification candidates.

Pair with corporate registries (via parent-company name matching or a future facility key) for operator diligence, with NUTS-keyed regional statistics for pollution-per-region analysis, and with EU emissions-trading or air-quality sources on `ISO_2` + `DATE`.

## Access notes

Two practical paths. For programmatic queries, hit the EEA DiscoMap ArcGIS REST FeatureServer directly, no auth: `https://air.discomap.eea.europa.eu/arcgis/rest/services/Air/EprtrFacilities_Dyna_WGS84/FeatureServer/0/query`. Standard ESRI query params apply (`where`, `outFields`, `resultRecordCount`, `resultOffset`, `f=json|geojson`). License and metadata are returned in each service description. For full analysis, download the canonical tabular dataset from the EEA SDI catalogue (`https://sdi.eea.europa.eu/catalogue/`) and the portal Download page in Excel, CSV/TXT/SQL, Geopackage, GDB, ESRI:REST, or OGC:WMS formats; a historic Microsoft Access build also exists. Reporting years run 2007-2021 for E-PRTR releases and 2016-2021 for large-combustion-plant detail in the current versioned release; check the catalogue record date for the latest reporting cycle. Values for a given facility-year can be restated in later reporting cycles, so treat as revisable.

## MCP / connector notes

No MCP found. The ArcGIS REST FeatureServer is a clean, standard, queryable interface, so an agent can call it directly; a thin connector would mainly add value by abstracting ESRI query syntax and joining the facility layer to the pollutant-release and LCP tables. Suggested surface: `find_facilities` (by country / NUTS / sector / bbox), `get_facility_releases` (facility id + year -> pollutant rows), `get_lcp_emissions`, `aggregate_by_sector`. Low-value tier: audience (industrial-emissions analysts) is narrower than the directory's scholarly/clinical core.

## Review notes

- License short name `CC-BY-4.0` is standard SPDX; no new short name introduced.
- Country code in the live payload is ISO 3166-1 alpha-2, mapped to `ISO_2`. The join-key hint suggested `ISO_3`; the data does not carry alpha-3, so `ISO_3` is left to a consumer-side crosswalk.
- Potential new join key for review: `EPRTR_FACILITY_ID`
    Entity type: industrial_facility
    Pattern: integer (source field `FacilityID`); INSPIRE `inspireId` is an alternate stable facility identifier in the tabular dataset
    Other datasets that would use it: EU Registry (IED/LCP), national PRTR registers, EU-ETS installation data
- Potential new join key for review: `NACE_CODE`
    Entity type: industry_classification
    Pattern: NACE rev. 2 code (e.g. `20.11`); present as economic-activity code in the tabular dataset, distinct from the E-PRTR Annex I `IAActivityCode`/`IASectorCode` codes carried in the ArcGIS layer
    Other datasets that would use it: Eurostat structural business statistics, national statistical offices, corporate registries
