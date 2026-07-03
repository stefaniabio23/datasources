---
id: bea
name: BEA Data API (Bureau of Economic Analysis)
domain: government-open-data
entry_kind: mixed
description: US Bureau of Economic Analysis API serving official national, industry, regional, and international economic accounts (GDP, personal income, trade, direct investment).
homepage_url: https://apps.bea.gov/api/
docs_url: https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf
type:
  - rest-api
  - bulk-download
auth_required: api-key-free
cost: free
license: US-Government-Public-Domain
rate_limit: "100 requests/min, 100 MB/min, 30 errors/min per key; exceeding any limit blocks the key for 1 hour"
bulk_available: true
frequency: "varies by dataset: annual, quarterly, monthly"
lag: "GDP advance estimate ~1 month after quarter-end; regional annual data lags ~1 year"
geography: [USA, global]
join_keys:
  - DATE
  - FIPS
primary_keys:
  - BEA_TABLE_NAME
  - BEA_LINE_CODE
  - BEA_SERIES_CODE
  - BEA_INDUSTRY_CODE
  - BEA_GEOFIPS
join_key_fields:
  - join_key: DATE
    fields: [TimePeriod, Year]
  - join_key: FIPS
    fields: [GeoFips]
mcp_status: mcp-needed-high-value
mcp_notes: >
  No first-party API-backed MCP. An Apify "bea-economic-scraper" MCP scrapes the
  website rather than calling the API. Official Python (us-bea/beaapi) and R
  (us-bea/bea.R) clients exist and would make a thin wrapper cheap. Suggested
  surface: list_datasets, list_parameters, get_parameter_values, get_data,
  resolve_table (name -> TableName), resolve_geofips.
agent_use_cases:
  - macro indicator retrieval
  - regional gdp and income lookup
  - industry value-added analysis
  - trade and direct-investment stats
  - point-in-time economic context
access_test:
  command: "curl -sf 'https://apps.bea.gov/api/data?&UserID=${BEA_API_KEY}&method=GETDATA&datasetname=NIPA&TableName=T10101&Frequency=Q&Year=2023&ResultFormat=JSON'"
  expected_status: 200
  expected_fields: [BEAAPI, Results, Data]
last_verified: 2026-07-02
build_priority: medium
notes: "access_test not executed; requires ${BEA_API_KEY} (free 36-char UserID). Host reachability confirmed: unauthenticated GETDATASETLIST returns HTTP 200 with a JSON error body (APIErrorCode 4, inactive UserId)."
pit_reconstructable: false
revisions_possible: true
---

# BEA Data API (Bureau of Economic Analysis)

## Why this source matters

The Bureau of Economic Analysis is the US Commerce Department agency that produces the country's headline economic accounts: GDP, personal income and outlays, the National Income and Product Accounts (NIPA), GDP-by-industry, fixed assets, international transactions (ITA), the international investment position (IIP), multinational-enterprise activity (MNE), and sub-national income and product for states, counties, and metros (Regional). One free API key exposes all of it as JSON or XML over HTTPS. This is the authoritative primary source behind most US macro reporting, which makes it a natural spine for any agent doing economic context, regional analysis, or trade and investment work. Secondary domain: much of the content is finance-markets relevant (macro series that pair with market data).

## Agent use cases

- macro indicator retrieval
- regional gdp and income lookup
- industry value-added analysis
- trade and direct-investment stats
- point-in-time economic context

## Join strategy

Two canonical join keys are exposed. `DATE` comes from the `TimePeriod` field (and the `Year` request parameter), covering annual (`2023`), quarterly (`2023Q1`), and monthly forms depending on dataset. `FIPS` comes from the `GeoFips` field in the Regional dataset, where US states are 2-digit and counties are 5-digit FIPS codes. Note that `GeoFips` also carries BEA-specific aggregate codes (national `00000`, BEA economic areas, MSAs) that are not pure Census FIPS, so filter to standard state/county codes before joining to Census, CDC, or EIA geography.

Everything else that identifies a BEA cell is source-internal and lives in `primary_keys`: `BEA_TABLE_NAME` (e.g. `T10101`), `BEA_LINE_CODE` (the row within a table), `BEA_SERIES_CODE`, and `BEA_INDUSTRY_CODE` (BEA's own industry grouping, close to but not identical to NAICS). These are not cross-source join keys and stay out of `join_keys`. See Review notes for a NAICS candidate.

Pair with FRED for a unified series interface over the same BEA aggregates, Census (ACS/CBP) for demographic and business geography on the same FIPS spine, and BLS for employment to complement BEA income and output.

## Access notes

Register for a free UserID (36-char key) at `https://apps.bea.gov/api/signup/`. Base endpoint is `https://apps.bea.gov/api/data` with three core methods: `GETDATASETLIST` (enumerate datasets), `GETPARAMETERLIST` / `GETPARAMETERVALUES` (discover valid `TableName`, `LineCode`, `GeoFips`, `Frequency`, `Year`, `Industry` values per dataset), and `GETDATA` (the actual pull). Always pass `datasetname=` plus the dataset's required parameters; `ResultFormat=JSON` or `XML`.

Rate limits are enforced per key: 100 requests/min, 100 MB/min, and 30 errors/min. Tripping any one blocks the key for an hour, so discover parameter values once and cache them rather than probing in a loop. The API returns HTTP 200 even on logical errors, embedding the failure in `BEAAPI.Results.Error`, so check the body, not just the status code. For large historical pulls, BEA also publishes bulk downloadable files on bea.gov and maintains official Python (`us-bea/beaapi`) and R (`us-bea/bea.R`) clients that self-throttle.

## MCP / connector notes

No first-party API-backed MCP. A community Apify server ("bea-economic-scraper") exists but scrapes the website rather than calling the API, so it inherits scraper fragility. A proper connector is high value: macro, regional, industry, and trade statistics overlap the audience of several other entries here. Because official Python and R clients already handle throttling and parameter resolution, an MCP is a thin wrapper. Suggested surface: `list_datasets`, `list_parameters(dataset)`, `get_parameter_values(dataset, param)`, `get_data(dataset, ...)`, plus helpers `resolve_table` (human name to `TableName`) and `resolve_geofips`. The connector should abstract the always-200 error convention and the per-dataset parameter differences (NIPA wants `TableName`+`LineCode`; Regional wants `TableName`+`GeoFips`+`LineCode`; GDPbyIndustry wants `Industry`).

## Review notes

Potential new join key for review: NAICS_CODE
  Entity type: industry_classification
  Pattern: ^[0-9]{2,6}$ (2-6 digit North American Industry Classification System)
  Other datasets that would use it: Census County Business Patterns, BLS QCEW, SEC EDGAR (SIC crosswalk), Census Economic Census. BEA's GDPbyIndustry uses BEA-defined industry groupings that crosswalk to NAICS but are not identical; a NAICS canonical key would need a documented crosswalk, so flagging rather than mapping. BEA's own `BEA_INDUSTRY_CODE` and `BEA_TABLE_NAME` are source-internal and kept in primary_keys, not proposed as canonical keys.

License: BEA statistics are US federal works in the public domain (mapped to `US-Government-Public-Domain`); BEA requests citation but imposes no redistribution restriction. Confirm the short name is acceptable (already used elsewhere in the registry per SCHEMA.md).
