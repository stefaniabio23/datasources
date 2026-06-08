---
id: gtex
name: GTEx (Genotype-Tissue Expression)
domain: bio-genomics
entry_kind: panel
description: Reference atlas of tissue-specific gene expression and genetic regulation (eQTL/sQTL) across ~54 human tissues from ~1000 post-mortem donors.
homepage_url: https://www.gtexportal.org/
docs_url: https://gtexportal.org/api/v2/redoc
type:
  - rest-api
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: GTEx-Open-Access
rate_limit: "unknown; no published per-IP limit on v2 API"
bulk_available: true
frequency: per-release
lag: "years between releases (V8 2017 data, V10 2023 data)"
geography: [global]
join_keys:
  - GENE_SYMBOL
  - ENSEMBL_ID
primary_keys:
  - GTEX_SUBJECT_ID
  - GTEX_SAMPLE_ID
  - GTEX_TISSUE_SITE_DETAIL_ID
  - GTEX_VARIANT_ID
  - GTEX_GENCODE_ID
join_key_fields:
  - join_key: GENE_SYMBOL
    fields: [geneSymbol, geneSymbolUpper]
  - join_key: ENSEMBL_ID
    fields: [gencodeId]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No MCP today. Suggested surface: get_gene, get_gene_expression_by_tissue,
  get_median_expression, get_single_tissue_eqtl, get_top_expressed_genes.
  Connector must abstract over GENCODE version suffixes and the gtex_v8 vs
  gtex_v10 datasetId parameter.
agent_use_cases:
  - tissue-specific expression lookup
  - eQTL / sQTL discovery
  - candidate-gene tissue profiling
  - regulatory-variant prioritisation
  - expression-context for GWAS hits
access_test:
  command: "curl -sf 'https://gtexportal.org/api/v2/reference/gene?geneId=BRCA1'"
  expected_status: 200
  expected_fields: [gencodeId, geneSymbol, chromosome, entrezGeneId]
last_verified: 2026-06-08
build_priority: low
---

# GTEx (Genotype-Tissue Expression)

## Why this source matters

NIH Common Fund reference atlas correlating human genetic variation with tissue-specific gene expression. Roughly 1,000 post-mortem donors sampled across ~54 tissues, processed for bulk RNA-seq, WGS, and (in later releases) single-cell and splicing data. Two access tiers: summary-level expression, eQTLs, and sQTLs are openly available via the portal, REST API, and Google Cloud bucket; individual-level genotypes and raw sequencing are dbGaP-controlled under accession `phs000424`. GTEx is the de facto baseline any agent should hit when a question involves "is this gene expressed in tissue X" or "is this variant a regulatory eQTL". Secondary domain: `clinical-biotech` for target-tissue validation in drug discovery.

## Agent use cases

- tissue-specific expression lookup
- eQTL / sQTL discovery
- candidate-gene tissue profiling
- regulatory-variant prioritisation
- expression-context for GWAS hits

## Join strategy

GTEx exposes `GENE_SYMBOL` (HGNC, e.g. `BRCA1`) and `ENSEMBL_ID` via versioned GENCODE identifiers (`gencodeId`, e.g. `ENSG00000012048.20`). Strip the version suffix when joining against unversioned Ensembl IDs from other sources. Variants are encoded as GTEx-internal `variantId` strings (`chr_pos_ref_alt_b38`) and as rsIDs (`snpId`); neither rsID nor positional variant identifiers are currently canonical join keys in this registry, see Review notes.

Source-internal IDs (subject `GTEX-[CODE]`, sample `GTEX-[ID]-[NUM]-SM-[CODE]`, tissue `tissueSiteDetailId`) are GTEx-only and stay out of the YAML; use them for direct portal lookups, not cross-source joins. Pair GTEx with Ensembl or NCBI Gene for gene metadata, with Open Targets / ClinVar for disease links, and with UK Biobank or FinnGen for GWAS variants you then want to contextualise as eQTLs.

## Access notes

Hit `https://gtexportal.org/api/v2/` for open summary data. No auth, no published rate limit; all endpoints accept an optional `datasetId` (defaults to the latest release; pin to `gtex_v8` or `gtex_v10` for reproducibility). Useful first endpoints: `/reference/gene` (symbol to gencodeId), `/expression/medianGeneExpression` (gene by tissue), `/association/singleTissueEqtl` (precomputed eQTLs), `/association/dyneqtl` (compute eQTL on demand). Responses are paged via `paging_info`; default page size 250.

Bulk: per-release flat files (TPM matrices, eQTL summary stats, sample annotations, covariates) are downloadable from the portal Datasets page and mirrored on Google Cloud Storage. Use bulk for any pull larger than a few hundred gene/tissue cells; the API is convenient but not optimised for matrix-scale downloads.

Controlled tier: WGS, RNA-seq BAMs, and individual-level genotypes require a dbGaP Data Access Request against `phs000424.v9.p2` (or current version). Approval is IRB-style, weeks to months. Open summary data does not require registration or attribution beyond standard citation.

## MCP / connector notes

No MCP exists. Audience is narrow (genomics-literate users), so build priority is low, but the API is clean enough that a thin connector is straightforward. Suggested surface: `get_gene`, `get_gene_expression_by_tissue`, `get_median_expression_across_tissues`, `get_single_tissue_eqtl`, `get_top_expressed_genes`, `list_tissues`. The connector should abstract over (a) GENCODE version suffixes on Ensembl IDs, (b) `gtex_v8` vs `gtex_v10` dataset selection, (c) pagination, and (d) the split between open API endpoints and dbGaP-gated raw data, by surfacing a clear "this requires DAR" error rather than silently returning empty.

## Review notes

- License: GTEx open-tier data is widely treated as unrestricted-use ("no restrictions on use" per portal terms, with citation requested). No SPDX identifier matches. Used canonical short name `GTEx-Open-Access`. Flag for review: this is not yet in the SCHEMA.md known-cases list; if accepted, add to `SCHEMA.md § License conventions`.
- Potential new join keys for review:
  - `RSID`
    - Entity type: genetic_variant
    - Pattern: `^rs[0-9]+$`
    - Other datasets that would use it: dbSNP, ClinVar, UK Biobank summary stats, FinnGen, GWAS Catalog, Open Targets Genetics
  - `VARIANT_HGVS` or `VARIANT_B38` (chrom_pos_ref_alt_build)
    - Entity type: genetic_variant
    - Pattern: e.g. `^chr[0-9XYM]+_[0-9]+_[ACGT]+_[ACGT]+_b38$`
    - Other datasets that would use it: gnomAD, ClinVar VCFs, UK Biobank, Open Targets, most variant-level summary stats
- Considered `UBERON_ID` as a join key for tissues (GTEx tissue IDs map to Uberon); not in the registry today. Probably worth a separate proposal alongside any other tissue-keyed dataset.
- `dbGaP_ACCESSION` (e.g. `phs000424`) is a recurring pattern across NIH-controlled-access datasets and may be worth registering as a canonical key in a future PR.
