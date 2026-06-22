---
id: clingen
name: ClinGen (Clinical Genome Resource)
domain: bio-genomics
entry_kind: knowledge-graph
description: NIH-funded expert-curated resource defining the clinical relevance of genes and variants, covering gene-disease validity, dosage sensitivity, variant pathogenicity, and clinical actionability, plus a canonical allele registry.
homepage_url: https://clinicalgenome.org/
docs_url: https://reg.clinicalgenome.org/doc/AlleleRegistry_1.01.xx_api_v1.pdf
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC0
rate_limit: "unpublished; polite use expected, bulk allele registration is account-gated"
bulk_available: true
frequency: "continuous expert curation; downloads refreshed as curations are published"
lag: "expert curation is slow; gene-disease and variant classifications lag new evidence by months"
geography: [global]
join_keys:
  - RSID
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
  - EFO_ID
primary_keys:
  - CLINGEN_CA_ID
  - CLINGEN_GENE_VALIDITY_ID
  - CLINGEN_DOSAGE_ID
  - CLINGEN_VCEP_ID
join_key_fields:
  - join_key: RSID
    fields: [externalRecords.dbSNP.rs]
  - join_key: GENE_SYMBOL
    fields: [transcriptAlleles.geneSymbol]
  - join_key: ENTREZ_GENE_ID
    fields: [transcriptAlleles.geneNCBI_id]
  - join_key: EFO_ID
    fields: [disease.efo_id]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  Open unauthenticated query API for the Allele Registry plus structured CSV/TSV/BED downloads
  for the curation activities. Verbose JSON-LD allele payloads. Suggested surface: resolve_allele
  (CA ID / HGVS / rsID -> canonical allele), get_gene_validity, get_dosage_sensitivity,
  get_variant_pathogenicity, get_clinical_actionability.
agent_use_cases:
  - gene-disease validity lookup
  - variant pathogenicity classification
  - dosage sensitivity lookup
  - clinical actionability assessment
  - canonical allele resolution
access_test:
  command: "curl -sf 'https://reg.clinicalgenome.org/allele/CA321211'"
  expected_status: 200
  expected_fields: ["@id", communityStandardTitle, externalRecords, genomicAlleles, transcriptAlleles]
last_verified: 2026-06-22
build_priority: medium
---

# ClinGen (Clinical Genome Resource)

## Why this source matters

ClinGen is the NIH-funded authority on the clinical relevance of human genes and variants, run since 2013 by a consortium of 2,800+ contributors across 77 countries with NHGRI/NIH funding. Where ClinVar aggregates submitted variant interpretations, ClinGen layers expert-panel curation on top: gene-disease validity (a six-tier scale from Definitive through Strong, Moderate, Limited, Disputed, to Refuted), dosage sensitivity (haploinsufficiency / triplosensitivity scores), Variant Curation Expert Panel (VCEP) pathogenicity calls under FDA-recognized ACMG/AMP criteria, and clinical actionability scored separately for adult and pediatric contexts. The companion Allele Registry mints a canonical "CA ID" (e.g. `CA321211`) that unifies the many ways one variant gets written (HGVS, dbSNP, ClinVar, gnomAD). For any agent doing variant interpretation, gene panel design, or assessing whether a gene-disease link is real, ClinGen is the curated ground truth that sits above raw submission databases. Secondary domain: clinical-biotech (target validation and clinical actionability).

## Agent use cases

- gene-disease validity lookup
- variant pathogenicity classification
- dosage sensitivity lookup
- clinical actionability assessment
- canonical allele resolution

## Join strategy

