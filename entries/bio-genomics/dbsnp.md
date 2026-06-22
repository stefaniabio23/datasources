---
id: dbsnp
name: dbSNP
domain: bio-genomics
entry_kind: registry
description: NIH/NCBI public archive of short genetic variation (SNVs, short indels, microsatellites) keyed to RefSNP (rs) clusters, with mapped coordinates, allele frequencies, and cross-references to genes and clinical resources.
homepage_url: https://www.ncbi.nlm.nih.gov/snp/
docs_url: https://www.ncbi.nlm.nih.gov/variation/docs/human_variation_vcf/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "E-utilities: 3 req/sec without key, 10 req/sec with a free NCBI API key; Variation Services has no published per-key limit (polite use expected)"
bulk_available: true
frequency: "periodic builds (Build 157 released 2025-03-18); ALFA allele-frequency updates quarterly"
lag: "months between builds; new variants and merges land at build cadence, not continuously"
geography: [global]
join_keys:
  - RSID
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
primary_keys:
  - RSID
  - DBSNP_SS_ID
join_key_fields:
  - join_key: RSID
    fields: [refsnp_id, "VCF:ID", "VCF:INFO.RS"]
  - join_key: GENE_SYMBOL
    fields: [primary_snapshot_data.allele_annotations.assembly_annotation.genes.locus, "VCF:INFO.GENEINFO"]
  - join_key: ENTREZ_GENE_ID
    fields: [primary_snapshot_data.allele_annotations.assembly_annotation.genes.id, "VCF:INFO.GENEINFO"]
mcp_status: api-direct-sufficient
agent_use_cases:
  - rsID to coordinate resolution
  - variant allele-frequency lookup
  - HGVS/SPDI variant normalisation
  - gene-to-variant retrieval
  - bulk variant annotation
access_test:
  command: "curl -sf 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=snp&id=328&retmode=json'"
  expected_status: 200
  expected_fields: [result, uids]
last_verified: 2026-06-22
build_priority: medium
notes: "access_test constructed, not executed: api.ncbi.nlm.nih.gov and eutils hosts were unreachable from the build environment (DNS/egress blocked). Homepage facts verified via WebFetch; build/record-count figures supplied and recorded as of Build 157."
---

# dbSNP

## Why this source matters

dbSNP is the reference public catalogue of short genetic variation, run by NCBI within the NIH National Library of Medicine. It aggregates single-nucleotide variants, short insertions/deletions, and microsatellites submitted as `ss` (submitted SNP) records, then clusters co-located, equivalent submissions into a stable RefSNP (`rs`) record that is the unit most of biology cites. Build 157 (released 2025-03-18) holds roughly 1.2 billion `rs` records, each mapped to the current human assembly GRCh38 with GRCh37 coordinates also supported. For any agent doing variant interpretation, GWAS follow-up, pharmacogenomics, or annotation, dbSNP is the canonical place to resolve an `rsID` to genomic coordinates, alleles, and population allele frequencies, and the hub the rest of the variant ecosystem (ClinVar, gnomAD, GWAS Catalog, Ensembl VEP) keys against. Allele frequencies come from the ALFA project, refreshed quarterly. Secondary relevance to `clinical-biotech` (variant-disease evidence via ClinVar cross-links) and `academic` (variant-supporting publications).

## Agent use cases

- rsID to coordinate resolution
- variant allele-frequency lookup
- HGVS/SPDI variant normalisation
- gene-to-variant retrieval
- bulk variant annotation

## Join strategy

dbSNP's load-bearing join key is `RSID`, the stable RefSNP cluster identifier (`rs328`) that is both dbSNP's primary key and the cross-system handle the entire variant ecosystem uses; pair it with ClinVar (clinical significance), GWAS Catalog (trait associations), gnomAD, and Ensembl VEP. dbSNP also exposes `GENE_SYMBOL` and `ENTREZ_GENE_ID` for the gene(s) a variant maps to (carried in VCF `INFO.GENEINFO` as `symbol:geneid` pairs), which join out to NCBI Gene, Ensembl, and UniProt-linked target data.

dbSNP mints two source-native identifiers: the `rs` accession (in `primary_keys` and `join_keys`, since it is registered and cross-system) and the `ss` (submitted SNP) accession, which is source-internal and stays in `primary_keys` only.

