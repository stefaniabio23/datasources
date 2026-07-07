---
id: sam-gov
name: SAM.gov Contract Opportunities
domain: government-open-data
entry_kind: event-stream
description: US federal contract opportunities (solicitations, awards, sources-sought, presolicitations) posted by federal agencies on SAM.gov.
homepage_url: https://sam.gov/opportunities
docs_url: https://open.gsa.gov/api/get-opportunities-public-api/
type:
  - rest-api
  - web-ui
auth_required: api-key-free
cost: free-with-registration
license: US-Government-Public-Domain
rate_limit: "per-day quota by role: ~10/day non-federal personal key, 1,000/day registered/federal; 429 with Retry-After to midnight UTC on exhaustion"
bulk_available: false
frequency: continuous
lag: "minutes-to-hours after an agency posts a notice"
geography: [USA]
join_keys:
  - US_STATE_CODE
primary_keys:
  - SAM_NOTICE_ID
  - SAM_SOLICITATION_NUMBER
join_key_fields:
  - join_key: US_STATE_CODE
    fields: [placeOfPerformance.state.code, officeAddress.state]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/blencorp/capture-mcp-server"
  - "github.com/martc03/gov-mcp-servers"
  - "1102Tools SAM.gov MCP (pulsemcp.com/servers/1102tools-sam-gov)"
mcp_notes: >
  Community MCPs wrap the Get Opportunities API alongside USASpending/FPDS.
  Suggested surface: search_opportunities (date range + NAICS + set-aside),
  get_opportunity_by_notice_id, list_awards. Must abstract the mandatory
  postedFrom/postedTo window (max 1 year) and the low daily quota.
agent_use_cases:
  - federal procurement monitoring
  - solicitation search by NAICS
  - set-aside opportunity tracking
  - award and awardee lookup
  - competitor contract intelligence
access_test:
  command: "curl -sf 'https://api.sam.gov/opportunities/v2/search?api_key=${SAM_GOV_API_KEY}&postedFrom=01/01/2026&postedTo=01/31/2026&limit=1'"
  expected_status: 200
  expected_fields: [totalRecords, opportunitiesData, noticeId, solicitationNumber]
last_verified: 2026-07-07
build_priority: medium
notes: "access_test not yet executed; requires ${SAM_GOV_API_KEY} (free public key from SAM.gov Account Details page)."
---

# SAM.gov Contract Opportunities

## Why this source matters

SAM.gov is the US federal government's official system for posting contract opportunities: presolicitations, solicitations, sources-sought, combined synopsis/solicitations, award notices, and special notices. Run by GSA, it is the authoritative feed of what the federal government is buying and who won. The Get Opportunities Public API (`api.sam.gov/opportunities/v2/search`) exposes each notice with its NAICS code, set-aside, place of performance, agency hierarchy, and, for awards, the awardee's name and UEI. For any agent doing government-contracting intelligence, market sizing, or competitor tracking, this is the primary source. Secondary domains: it overlaps `corporate-registry` (awardee entities identified by UEI) and pairs naturally with USASpending.gov for realized-spend history.

## Agent use cases

- federal procurement monitoring
- solicitation search by NAICS
- set-aside opportunity tracking
- award and awardee lookup
- competitor contract intelligence

## Join strategy

The one canonical key this source cleanly exposes is `US_STATE_CODE`, via the place-of-performance and office-address state fields (two-letter USPS abbreviations), which lets you join opportunities to state-level datasets.

Source-internal identifiers live in `primary_keys`: `SAM_NOTICE_ID` (the unique per-notice UUID, queryable via `noticeid`) and `SAM_SOLICITATION_NUMBER` (agency-assigned, queryable via `solnum`). Neither is currently a canonical registry key.

Two identifiers here have strong cross-source utility but are not yet in the registry, flagged below for review: the NAICS industry code (the primary axis for joining to Census/BLS industry statistics and to USASpending) and the awardee UEI (SAM's Unique Entity Identifier, which replaced DUNS and is the join key to entity-registration and USASpending award data).

## Access notes

Hit `GET https://api.sam.gov/opportunities/v2/search` with a free public `api_key` (request one from the Account Details page on SAM.gov). `postedFrom` and `postedTo` are mandatory (MM/dd/yyyy, max one year apart); `limit` maxes at 1000. Filter with `ncode` (NAICS, max 6 digits), `ptype` (procurement type), `typeOfSetAside`, `noticeid`, `solnum`, `state`, `zip`.

The binding constraint is the daily quota, not per-second rate: a non-federal personal key is throttled to roughly 10 requests/day, registered/federal keys to ~1,000/day; exceeding it returns 429 with a Retry-After pointing at midnight UTC. Personal keys auto-rotate every 90 days. There is no bulk snapshot; for large historical pulls, paginate the API within the quota or use the daily contract-opportunity CSV extracts published on the SAM.gov data-services page.

## MCP / connector notes

Multiple community MCP servers exist. `blencorp/capture-mcp-server` (MIT) wraps SAM.gov + USASpending + Tango with ~15 tools; `martc03/gov-mcp-servers` ships a gov-contracts server; 1102Tools publishes a SAM.gov MCP covering entities, exclusions, and opportunities. None is official. A connector should expose `search_opportunities`, `get_opportunity_by_notice_id`, and `list_awards`, and must abstract over the mandatory one-year date window and the low daily quota (batch and cache aggressively, surface Retry-After).

## Review notes

Potential new join keys for review:

- Proposed key: `NAICS`
  - Entity type: industry_classification
  - Pattern: `^[0-9]{2,6}$` (2- to 6-digit North American Industry Classification System code)
  - Other datasets that would use it: USASpending.gov, Census County Business Patterns, BLS QCEW, FPDS. High cross-source value; the registry currently has `SIC_UK_2007` but no US NAICS equivalent.

- Proposed key: `UEI_SAM`
  - Entity type: us_registered_entity
  - Pattern: `^[A-Z0-9]{12}$` (12-character SAM Unique Entity Identifier; replaced DUNS in 2022)
  - Other datasets that would use it: USASpending.gov, SAM.gov Entity Management, FPDS. Primary join key for federal awardee entities.

- Proposed keys: `SAM_NOTICE_ID` / `SAM_SOLICITATION_NUMBER` are source-native (kept in `primary_keys`). The solicitation number in particular appears across FPDS and USASpending award records and may warrant promotion to a canonical key if a second entry exposes it.

License: US federal work, treated as `US-Government-Public-Domain` (17 USC 105). No new short name needed.
