---
id: nci-genomic-data-commons
name: NCI Genomic Data Commons (GDC)
domain: bio-genomics
entry_kind: registry
description: NCI's unified repository of harmonised cancer genomic, clinical, and biospecimen data spanning TCGA, TARGET, CPTAC, MMRF, HCMI, and 30+ other programs, with a single REST API and bulk transfer tool.
homepage_url: https://gdc.cancer.gov/access-data/gdc-data-portal
docs_url: https://docs.gdc.cancer.gov/API/Users_Guide/Getting_Started/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: dars-or-equivalent
cost: free
license: US-Government-Public-Domain
rate_limit: unknown
bulk_available: true
frequency: continuous
lag: "tied to GDC data releases (roughly quarterly); submitter-controlled embargoes up to 6 months before harmonisation appears"
geography: [global]
join_keys:
  - ENSEMBL_ID
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
  - ICD_10
  - DOI
primary_keys:
  - GDC_CASE_ID
  - GDC_FILE_ID
  - GDC_PROJECT_ID
  - GDC_SUBMITTER_ID
  - GDC_ALIQUOT_ID
  - GDC_SAMPLE_ID
join_key_fields:
  - join_key: ENSEMBL_ID
    fields: [genes.gene_id, ssms.consequence.transcript.gene.gene_id]
  - join_key: GENE_SYMBOL
    fields: [genes.symbol, ssms.consequence.transcript.gene.symbol]
  - join_key: ENTREZ_GENE_ID
    fields: [genes.entrez_gene_id]
  - join_key: ICD_10
    fields: [diagnoses.icd_10_code]
  - join_key: DOI
    fields: [references.doi]
mcp_status: mcp-needed-high-value
mcp_notes: >
  No established MCP for GDC. A connector should wrap /projects, /cases, /files,
  /annotations, /data, /manifest, /slicing, /_mapping with thin filter helpers,
  surface case-to-file resolution and BAM slicing without forcing manifest-and-CLI
  flows, and route controlled-access requests through an X-Auth-Token header sourced
  from an env var. Critical surfaces: cohort assembly by clinical/biospecimen filters,
  mutation lookup by gene symbol or ENSEMBL ID, file manifest generation, dbGaP-gated
  download brokering.
agent_use_cases:
  - assemble cancer cohorts by clinical phenotype
  - resolve cases to harmonised genomic files
  - look up mutations by gene or genomic position
  - retrieve project-level metadata across TCGA / TARGET / CPTAC / MMRF
  - generate manifests for bulk download via the GDC Data Transfer Tool
access_test:
  command: "curl -sf 'https://api.gdc.cancer.gov/projects?size=2&format=json'"
  expected_status: 200
  expected_fields: [data, hits, id, primary_site]
last_verified: 2026-06-09
build_priority: high
notes: "Access test executed 2026-06-09, returned 200 with expected fields. Open-access endpoints work anonymously; controlled-access file downloads require an X-Auth-Token tied to dbGaP authorisation."
---

# NCI Genomic Data Commons (GDC)

## Why this source matters

The Genomic Data Commons is the NCI's central cancer genomics repository, holding harmonised molecular, clinical, and biospecimen data from TCGA, TARGET, CPTAC, MMRF-COMMPASS, HCMI, BEATAML1.0, CGCI, FM-AD, GENIE, ORGANOID, EXCEPTIONAL_RESPONDERS, and 30+ other programs run under NCI. All data are uniformly re-processed against the same reference genome and pipelines, which means an agent can run a single query across cohorts that originated in different consortia. Open-access data (clinical, biospecimen, mutation calls, gene expression matrices, copy number) are available anonymously; raw reads (BAM, FASTQ) and germline calls are dbGaP-controlled. Secondary relevance to `clinical-biotech` for trial-linked translational cohorts (NCI-MATCH, CMI) and `academic` for the publication backbone behind every project.

## Agent use cases

- assemble cancer cohorts by clinical phenotype
- resolve cases to harmonised genomic files
- look up mutations by gene or genomic position
- retrieve project-level metadata across TCGA / TARGET / CPTAC / MMRF
- generate manifests for bulk download via the GDC Data Transfer Tool

## Join strategy

Canonical join keys exposed by GDC:

- `ENSEMBL_ID` and `GENE_SYMBOL` on every mutation, expression, and gene record (`genes.gene_id`, `genes.symbol`, and the nested `ssms.consequence.transcript.gene.*` paths).
- `ENTREZ_GENE_ID` on gene records.
- `ICD_10` on diagnosis records (`diagnoses.icd_10_code`) for joining to ICD-coded clinical or claims data.
- `DOI` on the per-project publication `references` list.

