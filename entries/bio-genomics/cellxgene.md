---
id: cellxgene
name: CZ CELLxGENE Discover
domain: bio-genomics
entry_kind: panel
description: Chan Zuckerberg Initiative platform hosting standardized single-cell RNA-seq datasets plus the aggregated Census, a queryable cell-by-gene expression corpus with ontology-normalized cell, tissue, and assay metadata.
homepage_url: https://cellxgene.cziscience.com/
docs_url: https://chanzuckerberg.github.io/cellxgene-census/
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "unspecified; Census reads run against a hosted TileDB-SOMA store or S3, no documented per-key cap"
bulk_available: true
frequency: "portal: continuous dataset ingestion; Census: weekly latest build + ~6-monthly long-term-support releases"
lag: "days-to-weeks from author submission to portal publication"
geography: [global]
join_keys:
  - ENSEMBL_ID
  - UBERON_ID
  - EFO_ID
  - NCBI_TAXON_ID
  - DOI
primary_keys:
  - CELLXGENE_COLLECTION_ID
  - CELLXGENE_DATASET_ID
  - CELLXGENE_DATASET_VERSION_ID
join_key_fields:
  - join_key: ENSEMBL_ID
    fields: [feature_id, var.feature_id]
  - join_key: UBERON_ID
    fields: [tissue.ontology_term_id, tissue_ontology_term_id]
  - join_key: EFO_ID
    fields: [assay.ontology_term_id, assay_ontology_term_id]
  - join_key: NCBI_TAXON_ID
    fields: [organism.ontology_term_id, organism_ontology_term_id]
  - join_key: DOI
    fields: [doi]
mcp_status: mcp-needed-high-value
agent_use_cases:
  - single-cell expression lookup by gene and cell type
  - cell-type marker discovery
  - tissue-resolved expression slicing
  - dataset discovery for a disease or tissue
  - cross-study cell atlas assembly
access_test:
  command: "curl -sf 'https://api.cellxgene.cziscience.com/curation/v1/collections?visibility=PUBLIC' -H 'Accept: application/json'"
  expected_status: 200
  expected_fields: [collection_id, doi, datasets]
last_verified: 2026-07-02
build_priority: high
---

# CZ CELLxGENE Discover

## Why this source matters

CZ CELLxGENE Discover, run and funded by the Chan Zuckerberg Initiative, is the largest openly accessible single-cell RNA-seq platform: 33M+ cells across 400+ curated datasets, all conformed to one dataset schema so cell type, tissue, assay, disease, organism, and developmental stage carry ontology term IDs rather than free text. Two access surfaces sit on top of the same corpus. The Discover data portal is a registry of collections (research studies), datasets, and H5AD files browsable via a public REST curation API. The Census is an aggregated, standardized cell-by-gene expression store queryable at low latency from Python or R (TileDB-SOMA, exportable to AnnData/Seurat/SingleCellExperiment). For an agent, this is the cleanest free path from "which cell types express gene X in tissue Y" to an actual expression slice, without downloading and re-harmonizing dozens of studies.

## Agent use cases

- single-cell expression lookup by gene and cell type
- cell-type marker discovery
- tissue-resolved expression slicing
- dataset discovery for a disease or tissue
- cross-study cell atlas assembly

## Join strategy

Every dataset is schema-conformed, so the ontology term IDs are reliable join keys rather than best-effort tags. `ENSEMBL_ID` carries gene identity (`feature_id` in the Census `var` axis; the schema mandates Ensembl/GENCODE IDs so all datasets measure the same features). `UBERON_ID` (`tissue_ontology_term_id`), `EFO_ID` (`assay_ontology_term_id`), and `NCBI_TAXON_ID` (`organism_ontology_term_id`) come from the Census cell metadata (`obs`) and the portal dataset objects. Collection-level publisher `DOI` links each study back to its paper, joining to OpenAlex, Europe PMC, and Crossref.

The single-cell payoff is the `cell_type_ontology_term_id` field (Cell Ontology, `CL:` prefix), which has no canonical key in the registry yet; it is flagged below. Disease is captured as `disease_ontology_term_id` (MONDO, with `PATO:0000461` for "normal"), also not in the registry. Portal-internal identifiers (`CELLXGENE_COLLECTION_ID`, `CELLXGENE_DATASET_ID`, `CELLXGENE_DATASET_VERSION_ID`) are UUIDs for direct portal lookups, not cross-source joins. Pair with GTEx and Expression Atlas for bulk expression, Human Protein Atlas for protein-level tissue expression, and NCBI GEO for the raw upstream submissions.

## Access notes

Start with the curation REST API at `https://api.cellxgene.cziscience.com/curation/v1/` (interactive Swagger UI at `/curation/ui/`). `GET /collections?visibility=PUBLIC` lists every public study with DOIs, dataset lists, and download links; `GET /datasets` lists all public datasets with their tissue/assay/organism/disease ontology terms. All read endpoints are unauthenticated; write/submission endpoints need an API key, not relevant for consumers.

For expression values, use the `cellxgene-census` Python or R package (`pip install cellxgene-census`), which opens the latest Census build and slices by cell metadata. Query genes by Ensembl ID with `ensembl=True`, or by symbol. The Census is also mirrored on the AWS Registry of Open Data (`s3://cellxgene-data-public/`) for bulk pulls. Individual H5AD files download directly from portal-provided curl commands. Note the ontology term IDs use colon form (`EFO:0009922`, `UBERON:0002822`), while the registry `EFO_ID` pattern is written in underscore form; strip/normalize the separator when joining.

## MCP / connector notes

No CELLxGENE-specific MCP exists. High value: single-cell expression overlaps the audience of GTEx, Expression Atlas, Human Protein Atlas, and NCBI GEO entries already in the directory. A connector should expose `search_datasets` (by tissue/disease/cell-type/organism ontology term), `get_collection`, `get_expression` (gene x cell-type-or-tissue mean/fraction expressed, backed by the Census), and `list_cell_types`. The tricky part is abstracting over the two backends: the lightweight curation REST API for discovery versus the heavyweight TileDB-SOMA Census for actual expression, plus trimming Census slices so a single query does not pull millions of cells into context.

## Review notes

Potential new join key for review: CL_ID
  Entity type: cell_type
  Pattern: ^CL:[0-9]{7}$
  Other datasets that would use it: Human Protein Atlas (single-cell), Tabula Sapiens/Muris, Expression Atlas single-cell, HuBMAP, Azimuth. High cross-source utility for single-cell sources; strong candidate for the biology/genomics section of schema/join-keys.yaml.

Potential new join key for review: MONDO_ID
  Entity type: disease
  Pattern: ^MONDO:[0-9]{7}$
  Other datasets that would use it: CELLxGENE disease metadata, Open Targets, Monarch/HPO, GWAS Catalog cross-refs. Directory already has a MONDO entry file (bio-genomics/mondo.md) but no canonical join key; worth adding.

Format nuance: CELLxGENE writes ontology IDs with a colon separator (EFO:0009922, UBERON:0002822), but the registry EFO_ID pattern uses an underscore (EFO_[0-9]+). Same ontology, different serialization; consumers must normalize. Noting in case the registry wants an alias/format note rather than treating them as distinct.

entry_kind chosen as `panel` (aggregated cell x gene expression with cross-sectional metadata axes, matching GTEx). The Discover portal side is also registry-like (a directory of 400+ datasets); `is_directory` was left unset since the primary agent-facing object is the queryable expression Census, not source discovery. Flag if `mixed` is preferred for consistency.
