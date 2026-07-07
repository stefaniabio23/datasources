---
id: ror
name: ROR (Research Organization Registry)
domain: academic
entry_kind: registry
description: Global community-led registry of open persistent identifiers and metadata for research and funding organizations.
homepage_url: https://ror.org/
docs_url: https://ror.readme.io/docs/rest-api
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC0
rate_limit: "2000 req / 5 min per IP; from Q3 2026 unregistered clients drop to 50 req / 5 min (client ID keeps the standard limit)"
bulk_available: true
frequency: "at least monthly (community curation releases)"
lag: "days-to-weeks between org change request and published release"
geography: [global]
join_keys:
  - ROR
  - ISNI
  - WIKIDATA_QID
  - FUNDER_DOI
primary_keys:
  - ROR_ID
join_key_fields:
  - join_key: ROR
    fields: [id]
  - join_key: ISNI
    fields:
      - "external_ids[type=isni].all"
      - "external_ids[type=isni].preferred"
  - join_key: WIKIDATA_QID
    fields:
      - "external_ids[type=wikidata].all"
      - "external_ids[type=wikidata].preferred"
  - join_key: FUNDER_DOI
    fields:
      - "external_ids[type=fundref].preferred"
      - "external_ids[type=fundref].all"
mcp_status: mcp-needed-low-value
agent_use_cases:
  - institution name resolution
  - affiliation disambiguation
  - cross-registry id crosswalk
  - funder-to-org linking
  - org hierarchy lookup
access_test:
  command: "curl -sf 'https://api.ror.org/v2/organizations/https://ror.org/013cjyk83'"
  expected_status: 200
  expected_fields: [id, names, external_ids, locations, types]
last_verified: 2026-07-07
build_priority: medium
---

# ROR (Research Organization Registry)

## Why this source matters

ROR is a global, community-led registry of open persistent identifiers for research and funding organizations, launched in 2019 by California Digital Library, Crossref, and DataCite. Each record carries a stable ROR ID (a 9-character string behind a `https://ror.org/` URL) plus names, locations, org types, hierarchical relationships, and a crosswalk of external identifiers (ISNI, Wikidata, GRID, Crossref Funder ID). All IDs and metadata are CC0. Because OpenAlex, Crossref, DataCite, and most scholarly-metadata pipelines have adopted ROR as the canonical institution identifier, ROR is the authoritative resolver for turning a messy affiliation string into a single joinable institution ID. Secondary relevance to funding data: the registry now covers funding organizations and links them to their Crossref Funder Registry IDs.

## Agent use cases

- institution name resolution
- affiliation disambiguation
- cross-registry id crosswalk
- funder-to-org linking
- org hierarchy lookup

## Join strategy

ROR mints the canonical `ROR` id (in `primary_keys` and `join_keys`, since it is the registry of record) and exposes it in the `id` field as a full URL; strip the `https://ror.org/` prefix to get the bare 9-char key other sources store. For cross-source joining, each record's `external_ids` array carries `ISNI` and `WIKIDATA_QID` directly. `FUNDER_DOI` is also present but ROR stores only the numeric FundRef part (e.g. `501100009517`); prepend `10.13039/` to reconstruct the canonical Crossref Funder DOI (`10.13039/501100009517`) before joining. Organization name (with language-tagged variants and acronyms in `names[]`) is the lookup handle, not a join key.

ROR is the recommended hub for institution joins: pair with OpenAlex (`authorships.institutions.ror`) for scholarly output, Crossref for DOI-level affiliation, and the Crossref Funder Registry for grant/funder linkage. GRID is also carried in `external_ids` but has no canonical key in the registry (see Review notes); GRID froze in 2021 and ROR is its successor, so GRID is a legacy crosswalk only.

## Access notes

REST API at `https://api.ror.org/`, no auth today. Current version is v2: single-record fetch is `GET https://api.ror.org/v2/organizations/{ror_id}` (the tested URL passes the full `https://ror.org/<id>` form); affiliation matching via `GET /v2/organizations?affiliation=<string>` returns ranked candidates with match confidence, the right entry point for resolving raw affiliation text. Rate limit is 2000 requests per 5 minutes per IP; from Q3 2026 unregistered clients are throttled to 50 per 5 minutes and a free client ID restores the standard limit, so wire a client-ID header in before that cutover. For bulk work, use the versioned data dump on Zenodo (full registry as JSON + CSV, refreshed at least monthly) rather than paginating the API. Queries return every field and sub-field regardless of whether it has a value, so expect nulls in `external_ids[].preferred`.

## MCP / connector notes

No dedicated ROR MCP found on the official or community registries as of 2026-07-07. The API is small, clean, and unauthenticated, so an MCP adds limited value over direct calls; marked low-value. A minimal connector surface would be `resolve_affiliation(string)` (wrapping the `affiliation` matcher and returning the top ROR ID + confidence), `get_organization(ror_id)`, `search_organizations(query, filters)`, and `crosswalk_ids(ror_id)` to emit the ISNI / Wikidata / FundRef / GRID mappings. The main thing to abstract is the affiliation matcher's ranked-candidate shape and the FundRef-to-FUNDER_DOI prefix reconstruction.

## Review notes

Potential new join key for review: GRID_ID
  Entity type: institution
  Pattern: ^grid\.[0-9]+\.[0-9a-f]+$  (e.g. grid.440907.e)
  Other datasets that would use it: legacy scholarly-metadata dumps, Dimensions, pre-2022 OpenAlex/Crossref snapshots. GRID was retired in 2021 and superseded by ROR, so value is as a historical crosswalk only; may not be worth adding.

Note on FUNDER_DOI: ROR stores the FundRef identifier as a bare number (`external_ids[type=fundref]`), not the full `10.13039/<n>` DOI form the canonical `FUNDER_DOI` key expects. Mapped it to `FUNDER_DOI` with a prefix-reconstruction note; confirm this transform is acceptable for the join-graph or whether the numeric FundRef form should be treated separately.
