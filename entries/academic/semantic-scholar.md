---
id: semantic-scholar
name: Semantic Scholar
domain: academic
description: Ai2's scholarly knowledge graph covering 214M papers, 79M authors, and 2.49B citations across all disciplines, with paper-recommendation and bulk-snapshot endpoints.
homepage_url: https://www.semanticscholar.org/product/api
docs_url: https://api.semanticscholar.org/api-docs/
type:
  - rest-api
  - bulk-download
auth_required: api-key-free
cost: free-non-commercial
license: CC-BY-NC-4.0
rate_limit: "1000 req/sec shared across all anonymous users; 1 req/sec per API key (request via form, raised on review)"
bulk_available: true
frequency: weekly
lag: "weeks for newly indexed works; citation counts trail publication"
geography: [global]
join_keys:
  - DOI
  - PMID
  - PMCID
  - ARXIV_ID
primary_keys:
  - SEMANTIC_SCHOLAR_PAPER_ID
  - SEMANTIC_SCHOLAR_CORPUS_ID
  - SEMANTIC_SCHOLAR_AUTHOR_ID
join_key_fields:
  - join_key: DOI
    fields: [externalIds.DOI]
  - join_key: PMID
    fields: [externalIds.PubMed]
  - join_key: PMCID
    fields: [externalIds.PubMedCentral]
  - join_key: ARXIV_ID
    fields: [externalIds.ArXiv]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/akapet00/semantic-scholar-mcp
  - github.com/smaniches/semantic-scholar-mcp
  - github.com/FujishigeTemma/semantic-scholar-mcp
mcp_notes: >
  Multiple community MCPs exist; none official. Most wrap the Graph API's
  paper search / details / citations endpoints. Coverage of the
  Recommendations and Datasets APIs is thinner.
agent_use_cases:
  - literature search
  - citation chasing
  - paper recommendations
  - influential-citation ranking
  - tldr summary retrieval
access_test:
  command: "curl -sf 'https://api.semanticscholar.org/graph/v1/paper/DOI:10.1038/s41586-020-2649-2?fields=title,year,authors,externalIds,citationCount'"
  expected_status: 200
  expected_fields: [paperId, externalIds, title, year, citationCount, authors]
last_verified: 2026-06-08
build_priority: medium
notes: "Data is licensed CC BY-NC; commercial use is restricted. Verify license fit before agent workflows that produce paid outputs."
---

# Semantic Scholar

## Why this source matters

Scholarly graph built by Ai2 (Allen Institute for AI) covering ~214M papers, ~79M authors, and ~2.49B citations across every discipline. Three surfaces: the Academic Graph API (paper / author / citation / venue lookup), the Recommendations API (papers similar to a given seed), and the Datasets API (S2AG and S2ORC bulk snapshots). Distinctive features versus OpenAlex and Crossref are influential-citation counts, machine-generated tldr summaries, and embedding-based recommendations, all of which are computed in-house by Ai2.

## Agent use cases

- literature search
- citation chasing
- paper recommendations
- influential-citation ranking
- tldr summary retrieval

## Join strategy

Semantic Scholar normalises the major external identifiers and exposes them in `externalIds`: `DOI`, `PMID` (as `PubMed`), `PMCID` (as `PubMedCentral`), `ARXIV_ID` (as `ArXiv`). It also carries Microsoft Academic Graph (MAG) and DBLP IDs, plus its own `CorpusId` and `paperId` (40-char hex). Those Semantic-Scholar-internal IDs are intentionally outside the canonical registry; use them for direct Semantic Scholar lookups, not cross-source joins.

Lookup-by-identifier works via prefixed paths, e.g. `/graph/v1/paper/DOI:10.1038/s41586-020-2649-2`, `/graph/v1/paper/ARXIV:2106.15928`, `/graph/v1/paper/PMID:32939066`. Pair with OpenAlex when you need ROR / ORCID-level institution and author disambiguation, with Crossref when you need authoritative DOI registration metadata, with Europe PMC when you need full-text OA biomedical articles.

## Access notes

**Anonymous use:** No key required. The pool of unauthenticated callers shares 1000 req/sec globally, so individual workloads see frequent throttling at peak hours.

**API key (recommended):** Apply via the form linked from the product page. Default rate is 1 req/sec per key on introduction; Ai2 raises it on request for production workloads. Pass as the `x-api-key` header.

**Bulk snapshots:** The Datasets API exposes weekly S2AG releases (paper / author / citation / abstract files) and S2ORC (full-text NLP corpus). Both ship as gzipped JSON-lines, multi-GB per file, retrieved via signed S3 URLs after authenticating to the Datasets endpoint with an API key.

Known gotchas:

- `fields` parameter must be supplied to retrieve anything beyond `paperId`. Default response is minimal.
- The published 1 req/sec key limit is the introductory ceiling; higher tiers exist but require email contact with Ai2.
- The legacy `api.semanticscholar.org/v1/paper/` route still works but is unsupported; prefer `/graph/v1/`.
- `tldr` field is populated only for papers in their SciTLDR coverage; expect frequent nulls outside CS / biomed.

## MCP / connector notes

Several community MCPs exist (e.g. `akapet00/semantic-scholar-mcp` with ~22 stars wrapping search and analysis, `smaniches/semantic-scholar-mcp` with 14 tools including citation-graph traversal). None are official Ai2 releases, and coverage skews toward the Academic Graph endpoints; Recommendations and Datasets APIs are under-served. A consolidated connector should expose `search_papers`, `get_paper`, `get_paper_citations`, `get_paper_references`, `get_author`, `get_recommendations`, with `fields` defaulting to a sensible bundle and bulk-snapshot routing for large pulls.

## Review notes

License nuance: Semantic Scholar API data is licensed CC BY-NC (with some components under ODC-BY), which is more restrictive than OpenAlex (CC0) and Crossref (CC0). Flag for downstream agents whether any commercial use is in scope before recommending Semantic Scholar over OpenAlex for the same query. The current SPDX value `CC-BY-NC-4.0` is the closest fit; if a more granular license expression is needed, propose extending the license vocabulary.
