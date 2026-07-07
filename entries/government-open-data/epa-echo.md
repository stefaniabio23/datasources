---
id: epa-echo
name: EPA ECHO (Enforcement & Compliance History Online)
domain: government-open-data
entry_kind: mixed
description: US EPA integrated compliance, enforcement, inspection, and permit-discharge database for ~800,000 facilities regulated under the Clean Air Act, Clean Water Act, RCRA, and SDWA.
homepage_url: https://echo.epa.gov/
docs_url: https://echo.epa.gov/tools/web-services
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "no documented request cap; a hard queryset row limit rejects overly broad searches, refine with state/county/program filters and page via QueryID + responseset"
bulk_available: true
frequency: weekly
lag: "facility compliance snapshot refreshed weekly from contributing EPA program systems; enforcement cases and DMR effluent data lag their source systems by weeks to a quarter"
geography: [USA]
structure: registry-snapshot
join_keys:
  - FIPS
  - US_STATE_CODE
  - ZCTA
primary_keys:
  - FRS_REGISTRY_ID
  - NPDES_PERMIT_ID
  - RCRA_HANDLER_ID
  - PWSID
  - AIR_FACILITY_ID
join_key_fields:
  - join_key: FIPS
    fields: [FacFIPSCode, FacDerivedStctyFIPS]
  - join_key: US_STATE_CODE
    fields: [FacState]
  - join_key: ZCTA
    fields: [FacZip]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/pipeworx-io/epa-echo"
  - "apify.com/andrew_avina/epa-intelligence-mcp"
mcp_notes: >
  Community MCPs wrap the ECHO REST endpoints (combined all-media search plus
  Clean Water Act and hazardous-waste media services) and normalise output.
  No official EPA MCP. Suggested surface: search_facilities, get_facility_report,
  get_enforcement_cases, get_effluent_charts, screen_corporation.
agent_use_cases:
  - facility compliance screening
  - enforcement-history lookup
  - inspection and violation tracking
  - permit-discharge (DMR) retrieval
  - corporate multi-facility compliance screening
access_test:
  command: "curl -sf 'https://echodata.epa.gov/echo/echo_rest_services.get_facility_info?output=JSON&p_st=DC'"
  expected_status: 200
  expected_fields: [Results, Message, QueryID]
last_verified: 2026-07-07
build_priority: medium
---

# EPA ECHO (Enforcement & Compliance History Online)

## Why this source matters

ECHO is the US Environmental Protection Agency's public front end for compliance and enforcement history across the major environmental statutes. Where FRS (see `epa-frs`) answers "what facilities exist", ECHO answers "are they in compliance, when were they last inspected, what violations and penalties are on record". It integrates roughly 800,000 regulated facilities and stitches together the program systems behind the Clean Air Act (ICIS-Air), Clean Water Act (ICIS-NPDES), Resource Conservation and Recovery Act (RCRAInfo), and Safe Drinking Water Act (SDWIS), plus enforcement-case records, inspection counts, penalties, and permit-discharge monitoring reports (DMRs). For an agent doing environmental diligence, ESG screening, or facility risk assessment, ECHO is the single query surface that returns current compliance status and three-year violation history keyed to a facility. Secondary relevance to `corporate-registry` (the Corporate Compliance Screener rolls facilities up to parent organisations).

## Agent use cases

- facility compliance screening
- enforcement-history lookup
- inspection and violation tracking
- permit-discharge (DMR) retrieval
- corporate multi-facility compliance screening

## Join strategy

ECHO returns the standard US geographic canonical keys per facility: `US_STATE_CODE` (`FacState`), `FIPS` (`FacFIPSCode`, and `FacDerivedStctyFIPS` for the derived 5-digit county FIPS), and `ZCTA` (`FacZip`; this is the raw USPS ZIP, which approximates but is not strictly the Census ZCTA, join with that caveat). Pair these with Census, EIA, or CDC state/county data.

