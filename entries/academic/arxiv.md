---
id: arxiv
name: arXiv
domain: academic
entry_kind: corpus
description: Open-access preprint repository for physics, math, CS, quantitative biology, finance, statistics, EE, and economics, with a public metadata API and bulk full-text mirrors.
homepage_url: https://arxiv.org/
docs_url: https://info.arxiv.org/help/api/user-manual.html
type:
  - rest-api
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: CC0
rate_limit: "3 sec between requests, or bursts of 4 req/sec with a 1 sec sleep; max 2000 results/request, 30000 results total via pagination"
bulk_available: true
frequency: daily
lag: "hours to ~1 day from submission to indexing; OAI-PMH and S3 mirrors lag 1-2 days"
geography: [global]
join_keys:
  - ARXIV_ID
  - DOI
primary_keys:
  - ARXIV_ID
join_key_fields:
  - join_key: ARXIV_ID
    fields: [entry.id]
  - join_key: DOI
    fields: [entry.arxiv:doi]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/blazickjp/arxiv-mcp-server
  - github.com/openags/paper-search-mcp
  - github.com/andybrandt/mcp-simple-arxiv
  - github.com/takashiishida/arxiv-latex-mcp
  - "@futurelab-studio/latest-science-mcp (npm)"
mcp_command:
  - "npx -y @futurelab-studio/latest-science-mcp@latest"
mcp_notes: >
  Multiple community MCPs; blazickjp/arxiv-mcp-server (~2.8k stars) is the most mature general
  server. Pick by need: blazickjp for search + download, openags/paper-search-mcp for multi-source
  (arXiv + PubMed + bioRxiv), takashiishida for LaTeX-source extraction.
agent_use_cases:
  - preprint discovery
  - citation chasing in CS and physics
  - tracking new submissions in a category
  - fetching full-text PDFs and LaTeX source
  - author and category browsing
access_test:
  command: "curl -sf 'https://export.arxiv.org/api/query?id_list=2103.13630&max_results=1'"
  expected_status: 200
  expected_fields: [id, title, summary, author, category]
last_verified: 2026-06-08
build_priority: medium
---

# arXiv

## Why this source matters

arXiv is the canonical open-access preprint server for physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering, and economics, run by Cornell Tech. Roughly 2.5M+ preprints; the de facto first-publication venue for most of ML, theoretical physics, and large parts of math. Metadata is CC0; full-text licensing varies per submission (default arXiv Perpetual License plus CC variants). For any agent doing literature search, citation chasing, or topic monitoring in those fields, arXiv is the freshest source, often weeks or months ahead of journal indexing in OpenAlex or PubMed.

## Agent use cases

- preprint discovery
- citation chasing in CS and physics
- tracking new submissions in a category
- fetching full-text PDFs and LaTeX source
- author and category browsing

## Join strategy

arXiv exposes `ARXIV_ID` natively (canonical key in registry) and frequently `DOI` once a preprint is also posted by a publisher. The API entry's `<id>` field carries the arXiv URL form (`http://arxiv.org/abs/2103.13630v3`); strip the version suffix and host to get the canonical `ARXIV_ID`. DOIs appear in the `<arxiv:doi>` element when the author has registered one.

Pair with OpenAlex (which already normalises `ARXIV_ID` into its work records) for citation counts and concept tags, with Semantic Scholar for citation-context snippets, and with Crossref once a published-journal DOI exists for authoritative bibliographic metadata.

arXiv does not assign ORCID or ROR to authors and affiliations in its API output; cross-link those via OpenAlex or Semantic Scholar.

## Access notes

**API.** Base URL `https://export.arxiv.org/api/query`. Query by `search_query` (with field prefixes `ti:`, `au:`, `abs:`, `cat:`, `all:`, plus Boolean `AND`/`OR`/`ANDNOT`) or `id_list`. Atom 1.0 XML response. No auth.

**Rate limits.** Hard guidance: 3 seconds between consecutive requests, or "bursts of 4 req/sec with a 1 second sleep between bursts". Single response capped at 2000 results; pagination capped at 30000 total. Beyond that, switch to bulk.

**Bulk full text.** Amazon S3 requester-pays buckets (`arxiv` for PDFs, `arxiv/src` for LaTeX source). Use S3, not the API, for any corpus-scale pull. Kaggle also publishes a periodically refreshed metadata + abstracts snapshot.

**Bulk metadata.** OAI-PMH endpoint at `https://export.arxiv.org/oai2` is the recommended path for keeping a complete metadata mirror in sync.

**Gotchas.**
- Metadata is CC0, but redistributing full-text PDFs requires linking back to arXiv per the default Perpetual License.
- Versioning: identifiers like `2103.13630v3` carry the version suffix. Strip for canonical joins; preserve when fetching a specific revision.
- The old (pre-April 2007) identifier scheme (`cs/0606001`) is still in use; the `ARXIV_ID` registry pattern in this directory only matches the new `YYMM.NNNNN` form. Flag for review below.

## MCP / connector notes

Multiple community MCP servers exist. `blazickjp/arxiv-mcp-server` (~2.8k stars) is the most mature general-purpose server, covering search and download. `openags/paper-search-mcp` (~1.7k stars) wraps arXiv alongside PubMed and bioRxiv for multi-source search. `takashiishida/arxiv-latex-mcp` is the only one focused on LaTeX-source extraction, useful when math precision matters. No Anthropic-official server yet.

A reference connector should expose `search_papers` (with field prefixes and Boolean), `get_paper_by_id` (single or batch), `list_recent` (by category), `download_pdf`, and `get_latex_source`. The connector must enforce the 3-second pacing budget, handle the OAI-PMH path for bulk-mirror use cases, and abstract the old vs new identifier formats.

## Review notes

- The current `ARXIV_ID` pattern in `schema/join-keys.yaml` (`^[0-9]{4}\.[0-9]{4,5}(v[0-9]+)?$`) only matches the post-April-2007 scheme. Pre-2007 identifiers like `cs/0606001`, `hep-th/9901001`, `math.GT/0309136` are still valid arXiv IDs in active use. Consider broadening the pattern or noting both forms.
- arXiv exposes an OAI-PMH endpoint that could justify an `oai-pmh` value in the `type` enum if more sources start surfacing it (currently absent from the closed enum). Not blocking; `bulk-download` covers it for now.
