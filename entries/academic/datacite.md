---
id: datacite
name: DataCite
domain: academic
description: Global DOI registration agency and metadata graph for research datasets, software, preprints, and other non-article research outputs.
homepage_url: https://datacite.org/
docs_url: https://support.datacite.org/docs/api
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC0
rate_limit: "500 req/5min anon; 1000 req/5min with User-Agent mailto; 3000 req/5min authenticated"
bulk_available: true
frequency: continuous (API); annual snapshot (Public Data File)
lag: "minutes for newly registered DOIs in API; ~1 year for the annual bulk snapshot"
geography: [global]
join_keys:
  - DOI
  - ORCID
  - ROR
  - FUNDER_DOI
  - URL
primary_keys:
  - DOI
  - DATACITE_CLIENT_ID
  - DATACITE_PROVIDER_ID
join_key_fields:
  - join_key: DOI
    fields: [data.attributes.doi, data.attributes.relatedIdentifiers.relatedIdentifier]
  - join_key: ORCID
    fields: [data.attributes.creators.nameIdentifiers.nameIdentifier, data.attributes.contributors.nameIdentifiers.nameIdentifier]
  - join_key: ROR
    fields: [data.attributes.creators.affiliation.affiliationIdentifier, data.attributes.contributors.affiliation.affiliationIdentifier]
  - join_key: FUNDER_DOI
    fields: [data.attributes.fundingReferences.funderIdentifier]
  - join_key: URL
    fields: [data.attributes.url]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/pipeworx-io/mcp-datacite
mcp_notes: >
  Single community MCP (June 2026, 0 stars, experimental). Suggested surface:
  search_dois, get_doi, list_by_client, list_by_funder, list_by_orcid.
  Connector should reconstruct related_identifiers into a navigable graph
  and trim verbose JSON:API envelopes.
agent_use_cases:
  - dataset discovery by DOI
  - research output lookup for an ORCID or ROR
  - funder-to-output mapping via FUNDER_DOI
  - citation graph traversal for non-article outputs
  - DOI metadata enrichment
access_test:
  command: "curl -sf -H 'User-Agent: datasources (you@example.com)' 'https://api.datacite.org/dois/10.14454/3w3z-sa82'"
  expected_status: 200
  expected_fields: [data.id, data.type, data.attributes.doi, data.attributes.creators, data.attributes.titles]
last_verified: 2026-06-08
build_priority: medium
---

# DataCite

## Why this source matters

DataCite is the DOI registration agency for research datasets, software, samples, preprints, and other non-article research outputs (the complement to Crossref, which covers journal articles and books). A global non-profit founded in 2009 and run as a membership organisation of ~3,000 repositories, libraries, and funders, it registers and resolves DOIs and exposes the full metadata graph for free under CC0. For an agent stitching together research provenance, DataCite is the canonical source for "what dataset underlies this paper", funder-to-output mapping, and discovery of grey research outputs that never reach a journal.

## Agent use cases

- dataset discovery by DOI
- research output lookup for an ORCID or ROR
- funder-to-output mapping via FUNDER_DOI
- citation graph traversal for non-article outputs
- DOI metadata enrichment

## Join strategy

DataCite is a `DOI`-native graph. Every record carries the canonical `DOI` and normalises related identifiers across schemes. People are tagged with `ORCID`, affiliations with `ROR`, funders with `FUNDER_DOI` (the Crossref Open Funder Registry subspace). Related works (supplements, derivations, versions) are linked via cross-scheme `relatedIdentifiers` which include DOIs, URLs, and a long tail of source-side schemes (Handle, URN, ARK, IGSN, PMID, arXiv).

DataCite-internal IDs (the DOI prefix, client/repository IDs like `datacite.datacite`, provider IDs) are outside the canonical registry; use them for navigation inside DataCite, not cross-source joins. Pair DataCite with Crossref for the article-side complement, OpenAlex for citation context, and ROR for institution resolution.

## Access notes

**Low-volume agent queries:** REST API at `https://api.datacite.org`, no auth required for the public (Findable-state) DOIs. Always send a `User-Agent` header with a contact email to move from the 500 req/5min anonymous tier to the 1000 req/5min identified tier. JSON:API envelopes are verbose; expect to trim `data.attributes` aggressively.

**Large analyses:** The DataCite Public Data File (annual snapshot, ~58 GB compressed, CC0) is served as TAR.GZ archives of JSON Lines from `https://datafiles.datacite.org/`. The 2025 file was released January 2026 with DOI `10.14454/t5qb-d995`. Use the bulk file for any pull over a few hundred thousand DOIs; the API is rate-limited and pagination across the full corpus is impractical.

Known gotchas:

- Public API returns only Findable-state DOIs. Drafts and Registered-only DOIs require Member API auth.
- The annual bulk file lags by up to a year (good for snapshots, bad for fresh DOIs).
- `relatedIdentifiers` mix schemes; client must dispatch on `relatedIdentifierType`.
- For sustained workloads above 100K req/day DataCite asks operators to contact support.

## MCP / connector notes

One community MCP exists: `github.com/pipeworx-io/mcp-datacite` (created June 2026, 0 stars, experimental). Treat as a starting point, not a stable dependency. A production connector should expose `search_dois`, `get_doi`, `list_by_client`, `list_by_funder`, `list_by_orcid`, reconstruct `relatedIdentifiers` into a navigable graph, trim JSON:API envelopes, and route bulk pulls to the Public Data File rather than paginating the API.

## Review notes

None.
