---
id: depmap
name: DepMap (Cancer Dependency Map)
domain: bio-genomics
entry_kind: panel
description: Genome-wide CRISPR (Chronos) and RNAi (DEMETER2) loss-of-function screens plus PRISM drug screens across ~1,100 cancer cell lines, giving per-gene dependency (gene-effect) scores; the functional-dependency layer over CCLE's molecular characterisation, hosted on the Broad Institute's DepMap Portal.
homepage_url: https://depmap.org/portal/
docs_url: https://depmap.org/portal/data_page/?tab=overview
type:
  - bulk-download
  - web-ui
  - dataset-dump
auth_required: none
cost: free-non-commercial
license: DepMap-Terms-Of-Use
rate_limit: "no published per-IP limit; bulk matrices served via HTTPS and Google Cloud Storage"
bulk_available: true
frequency: "bi-annual releases (e.g. 25Q2, 25Q4, 26Q1)"
lag: "current release lags screen collection by roughly one quarter"
geography: [global]
join_keys:
  - GENE_SYMBOL
  - ENSEMBL_ID
  - ENTREZ_GENE_ID
primary_keys:
  - DEPMAP_ID
  - CCLE_NAME
  - SANGER_MODEL_ID
join_key_fields:
  - join_key: GENE_SYMBOL
    fields: [gene, hugo_symbol, gene_symbol]
  - join_key: ENSEMBL_ID
    fields: [ensembl_gene_id, gene_id]
  - join_key: ENTREZ_GENE_ID
    fields: [entrez_id, entrez_gene_id]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/openpharma-org/depmap-mcp-server
  - github.com/QuentinCody/depmap-mcp-server
  - github.com/Saurabhsing21/Deepmap-mcp
mcp_notes: >
  Three community MCP servers wrap the DepMap/CCLE portal; none are official Broad releases.
  A canonical connector should surface per-gene Chronos gene-effect and dependency-probability,
  RNAi (DEMETER2), and PRISM drug sensitivity, abstract over the release-versioned file layout
  (release_25q4/, release_26q1/), and resolve DEPMAP_ID to lineage via the Model.csv metadata
  table so callers do not hand-load the index.
agent_use_cases:
  - rank cancer cell lines by dependency on a target gene
  - find lineage- or mutation-selective genetic dependencies
  - correlate gene-effect scores with expression or copy-number biomarkers
  - prioritise CRISPR-validated targets for a disease context
  - cross-check RNAi against CRISPR essentiality for a gene
access_test:
  command: "curl -sf 'https://depmap.org/portal/download/api/downloads'"
  expected_status: 200
  expected_fields: ["table[].fileName", "table[].releaseName", "table[].downloadUrl", "table[].fileType", "releaseData[].releaseName"]
last_verified: 2026-07-02
build_priority: high
structure: cross-section
pit_reconstructable: false
revisions_possible: true
notes: "Access test executed 2026-07-02: GET https://depmap.org/portal/download/api/downloads returned 200 (JSON manifest of all release files; table[], releaseData[]); latest release DepMap Public 26Q1. Per-file downloadUrl values are time-limited GCS signed URLs, so this is a queryable file index, not a query/analytics data API. Gene-effect matrices are restated each release (Chronos model + line set change), so treat scores as revisable across releases."
---

# DepMap (Cancer Dependency Map)

## Why this source matters

DepMap is the Broad Institute's map of cancer genetic dependencies: genome-wide CRISPR knockout screens (scored with the Chronos cell-population-dynamics model), legacy RNAi knockdown screens (DEMETER2), and PRISM small-molecule viability screens run across roughly 1,100 human cancer cell lines. For each gene in each line it publishes a gene-effect score (more negative = stronger loss-of-fitness on knockout) and a dependency probability, which is the primary readout for whether a gene is a candidate therapeutic target in a given lineage or genetic background. It is the functional-dependency layer that sits on top of, and is released alongside, CCLE's molecular characterisation (expression, mutation, copy number) on the same portal, so dependency scores can be joined directly to omics biomarkers per cell line. Any agent doing target identification, target validation, synthetic-lethality search, or biomarker-of-response reasoning should treat DepMap as the default genetic-dependency reference. Secondary domain: `clinical-biotech` for the PRISM drug-viability screens used in preclinical pharmacology.

## Agent use cases

- rank cancer cell lines by dependency on a target gene
- find lineage- or mutation-selective genetic dependencies
- correlate gene-effect scores with expression or copy-number biomarkers
- prioritise CRISPR-validated targets for a disease context
- cross-check RNAi against CRISPR essentiality for a gene

## Join strategy

Every per-line record keys on the Broad-minted `DEPMAP_ID` (e.g. `ACH-000019` for MCF7); the `Model.csv` metadata table also carries the legacy `CCLE_NAME` (e.g. `A549_LUNG`) and the Sanger `SANGER_MODEL_ID` (`SIDM*`, Cell Model Passports), so agents can pivot into GDSC, Project Score, and Cellosaurus without hand-mapping. Gene-level columns in the dependency matrices carry `GENE_SYMBOL` (HGNC) with `ENTREZ_GENE_ID` in parentheses; omics files add `ENSEMBL_ID`. The `DEPMAP_ID` is the shared spine between DepMap dependency data and the CCLE omics entry, so a target-validation join is usually DepMap gene-effect keyed on `DEPMAP_ID` + `GENE_SYMBOL` against CCLE expression/mutation keyed on the same pair.

Pair DepMap with CCLE (molecular features by `DEPMAP_ID`), Open Targets (target-disease evidence by `ENSEMBL_ID`), ChEMBL or DrugBank (drug structures by `CHEMBL_ID`), and the Sanger Cell Model Passports and GDSC (orthogonal CRISPR/drug response by `SANGER_MODEL_ID`).

