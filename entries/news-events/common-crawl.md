---
id: common-crawl
name: Common Crawl
domain: news-events
entry_kind: corpus
description: Free open repository of monthly web crawls (300B+ pages, 15 years) with raw HTML, metadata, and extracted plaintext available as bulk WARC/WAT/WET files plus a CDX URL index.
homepage_url: https://commoncrawl.org/
docs_url: https://commoncrawl.org/get-started
type:
  - bulk-download
  - rest-api
  - dataset-dump
auth_required: none
cost: free
license: Common-Crawl-Terms-of-Use
rate_limit: "CDX index server: be polite, no published quota ('do not overload'). S3/HTTP bulk: unmetered (anonymous, AWS Open Data)."
bulk_available: true
frequency: monthly
lag: "~2-4 weeks between crawl start and public availability"
geography: [global]
join_keys:
  - URL
  - DATE
primary_keys:
  - CC_CRAWL_ID
  - CC_URLKEY
  - WARC_FILENAME
  - WARC_RECORD_OFFSET
  - WARC_RECORD_LENGTH
  - CONTENT_DIGEST
join_key_fields:
  - join_key: URL
    fields: [url, urlkey]
  - join_key: DATE
    fields: [timestamp, from, to]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/arturseo-geo/mcp-common-crawl
  - github.com/lawriec/mcp-common-crawl
mcp_notes: >
  Existing community MCPs focus on backlink/SEO use cases over the CDX index.
  A general-purpose connector should also surface WARC/WET retrieval, columnar-index
  Athena queries, and crawl-list discovery for corpus-building workflows.
agent_use_cases:
  - web corpus construction
  - historical page snapshots
  - backlink and link-graph analysis
  - domain or URL presence checks across time
  - LLM pretraining data sourcing
access_test:
  command: "curl -sf 'https://index.commoncrawl.org/collinfo.json'"
  expected_status: 200
  expected_fields: [id, name, cdx-api, from, to]
last_verified: 2026-06-08
build_priority: medium
notes: Crawled content remains subject to the original publishers' copyrights; CC grants access but does not relicense third-party content. Legal counsel recommended for commercial / ML training uses.
---

# Common Crawl

## Why this source matters

Free, open repository of web crawl data run by the Common Crawl Foundation (501(c)(3), founded 2007). Spans 300B+ pages across 15 years with 3-5B new pages added monthly, hosted as AWS Open Data in `s3://commoncrawl/`. The default substrate for open LLM pretraining corpora (C4, RefinedWeb, FineWeb, RedPajama all derive from CC) and the only free, at-scale source for historical web snapshots, link-graph analysis, and large-N domain studies. Secondary domains: useful for `academic` (cited by 10K+ papers) and any agent needing a historical web corpus.

## Agent use cases

- web corpus construction
- historical page snapshots
- backlink and link-graph analysis
- domain or URL presence checks across time
- LLM pretraining data sourcing

## Join strategy

External (registry-defined): `URL` (the canonical join key, every record is keyed by source URL) and `DATE` (each crawl has a from/to window, every captured page has a fetch timestamp).

Common Crawl-internal identifiers (`CC-MAIN-YYYY-WW` crawl IDs, WARC record IDs, WARC offset+length pairs) are intentionally outside the canonical registry; use them for direct CC fetches, not cross-source joins.

Pair with: GDELT, OpenAlex, or any URL-keyed source (news article URL, paper landing page, company homepage) to attach raw HTML, captured text, or backlink counts to existing records. Pair with `WIKIDATA_QID` or `DOI` indirectly via URL.

## Access notes

Three access surfaces, pick by query shape:

- **CDX URL Index API (`https://index.commoncrawl.org/CC-MAIN-YYYY-WW-index`)** — query "is this URL in this crawl, when was it captured, where in the WARC". One endpoint per monthly crawl; full list at `https://index.commoncrawl.org/collinfo.json`. Anonymous, no auth, no published quota. Built on PyWB; supports URL-prefix and wildcard matching. Operator explicitly asks: do not overload.
- **Columnar Index (Parquet on S3, queryable via Athena/DuckDB)** — for bulk URL/host/domain filtering and aggregation across many crawls. The right tool for anything beyond a few thousand lookups.
- **Bulk WARC/WAT/WET files** — `s3://commoncrawl/` (anonymous, `--no-sign-request`) or `https://data.commoncrawl.org/<path>`. WARC = raw HTTP responses; WAT = JSON metadata (headers, links); WET = extracted plaintext. AWS transfer is free within us-east-1, charged elsewhere.

Discover paths via the per-crawl `wat.paths.gz`, `wet.paths.gz`, `warc.paths.gz` manifests in each `crawl-data/CC-MAIN-YYYY-WW/` prefix.

Known gotchas:

- Crawl coverage is broad but biased toward popular/well-linked domains; long-tail and paywalled content underrepresented.
- WET (extracted text) quality varies; boilerplate stripping is imperfect. Most downstream LLM corpora re-extract from WARC.
- Robots.txt and CCBot opt-outs honoured at crawl time, so historical snapshots exist for sites that later opted out.
- Crawled content remains subject to original copyrights; CC's terms grant access but do not relicense.
- Each monthly crawl is an independent sample, not a continuation. A URL absent from one crawl may be present in the next.

## MCP / connector notes

Two community MCPs exist (`github.com/arturseo-geo/mcp-common-crawl`, `github.com/lawriec/mcp-common-crawl`), both narrowly scoped to backlink discovery and SEO use cases over the CDX index (tools: `discover_backlinks`, `find_expired`, `check_domain`, `competitor_gap`).

A general-purpose connector is still missing. Suggested surface: `query_url_in_crawl(url, crawl_id)`, `list_crawls()`, `fetch_warc_record(warc_path, offset, length)`, `fetch_wet_text(warc_path, offset, length)`, `columnar_query(sql)` (Athena/DuckDB over the Parquet index). Connector must abstract over the CDX-vs-columnar tradeoff (CDX for one URL, columnar for many) and warn on bulk WARC pulls (multi-GB per file).

## Review notes

- License field: `Common-Crawl-Terms-of-Use` is a new canonical short name (no SPDX equivalent). CC publishes terms-of-use rather than a standard open data licence; the terms grant a limited non-transferable access licence and explicitly do not relicense third-party crawled content. Other valid options would be `CC-Terms-of-Use` or treating it as unlicensed bulk-with-terms. Flagging for Stephanie to confirm canonical short name before merge.
- `type` includes `dataset-dump` alongside `bulk-download` because CC also publishes derived datasets (web graphs, columnar index, host-level summaries) beyond raw WARC. If this overlap is intentional duplication, drop `dataset-dump`.
- Only two registry join keys map cleanly (`URL`, `DATE`). Considered but rejected: no canonical key exists for `DOMAIN` or `HOST` (the natural Common Crawl unit). If a `DOMAIN` or `REGISTERED_DOMAIN` canonical key is added later, CC should be updated. Not flagging as a new key here because the value to cross-source joins is unclear (most sources don't expose registered domain as a first-class identifier).
