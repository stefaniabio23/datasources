---
id: gwas-catalog
name: GWAS Catalog
domain: bio-genomics
description: NHGRI-EBI curated catalogue of published genome-wide association studies, variant-trait associations, study metadata, and full summary statistics where available.
homepage_url: https://www.ebi.ac.uk/gwas/
docs_url: https://www.ebi.ac.uk/gwas/docs/api
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: EMBL-EBI-Terms-of-Use
rate_limit: "no documented hard limit; standard EBI fair-use applies, expect throttling under sustained heavy load"
bulk_available: true
frequency: "approximately weekly catalogue release; summary-statistics ingest is continuous"
lag: "weeks-to-months between paper publication and curated inclusion"
geography: [global]
join_keys:
  - PMID
  - DOI
  - GENE_SYMBOL
  - ENSEMBL_ID
  - EFO_ID
primary_keys:
  - GWAS_CATALOG_STUDY_ACCESSION
  - GWAS_CATALOG_ASSOCIATION_ID
join_key_fields:
  - join_key: PMID
    fields: [publicationInfo.pubmedId]
  - join_key: GENE_SYMBOL
    fields: [_embedded.associations.loci.authorReportedGenes.geneName]
  - join_key: ENSEMBL_ID
    fields: [_embedded.associations.loci.authorReportedGenes.ensemblGeneIds.ensemblGeneId]
  - join_key: EFO_ID
    fields: [_embedded.efoTraits.shortForm]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/openpharma-org/gwas-mcp-server
  - github.com/QuentinCody/gwas-catalog-mcp-server
  - github.com/koido/gwas-catalog-mcp
mcp_notes: >
  Three overlapping community MCPs; none official from EMBL-EBI. All wrap REST API v2.
  A consolidated connector should expose search_studies, get_study, get_associations_for_variant,
  get_associations_for_trait, get_summary_stats_url, with rs-ID and EFO disambiguation
  and clean handoff to the summary-statistics FTP for full GWAS results.
agent_use_cases:
  - variant-trait association lookup
  - study metadata retrieval by PMID or accession
  - trait-to-gene mapping via EFO
  - summary-statistics discovery and download
  - GWAS evidence aggregation for a phenotype
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/gwas/rest/api/studies/GCST000028'"
  expected_status: 200
  expected_fields: [accessionId, diseaseTrait, ancestries, publicationInfo]
last_verified: 2026-06-08
build_priority: medium
---

# GWAS Catalog

## Why this source matters

The NHGRI-EBI Catalog of human genome-wide association studies, jointly curated by EMBL-EBI and the US National Human Genome Research Institute. Holds the canonical record of published SNP-trait associations meeting genome-wide significance (p <= 5x10^-8), associated study metadata, sample ancestry, and full summary statistics for studies that contribute them. Any agent doing genetic-evidence aggregation, target-trait mapping, or polygenic-score work hits this catalogue first; it underpins Open Targets, the GWAS summary-stats ecosystem, and most large-scale post-GWAS pipelines.

## Agent use cases

- variant-trait association lookup
- study metadata retrieval by PMID or accession
- trait-to-gene mapping via EFO
- summary-statistics discovery and download
- GWAS evidence aggregation for a phenotype

## Join strategy

GWAS Catalog exposes `PMID` and `DOI` on every curated study (every entry is paper-derived), `GENE_SYMBOL` and `ENSEMBL_ID` on mapped genes, and `EFO_ID` on every curated trait. EFO mapping is the load-bearing join: the catalogue is the upstream source of trait normalisation for much of the human-disease GWAS world, so EFO-keyed joins to Open Targets, OLS, MONDO, and DisGeNET work cleanly.

Source-internal identifiers (`GCST` study accessions like `GCST90132222`, `STUDY_ACCESSION`, association IDs, dbSNP rsIDs for variants) are not in the canonical registry and stay inside GWAS-Catalog-direct lookups, not cross-source joins. The rsID is universally understood across genomics tooling but is a dbSNP identifier, not a GWAS-Catalog identifier.

Pair with Ensembl for variant context and consequence, with Open Targets for target-disease scoring, with UK Biobank / FinnGen summary stats for replication, and with PubMed/Europe PMC for the underlying paper.

## Access notes

**REST API v2** at `https://www.ebi.ac.uk/gwas/rest/api/` returns HAL-JSON (HATEOAS links between resources). No auth. Useful starting endpoints: `/studies/{accession}`, `/studies/search/findByPublicationIdPubmedId?pubmedId={pmid}`, `/associations/search/findByEfoTrait?efoTrait={trait}`, `/singleNucleotidePolymorphisms/{rsId}`.

**Bulk catalogue downloads** at `https://www.ebi.ac.uk/gwas/docs/file-downloads` ship the full association and study tables in TSV plus EFO trait mappings in OWL/RDF, refreshed roughly weekly. Use these instead of paginating the API for catalogue-wide pulls.

**Full summary statistics** live at `https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/` (per-study folders, harmonised + raw, GWAS-SSF format). Not every study contributes summary stats; the `fullPvalueSet` field on a study object flags availability.

Known gotchas:

- The REST API is HAL-style; clients must follow `_links` to traverse studies -> associations -> variants. Plan for multi-hop queries.
- Summary statistics are large (per-study files routinely 100 MB+); never pull them through the REST API, always via FTP/HTTPS bulk paths.
- EFO mapping lags curation; very recent studies may have placeholder traits.
- Catalogue curation is publication-driven, so unpublished or preprint-only GWAS are absent.
- License is EMBL-EBI terms of use rather than an SPDX licence; permissive in practice (open redistribution, attribution expected) but flag for downstream commercial users.

## MCP / connector notes

Three community MCPs exist (`openpharma-org/gwas-mcp-server` in JavaScript, `QuentinCody/gwas-catalog-mcp-server` in TypeScript, `koido/gwas-catalog-mcp` in Python); none official from EMBL-EBI. All wrap REST API v2 with varying coverage. A consolidated connector should expose `search_studies`, `get_study`, `get_associations_for_variant`, `get_associations_for_trait`, `get_summary_stats_url`, with rsID and EFO disambiguation, HAL-link traversal hidden from the caller, and clean handoff to the summary-statistics FTP path when full results are requested rather than tombstoned associations.

## Review notes

License field uses `EMBL-EBI-Terms-of-Use` as a canonical kebab-case short name; this is not in the documented known-cases list in `SCHEMA.md` (`US-Government-Public-Domain`, `GDELT-Open-Data`, `ECDC-Public-Data`, `Crown-Copyright`). Several EBI-hosted resources (Ensembl, ChEMBL, UniProt) sit under the same terms or close variants; consider promoting `EMBL-EBI-Terms-of-Use` to the canonical short-name list if more EBI entries land. Note that `entries/bio-genomics/ensembl.md` currently uses `Apache-2.0`, which covers the Ensembl software but not the genome-annotation data; that may itself be worth a review pass.

Potential new join keys for review:
- `GWAS_CATALOG_STUDY_ACCESSION` — entity_type: gwas_study; pattern: `^GCST[0-9]+$`. Universally used to identify a GWAS Catalog study and propagated by Open Targets, GWAS-SSF, IEU OpenGWAS. Would also be exposed by Open Targets and any summary-stats-aware source.
- `RSID` — entity_type: variant; pattern: `^rs[0-9]+$`. dbSNP-issued but the lingua franca for SNP joins across GWAS Catalog, Ensembl variation, ClinVar, gnomAD, Open Targets, UK Biobank.
