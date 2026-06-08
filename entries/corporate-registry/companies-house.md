---
id: companies-house
name: Companies House (UK)
domain: corporate-registry
description: UK statutory register of incorporated companies with profiles, officers, filing history, and persons with significant control.
homepage_url: https://www.gov.uk/government/organisations/companies-house
docs_url: https://developer.company-information.service.gov.uk/
type:
  - rest-api
  - bulk-download
auth_required: api-key-free
cost: free
license: OGL-3.0
rate_limit: "600 req per 5-minute window per key. HTTP 429 on exceed."
bulk_available: true
frequency: real-time for filings, monthly for bulk snapshot
lag: "minutes for API, ~1 month for bulk"
geography: [GBR]
join_keys:
  - COMPANIES_HOUSE_NUMBER
  - ISO_3
  - DATE
  - URL
primary_keys:
  - COMPANIES_HOUSE_NUMBER
  - COMPANIES_HOUSE_OFFICER_ID
join_key_fields:
  - join_key: COMPANIES_HOUSE_NUMBER
    fields: [company_number]
  - join_key: ISO_3
    fields: [registered_office_address.country]
  - join_key: DATE
    fields: [date_of_creation, date_of_cessation]
  - join_key: URL
    fields: [links.self, links.filing_history]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  Suggested surface: search_companies, get_company, get_officers, get_psc,
  get_filing_history, get_charges. MCP must track the 5-minute rate-limit window
  client-side and queue rather than 429.
agent_use_cases:
  - UK company diligence
  - KYC
  - beneficial-ownership tracking
  - investigative journalism
  - supply-chain risk analysis
access_test:
  command: 'curl -sf -u "${COMPANIES_HOUSE_KEY}:" "https://api.company-information.service.gov.uk/search/companies?q=apple&items_per_page=5"'
  expected_status: 200
  expected_fields: [items, total_results, page_number]
last_verified: 2026-06-08
build_priority: high
notes: access_test not yet executed; requires COMPANIES_HOUSE_KEY env var. Free bulk omits officers and PSC, API only for those.
---

# Companies House (UK)

## Why this source matters

UK statutory company register: ~5M companies, ~10M officers, ~6M persons with significant control. Real-time on filings. Crown Copyright, freely usable under OGL v3.0. The only authoritative, free, programmatic source for UK corporate metadata. KYC pipelines, M&A diligence, journalism, beneficial-ownership investigations, supply-chain risk analysis all hit this API.

## Agent use cases

- UK company diligence
- KYC
- beneficial-ownership tracking
- investigative journalism
- supply-chain risk analysis

## Join strategy

`COMPANIES_HOUSE_NUMBER` is the canonical UK-company identifier (8-character, e.g. `00006400`). Pair with `ISIN` (via OpenFIGI) for UK-listed equities, `LEI` if you bring in GLEIF data, `DATE` for incorporation/dissolution filters, `URL` for filing-PDF deep links.

CH-internal IDs (`COMPANIES_HOUSE_OFFICER_ID`) are not in the canonical registry; use them for direct intra-CH joins only.

For PSC and beneficial-ownership work, pair with OpenSanctions or Open Ownership.

## Access notes

**Most queries:** REST API at `https://api.company-information.service.gov.uk/`. Free API key via HTTP Basic Auth (key as username, empty password). The 600 req / 5-minute window is the binding constraint.

**Wide-net analyses:** monthly bulk CSV at `http://download.companieshouse.gov.uk/en_output.html`. Basic company data only, no officers or PSC.

Known gotchas:

- PSC data is self-reported; ~10% of records have known quality issues.
- Rate limit applies per-API-key, not per-IP. Multi-tenant agents need separate keys.
- Dissolved companies remain indefinitely. Filter by `company_status` for active-only.
- Filing-document deep links return PDFs, not structured data.

## MCP / connector notes

No official MCP. Clean public registry, well-documented API, well-defined rate limit. Suggested surface: `search_companies`, `get_company`, `get_officers`, `get_psc`, `get_filing_history`, `get_charges`. The MCP should queue client-side rather than triggering 429s.

## Review notes

None.
