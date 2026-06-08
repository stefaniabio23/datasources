---
id: ncbi-geo
name: NCBI GEO
domain: bio-genomics
entry_kind: registry
description: NIH/NCBI Gene Expression Omnibus, public repository of microarray, RNA-seq, and other high-throughput functional genomics data with 286k+ series and 8.5M+ samples.
homepage_url: https://www.ncbi.nlm.nih.gov/geo/
docs_url: https://www.ncbi.nlm.nih.gov/geo/info/geo_paccess.html
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "3 req/sec anon; 10 req/sec with free NCBI API key (api_key= param)"
bulk_available: true
frequency: daily
lag: "days from submitter release to public availability; embargo dates set by submitters"
geography: [global]
join_keys:
  - PMID
  - GENE_SYMBOL
  - MESH_TERM
primary_keys:
  - GSE_ACCESSION
  - GSM_ACCESSION
  - GPL_ACCESSION
  - GDS_ACCESSION
  - GEO_UID
join_key_fields:
  - join_key: PMID
    fields: [pubmedids]
  - join_key: GENE_SYMBOL
    fields: [genename]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/MCPmed/GEOmcp
  - github.com/openpharma-org/geo-mcp-server
  - github.com/musharna/data-aggregator-mcp
mcp_notes: >
  Several overlapping community MCPs wrap E-utilities for GEO. None official. Suggested
  consolidated surface: search_series, get_series, get_sample, get_platform, list_samples_in_series,
  fetch_supplementary_files, with response trimming for verbose SOFT/MINiML payloads and
  routing to FTP for raw data downloads (E-utilities returns metadata only).
agent_use_cases:
  - find expression studies by disease or gene
  - retrieve sample metadata for a series
  - link publications to deposited datasets
  - locate platform annotation for an array
  - bulk download raw/processed expression matrices
access_test:
  command: "curl -sf 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200240191&retmode=json'"
  expected_status: 200
  expected_fields: [accession, title, gse, pubmedids, ftplink, bioproject]
last_verified: 2026-06-08
build_priority: medium
---

# NCBI GEO

## Why this source matters

The Gene Expression Omnibus is NIH/NCBI's public archive for functional genomics data, holding 286k+ Series (studies), 8.5M+ Samples, and 28k+ Platforms covering microarray, RNA-seq, ChIP-seq, methylation, and single-cell experiments. Run by the National Center for Biotechnology Information under NLM/NIH, MIAME-compliant, fully public domain. Together with ArrayExpress (EMBL-EBI) and SRA (raw reads), GEO is the canonical first stop for an agent that needs to find or reuse published expression data. Secondary relevance to `clinical-biotech` (many submissions link to NCT trial IDs in study summaries) and `academic` (every series typically has a backing PubMed paper).

## Agent use cases

- find expression studies by disease or gene
- retrieve sample metadata for a series
- link publications to deposited datasets
- locate platform annotation for an array
- bulk download raw/processed expression matrices

## Join strategy

Canonical join keys exposed by GEO:

- `PMID` via the `pubmedids` array on every Series eSummary, the strongest cross-source pivot (lets agents reach back to OpenAlex, Europe PMC, PubMed for the originating paper).
- `GENE_SYMBOL` in study/sample annotation fields and expression matrices (HGNC for human, model-organism nomenclature elsewhere).
- `MESH_TERM` indexed for searching `db=gds` via E-utilities.

GEO-internal IDs (`GSE` series, `GSM` sample, `GPL` platform, `GDS` curated dataset) are intentionally outside the canonical registry, use them for direct GEO/E-utility lookups, not cross-source joins. The eSummary response also surfaces a `bioproject` field (e.g. `PRJNA1002782`) that joins to NCBI BioProject and SRA, and clinical studies frequently mention `NCT_ID` in free-text summaries (extractable but not structured).

Pair with SRA for raw FASTQ behind the GSE, ArrayExpress for European mirror coverage, Ensembl/UniProt to resolve gene/protein annotations, and OpenAlex/PubMed for the backing literature.

## Access notes

**Low-volume queries:** E-utilities at `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` with `db=gds` (GEO DataSets) or `db=geoprofiles`. No auth required, 3 req/sec anonymous. First endpoint to try is `esearch.fcgi?db=gds&term=<query>` then `esummary.fcgi?db=gds&id=<uid>&retmode=json`. Add `&api_key=<key>` for 10 req/sec, register a free key at NCBI account settings, and always pass `&tool=<name>&email=<addr>`.

**Large analyses:** FTP at `https://ftp.ncbi.nlm.nih.gov/geo/` with the pattern `/geo/{series|samples|platforms}/{ACCnnn}/{ACCESSION}/{soft|miniml|matrix|suppl}/`. SOFT and MINiML XML carry metadata, Series Matrix files carry processed expression tables, supplementary files carry raw or author-processed data. E-utilities returns metadata only, raw data lives on FTP.

Known gotchas:

- UIDs returned by `esearch` differ from accessions (UID `200240191` corresponds to `GSE240191`, the `200` prefix denotes Series in `db=gds`); always read `accession` from eSummary rather than building accessions from UIDs.
- Schedule large jobs on weekends or between 9pm and 5am US Eastern per NCBI guidance.
- Submitter embargoes can hide data until publication, "reviewer tokens" exist for unreleased records.
- Sample metadata quality varies widely, MIAME is the floor not the ceiling; expect missing fields, free-text condition labels, and inconsistent units.
- Raw data formats differ by platform (CEL for Affymetrix, IDAT for Illumina methylation, FASTQ via linked SRA for sequencing).

## MCP / connector notes

Community MCPs exist (`MCPmed/GEOmcp` Python, `openpharma-org/geo-mcp-server` JS, plus `musharna/data-aggregator-mcp` covering GEO/SRA/BioProject in one server); none official from NCBI. Most wrap a subset of E-utilities. A consolidated connector should expose `search_series`, `get_series`, `get_sample`, `get_platform`, `list_samples_in_series`, `fetch_supplementary_files`, with response trimming for verbose SOFT/MINiML payloads, automatic `api_key`/`tool`/`email` injection, and routing to FTP for any raw-data fetch (since E-utilities only returns metadata). Cross-database eLink calls (`gds` -> `pubmed`, `gds` -> `bioproject`, `gds` -> `sra`) are the most valuable surface for agent workflows.

## Review notes

Potential new join keys for review:

- `GEO_ACCESSION` (entity_type: functional_genomics_record, pattern: `^G(SE|SM|PL|DS)[0-9]+$`) — would let other datasets that cite GEO studies (publications, Open Targets evidence, ArrayExpress mirrors) pivot back to the source record.
- `BIOPROJECT_ACCESSION` (entity_type: sequencing_project, pattern: `^PRJ[NDE][A-Z][0-9]+$`) — surfaces on every GEO eSummary and is the canonical join into SRA, BioSample, and ENA; high value once SRA/BioSample are added to the directory.

Neither is added to YAML in this entry; flagged here for Stephanie's review before PRing into `schema/join-keys.yaml`.
