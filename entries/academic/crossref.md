---
id: crossref
name: Crossref
domain: academic
entry_kind: registry
description: DOI registration agency and open metadata API for scholarly works, covering ~180M records deposited by member publishers across journals, books, conference proceedings, preprints, and datasets.
homepage_url: https://www.crossref.org/
docs_url: https://api.crossref.org/swagger-ui/index.html
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC0
rate_limit: "no hard published limit; polite pool via ?mailto= or User-Agent with mailto returns higher-priority routing. Limits announced dynamically in X-Rate-Limit-Limit / X-Rate-Limit-Interval response headers."
bulk_available: true
frequency: "continuous (REST API); annual public data file snapshot"
lag: "minutes to hours for new DOI deposits; abstracts and references depend on publisher submission"
geography: [global]
join_keys:
  - DOI
  - ISSN
  - ORCID
  - ROR
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/JackKuo666/Crossref-MCP-Server
  - github.com/botanicastudios/crossref-mcp
  - github.com/h-lu/crossref-cite-mcp
mcp_notes: >
  Three community MCPs exist plus several multi-source scholarly servers that embed Crossref
  (afrise/Academic-Search-MCP-Server, Seelly/Scholar-MCP-Server, lstudlo/ScholarMCP). None
  are official. A consolidated MCP should expose works_search, get_work_by_doi, get_references,
  get_citations_via_oc, list_funders, and route bulk needs to the annual public data file.
agent_use_cases:
  - DOI metadata lookup
  - reference list extraction
  - funder and grant attribution
  - journal coverage checks
  - DOI minting authority verification
access_test:
  command: "curl -sf -H 'User-Agent: datasources/0.1 (mailto:${CROSSREF_MAILTO})' 'https://api.crossref.org/works/10.1038/s41586-020-2649-2'"
  expected_status: 200
  expected_fields: [status, message-type, message]
last_verified: 2026-06-08
build_priority: medium
---

# Crossref

## Why this source matters

Crossref is the largest DOI registration agency for scholarly publishing and the upstream authority for most paper-level metadata that downstream sources (OpenAlex, Europe PMC, Semantic Scholar) re-index. Run by a not-for-profit membership organisation of ~20K publishers and societies, it exposes deposited metadata (titles, authors, affiliations, references, funders, licenses, abstracts where supplied) under CC0 via a free no-auth REST API plus an annual ~208 GB JSON-Lines public data file. For any agent that needs the authoritative record behind a DOI (publisher, license terms, reference list, funder IDs), Crossref is the source rather than the cache.

## Agent use cases

- DOI metadata lookup
- reference list extraction
- funder and grant attribution
- journal coverage checks
- DOI minting authority verification

## Join strategy

Crossref is DOI-native and normalises identifiers contributed by depositing publishers: `DOI` (primary key), `ISSN` (and ISBN, which is not yet a canonical key in the registry) for venues, `ORCID` for authors when supplied, and `ROR` for institutional affiliations and funders. Funder IDs use Crossref's internal Funder Registry ID (Open Funder Registry, not a canonical key here). Pair with OpenAlex for citation graph and concept tagging, Europe PMC for full-text OA biomedical content, and ClinicalTrials.gov via DOI cross-references when trials cite publications.

## Access notes

Start at `https://api.crossref.org/works/{doi}` for single-record lookups and `https://api.crossref.org/works?query=...&rows=20` for search. No API key, but always send `User-Agent: appname/version (mailto:you@example.com)` or `?mailto=` to enter the polite pool — anonymous requests get throttled first during incidents. Pagination uses `cursor=*` (deep paging beyond 10K results requires the cursor, not `offset`). Rate limits are announced in `X-Rate-Limit-Limit` and `X-Rate-Limit-Interval` headers and adjusted dynamically; respect them rather than assuming a fixed ceiling. For anything over a few hundred thousand records, switch to the annual public data file (208 GB, JSON-Lines, distributed via direct download and Academic Torrents) instead of paginating. Most metadata is CC0; some abstracts may retain publisher copyright.

## MCP / connector notes

Three single-source community MCPs exist (`JackKuo666/Crossref-MCP-Server` Python, `botanicastudios/crossref-mcp` JS, `h-lu/crossref-cite-mcp` for citations) plus several multi-source academic MCPs that wrap Crossref alongside Semantic Scholar, arXiv, ADS, and Scopus. None are official, none are clearly canonical, and they appear early-to-mid stage. A consolidated MCP should expose `works_search`, `get_work_by_doi`, `get_references`, `get_citations_via_opencitations`, and `list_funders`, abstract the cursor pagination, set the polite-pool mailto from env, and route bulk requests to the annual public data file rather than hammering the REST endpoint.

## Review notes

- Potential new join key for review: `ISBN`
  Entity type: scholarly_work (book or book chapter)
  Pattern: `^(97[89])?[0-9]{9}[0-9X]$` (ISBN-10 or ISBN-13)
  Other datasets that would use it: OpenAlex, Google Books, OpenLibrary, WorldCat, library catalogues. Crossref deposits ISBNs for book and chapter DOIs.
- Potential new join key for review: `FUNDER_DOI` (Open Funder Registry ID, e.g. `10.13039/100000001` for NSF)
  Entity type: funding_organisation
  Pattern: `^10\\.13039/[0-9]+$` (subset of DOI but semantically distinct)
  Other datasets that would use it: any source that records grant attribution (NIH RePORTER, OpenAlex funders, Dimensions). Could also be modelled as a DOI sub-type rather than a separate key.