The Allele Registry is the join workhorse. Querying it by CA ID, HGVS, or rsID returns a JSON-LD record whose `externalRecords` block cross-links the same variant across ClinVar (allele + variation IDs), dbSNP (`RSID`), gnomAD v2/v3/v4, ExAC, and MyVariant. From the registry ClinGen exposes the canonical `RSID` for variant-level joins to dbSNP, GWAS Catalog, and gnomAD. The curation activities key on `GENE_SYMBOL` and `ENTREZ_GENE_ID`, the natural bridges to NCBI Gene, Ensembl, UniProt, and OpenTargets; disease assertions in the gene-validity and actionability records carry `EFO_ID` where used, joining to OpenTargets and the GWAS Catalog. Coordinates are reported on GRCh38 as primary with GRCh37 mappings retained, so genomic-coordinate joins should anchor on GRCh38.

The source-internal canonical allele identifier (CA ID) is the most useful cross-database key ClinGen mints, but it is not yet in the join-key registry, see Review notes. Gene-disease validity records, dosage records, and VCEP records also carry ClinGen-internal accession IDs (in `primary_keys`); use these for direct ClinGen lookups, not cross-source joins.

## Access notes

Allele Registry query is open and unauthenticated: hit `https://reg.clinicalgenome.org/allele/<CA_ID>` for a single canonical allele, or resolve by HGVS / rsID / ClinVar / gnomAD via the registry query endpoints (JSON-LD responses, no key). Registering new alleles (writing to the registry) is the only account-gated operation, request login credentials by email at brl-allele-reg@bcm.edu. The curation activities (gene-disease validity, dosage, variant pathogenicity, actionability) are browsable and searchable at `https://search.clinicalgenome.org/` with per-activity downloads in CSV, TSV, and BED. For freshness, check the file dates on the downloads pages and the registry's continuously updated allele records; there is no fixed release cadence because curation is continuous. License is CC0 1.0, no attribution or share-alike obligation, the most permissive open-data terms.

## MCP / connector notes

No official MCP. High-value: variant-interpretation, gene-panel, and clinical-genomics agents are a recurring audience, the Allele Registry query API is open and stable, and the JSON-LD allele payloads are verbose (multiple genomic + transcript representations plus a large `externalRecords` block) and need trimming for context windows. Suggested surface: `resolve_allele` (CA ID / HGVS / rsID / ClinVar / gnomAD -> trimmed canonical allele with cross-refs), `get_gene_validity` (gene symbol -> classification + evidence summary), `get_dosage_sensitivity`, `get_variant_pathogenicity` (VCEP calls), `get_clinical_actionability`. The connector must abstract over the split between the unauthenticated query path and the account-gated registration path, and should default to summarising the six-tier validity scale rather than dumping raw scoring matrices.

## Review notes

Potential new join key for review: CLINGEN_CA_ID
  Entity type: variant (canonical allele)
  Pattern: ^CA[0-9]+$
  Other datasets that would use it: ClinVar, gnomAD, dbSNP, MyVariant, ClinGen-internal curation records. This is ClinGen's highest-value cross-database identifier (it canonicalizes HGVS / rsID / ClinVar / gnomAD into one ID); strong candidate for the registry. Currently held only in primary_keys.

Potential new join key for review: HGNC_ID
  Entity type: gene
  Pattern: ^HGNC:[0-9]+$
  Other datasets that would use it: HGNC, Ensembl, NCBI Gene, UniProt, OpenTargets, MONDO. ClinGen curation records key genes by HGNC ID alongside symbol; GENE_SYMBOL is in the registry but the stable HGNC ID is not.

Potential new join key for review: MONDO_ID
  Entity type: disease
  Pattern: ^MONDO:[0-9]{7}$
  Other datasets that would use it: Monarch, OpenTargets, ClinGen gene-disease assertions, Orphanet. ClinGen increasingly anchors disease assertions on MONDO; not in the registry (only EFO_ID is). Flagging the disease-ontology gap.

Note: CA ID, HGNC ID, and MONDO ID are deliberately kept OUT of `join_keys` because they are not in `schema/join-keys.yaml`. Only registry-defined keys ClinGen actually exposes (RSID, GENE_SYMBOL, ENTREZ_GENE_ID, EFO_ID) are in `join_keys`.
