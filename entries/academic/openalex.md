---
id: openalex
name: OpenAlex
domain: academic
entry_kind: knowledge-graph
description: Open scholarly knowledge graph covering papers, authors, institutions, concepts, topics, and citations across all of academia.
homepage_url: https://openalex.org/
docs_url: https://docs.openalex.org/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC0
rate_limit: "10 req/sec anon; 100K req/day with polite pool (add ?mailto=)"
bulk_available: true
frequency: daily
lag: "days-to-weeks for newly published works to be indexed"
geography: [global]
join_keys:
  - DOI
  - PMID
  - PMCID
  - ARXIV_ID
  - ORCID
  - ROR
  - ISSN
  - WIKIDATA_QID
  - MAG_ID
primary_keys:
  - OPENALEX_WORK_ID
  - OPENALEX_AUTHOR_ID
  - OPENALEX_INSTITUTION_ID
  - OPENALEX_SOURCE_ID
join_key_fields:
  - join_key: DOI
    fields: [doi, ids.doi]
  - join_key: PMID
    fields: [ids.pmid]
  - join_key: PMCID
    fields: [ids.pmcid]
  - join_key: ARXIV_ID
    fields: [ids.arxiv]
  - join_key: ORCID
    fields: [authorships.author.orcid]
  - join_key: ROR
    fields: [authorships.institutions.ror]
  - join_key: ISSN
    fields: [primary_location.source.issn, primary_location.source.issn_l]
  - join_key: WIKIDATA_QID
    fields: [ids.wikidata]
  - join_key: MAG_ID
    fields: [ids.mag]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "openalex-research-mcp (npm)"
  - "@futurelab-studio/latest-science-mcp (npm)"
mcp_command:
  - "npx -y openalex-research-mcp (set OPENALEX_EMAIL)"
  - "npx -y @futurelab-studio/latest-science-mcp@latest"
mcp_notes: >
  Broad use case, stable API, verbose response shape. Suggested surface: search_works,
  get_work, get_citations, disambiguate_author, get_concepts_for_topic.
agent_use_cases:
  - literature search
  - citation chasing
  - author disambiguation
  - institution lookup
  - concept-tagged retrieval
access_test:
  command: "curl -sf 'https://api.openalex.org/works/W2741809807'"
  expected_status: 200
  expected_fields: [id, doi, title, authorships, cited_by_count]
last_verified: 2026-06-08
build_priority: high
---

# OpenAlex

## Why this source matters

Scholarly knowledge graph of ~250M works, ~100M authors, ~100k institutions, ~250k concepts/topics. CC0, REST API + bulk Parquet snapshot. The cleanest free substitute for paid scholarly graphs (Web of Science, Scopus); one API call covers literature reviews, citation-chasing, author disambiguation, institution lookups, concept-tagged retrieval.

## Agent use cases

- literature search
- citation chasing
- author disambiguation
- institution lookup
- concept-tagged retrieval

## Join strategy

OpenAlex deliberately normalises every external identifier it can find: `DOI`, `PMID`, `PMCID`, `ARXIV_ID` for papers; `ORCID` for people; `ROR` for institutions; `ISSN` for venues; `WIKIDATA_QID` for cross-domain.

OpenAlex-internal IDs (`OPENALEX_WORK_ID`, `OPENALEX_AUTHOR_ID`, `OPENALEX_INSTITUTION_ID`) are intentionally outside the canonical registry; use them for direct OpenAlex lookups, not cross-source joins.

That cross-mapping makes OpenAlex the recommended hub for any agent stitching scholarly sources together. Pair with Europe PMC for full-text OA biomedical articles, Crossref for DOI metadata authority, Semantic Scholar for citation-context snippets.

## Access notes

**Low-volume agent queries:** REST API, no auth. Add `?mailto=you@example.com` to enter the polite pool (same 10 req/sec but 100K calls/day quota + priority during incidents).

**Large analyses:** Bulk snapshot from `s3://openalex` (~330 GB Parquet, monthly refresh). Faster than paginating the API for anything over a few hundred thousand works.

Known gotchas:

- Abstracts stored as inverted indexes in `abstract_inverted_index`, not raw text. Reconstruct client-side.
- Concept tagging quality varies. High-score concepts (>0.5) are reliable; long-tail tags are noisy.
- Citation counts lag publication by weeks-to-months.
- Polite-pool routing only kicks in once your mailto is recognised; new emails take ~24h.

## MCP / connector notes

No official MCP. Broad use case, stable API, verbose response shape. Connector should expose `search_works`, `get_work`, `get_citations`, `disambiguate_author`, `get_concepts_for_topic`, with response trimming, query budget tracking, and bulk-vs-API routing for large pulls.

## Review notes

None.