ECHO's real linking value is its facility identifier `RegistryID`, which is the EPA FRS Registry ID (12-digit `110...`). That is the hub that resolves an ECHO facility to FRS and to every other EPA program dataset. ECHO also surfaces program-native permit and handler IDs (`primary_keys`): NPDES permit numbers (ICIS-NPDES `SourceID`), RCRA handler IDs, public water system IDs (PWSID), and air program facility IDs. Industry codes are present as `FacNAICSCodes` (US NAICS) and `FacSICCodes` (US SIC). None of the EPA registry/facility/permit IDs nor NAICS are canonical keys in this registry yet; all are flagged in Review notes (`FRS_REGISTRY_ID` and `NAICS` are the same candidates already raised by the `epa-frs` entry, ECHO reinforces the case for both).

## Access notes

Query-only REST services live under `https://echodata.epa.gov/echo/`. The combined all-media service is `echo_rest_services.get_facility_info` (append `?output=JSON&p_st=<state>` plus optional `p_co` county, `p_naics`, program flags); media-specific services are `cwa_rest_services`, `air_rest_services`, `rcra_rest_services`, and `sdwa_rest_services`. Output is JSON, JSONP, or XML. No auth, no API key. Search calls return a `QueryID` and summary counts; fetch the actual facility rows with `get_qid?qid=<QueryID>&responseset=<page>`. Broad searches are rejected with a queryset-limit error, so filter by state/county/program and paginate. For full-corpus work, use the ECHO Exporter and program flat-file downloads under `https://echo.epa.gov/tools/data-downloads` rather than paginating the API; the same data is mirrored as a dataset on data.gov.

## MCP / connector notes

Community MCP servers exist (no official EPA one as of 2026-07): `github.com/pipeworx-io/epa-echo` wraps the CWA, hazardous-waste, and combined endpoints into a normalised schema, and an Apify-hosted `epa-intelligence-mcp` exposes ECHO enforcement data. Both are community-maturity. A connector should abstract the two-step `get_facility_info` -> `get_qid` pagination, the queryset-limit rejection, and the per-media service split behind named tools such as `search_facilities`, `get_facility_report`, `get_enforcement_cases`, and `get_effluent_charts`, with response trimming.

## Review notes

Join keys flagged by the task hints and confirmed present in ECHO but absent from `schema/join-keys.yaml`:

Potential new join key for review: NAICS
  Entity type: industry_classification
  Pattern: `^[0-9]{2,6}$` (US/North American Industry Classification System code)
  Other datasets that would use it: Census County Business Patterns, BLS, EIA, EPA FRS/ECHO, SEC EDGAR crosswalks. Registry currently has only `SIC_UK_2007`; a US NAICS key would be broadly reused. Same candidate already raised in `epa-frs`.

Potential new join key for review: FRS_REGISTRY_ID
  Entity type: regulated_facility
  Pattern: `^1[0-9]{11}$` (12-digit EPA facility identifier, `110...`; ECHO returns it as `RegistryID`)
  Other datasets that would use it: every EPA program dataset (FRS, TRI, NPDES/ICIS, RCRAInfo, SDWIS, GHGRP) resolves to this ID. Same candidate already raised in `epa-frs`; ECHO strengthens it.

Potential new join key for review: NPDES_ID
  Entity type: water_discharge_permit
  Pattern: `^[A-Z]{2}[A-Z0-9]{7}$` (ICIS-NPDES permit / source ID, e.g. state prefix + 7 chars; ECHO returns it as `SourceID` in the CWA service)
  Other datasets that would use it: ICIS-NPDES, EPA Water Pollutant Loading Tool, state discharge-monitoring datasets. Distinct facility-permit identifier not covered by FRS registry ID.

Program-native RCRA handler IDs, PWSID (public water system IDs), and air program facility IDs are also surfaced; they are narrower and left as `primary_keys` rather than proposed for the canonical registry.

License: EPA data is a US federal government work, public domain under 17 USC 105 (`US-Government-Public-Domain`). No redistribution restriction published; attribution to EPA is customary but not required.
