---
id: cancer-cell-line-encyclopedia
name: Cancer Cell Line Encyclopedia (CCLE)
domain: bio-genomics
entry_kind: mixed
description: Multi-omic characterisation of ~1,000 human cancer cell lines (RNA-seq, WES/WGS, copy number, methylation, proteomics, metabolomics, drug sensitivity), distributed through the Broad Institute's DepMap Portal.
homepage_url: https://sites.broadinstitute.org/ccle
docs_url: https://depmap.org/portal/data_page/?tab=overview
type:
  - bulk-download
  - web-ui
  - dataset-dump
auth_required: none
cost: free-non-commercial
license: DepMap-Terms-Of-Use
rate_limit: "no published per-IP limit; bulk files served via HTTPS and Google Cloud Storage"
bulk_available: true
frequency: "DepMap releases bi-annually (e.g. 25Q2, 25Q4, 26Q1); historical CCLE Phase I-III drops are static"
lag: "current release lags collection by one quarter; legacy CCLE bulk files are pinned to publication dates (2012, 2015, 2019)"
geography: [global]
join_keys:
  - ENSEMBL_ID
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
  - DOI
  - PMID
primary_keys:
  - DEPMAP_ID
  - CCLE_NAME
  - SANGER_MODEL_ID
  - BROAD_ID
join_key_fields:
  - join_key: ENSEMBL_ID
    fields: [ensembl_gene_id, gene_id]
  - join_key: GENE_SYMBOL
    fields: [gene, hugo_symbol, gene_symbol]
  - join_key: ENTREZ_GENE_ID
    fields: [entrez_id, entrez_gene_id]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/openpharma-org/depmap-mcp-server
  - github.com/QuentinCody/depmap-mcp-server
  - github.com/Saurabhsing21/Deepmap-mcp
mcp_notes: >
  Three community MCP servers wrap DepMap/CCLE; none are official Broad releases. Coverage
  varies: per-gene essentiality, expression, mutations, copy number across adult and
  paediatric lines. A canonical connector should abstract over the release-versioned file
  layout (release_25q4/, release_26q1/) and surface the model metadata table so callers can
  resolve DEPMAP_ID, CCLE name, and Sanger model ID without hand-loading the index.
agent_use_cases:
  - cancer cell line lookup by gene or mutation
  - drug sensitivity benchmarking across lines
  - expression and copy-number profiling for target validation
  - CRISPR essentiality scoring for dependency mapping
  - tissue-of-origin and lineage annotation for in vitro models
access_test:
  command: "curl -sf 'https://depmap.org/portal/download/api/downloads'"
  expected_status: 200
  expected_fields: ["table[].fileName", "table[].releaseName", "table[].downloadUrl", "table[].fileType", "releaseData[].releaseName"]
last_verified: 2026-06-22
build_priority: medium
notes: "Access test executed 2026-06-22: GET https://depmap.org/portal/download/api/downloads returned 200 with a JSON manifest (table[], releaseData[]) of all release files; latest release DepMap Public 26Q1. Per-file downloadUrl values are time-limited GCS signed URLs, so this endpoint is a queryable file index rather than a data API. Freshness check: read releaseData[].releaseName (isLatest: true) or the release tag at https://depmap.org/portal/data_page/?tab=allData."
---

# Cancer Cell Line Encyclopedia (CCLE)

## Why this source matters

CCLE is the canonical multi-omic reference for human cancer cell lines, originally a Broad Institute and Novartis collaboration and now hosted alongside DepMap on the Broad's portal. Across three phases (Phase I 2012, Phase II 2015-2019, Phase III 2020) it characterises ~1,000 lines with RNA-seq, exome and whole-genome sequencing, SNP-array copy number, methylation, miRNA, metabolomics (225 metabolites), reverse-phase protein arrays, TMT proteomics on 375 lines, and pharmacological screens. Any agent doing target validation, biomarker discovery, drug-repurposing diligence, or in vitro model selection should treat CCLE plus DepMap dependency screens as the default starting point. Secondary domain: `clinical-biotech` for drug sensitivity data (PRISM, CTRP, GDSC merges) used in preclinical pharmacology.

## Agent use cases

- cancer cell line lookup by gene or mutation
- drug sensitivity benchmarking across lines
- expression and copy-number profiling for target validation
- CRISPR essentiality scoring for dependency mapping
- tissue-of-origin and lineage annotation for in vitro models

## Join strategy

CCLE keys every per-line record on the Broad-minted `DEPMAP_ID` (e.g. `ACH-000001`) and legacy `CCLE_NAME` (e.g. `A549_LUNG`). The DepMap model metadata table also carries `SANGER_MODEL_ID` (Cell Model Passport, e.g. `SIDM00001`), letting agents pivot into Cell Model Passports, GDSC, and Cellosaurus without manual mapping. Gene-level rows expose `GENE_SYMBOL` (HGNC), `ENSEMBL_ID` (versioned and unversioned depending on file), and `ENTREZ_GENE_ID`. Variants are recorded with HGVS strings plus chromosomal coordinates on hg38; rsID appears in mutation files where applicable.

Pair CCLE with Open Targets (target-disease scores by `ENSEMBL_ID`), ChEMBL or DrugBank (drug structures by `CHEMBL_ID` and name), GDSC and the Sanger Cell Model Passports (orthogonal drug response and richer line annotation by `SANGER_MODEL_ID`), and GTEx or Human Protein Atlas (normal-tissue baselines by `ENSEMBL_ID`).

