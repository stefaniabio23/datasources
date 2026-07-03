---
id: human-cell-atlas
name: Human Cell Atlas Data Portal
domain: bio-genomics
entry_kind: registry
description: Open portal aggregating community-contributed single-cell and multi-omic datasets, with a faceted metadata API over projects, donors, samples, and files plus downloadable expression matrices.
homepage_url: https://data.humancellatlas.org/
docs_url: https://data.humancellatlas.org/apis/api-documentation/data-browser-api
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "not published; public Azul REST service, no API key"
bulk_available: true
frequency: "rolling; new DCP catalog snapshots (dcp59, dcp60, ...) released periodically"
lag: "months from data generation to portal ingestion/curation"
geography: [global]
join_keys:
  - ENSEMBL_ID
  - UBERON_ID
primary_keys:
  - HCA_PROJECT_UUID
  - HCA_DONOR_ID
  - HCA_SAMPLE_ID
  - HCA_SPECIMEN_ID
  - HCA_FILE_UUID
join_key_fields:
  - join_key: ENSEMBL_ID
    fields:
      - "expression-matrix feature ids (var index in .h5ad; features/genes.tsv in .mtx; row_attrs in .loom)"
  - join_key: UBERON_ID
    fields:
      - "specimen_from_organism.organ.ontology"
      - "specimen_from_organism.organ_parts.ontology"
mcp_status: mcp-needed-high-value
agent_use_cases:
  - single-cell dataset discovery
  - tissue and organ-scoped cohort building
  - cell-by-gene matrix retrieval
  - cross-atlas metadata faceting
  - donor and sample provenance lookup
access_test:
  command: "curl -sf 'https://service.azul.data.humancellatlas.org/index/projects?size=1'"
  expected_status: 200
  expected_fields: [hits, pagination, termFacets]
last_verified: 2026-07-02
build_priority: medium
---

# Human Cell Atlas Data Portal

## Why this source matters

The Human Cell Atlas (HCA) Data Portal is the reference repository for community-generated, multi-omic single-cell data, run by the UC Santa Cruz Genomics Institute as the Data Coordination Platform for the international HCA consortium. It aggregates ~530 projects (~11k donors, ~70M cells, ~590k files) spanning 16 biological-network atlases (lung, brain, gut, immune, kidney, and more). The metadata layer is served by Azul, a faceted REST service that gives a uniform view over projects, donors, samples, specimens, and files despite underlying schema churn; the data layer is cell-by-gene expression matrices (h5ad, loom, mtx) plus raw sequence. This is the canonical entry point for any agent building single-cell cohorts or pulling reference expression profiles across human tissues. Secondary relevance to `public-health` and `clinical-biotech` where disease-annotated donor cohorts are useful.

## Agent use cases

- single-cell dataset discovery
- tissue and organ-scoped cohort building
- cell-by-gene matrix retrieval
- cross-atlas metadata faceting
- donor and sample provenance lookup

## Join strategy

Two canonical keys in the registry are exposed by HCA data. `ENSEMBL_ID` is the feature identifier for genes in every downloadable expression matrix (var index of `.h5ad`, `features.tsv` of `.mtx`, row attributes of `.loom`), which is the join surface for pairing HCA expression against Ensembl, GTEx, Open Targets, or any Ensembl-keyed resource. `UBERON_ID` tags anatomy in the HCA metadata standard's `organ` / `organ_parts` ontology fields; note that the faceted Azul API returns only human-readable organ labels (`samples.organ = ["brain"]`), so the UBERON term itself lives in the full project metadata TSVs, not the `/index` facets.

HCA also mints its own UUIDs, held in `primary_keys`: project UUID (`entryId` / `projectId`), donor id, sample id, specimen id, and file UUID. Use these for direct Azul lookups, not cross-source joins.

The Azul `accessions` block additionally surfaces external repository ids the registry does not yet model: GEO series (`GSE...`), INSDC/SRA study (`SRP...`), and BioProject (`PRJNA...`). These are strong candidate join keys and are flagged under Review notes rather than invented into `join_keys`.

## Access notes

Start with the Azul service at `https://service.azul.data.humancellatlas.org/`. Useful no-auth endpoints: `/index/catalogs` (lists snapshot catalogs; default was `dcp59` at verification), `/index/summary` (global counts), `/index/projects`, `/index/samples`, `/index/files` (all filterable via a URL-encoded `filters` JSON param and faceted by `termFacets`). Pin a specific catalog with `?catalog=dcp60` for reproducibility; the default catalog advances over time and the earlier `dcp2` label 404s. Bulk file access is an unauthenticated public S3 bucket managed on the AWS Open Data registry: `aws s3 ls --no-sign-request s3://humancellatlas/` (us-east-1). Most public data needs no auth; a subset of managed-access projects gate raw sequence behind DUOS/controlled access (`dataUseRestriction`, `duosId` on the project). No published rate limit; be polite. License is CC-BY-4.0 per the data-use agreement (attribution required, commercial use and redistribution allowed), but the portal warns per-dataset licensing may differ in future releases, so check the project record.

## MCP / connector notes

No HCA-specific MCP server found on GitHub, npm, or PyPI as of verification (the MCPmed bioinformatics effort wraps GEO/STRING/UCSC Cell Browser, not HCA directly). High value: single-cell agents, and several `bio-genomics` entries (Ensembl, GTEx, Open Targets, CELLxGENE) share the same Ensembl/UBERON join surface, so one connector would serve overlapping audiences. Suggested surface: `search_projects(filters)`, `get_project(uuid)`, `list_samples(filters)`, `list_files(filters, format)`, `download_manifest(filters)`. The connector must abstract over: the URL-encoded `filters` JSON grammar, catalog pinning, faceted pagination, and the label-vs-ontology gap (resolve organ labels back to UBERON from the full metadata, and expose Ensembl feature ids from matrix headers).

## Review notes

Potential new join keys for review (present in Azul `projects.accessions`, not in `schema/join-keys.yaml`):

Potential new join key for review: GEO_SERIES
  Entity type: gene_expression_series
  Pattern: "^GSE[0-9]+$"
  Other datasets that would use it: NCBI GEO, ArrayExpress/BioStudies, CELLxGENE, recount

Potential new join key for review: SRA_STUDY
  Entity type: sequencing_study
  Pattern: "^[SED]RP[0-9]+$"
  Other datasets that would use it: NCBI SRA, ENA, INSDC mirrors

Potential new join key for review: BIOPROJECT_ID
  Entity type: sequencing_project
  Pattern: "^PRJ(NA|EB|DB)[0-9]+$"
  Other datasets that would use it: NCBI BioProject, ENA, any INSDC-derived dataset

Also worth considering: a cell-type ontology key (Cell Ontology, `CL:[0-9]{7}`) and a mouse/human developmental-stage ontology, both used in HCA metadata but out of scope of the current registry. `ENSEMBL_ID` and `UBERON_ID` are claimed as join keys even though the faceted Azul API returns organ *labels*; the ontology terms live in the downloadable metadata/matrices, so `join_key_fields` point at those file-internal paths rather than `/index` JSON paths. Confirm this is acceptable for the reverse index. No license ambiguity for current public datasets (CC-BY-4.0); managed-access subsets exist and are gated separately.
