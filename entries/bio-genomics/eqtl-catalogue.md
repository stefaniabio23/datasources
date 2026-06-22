---
id: eqtl-catalogue
name: eQTL Catalogue
domain: bio-genomics
entry_kind: mixed
description: Uniformly reprocessed QTL summary statistics (eQTL, sQTL, and other molecular traits) across ~74 cell types and tissues, all on GRCh38.
homepage_url: https://www.ebi.ac.uk/eqtl/
docs_url: https://www.ebi.ac.uk/eqtl/api_docs/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "unpublished; polite use expected, default page size 20 / max 1000, bulk FTP for large pulls"
bulk_available: true
frequency: "irregular major releases; r8 pre-release Jan 2026, prior stable r7 Jun 2024"
lag: "months for newly published studies to be reprocessed and released"
geography: [global]
join_keys:
  - RSID
  - ENSEMBL_ID
  - EFO_ID
  - GENE_SYMBOL
  - UBERON_ID
primary_keys:
  - QTS_ACCESSION
  - QTD_ACCESSION
  - EQTL_VARIANT_ID
  - MOLECULAR_TRAIT_ID
join_key_fields:
  - join_key: RSID
    fields: [rsid]
  - join_key: ENSEMBL_ID
    fields: [gene_id]
  - join_key: GENE_SYMBOL
    fields: [gene_id]
  - join_key: UBERON_ID
    fields: [tissue_id]
  - join_key: EFO_ID
    fields: [tissue_id]
mcp_status: mcp-needed-low-value
mcp_maturity: none
agent_use_cases:
  - cis-eqtl lookup for a gene
  - variant-to-molecular-trait association retrieval
  - tissue-specific QTL filtering
  - colocalisation input assembly
  - gwas-to-eqtl bridging
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/eqtl/api/v2/datasets/QTD000001/associations?size=1'"
  expected_status: 200
  expected_fields: [variant, rsid, gene_id, molecular_trait_id, pvalue, beta]
last_verified: 2026-06-22
build_priority: medium
---

# eQTL Catalogue

## Why this source matters

The eQTL Catalogue is EMBL-EBI's uniformly reprocessed collection of quantitative trait loci, run alongside the GWAS Catalog at the EBI SPOT team. It takes public RNA-seq and microarray studies and recomputes them through one shared pipeline so that QTL summary statistics are comparable across roughly 74 cell types and tissues. Coverage spans expression QTLs (eQTL), splicing QTLs (sQTL), and other molecular-trait QTLs (exon, transcript-usage, and txrevise quantifications). All data is on GRCh38. For an agent doing target validation, colocalisation against GWAS hits, or asking "which tissue is this variant regulatory in," the eQTL Catalogue is the closest free, harmonised analogue to assembling per-study QTL data by hand. Secondary domains: academic (each dataset traces to a source publication) and public-health/clinical-biotech (disease-context tissues tagged via EFO).

## Agent use cases

- cis-eqtl lookup for a gene
- variant-to-molecular-trait association retrieval
- tissue-specific QTL filtering
- colocalisation input assembly
- gwas-to-eqtl bridging

## Join strategy

The eQTL Catalogue exposes five canonical join keys. Variants carry `RSID` (dbSNP) for cross-source variant joins. Molecular traits expose the Ensembl `gene_id`, which maps to `ENSEMBL_ID` and, for protein-coding genes, to `GENE_SYMBOL` (HGNC). Tissue context is reported in the `tissue_id` field as an ontology term: depending on the dataset this is a `UBERON_ID` (anatomy), a Cell Ontology CL term, or an EFO term (`EFO_ID`) for disease/condition contexts. Use `RSID` + `ENSEMBL_ID` to bridge GWAS Catalog hits to regulatory effects, and `UBERON_ID` / `EFO_ID` to align tissue context with GTEx and Open Targets.

Source-internal identifiers (not canonical join keys): the positional `variant` ID, the `molecular_trait_id`, the study accession (`QTS` prefix, e.g. `QTS000001`), and the dataset accession (`QTD` prefix, e.g. `QTD000001`, one per study x quantification x tissue x condition). These live in `primary_keys` for direct eQTL Catalogue lookups, not cross-source joins.

The effect allele is the ALT allele: `beta` is the effect of `alt` relative to `ref`. Anyone aligning betas across sources must check effect-allele direction before combining.

## Access notes

**Low-volume agent queries:** REST API v2 at `https://www.ebi.ac.uk/eqtl/api/v2/`, no auth. Discovery endpoints (`/datasets`, `/studies`, `/tissues`, `/genes`, `/qtl_groups`) resolve accessions and ontology terms; associations come from `/datasets/{QTD}/associations`. Responses are HAL+JSON, default page size 20, max 1000 via `size=`. The legacy `/eqtl/api` (v1) is still live but v2 is the current surface.

**Large analyses:** Bulk FTP at `ftp://ftp.ebi.ac.uk/pub/databases/spot/eQTL/` ships per-dataset summary statistics as tab-delimited `.tsv.gz` plus `.hdf5`; the r8 pre-release adds parquet. Fine-mapping (`/susie/`) and credible-set (`/credible_sets/`) outputs are under the same root. For any genome-wide or multi-tissue pull, FTP is the right path; the API is for targeted gene/variant lookups. Verify freshness against the Release notes page and the latest file dates under the FTP root.

License is CC BY 4.0: attribution required, cite the 2021 Nature Genetics and/or 2023 PLoS Genetics papers. Less restrictive than ChEMBL's share-alike but, unlike most EBI core resources, not CC0, so attribution is a hard requirement for redistribution.

## MCP / connector notes

No official MCP. Lower-value than a broad bibliographic connector: the audience is genetics/colocalisation work specifically, and the clean REST v2 surface plus FTP covers most needs. If built, suggested surface: `search_datasets` (by tissue/study/quant method), `get_eqtls_for_gene` (resolve `gene_id` then pull associations across relevant `QTD` datasets), `get_associations_for_variant` (by rsid or positional ID), `list_tissues` (ontology resolution). The connector must abstract over the study/dataset accession split (one gene query fans out across many `QTD` datasets) and trim the verbose per-association payload.

## Review notes

Not-registered identifiers flagged for review (currently in `primary_keys`, no canonical join key exists):

Potential new join key for review: EQTL_VARIANT_ID
  Entity type: variant (positional, GRCh38)
  Pattern: ^chr[0-9XYM]+_[0-9]+_[ACGT]+_[ACGT]+$  (e.g. chr1_791100_G_GGGA)
  Other datasets that would use it: GTEx, GWAS sumstats harmonised to GRCh38, Open Targets Genetics

Potential new join key for review: MOLECULAR_TRAIT_ID
  Entity type: molecular_trait (gene, exon, transcript, or txrevise event)
  Pattern: free-form; gene-level equals the Ensembl gene id, sub-gene traits use suffixed/compound ids
  Other datasets that would use it: GTEx sQTL, other QTL summary-stat collections

Note: the positional `variant` ID format (`chr{N}_{pos}_{ref}_{alt}`, underscore-delimited, `chr` prefix) does NOT match the gnomAD variant ID convention (`{chr}-{pos}-{ref}-{alt}`, hyphen-delimited, no `chr` prefix). Any agent joining eQTL Catalogue to gnomAD on positional variant ID must normalise the delimiter and the `chr` prefix; the safer cross-source key is `RSID`. Effect allele is ALT.