The load-bearing identifiers are GDC-internal UUIDs and human-readable submitter IDs, intentionally outside the canonical registry. Cases, files, aliquots, samples, and annotations are all keyed by UUIDv4. Projects use the program-prefixed form `TCGA-BRCA`, `TARGET-AML`, `CPTAC-3`, `MMRF-COMMPASS`. Cases also carry TCGA-style barcodes in `submitter_id` (`TCGA-BH-A0EA`). For dbGaP-controlled programs the `dbgap_accession_number` field on the project record (`phs000178` for TCGA, `phs000218` for TARGET, etc.) is the bridge to the dbGaP study registry.

Pair with NCBI SRA for BioProject/BioSample lineage on the underlying reads, Ensembl for variant annotation context, Open Targets for target-disease evidence on the same `ENSEMBL_ID`s, ClinicalTrials.gov for trial-linked cohorts (NCI-MATCH `NCT01827384`, CMI), and OpenAlex / PubMed for the publication trail via the project `references.doi` field.

## Access notes

**Programmatic access:** REST API at `https://api.gdc.cancer.gov/` with eight main endpoints: `status`, `projects`, `cases`, `files`, `annotations`, `data`, `manifest`, `slicing` (plus `_mapping` for field discovery and `history` for file versioning). No auth required for open-access metadata queries. First endpoint to try: `GET /projects?size=10&format=json` for a project inventory; `GET /cases?filters=...` and `GET /files?filters=...` for cohort and file assembly.

Filters use a JSON syntax with `op` (`=`, `!=`, `in`, `and`, `or`, `exclude`, `excludeifany`) and `content.field` / `content.value` payloads. POST is recommended for any filter beyond trivial size. Pagination via `from` and `size`; `format=json|tsv|xml`; restrict the response shape with `fields=` and aggregate with `facets=`.

**Bulk download:** Generate a manifest via `POST /manifest` with a filter or list of file UUIDs, then use the GDC Data Transfer Tool (`gdc-client download -m manifest.txt`) to pull files. Open-access files stream over plain HTTPS; controlled-access files need `--token-file` with a dbGaP-authorised user token.

**Controlled access:** Files flagged `access: controlled` (BAM, FASTQ, germline VCFs) require an `X-Auth-Token` header from the user's GDC token, which is only issued to users who have been approved through dbGaP for the relevant `phs` study. Approval typically takes weeks; budget for that lag.

Verify freshness by hitting `GET /status` for the current API version and the data-release version stamp, or by listing the latest entry on the GDC release notes page.

## MCP / connector notes

No established MCP for GDC. The most agent-useful surface is a thin wrapper over `/projects`, `/cases`, `/files`, `/annotations`, `/data`, `/manifest`, and `/slicing`, plus a `_mapping`-backed field-discovery helper so agents can introspect the fairly verbose nested schema (cases.diagnoses.*, cases.samples.portions.aliquots.*, cases.exposures.*) without round-tripping. Critical abstractions: filter-builder ergonomics over the raw JSON op syntax, case-to-file resolution in one call rather than chained filters, manifest generation from a cohort, BAM slicing (region-restricted read retrieval without downloading the full BAM), and credential brokering for the `X-Auth-Token` header sourced from `${GDC_TOKEN}` for controlled-access workflows. Three or more entries in this directory (NCBI SRA, Open Targets, future ClinicalTrials.gov pairing) would benefit from a stable GDC connector, which puts this in the high-value bucket.

## Review notes

Potential new join keys for review (GDC-internal but reusable across NCI cancer-genomics infrastructure):

```
Potential new join key for review: GDC_CASE_ID
  Entity type: cancer_case
  Pattern: ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$
  Other datasets that would use it: NCI Proteomic Data Commons, NCI Imaging Data Commons, ISB-CGC, future cancer-genomics entries

Potential new join key for review: GDC_FILE_ID
  Entity type: genomic_file
  Pattern: ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$
  Other datasets that would use it: NCI Proteomic Data Commons, NCI Imaging Data Commons, ISB-CGC

Potential new join key for review: GDC_PROJECT_ID
  Entity type: cancer_genomics_project
  Pattern: ^[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)?$
  Other datasets that would use it: cBioPortal, ISB-CGC, Genomic Data Analysis Network products

Potential new join key for review: DBGAP_PHS
  Entity type: dbgap_study
  Pattern: ^phs[0-9]{6}$
  Other datasets that would use it: dbGaP, NCBI SRA controlled-access metadata, AnVIL
```

The `dars-or-equivalent` auth value covers controlled-access files even though no UK DARS analogue applies; the dbGaP DAC review is the closest match in the existing enum. Open-access metadata and many derived files are anonymous and would arguably be `none`, but the entry-level value reflects the controlled portion since that is what gates the most scientifically valuable files (BAMs, germline VCFs). Flagging in case a future `dbgap-controlled` enum value is preferable.

License recorded as `US-Government-Public-Domain` per NCI's role as a federal program. The GDC policy page does not state a single SPDX-style licence; users are bound by the NIH Genomic Data Sharing Policy and (for controlled data) dbGaP Data Use Certifications rather than a copyright licence. Citation of the specific dataset(s) and NIH-designated repository is required for any publication.
