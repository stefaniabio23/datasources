---
id: core
name: CORE
domain: academic
description: World's largest aggregator of open access research papers, harvesting metadata and full text from thousands of repositories and journals globally.
homepage_url: https://core.ac.uk/
docs_url: https://api.core.ac.uk/docs/v3
type:
  - rest-api
  - bulk-download
  - dataset-dump
auth_required: api-key-free
cost: freemium
license: unknown
rate_limit: "10 req per short window anonymous; higher tiered limits with registered API key; institutional members get further uplift"
bulk_available: true
frequency: continuous
lag: "days-to-weeks from repository deposit to CORE harvest; full dataset snapshot refreshed periodically"
geography: [global]
join_keys:
  - DOI
  - ARXIV_ID
  - PMID
  - ISSN
  - URL
primary_keys:
  - CORE_ID
  - CORE_OUTPUT_ID
  - CORE_DATA_PROVIDER_ID
  - OAI_ID
  - MAG_ID
join_key_fields:
  - join_key: DOI
    fields: [doi, identifiers]
  - join_key: ARXIV_ID
    fields: [arxivId]
  - join_key: PMID
    fields: [pubmedId, identifiers]
  - join_key: ISSN
    fields: [journals.identifiers]
  - join_key: URL
    fields: [downloadUrl, sourceFulltextUrls]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No known MCP. Stable v3 REST API, but anonymous tier strips full-text fields
  ("Not available for public API users") and tight rate-limit window forces key use
  for any real workload. Suggested surface: search_works, get_work_by_id, get_outputs,
  list_data_providers, resolve_by_doi.
agent_use_cases:
  - open-access full-text discovery
  - repository-level harvesting
  - doi-to-pdf resolution
  - cross-repository deduplication
  - bulk corpus construction for nlp
access_test:
  command: "curl -sfL 'https://api.core.ac.uk/v3/search/works/?q=climate+change&limit=1'"
  expected_status: 200
  expected_fields: [totalHits, results, limit, offset]
last_verified: 2026-06-08
build_priority: medium
notes: "Anonymous access works for search but full-text and some metadata are gated behind an API key (register at core.ac.uk/services/api). License of harvested content is heterogeneous; CORE itself is reviewing its data-licensing framework (factual metadata likely CC0/ODC-0, expressive content conditional)."
---

# CORE

## Why this source matters

CORE is the largest open access aggregator on the web, ~431M metadata records and ~46M directly hosted full-text PDFs harvested from thousands of repositories and journals across 100+ countries. Built and run by The Open University's Knowledge Media Institute (UK) since 2011, funded by Jisc and the European Commission. Where OpenAlex and Crossref give clean metadata graphs, CORE is the place to actually pull the PDF: it dereferences DOIs and OAI identifiers to a downloadable open-access copy when one exists anywhere in its harvested repositories. That makes it the high-recall complement to Europe PMC (biomedical-only) and arXiv (preprints-only) for any agent that needs full text rather than abstracts.

## Agent use cases

- open-access full-text discovery
- repository-level harvesting
- doi-to-pdf resolution
- cross-repository deduplication
- bulk corpus construction for nlp

## Join strategy

CORE exposes canonical identifiers `DOI`, `ARXIV_ID`, `PMID` (as `pubmedId`), and `ISSN` (via the `journals[]` block) on each work. `URL` is the last-resort join via `downloadUrl` and `sourceFulltextUrls`.

CORE-internal identifiers (`CORE_ID`, `OAI_ID`, `MAG_ID`, the per-output URL under `outputs[]`, and `dataProviders[].id`) live outside the canonical registry. Use them for direct CORE lookups and for cross-walking to specific source repositories, not for joining to other datasets in this directory.

Pair with OpenAlex or Crossref for richer citation and authorship metadata (CORE's author and citation fields are thin), and with Unpaywall or Europe PMC when you want a second opinion on whether an OA copy exists.

## Access notes

**API.** Base URL `https://api.core.ac.uk/v3/`. Endpoints follow REST shape: `search/works/?q=...`, `works/{id}`, `outputs/{id}`, `data-providers/{id}`. Anonymous calls work for search and return ~10 results per short window before hitting `x-ratelimit-remaining: 0` (header confirms a 10-call budget). Register at `core.ac.uk/services/api` for a free API key with higher allowance; pass as `Authorization: Bearer ${CORE_API_KEY}`. Anonymous responses explicitly null out `fullText` with the string `"Not available for public API users."` — an API key is required for the actual text body.

**Bulk.** A periodically refreshed CORE Dataset is available for download (multi-hundred-GB compressed JSON / XML of metadata + full text). FastSync is the incremental-changes feed for institutional members keeping a local mirror in sync. Both gated behind registration; not a drop-in like OpenAlex's S3 bucket.

**Gotchas.**

- API redirects trailing-slash-less paths (use `curl -L` or always include the trailing slash on `search/works/`).
- `fullText` field is gated; only the URL to the PDF is exposed on the free tier.
- Heterogeneous source licensing means a CORE-hosted PDF may not be redistributable even though CORE itself surfaces it; downstream pipelines must respect per-record provenance.
- Citation and reference fields are sparse compared to OpenAlex / Semantic Scholar.

## MCP / connector notes

No known MCP. Stable v3 REST API and clear endpoint structure make it a clean build, but two things the connector must abstract: (a) anonymous-vs-keyed mode switching with graceful degradation when `fullText` is gated, and (b) the redirect/trailing-slash quirk. Suggested surface: `search_works`, `get_work_by_id`, `get_outputs`, `list_data_providers`, `resolve_by_doi`. Add a budget tracker against the `x-ratelimit-*` headers so agents do not blow through the small anonymous window.

## Review notes

- `license` set to `unknown`. CORE is actively reviewing its data-licensing framework, splitting factual metadata (likely `CC0` or `ODC-0`) from expressive content (conditional access for TDM). Until they publish a single canonical license string, hard-coding one would misrepresent. Worth revisiting on next verification pass.
- Potential new join key for review: `OAI_ID`
  Entity type: harvested_repository_record
  Pattern: `^oai:[a-zA-Z0-9._-]+:[a-zA-Z0-9._/-]+$`
  Other datasets that would use it: any OAI-PMH-compliant repository aggregator (BASE, OpenAIRE, DataCite Search), making it a plausible cross-aggregator join key.
- Potential new join key for review: `MAG_ID`
  Entity type: scholarly_work
  Pattern: `^[0-9]+$`
  Other datasets that would use it: Microsoft Academic Graph successors (OpenAlex retains `mag_id` on legacy records); narrow but useful for historical joins.
