---
id: ukri-gtr
name: UKRI Gateway to Research (GtR)
domain: government-open-data
entry_kind: knowledge-graph
description: UK Research and Innovation's registry of publicly funded research projects, linked to funding, people, organisations, and outcomes.
homepage_url: https://gtr.ukri.org/
docs_url: https://gtr.ukri.org/resources/api.html
type:
  - rest-api
auth_required: none
cost: free
license: OGL-3.0
rate_limit: "no formal limit; UKRI asks users to follow web etiquette and not flood the service"
bulk_available: false
frequency: periodic (data refreshed roughly monthly)
geography: [GBR]
structure: registry-snapshot
join_keys:
  - ORCID
primary_keys:
  - GTR_PROJECT_ID
  - GTR_PERSON_ID
  - GTR_ORGANISATION_ID
  - GTR_FUND_ID
  - GTR_OUTCOME_ID
  - RCUK_GRANT_REFERENCE
join_key_fields:
  - join_key: ORCID
    fields: [orcidId]
mcp_status: api-direct-sufficient
agent_use_cases:
  - uk research funding lookup
  - grant-to-institution mapping
  - principal-investigator project history
  - funder portfolio analysis
  - research-outcome tracing
access_test:
  command: "curl -sf -H 'Accept: application/vnd.rcuk.gtr.json-v7' 'https://gtr.ukri.org/gtr/api/projects?q=graphene&p=1&s=10'"
  expected_status: 200
  expected_fields: [page, size, totalSize, project]
last_verified: 2026-07-07
build_priority: medium
---

# UKRI Gateway to Research (GtR)

## Why this source matters

Gateway to Research is UK Research and Innovation's public portal for data on UK publicly funded research. It links five entity types, projects, people, organisations, funds, and outcomes, into a navigable graph: which grant funded which project, run by which principal investigator at which lead organisation, producing which publications and other outcomes. It is the authoritative source for UK research council and Innovate UK grant funding, covering the seven research councils, Innovate UK, and Research England. As a research-funding registry it sits in `government-open-data`; its graph shape and cross-links to ORCID and scholarly outputs give it strong secondary relevance to the `academic` domain.

## Agent use cases

- uk research funding lookup
- grant-to-institution mapping
- principal-investigator project history
- funder portfolio analysis
- research-outcome tracing

## Join strategy

The only canonical join key GtR natively exposes is `ORCID`, carried on person records in the `orcidId` field (populated for a minority of researchers; treat as sparse). Everything else is source-internal: every entity carries a GtR UUID (`GTR_PROJECT_ID`, `GTR_PERSON_ID`, `GTR_ORGANISATION_ID`, `GTR_FUND_ID`, `GTR_OUTCOME_ID`), and projects carry an RCUK grant reference number under `identifiers` (type `RCUK`, e.g. `132259`), captured here as `RCUK_GRANT_REFERENCE`. Relationships between entities are expressed as typed `links` (e.g. `PI_PER`, `LEAD_ORG`, `PUBLICATION`, `PARTICIPANT_ORG`) that resolve by UUID.

GtR does NOT emit `ROR` for organisations; org records give only the GtR UUID, `name`, `website`, `regNumber`, and addresses. Joining GtR institutions to ROR (or an org's `regNumber` to `COMPANIES_HOUSE_NUMBER` for company participants) requires an external name/registration-number resolver. See Review notes.

To enrich UK research intelligence, pair GtR with OpenAlex or ORCID (author identity), Crossref/OpenAlex (publication outcomes named in GtR by title/DOI-in-text), and a ROR resolver for institution normalisation.

## Access notes

Two REST APIs sit behind the same data. GtR-2 (base `https://gtr.ukri.org/gtr/api/`) is the recommended interface: version-pinned, UI-independent, and content-negotiated. Request JSON with an Accept header, `Accept: application/vnd.rcuk.gtr.json-v7` (v7 is current; XML via `...xml-v7`). Without an Accept header the API defaults to the oldest supported XML version.

Endpoints: `/projects`, `/persons`, `/organisations`, `/funds`, `/outcomes`, each supporting a full-text `q` parameter and page-based pagination via `p` (page) and `s` (size, 10-100, default 20). Single records fetch by UUID (e.g. `/gtr/api/projects/{uuid}`). Responses carry `totalPages` / `totalSize` for pagination planning. No authentication, no API key. No official bulk dump; large pulls mean paginating politely.

## MCP / connector notes

No MCP server found (only community R wrappers exist: `MatthewSmith430/GtR`, `shanej90/gtR`). The API is clean, unauthenticated, paginated JSON, so direct API use is sufficient for most agents. A thin connector, if built, would expose `search_projects`, `get_project`, `get_organisation`, `get_person`, `get_outcomes_for_project`, abstract over the Accept-header version negotiation (easy to forget, and the XML default surprises callers), and follow typed `links` to hydrate related entities in one call.

## Review notes

- ROR is not natively exposed by GtR despite being a requested join target; organisations resolve only to GtR UUID + name + `regNumber`. Flagging rather than asserting a `ROR` join_key the source does not carry.
- Potential join via existing canonical key: organisation `regNumber` for UK company participants often equals the Companies House company number (`COMPANIES_HOUSE_NUMBER`), but the field is unlabelled and mixes charity/company registration schemes, so it is not asserted as a join_key here.
- Potential new join key for review: RCUK_GRANT_REFERENCE
    Entity type: research_grant / funded_project
    Pattern: short numeric or alphanumeric grant reference (e.g. `132259`, `EP/L016087/1`); GtR emits it under project `identifiers` with type `RCUK`.
    Other datasets that would use it: UKRI/research-council award data, Crossref funder-linked grant metadata, institutional CRIS systems. Currently held only in `primary_keys`.
- License is OGL-3.0 (Open Government Licence v3), an established canonical short name already used in this registry; UKRI Terms of Use and Privacy Notice govern personal data (researcher names/emails) that appear in person records.
