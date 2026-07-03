---
id: pmc
name: PubMed Central Open Access Subset
domain: academic
entry_kind: corpus
description: Machine-reusable full-text subset of PubMed Central covering millions of biomedical journal articles and preprints published under open licenses.
homepage_url: https://pmc.ncbi.nlm.nih.gov/tools/openftlist/
docs_url: https://pmc.ncbi.nlm.nih.gov/tools/oa-service/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: PMC-Open-Access
rate_limit: "no key required for OA/bulk services; E-utilities: 3 req/sec anon, 10 req/sec with free NCBI API key"
bulk_available: true
frequency: "daily incremental packages; full baseline snapshots twice yearly (mid-June, mid-December)"
lag: "days-to-weeks after publication for OA deposit + indexing"
geography: [global]
join_keys:
  - DOI
  - PMID
  - PMCID
primary_keys:
  - PMCID
join_key_fields:
  - join_key: PMCID
    fields:
      - "oa_file_list.csv (Accession ID column)"
      - "OA-service records/record@id"
      - "article-meta.article-id[pub-id-type=pmc]"
  - join_key: PMID
    fields:
      - "oa_file_list.csv (PMID column)"
      - "article-meta.article-id[pub-id-type=pmid]"
  - join_key: DOI
    fields:
      - "article-meta.article-id[pub-id-type=doi]"
mcp_status: mcp-needed-high-value
agent_use_cases:
  - full-text retrieval
  - biomedical text mining
  - open-access corpus building
  - license-aware reuse filtering
  - full-text-to-metadata joins
access_test:
  command: "curl -sf 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC5334499'"
  expected_status: 200
  expected_fields: [OA, records, record, link]
last_verified: 2026-07-02
build_priority: high
---

# PubMed Central Open Access Subset

## Why this source matters

The PMC Open Access Subset is the largest free, machine-reusable full-text corpus of biomedical literature: millions of journal articles and preprints from PubMed Central that carry open licenses (Creative Commons or equivalent) permitting redistribution and text mining. It is run by the US National Library of Medicine (NLM/NCBI). Where most scholarly indices (OpenAlex, Crossref, PubMed) give you metadata and abstracts, the OA Subset gives you the actual JATS full-text XML, plain text, and PDFs, which is what agents need for extraction, RAG, and mining tasks. It is the canonical primary-source layer that metadata graphs point at via PMCID. Secondary domains: `clinical-biotech` and `bio-genomics` for full-text mining of trials, drugs, and genes.

## Agent use cases

- full-text retrieval
- biomedical text mining
- open-access corpus building
- license-aware reuse filtering
- full-text-to-metadata joins

## Join strategy

PMC mints `PMCID` (e.g. `PMC5334499`) as its native article identifier; it is also the canonical join key other scholarly sources (OpenAlex, Europe PMC, PubMed) use to point at PMC full text, so it lives in both `primary_keys` and `join_keys`. The `oa_file_list.csv`/`.txt` mapping files pair each `PMCID` with its `PMID` and the download path, making PMID<->PMCID resolution a bulk lookup with no API calls. `DOI` is not in the file-list CSV but is carried inside each article's JATS XML as `article-id[pub-id-type=doi]`, alongside the pmc and pmid article-ids. Recommended pattern: use OpenAlex or Europe PMC to resolve a DOI/PMID to a PMCID, then pull full text here; or harvest the file list, filter by license, and mine in bulk. Pair with OpenAlex/Crossref for authoritative metadata and Europe PMC for an alternative full-text API surface.

## Access notes

Three practical entry points, no auth required. (1) **OA Web Service API** at `https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi` returns per-article download links (tgz full-text package, pdf) filtered by `id`, `from`/`until` date range, or `format`; paginate with `resumptionToken` past 1,000 records. (2) **Bulk FTP/HTTPS** at `https://ftp.ncbi.nlm.nih.gov/pub/pmc/` serves baseline `.tar.gz` packages (split by license group: commercial-use, non-commercial-use, other) plus daily incrementals, with `oa_file_list.csv` as the PMCID->PMID->path map. (3) **E-utilities** (`efetch`/`esearch` with `db=pmc`) for single-record full-text XML; add a free NCBI API key to raise the rate limit from 3 to 10 req/sec. Note: legacy FTP bulk paths are being restructured under the PMC Cloud Service (transition flagged for August 2026), so pin to the Cloud Service structure for new bulk pipelines. Licenses vary per article; always read the `license` attribute (OA service) or the file-list License column before redistributing, and note PDFs in the subset are non-commercial-use only.

## MCP / connector notes

No MCP wraps the OA Subset's bulk/full-text surface. Community PubMed MCP servers (e.g. `github.com/Augmented-Nature/PubMed-MCP-Server`, `mcp-simple-pubmed`, `github.com/emi-dm/PubMed-MCP`) can fetch PMC full text per-article via E-utilities, so the single-paper retrieval case is partially covered, but none handle license-aware bulk corpus building, which is the high-value gap. Suggested MCP surface: `resolve_to_pmcid(doi|pmid)`, `get_fulltext(pmcid, format=xml|txt)`, `list_oa_updates(from, until, format)`, `filter_by_license(commercial|non-commercial)`, `download_package(pmcid)`. The connector must abstract over the OA-service tgz-vs-pdf link shapes, the file-list bulk map, and per-article license gating, and should parse JATS XML into clean text server-side.

## Review notes

New license short name for review: `PMC-Open-Access`. The subset is a mix of per-article licenses (CC0, CC BY, CC BY-SA, CC BY-ND, CC BY-NC, CC BY-NC-SA, CC BY-NC-ND, and custom/"other" terms), so no single SPDX code fits. Proposing `PMC-Open-Access` as a canonical kebab-ish short name (parallel to `GDELT-Open-Data`); the real per-article license is available in the OA-service `license` attribute and the file-list License column. Stephanie to confirm the short name or prefer a `mixed-license` convention. All three join keys (DOI, PMID, PMCID) are already in the registry; none invented.
