---
id: orcid
name: ORCID
domain: academic
description: Global registry of persistent researcher identifiers linking people to their works, affiliations, funding, and peer review activity.
homepage_url: https://orcid.org/
docs_url: https://info.orcid.org/documentation/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC0
rate_limit: "anon: 12 req/sec, 40 burst, 25K reads/day per IP; public-registered: 100K reads/day per client_id"
bulk_available: true
frequency: annual
lag: "real-time API; annual public data file"
geography: [global]
join_keys:
  - ORCID
  - DOI
  - ROR
  - WIKIDATA_QID
primary_keys:
  - ORCID
  - ORCID_PUT_CODE
join_key_fields:
  - join_key: ORCID
    fields: [orcid-identifier.path, orcid-identifier.uri]
  - join_key: DOI
    fields: [activities-summary.works.group.external-ids.external-id.external-id-value, activities-summary.works.group.work-summary.external-ids.external-id.external-id-value]
  - join_key: ROR
    fields: [activities-summary.employments.affiliation-group.summaries.employment-summary.organization.disambiguated-organization.disambiguated-organization-identifier, activities-summary.educations.affiliation-group.summaries.education-summary.organization.disambiguated-organization.disambiguated-organization-identifier]
  - join_key: WIKIDATA_QID
    fields: [person.external-identifiers.external-identifier.external-id-value]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cyanheads/orcid-mcp-server
  - github.com/pipeworx-io/mcp-orcid
  - github.com/Epistemic-Technology/orcid-mcp
  - github.com/dmachi/orcid-mcp
  - github.com/QuentinCody/scholarly-graph-mcp-server
mcp_notes: >
  Multiple community MCP servers exist (TypeScript-heavy). None are official. Suggested
  surface: search_researchers, get_record, get_works, get_employments, get_fundings,
  resolve_orcid_to_works.
agent_use_cases:
  - author disambiguation
  - researcher profile lookup
  - affiliation history retrieval
  - cross-source identity stitching
  - works-by-researcher enumeration
access_test:
  command: "curl -sf -H 'Accept: application/json' 'https://pub.orcid.org/v3.0/0000-0002-1825-0097/record'"
  expected_status: 200
  expected_fields: [orcid-identifier, person, activities-summary, history]
last_verified: 2026-06-08
build_priority: medium
notes: "ISNI is exposed as an external identifier on ORCID records but ISNI is not yet a canonical join key in schema/join-keys.yaml; flagged in Review notes."
---

# ORCID

## Why this source matters

ORCID (Open Researcher and Contributor ID) is a global non-profit that issues a persistent 16-digit identifier per researcher and curates the registry that maps each ID to the researcher's works, employments, educations, fundings, peer reviews, and external identifiers (DOI, ROR, ISNI, Scopus Author ID, ResearcherID). Funded by member fees from universities, publishers, and funders. Public data is released under CC0 via both a real-time REST API and an annual bulk public data file. For any agent doing author disambiguation or stitching scholarly identities across sources (OpenAlex, Crossref, PubMed), ORCID is the authoritative person-side anchor.

## Agent use cases

- author disambiguation
- researcher profile lookup
- affiliation history retrieval
- cross-source identity stitching
- works-by-researcher enumeration

## Join strategy

ORCID is itself a canonical join key (`ORCID`) and is the primary reason this source exists. Per researcher record it also exposes `DOI` (per work in `activities-summary.works`), `ROR` (per employment/education affiliation, when the institution is ROR-disambiguated), and `WIKIDATA_QID` (when the researcher has added Wikidata as an external identifier). Many records also carry an ISNI under `external-identifiers`, which is the natural author-side bridge to library and publisher metadata, but ISNI is not yet in the canonical registry (see Review notes).

Source-internal identifiers (work `put-code`, employment `put-code`) are only valid for further ORCID API calls against the same record and should not be used for cross-source joins.

Pair with OpenAlex for the works graph (OpenAlex normalises ORCID on authorships), with Crossref for DOI-level metadata authority, and with ROR for institution disambiguation.

## Access notes

**Anonymous Public API:** No auth, no registration. Base URL `https://pub.orcid.org/v3.0/`. Fetch a record with `GET /{orcid}/record`. Returns JSON with `Accept: application/json` or XML by default. Limited to 12 req/sec (40 burst) and 25K reads/day per IP.

**Registered Public API:** Free OAuth client_credentials token (`/read-public` scope) raises daily quota to 100K reads per client_id and enables search endpoints (`/search/`, `/expanded-search/`). Search returns only ORCID iDs (or expanded fields like name + affiliation); follow up with `/record` calls per iD.

**Bulk:** Annual ORCID Public Data File (CC0) is released on Figshare each October as a tarball of XML/JSON summaries plus activities. Also mirrored on Google BigQuery for query-time access. Use the dump rather than the API for analyses over more than a few thousand researchers.

**Sandbox:** `https://pub.sandbox.orcid.org/v3.0/` for development. Production iDs do not exist in sandbox.

Privacy gotcha: ORCID records have per-field visibility (`public` / `limited` / `private`). The Public API and the Public Data File only ever return `public` fields. A researcher's full work list via API may legitimately be smaller than what appears on their UI profile when logged in.

## MCP / connector notes

Multiple community MCP servers exist (`cyanheads/orcid-mcp-server`, `pipeworx-io/mcp-orcid`, `Epistemic-Technology/orcid-mcp`, `dmachi/orcid-mcp`, plus `QuentinCody/scholarly-graph-mcp-server` which bundles ORCID with OpenAlex / Crossref / ROR / OpenAIRE). No official MCP from ORCID itself. Coverage varies: most expose record fetch and works enumeration; fewer expose `/search/` or `/expanded-search/`, fundings, or peer reviews. A consolidated connector should expose `search_researchers`, `get_record`, `get_works`, `get_employments`, `get_fundings`, `resolve_orcid_to_works`, and abstract over the public-vs-member API distinction (most agent use cases never need member-tier writes).

## Review notes

Potential new join key for review: ISNI
  Entity type: person (and organisation; ISNI covers both)
  Pattern: `^[0-9]{4} [0-9]{4} [0-9]{4} [0-9]{3}[0-9X]$` (16 digits, space-grouped; some sources strip spaces)
  Other datasets that would use it: VIAF, Library of Congress NAF, BnF, ORCID (external-identifiers), Crossref author records, Wikidata (P213).
