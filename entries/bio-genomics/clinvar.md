---
id: clinvar
name: ClinVar
domain: bio-genomics
entry_kind: registry
description: NIH/NCBI public archive of human genetic variants and their clinically asserted relationships to diseases and drug responses, with submitter evidence and a review-status confidence rating.
homepage_url: https://www.ncbi.nlm.nih.gov/clinvar/
docs_url: https://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "E-utilities: 3 req/sec without key, 10 req/sec with a free NCBI API key"
bulk_available: true
frequency: "weekly XML release; monthly XML/VCF/TSV archives; some TSV summaries daily"
lag: "days-to-weeks for new submissions to appear; aggregate VCV classifications recomputed on each release"
geography: [global]
join_keys:
  - RSID
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
  - MESH_TERM
primary_keys:
  - CLINVAR_VCV
  - CLINVAR_RCV
  - CLINVAR_SCV
  - CLINVAR_VARIATION_ID
  - CLINVAR_ALLELE_ID
join_key_fields:
  - join_key: RSID
    fields: [measure.xref.rs, "VCF:INFO.RS"]
  - join_key: GENE_SYMBOL
    fields: [measure.measure_relationship.symbol, "VCF:INFO.GENEINFO"]
  - join_key: ENTREZ_GENE_ID
    fields: [measure.measure_relationship.xref.gene_id, "VCF:INFO.GENEINFO"]
  - join_key: MESH_TERM
    fields: [trait_set.trait.xref.mesh]
mcp_status: api-direct-sufficient
mcp_maturity: none
agent_use_cases:
  - variant pathogenicity lookup
  - gene-to-variant retrieval
  - condition-to-variant mapping
  - clinical-significance assertion check
  - bulk variant annotation
access_test:
  command: "curl -sf 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=12345&retmode=json'"
  expected_status: 200
  expected_fields: [result, uids]
last_verified: 2026-06-22
build_priority: medium
---

# ClinVar

## Why this source matters

ClinVar is the reference public archive of human genetic-variant interpretations, run by NCBI within the NIH National Library of Medicine. It aggregates clinical-significance assertions (pathogenic, likely pathogenic, benign, VUS, drug-response, etc.) that submitters attach to variant-condition pairs, then computes an aggregate classification and a 0-4 star review-status rating per variant. As of mid-2026 it holds roughly 4.5M distinct variants and 6.9M submissions from 3,400+ submitters across ~97 countries. For any agent doing clinical genomics, variant triage, or gene-disease evidence work, ClinVar is the canonical place to ask "is this variant known to be pathogenic, and how strong is the evidence?" It is the genetics-side complement to academic and clinical-trial sources, and it links out to MedGen, dbSNP, OMIM, and gene records.

## Agent use cases

- variant pathogenicity lookup
- gene-to-variant retrieval
- condition-to-variant mapping
- clinical-significance assertion check
- bulk variant annotation

## Join strategy

ClinVar exposes a small set of registry join keys: `RSID` (dbSNP cross-reference per variant), `GENE_SYMBOL` and `ENTREZ_GENE_ID` for the affected gene, and `MESH_TERM` where a trait carries a MeSH cross-reference. These are the cross-source handles: pair `RSID` with dbSNP/GWAS resources, `ENTREZ_GENE_ID`/`GENE_SYMBOL` with Ensembl, UniProt-linked target data, and gene-level annotation, and `MESH_TERM` with PubMed/biomedical-concept sources.

ClinVar's own accessions are source-native and stay in `primary_keys`, not `join_keys`: VCV (variant aggregate), RCV (variant x condition aggregate), SCV (individual submission), the integer VariationID that is the flat-file/VCF key, and the per-allele AlleleID. Several richer identifiers ClinVar carries (HGVS expressions, HGNC ID, MONDO, MedGen CUI) are not yet in the canonical registry; see `## Review notes`.

## Access notes