See Review notes for `DEPMAP_ID`, `CCLE_NAME`, and `SANGER_MODEL_ID` as candidate canonical join keys (first proposed in `cancer-cell-line-encyclopedia.md`; do not invent them into `join_keys` until registered).

## Access notes

No public query/analytics REST API for the dependency matrices themselves, but the portal exposes a callable, no-auth file-manifest endpoint at `https://depmap.org/portal/download/api/downloads` (JSON: `table[]` of every release file with `fileName`, `releaseName`, `fileType`, and a `downloadUrl`; `releaseData[]` of release metadata). The `downloadUrl` values are time-limited Google Cloud Storage signed URLs, so this is a queryable index over the bulk files rather than a data API. Practical path: read the manifest, pull the dependency matrices for the target release (`CRISPRGeneEffect.csv`, `CRISPRGeneDependency.csv`, `Chronos_Combined`, RNAi `D2_combined`, PRISM), and always pull `Model.csv` to resolve `DEPMAP_ID` to lineage, primary disease, and `SANGER_MODEL_ID`. Files are versioned per release (`release_25q4/`, `release_26q1/`). A community-spec REST wrapper exists at `github.com/broadinstitute/depmap-api` (endpoints like `/gene_dependency/by_gene/{entrez_gene_id}` and `/gene_dependency/by_cell_line/{depmap_id}`), and the `depmap` R/Bioconductor package caches the release matrices, but neither is a first-party hosted live API.

License is the **DepMap Terms of Use**: free for academic and non-commercial research, with explicit restrictions on commercial productisation and on training or fine-tuning ML/AI models on the data outside internal research. Citation is required (cite Chronos, Tsherniak et al. 2017 Cell for the dependency map, and the relevant release). When redistributing, the same terms must propagate downstream.

Freshness check: GET the downloads manifest and read `releaseData[]` for the entry with `isLatest: true`, or read the release tag at `https://depmap.org/portal/data_page/?tab=allData`. Gene-effect scores are restated each release (`revisions_possible: true`) because the Chronos model and cell-line panel change, so pin a release for reproducibility.

## MCP / connector notes

Three community MCP servers wrap the DepMap/CCLE portal: `openpharma-org/depmap-mcp-server` (JavaScript), `QuentinCody/depmap-mcp-server` (TypeScript, per-gene CRISPR essentiality, expression, mutations, copy number across adult and paediatric lines), and `Saurabhsing21/Deepmap-mcp` (Python). None are official Broad releases. A canonical connector should expose `get_dependency(gene, lines)`, `get_dependency_probability(gene, lines)`, `top_dependent_lines(gene)`, `selective_dependencies(lineage|mutation)`, `get_rnai(gene, lines)`, and `get_drug_sensitivity(drug, lines)`, and abstract over (a) the release-versioned file layout, (b) resolution between `DEPMAP_ID`, `CCLE_NAME`, and `SANGER_MODEL_ID`, and (c) the CRISPR-vs-RNAi-vs-PRISM split so agents do not have to know which matrix a score comes from.

## Review notes

- This entry deliberately overlaps with `cancer-cell-line-encyclopedia.md`: DepMap and CCLE share the Broad portal, the same `DEPMAP_ID` model spine, and the same download manifest. Split rationale: CCLE is the molecular-characterisation layer (`entry_kind: mixed`, omics + drug + metabolomics), DepMap is the functional loss-of-function dependency layer (`entry_kind: panel`, genes x lines gene-effect matrix). Confirm the two entries should coexist rather than merge; if merged, DepMap's dependency surface would be the load-bearing half.
- License: `DepMap-Terms-Of-Use` has no SPDX identifier and is stricter than CC-BY (non-commercial plus an explicit ML/AI training restriction). Same canonical short name as the CCLE entry; not yet in `SCHEMA.md § License conventions`. Flag for review to add there once.
- Cost enum: `free-non-commercial`, matching CCLE, because the terms forbid commercial use and AI model training outside internal research even though academic access is unrestricted.
- Potential new canonical join keys for review (all first proposed in `cancer-cell-line-encyclopedia.md`, restated here because DepMap is the higher-value consumer of them):
  - `DEPMAP_ID`
    - Entity type: `cancer_cell_line`
    - Pattern: `^ACH-[0-9]{6}$`
    - Other datasets that would use it: CCLE, DepMap dependency screens, PRISM, Cellosaurus (cross-ref), Cell Model Passports.
  - `CCLE_NAME`
    - Entity type: `cancer_cell_line`
    - Pattern: `^[A-Z0-9]+_[A-Z_]+$` (e.g. `A549_LUNG`)
    - Other datasets that would use it: legacy CCLE files, GDSC, CTRP.
  - `SANGER_MODEL_ID`
    - Entity type: `cancer_cell_line`
    - Pattern: `^SIDM[0-9]+$`
    - Other datasets that would use it: Cell Model Passports, GDSC, Project Score (Sanger CRISPR).
  - Cellosaurus accession (`CVCL_*`) remains the de facto international cell-line registry ID and DepMap rows map to it through `Model.csv`; worth proposing alongside any cell-line-keyed dataset.
- `entry_kind`: `panel` (genes x cell lines gene-effect matrix) rather than CCLE's `mixed`, to mark DepMap as the single-measurement-type dependency layer.
- `access_test` shares the CCLE endpoint (`.../download/api/downloads`, no-auth JSON manifest, verified 200 on 2026-07-02). The dependency matrices are served from versioned GCS paths via time-limited signed URLs, not a query API, so the manifest carries the access test.