SPDI is NCBI's canonical normalised variant representation (sequence:position:deleted:inserted) and the form the Variation Services API speaks natively; HGVS expressions interconvert with SPDI through the same API. Neither SPDI nor HGVS is in the canonical join-key registry, so they are flagged in `## Review notes` rather than listed in `join_keys`.

## Access notes

**Single-variant / low-volume queries:** two no-auth REST surfaces. (1) NCBI E-utilities at `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` with `db=snp`: `esearch` to resolve a term/gene to UIDs, `esummary` for record summaries (`retmode=json`), `efetch` for full records. 3 req/sec anonymous, 10 req/sec with a free NCBI API key passed as `&api_key=`. (2) Variation Services / SPDI REST at `https://api.ncbi.nlm.nih.gov/variation/v0` for the variant-normalisation workflow: `/refsnp/{id}` for RefSNP detail, plus SPDI <-> HGVS <-> RefSNP interconversion endpoints (no auth). The web UI at the homepage is the human entry point.

**Large analyses:** bulk download from `https://ftp.ncbi.nlm.nih.gov/snp/`. Each build ships per-assembly VCFs under `latest_release/VCF/`: GRCh38 (the `.40` assembly accession suffix) and GRCh37 (the `.25` suffix). JSON dumps of the full RefSNP set are also published per build. For annotating more than a few hundred variants, pull the VCF rather than paginating E-utilities. To verify freshness, check the build directory and file dates under the FTP `latest_release/` path.

Two stability gotchas that matter for any pipeline:

- **rsID merges and withdrawals.** RefSNP clusters are merged when later evidence shows two `rs` records describe the same variant; the lower-numbered `rs` survives and the merged one redirects. Records can also be withdrawn (e.g. when an underlying submission is retracted). Always resolve an `rsID` against the current build rather than assuming a historical `rs` number still points where it did; the API returns the merge target.
- **Build-dependent coordinates.** Genomic positions are assembly-relative. A coordinate is only meaningful with its assembly (GRCh38 `.40` vs GRCh37 `.25`); never mix coordinates across assemblies, and pin the build/assembly when caching positions.

Public domain (US federal work under 17 USC 105). NCBI imposes no redistribution restriction but requests citation of the dbSNP publication ("The evolution of dbSNP: 25 years of impact in genomic research").

## MCP / connector notes

No dedicated MCP needed: E-utilities (`db=snp`) and the Variation Services SPDI API are clean, stable, no-auth REST surfaces, and a generic NCBI E-utilities connector already covers the lookup path. If a focused wrapper were built, the useful surface would be `resolve_rsid` (rsID -> coordinates, alleles, gene, following merges), `get_frequencies` (ALFA + population frequencies for a variant), `normalise_variant` (HGVS/SPDI/coordinate -> canonical SPDI + rsID), `variants_in_gene` (gene -> rs records), and `annotate_vcf` (batch lookup routed to the bulk build VCF). The connector must abstract the esearch-then-esummary two-step, transparently follow rsID merges, pin assembly on every coordinate it returns, and switch to the bulk VCF automatically above a batch-size threshold.

## Review notes

Potential new join keys for review (dbSNP exposes these but they are not in `schema/join-keys.yaml`; do not add without a separate PR):

- `SPDI`
  - Entity type: variant (NCBI's canonical normalised representation, `sequence:position:deleted:inserted`, e.g. `NC_000001.11:1014041:A:T`)
  - Pattern: `^[A-Za-z0-9_.]+:[0-9]+:[A-Za-z0-9]*:[A-Za-z0-9]*$`
  - Other datasets that would use it: NCBI Variation Services, ClinVar, gnomAD, GA4GH variant-representation tooling, variant-normalisation pipelines
- `HGVS`
  - Entity type: variant (sequence-level variant expression, e.g. `NM_000059.3:c.68_69delAG`, `NC_000001.11:g.1014041A>T`)
  - Pattern: HGVS nomenclature string (reference:change)
  - Other datasets that would use it: Ensembl VEP, ClinVar, gnomAD, dbSNP Variation Services, most variant-annotation pipelines
  - Note: ClinVar's entry also flagged `HGVS`; consolidate into one registry decision.

License note: public domain (US-Government-Public-Domain); citation requested but not legally required. Flagged for awareness, no schema action needed.