**Low-volume agent queries:** NCBI E-utilities at `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` with `db=clinvar`. Use `esearch` to resolve a term/RSID/gene to UIDs, `esummary` for record summaries (JSON available via `retmode=json`), and `efetch` for full XML. No auth; 3 req/sec by default, 10 req/sec with a free NCBI API key passed as `&api_key=`. The web UI at the homepage is the human entry point.

**Large analyses:** Bulk download from `https://ftp.ncbi.nlm.nih.gov/pub/clinvar/`. The full XML (`ClinVarVCVRelease` and `ClinVarRCVRelease`) ships weekly with monthly archives; `vcf_GRCh37/` and `vcf_GRCh38/` hold monthly VCFs of short variants keyed by VariationID; `tab_delimited/` holds TSV summaries (e.g. `variant_summary.txt`), some refreshed daily. For annotating more than a few hundred variants, pull the VCF or TSV rather than paginating E-utilities. To verify freshness, check the file dates under the FTP `weekly_release/` and `vcf_*` directories.

Public domain (US federal work). NCBI requests attribution to ClinVar as a data source in derivative work and citation of the ClinVar publication (PMID 29165669), but imposes no redistribution restriction. Data is explicitly not for direct diagnostic use without review by a genetics professional.

## MCP / connector notes

No dedicated MCP needed; E-utilities is a clean, stable, no-auth REST surface and a generic NCBI E-utilities connector already covers ClinVar via `db=clinvar`. If a focused wrapper were built, the useful surface would be `search_variant` (by RSID, gene, HGVS, or condition), `get_variant` (trimmed VCV summary with aggregate classification + star rating), `get_submissions` (SCV-level assertions for a variant), and `annotate_vcf` (batch lookup routed to the bulk VCF). The connector should abstract the esearch-then-esummary/efetch two-step, trim the verbose XML, and switch to the bulk VCF/TSV automatically above a batch-size threshold.

## Review notes

Potential new join keys for review (ClinVar carries these but they are not in `schema/join-keys.yaml`; do not add without a separate PR):

- `CLINVAR_VCV` / `CLINVAR_RCV` / `CLINVAR_SCV`
  - Entity type: variant_interpretation (VCV = variant aggregate, RCV = variant-condition aggregate, SCV = single submission)
  - Pattern: `^VCV[0-9]{9}(\.[0-9]+)?$`, `^RCV[0-9]{9}(\.[0-9]+)?$`, `^SCV[0-9]{9}(\.[0-9]+)?$`
  - Other datasets that would use them: GA4GH/ClinGen, variant-curation tools citing ClinVar accessions
- `CLINVAR_VARIATION_ID`
  - Entity type: variant (integer; the flat-file/VCF primary key)
  - Pattern: integer
  - Other datasets that would use it: dbSNP/Variation Viewer cross-links, ClinVar VCF consumers
- `HGVS`
  - Entity type: variant (sequence-level variant expression, e.g. `NM_000059.3:c.68_69delAG`)
  - Pattern: HGVS nomenclature string (transcript/genomic:change)
  - Other datasets that would use it: Ensembl VEP, gnomAD, dbSNP, most variant-annotation pipelines
- `HGNC_ID`
  - Entity type: gene (e.g. `HGNC:1100`)
  - Pattern: `^HGNC:[0-9]+$`
  - Other datasets that would use it: HGNC, Ensembl, UniProt, OpenTargets
- `MONDO_ID`
  - Entity type: disease (e.g. `MONDO:0007254`)
  - Pattern: `^MONDO:[0-9]{7}$`
  - Other datasets that would use it: OpenTargets, Monarch, MedGen-linked disease sources
- `MEDGEN_CUI`
  - Entity type: disease_or_phenotype (NCBI MedGen concept ID, e.g. `C0006142`)
  - Pattern: `^C[0-9]{7}$`
  - Other datasets that would use it: MedGen, OMIM cross-references, UMLS-anchored sources

License note: public domain (US-Government-Public-Domain); attribution is requested but not legally required. Flagged for awareness, no schema action needed.