See Review notes for `ENTREZ_GENE_ID`, `DEPMAP_ID`, `CCLE_NAME`, and `SANGER_MODEL_ID` as candidate canonical join keys.

## Access notes

There is no query/analytics REST API for the data matrices themselves, but DepMap does expose a callable, no-auth file-manifest endpoint at `https://depmap.org/portal/download/api/downloads` (JSON: `table[]` of every release file with `fileName`, `releaseName`, `fileType`, and a `downloadUrl`; `releaseData[]` of release metadata). The `downloadUrl` values are time-limited Google Cloud Storage signed URLs, so this is a queryable index over the bulk files rather than a programmatic data API. The two practical paths for the data are:

1. **DepMap Portal downloads.** Bulk CSV/TSV (sometimes Parquet for large matrices) at `https://depmap.org/portal/data_page/?tab=allData`. Files are versioned per release (`release_25q4/`, `release_26q1/`); always download the `Model.csv` metadata table to resolve `DEPMAP_ID` to lineage, primary disease, and `SANGER_MODEL_ID`. Releases land bi-annually (recent: 26Q1).
2. **Legacy CCLE bulk archive.** Phase I files (2012 SNP arrays, expression arrays, MAF, drug response) are pinned at the broad-institute.org CCLE site and on the Broad's legacy data portal. Phase II and Phase III files (RNA-seq, proteomics, metabolomics) are hosted on Figshare and the DepMap portal under each release.

License is the **DepMap Terms of Use**: free for academic and non-commercial research, with explicit restrictions on commercial productisation and on training or fine-tuning ML or AI models with the data outside internal research use. Citation is required (per the `how-to-cite` panel on each release page). When redistributing, the same terms must propagate downstream; rehosting agents must enforce them. Acknowledge the Broad Institute and cite the relevant Nature 2012, Nature 2019, and Cell 2020 publications depending on which data type is used.

Freshness check: GET `https://depmap.org/portal/download/api/downloads` and read `releaseData[]` for the entry with `isLatest: true`, or hit `https://depmap.org/portal/data_page/?tab=allData` and read the release tag at the top of the page. `access_test` populated against the JSON manifest endpoint (verified 200, 2026-06-22).

## MCP / connector notes

Three community MCP servers exist: `openpharma-org/depmap-mcp-server` (JavaScript), `QuentinCody/depmap-mcp-server` (TypeScript, focused on per-gene CRISPR essentiality, expression, mutations, copy number across adult and paediatric lines), and `Saurabhsing21/Deepmap-mcp` (Python). None are official Broad releases. A canonical connector should expose `get_cell_line(depmap_id)`, `search_lines(lineage, disease)`, `get_expression(gene, lines)`, `get_mutations(gene, lines)`, `get_copy_number(gene, lines)`, `get_dependency(gene, lines)`, and `get_drug_sensitivity(drug, lines)`, and abstract over (a) the release-versioned file layout, (b) resolution between `DEPMAP_ID`, `CCLE_NAME`, and `SANGER_MODEL_ID`, and (c) the split between current DepMap releases and pinned legacy CCLE archives.

## Review notes

- License: the DepMap Terms of Use have no SPDX identifier and are stricter than CC-BY (non-commercial plus an explicit ML/AI training restriction). Used canonical short name `DepMap-Terms-Of-Use`. Flag for review: not yet listed in `SCHEMA.md § License conventions`; if accepted, add there. The ML/AI training prohibition is unusual and likely worth a short note in the registry's licence guidance.
- Cost enum: chose `free-non-commercial` because the terms explicitly forbid commercial use and AI model training outside internal research, even though academic access is unrestricted.
- Potential new canonical join keys for review:
  - `DEPMAP_ID`
    - Entity type: `cancer_cell_line`
    - Pattern: `^ACH-[0-9]{6}$`
    - Other datasets that would use it: DepMap dependency screens, PRISM repurposing, Cellosaurus (cross-ref), Cell Model Passports.
  - `CCLE_NAME`
    - Entity type: `cancer_cell_line`
    - Pattern: `^[A-Z0-9]+_[A-Z_]+$` (e.g. `A549_LUNG`)
    - Other datasets that would use it: legacy CCLE files, GDSC, CTRP, older expression atlases referencing the Broad naming convention.
  - `SANGER_MODEL_ID`
    - Entity type: `cancer_cell_line`
    - Pattern: `^SIDM[0-9]+$`
    - Other datasets that would use it: Cell Model Passports, GDSC, Project Score (Sanger CRISPR), iCellSeqDB.
  - `ENTREZ_GENE_ID`
    - Entity type: `gene`
    - Pattern: `^[0-9]+$`
    - Other datasets that would use it: NCBI Gene, GTEx, HPA, OpenAlex MeSH expansions, most biomedical cross-references. Already flagged in `human-protein-atlas.md`; consolidating the proposal here.
- Cellosaurus accession (`CVCL_*`) is the de facto international cell line registry identifier and CCLE rows can be mapped to it through the model metadata table; worth a separate proposal alongside any other cell-line-keyed dataset.
- `entry_kind` choice: `mixed` over `panel`, because CCLE spans genomics, transcriptomics, proteomics, metabolomics, and pharmacology rather than a single multi-dimensional measurement.
- `access_test` populated against `https://depmap.org/portal/download/api/downloads` (no-auth JSON file manifest, verified 200 on 2026-06-22). The data matrices themselves are served from versioned GCS paths via time-limited signed URLs rather than a query API, but the manifest endpoint is a stable callable surface, so it carries the access test. Freshness check documented in Access notes.
