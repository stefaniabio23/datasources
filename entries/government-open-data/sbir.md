---
id: sbir
name: SBIR.gov (America's Seed Fund)
domain: government-open-data
entry_kind: registry
description: US federal SBIR/STTR seed-fund award records, awarded small businesses, and open solicitations across the participating federal agencies.
homepage_url: https://www.sbir.gov/
docs_url: https://www.sbir.gov/api
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "not documented; public API returns 429 during maintenance windows"
bulk_available: true
frequency: irregular
geography: [USA]
join_keys:
  - US_STATE_CODE
primary_keys:
  - SBIR_FIRM_NID
  - SBIR_AGENCY_TRACKING_NUMBER
  - SBIR_CONTRACT_NUMBER
  - SBIR_SOLICITATION_NUMBER
join_key_fields:
  - join_key: US_STATE_CODE
    fields: [state]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - federal seed-funding diligence on a company
  - map SBIR/STTR awards by agency and year
  - find open solicitations and topics
  - track small-business award history and amounts
access_test:
  command: "curl -sf 'https://api.www.sbir.gov/public/api/awards?agency=DOE&rows=1&format=json'"
  expected_status: 200
  expected_fields: [firm, agency, award_amount, award_year, uei, duns]
last_verified: 2026-07-07
notes: "access_test not executed successfully; endpoint returned HTTP 429 (SBIR Public API under maintenance) on 2026-07-07. Command constructed against the documented awards endpoint."
build_priority: low
---

# SBIR.gov (America's Seed Fund)

## Why this source matters

SBIR.gov is the US Small Business Administration's public portal for the Small Business Innovation Research (SBIR) and Small Business Technology Transfer (STTR) programs, the federal "seed fund" that has issued non-dilutive R&D awards to small companies since 1982. It aggregates award, company, and solicitation data across the participating federal agencies (DOD, HHS/NIH, DOE, NASA, NSF, USDA, EPA, DOC, ED, DOT, DHS). For an agent, it is the authoritative source for "which US small companies received federal early-stage R&D money, from which agency, for what, and how much." Useful for company diligence, tech-scouting, and mapping government funding flows into a sector or firm. Secondary relevance to `corporate-registry` (awarded firms with UEI/DUNS) and `finance-markets` (non-dilutive funding signal).

## Agent use cases

- federal seed-funding diligence on a company
- map SBIR/STTR awards by agency and year
- find open solicitations and topics
- track small-business award history and amounts

## Join strategy

The high-value company identifiers this source exposes are `uei` (SAM.gov Unique Entity Identifier) and `duns` (legacy DUNS number) on both award and company records, plus `agency`. None of these are in the canonical registry yet, so they are flagged under Review notes rather than mapped. The only canonical join key currently exposed is `US_STATE_CODE` via the awardee `state` field (two-letter USPS abbreviation), a weak geographic join.

Source-internal identifiers used for direct lookups (not cross-source joins): `firm_nid` (SBIR company node id), `agency_tracking_number`, `contract` (agency contract number), and `solicitation_number`. Awards also carry `topic_code`, `solicitation_year`, and `award_year`.

Pair with SAM.gov / USASpending (via UEI) for full federal-award context, and with a corporate registry (via UEI or company name) to resolve awardees to legal entities, once UEI/DUNS are promoted to canonical keys.

## Access notes

Base URL is `https://api.www.sbir.gov/public/api/` with three endpoints: `awards`, `company` (aka firm), and `solicitation`. Query awards by `agency=` (DOE, NASA, NSF, HHS, USDA, EPA, DOC, ED, DOT, DHS), `firm=`, `year=`, or `ri=` (research institution). Pagination via `rows=` (default 100) and `start=` (offset); `format=` accepts `json` (default) or `xml`. Default sort is award date descending and cannot be changed. No auth key required.

Note: on 2026-07-07 the public API returned HTTP 429 with `{"Code":"TooManyRequestsError","Message":"The SBIR Public API is not available at this time."}`, and the docs page states the APIs are undergoing maintenance. For large or reliable pulls, prefer the bulk downloads on the Data Resources page: award data with abstracts (~290 MB), without abstracts (~65 MB), plus topics/awards/company files in XLS, JSON, and CSV (web interface caps interactive downloads at 10,000 records).

## MCP / connector notes

No MCP found on the official or community registries. Audience is narrow (federal-funding analysts), so low build value. A thin connector would expose `search_awards` (by agency/firm/year/ri), `get_company`, and `list_solicitations`, abstracting over `rows`/`start` pagination, the JSON-vs-XML `format` flag, and the bulk-file fallback for large pulls (the live API is rate-limited and intermittently in maintenance). Given the small, clean parameter surface, the raw REST API is close to sufficient once it is back online.

## Review notes

Potential new join keys for review:

Potential new join key for review: UEI
  Entity type: legal_entity (US SAM.gov registrant)
  Pattern: ^[A-Z0-9]{12}$ (12-char alphanumeric, no vowels/ambiguous chars)
  Other datasets that would use it: SAM.gov, USASpending.gov, Grants.gov, FPDS, any post-2022 US federal award or contract source. High cross-source value; strong candidate for the finance/corporate section.

Potential new join key for review: DUNS
  Entity type: legal_entity (legacy Dun & Bradstreet business number)
  Pattern: ^[0-9]{9}$
  Other datasets that would use it: legacy US federal award data pre-2022 UEI transition, D&B-linked corporate datasets. Deprecated by the US government in favour of UEI but still present in historical records.

License: SBIR.gov content is a US federal government work; treated as `US-Government-Public-Domain` (17 USC 105). The site does not publish an explicit license or terms-of-use string for the API/data, so confirm before commercial redistribution.
