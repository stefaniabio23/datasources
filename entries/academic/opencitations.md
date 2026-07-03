---
id: opencitations
name: OpenCitations
domain: academic
entry_kind: knowledge-graph
description: Open, CC0 infrastructure for scholarly citation and bibliographic metadata, exposing DOI-to-DOI citation links and document metadata via REST, SPARQL, and bulk dumps.
homepage_url: https://opencitations.net/
docs_url: https://api.opencitations.net/index/v2
type:
  - rest-api
  - bulk-download
  - database
auth_required: none
cost: free
license: CC0
rate_limit: "180 requests/minute per IP; optional access-token header for monitoring"
bulk_available: true
frequency: "periodic releases (several times per year)"
lag: "months; depends on upstream Crossref/DataCite ingestion and release cadence"
geography: [global]
join_keys:
  - DOI
  - PMID
  - ORCID
  - ISSN
  - ISBN
primary_keys:
  - OMID
  - OCI
join_key_fields:
  - join_key: DOI
    fields: [id, citing, cited]
  - join_key: PMID
    fields: [id]
  - join_key: ORCID
    fields: [author]
  - join_key: ISSN
    fields: [id, venue]
  - join_key: ISBN
    fields: [id, venue]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - citation counting
  - citation chasing
  - reference extraction
  - venue impact lookup
  - open-citation-graph traversal
access_test:
  command: "curl -sf 'https://api.opencitations.net/index/v2/citation-count/doi:10.1108/jd-12-2013-0166'"
  expected_status: 200
  expected_fields: [count]
last_verified: 2026-07-02
build_priority: low
---

# OpenCitations

## Why this source matters

OpenCitations is a community-guided open infrastructure run by the Research Centre for Open Scholarly Metadata at the University of Bologna, established 2010 as a free CC0 alternative to proprietary citation services (Web of Science, Scopus). It publishes two complementary layers: the OpenCitations Index (DOI-to-DOI citation links harvested from Crossref, DataCite, and other sources, unified under a single v2 API) and OpenCitations Meta (bibliographic metadata: titles, authors, venues, dates for the documents involved in those citations). Everything is CC0 public domain, freely reusable including commercially. For an agent, it is the open citation graph, use it when you need who-cites-whom edges rather than the richer per-work metadata graph of OpenAlex.

## Agent use cases

- citation counting
- citation chasing
- reference extraction
- venue impact lookup
- open-citation-graph traversal

## Join strategy

OpenCitations is DOI-native: both the Index and Meta APIs accept and return `DOI` as the primary lookup key, with `PMID` also queryable (and `ISSN` for venue-level citation counts). OpenCitations Meta additionally resolves `ORCID` for authors and `ISSN`/`ISBN` for venues. Identifiers come back prefixed and space-joined inside the `id` field (e.g. `doi:10.1108/... pmid:... omid:...`); Index citation objects expose `citing` and `cited` identifier lists.

Two source-native identifiers sit outside the canonical registry and go in `primary_keys`: `OMID` (OpenCitations Meta Identifier, e.g. `br/0601`, the persistent internal id for every entity) and `OCI` (Open Citation Identifier, e.g. `oci:...`, a persistent id for a single citation edge). Use these for direct OpenCitations lookups, not cross-source joins. See Review notes, OMID is a candidate future canonical key.

Pair with OpenAlex or Crossref for richer per-work metadata, with Europe PMC for OA full text, and use the shared `DOI` as the hub key.

## Access notes

Hit the unified Index v2 API first: `https://api.opencitations.net/index/v2/citations/doi:<DOI>` for incoming citations, `/references/doi:<DOI>` for outgoing, `/citation-count/doi:<DOI>` and `/reference-count/doi:<DOI>` for counts, `/venue-citation-count/issn:<ISSN>` for venue totals. Meta metadata lives under `https://api.opencitations.net/meta/v1/metadata/doi:<DOI>`. No auth required; an optional opaque `access-token` header lets OpenCitations track unique users. Rate limit is 180 req/min per IP. Responses are JSON by default or CSV via the `Accept` header. The REST layer is RAMOSE over SPARQL endpoints; for large graph traversals use the bulk CC0 dumps at download.opencitations.net or query the SPARQL endpoints directly rather than paginating the API.

## MCP / connector notes

No MCP found on the modelcontextprotocol org, npm, or PyPI as of last check. Narrow audience (citation-graph specialists) so low build priority; the REST API is clean and well-documented, so `api-direct-sufficient` is nearly true. A thin connector would expose `get_citations`, `get_references`, `citation_count`, `venue_citation_count`, and a Meta `get_metadata`, abstracting over the DOI/PMID/OMID prefix syntax and the space-joined `id` field, and routing large pulls to the bulk dumps.

## Review notes

Potential new join key for review: OMID
  Entity type: scholarly_work (also authors, venues; OpenCitations Meta entity)
  Pattern: `^(br|ra|re|id|ar)/[0-9]+$` (entity-type abbreviation + supplier prefix + sequential number; prefixed `omid:` in API payloads)
  Other datasets that would use it: currently OpenCitations-only (Index + Meta); include only if a second source adopts OMID.

OCI (Open Citation Identifier) is left in `primary_keys` rather than proposed as a canonical key: it identifies a citation edge, not a bibliographic entity, so it has no natural cross-source join semantics.

License nuance: datasets are CC0; website prose is CC-BY-4.0 and OpenCitations software is ISC-licensed. The `license: CC0` field reflects the data, which is what this registry cares about.
