---
id: osha-inspections
name: OSHA Inspections
domain: government-open-data
entry_kind: event-stream
description: US OSHA workplace safety inspection, citation, and penalty records from the IMIS enforcement database, covering federal and state-plan inspections since 1972.
homepage_url: https://www.osha.gov/ords/imis/establishment.html
docs_url: https://developer.dol.gov/health-and-safety/dol-osha-enforcement/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free
license: US-Government-Public-Domain
rate_limit: "DOL API: free key, per-key throttling (undocumented ceiling); bulk CSV: none"
bulk_available: true
frequency: quarterly
lag: "inspection records post weeks-to-months after case activity; citations subject to continuing correction"
geography: [USA]
join_keys:
  - US_STATE_CODE
  - NAICS_CODE
primary_keys:
  - OSHA_ACTIVITY_NR
  - OSHA_REPORTING_ID
join_key_fields:
  - join_key: US_STATE_CODE
    fields: [site_state, mail_state]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - workplace-safety diligence on an employer
  - citation and penalty lookup by establishment
  - industry-level enforcement pattern analysis
  - fatality and severe-injury inspection retrieval
  - ESG / labour-risk screening
access_test:
  command: "curl -sf -o /dev/null -w '%{http_code}' 'https://www.osha.gov/ords/imis/establishment.html'"
  expected_status: 200
  expected_fields: []
last_verified: 2026-07-07
build_priority: low
notes: "access_test hits the public establishment-search web UI (no auth); the programmatic DOL OSHA Enforcement API requires a free key (${DOL_API_KEY}) and was not executed."
---

# OSHA Inspections

## Why this source matters

The US Occupational Safety and Health Administration (OSHA) runs the Integrated Management Information System (IMIS), the enforcement database of record for workplace-safety inspections. It holds more than 3 million inspections conducted since 1972, roughly 90,000 new inspections a year, each linked to the citations, violated standards, penalty assessments, accident/fatality details, and inspecting office. An agent doing employer due diligence, labour-risk or ESG screening, or industry-level safety-pattern analysis can pull an establishment's full enforcement history: inspection dates, scope and type, violation counts by severity (serious/willful/repeat), and initial vs. current penalty amounts. Secondary domain is corporate-registry (records key on employer establishment name and address).

## Agent use cases

- workplace-safety diligence on an employer
- citation and penalty lookup by establishment
- industry-level enforcement pattern analysis
- fatality and severe-injury inspection retrieval
- ESG / labour-risk screening

## Join strategy

The only registry join key OSHA exposes cleanly is `US_STATE_CODE` (2-letter USPS in `site_state`/`mail_state`). Site zip is present but is a mailing zip, not a Census ZCTA, so it is not mapped to `ZCTA` here.

Industry is recorded as a 6-digit US NAICS code (`naics_code`) and a 4-digit 1987 US SIC code (`sic_code`). Neither has a canonical join key in the registry today (the only SIC key present is `SIC_UK_2007`, a different scheme). Both are flagged under Review notes as candidate keys, since they are the natural bridge to any US industry-coded source (Census, BLS, corporate registries).

Source-internal identifiers: `activity_nr` is OSHA's unique inspection/activity number (the primary key across the inspection, violation, and accident tables), and `reporting_id` identifies the OSHA office. These are in `primary_keys`, not `join_keys`. There is no stable establishment ID; an employer is identified by name plus address, so cross-source company matching requires name/address resolution rather than a mint key.

## Access notes

Three access paths. First, the establishment-search web UI at the homepage URL (no auth, good for a single-employer lookup and the freshness check used in `access_test`). Second, bulk CSV: OSHA publishes the full inspection/violation/accident tables through the DOL Open Data Portal (the legacy `enforcedata.dol.gov` catalog now redirects to `data.dol.gov`); files are zipped CSVs, no auth, refreshed quarterly, and are the right path for any analysis over more than a handful of establishments. Third, the DOL OSHA Enforcement API (`developer.dol.gov`) exposes the same tables (`osha_inspection`, `osha_violation`, `osha_accident`, and related) as JSON/XML but requires a free API key registered at the DOL developer portal; substitute `${DOL_API_KEY}` at runtime. IMIS citation data is explicitly flagged by OSHA as subject to continuing correction, so treat penalty and citation fields as provisional and verify against field-office case files for high-stakes use.

## MCP / connector notes

No MCP found (searched modelcontextprotocol org, GitHub, npm, PyPI). Audience is relatively narrow, so low build priority. A useful connector surface would be: `search_inspections(estab_name|naics|state|date_range)`, `get_inspection(activity_nr)`, `get_violations(activity_nr)`, `get_accidents(activity_nr)`. The MCP must abstract over the two backends (clean DOL API with a key vs. the quarterly bulk CSV), normalise NAICS/SIC industry filtering, and surface the "citations subject to correction" caveat in responses.

## Review notes

Potential new join key for review: NAICS_CODE
  Entity type: industry_classification
  Pattern: `^[0-9]{2,6}$` (6-digit at full resolution; 2-5 digit rollups exist)
  Other datasets that would use it: US Census (County Business Patterns, Economic Census), BLS (QCEW, OES), openFDA, EPA FRS, most US corporate/economic sources. High cross-source value; strong candidate.

Potential new join key for review: SIC_US_1987
  Entity type: industry_classification
  Pattern: `^[0-9]{4}$`
  Other datasets that would use it: legacy US enforcement/economic datasets, SEC EDGAR (SEC uses its own SIC list). Note the registry already has `SIC_UK_2007`; a US SIC key would be a distinct scheme, so do not overload the UK key.

License is US federal work (17 USC 105), mapped to `US-Government-Public-Domain`; no new short name needed.
