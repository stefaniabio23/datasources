---
id: open-targets
name: Open Targets
domain: clinical-biotech
description: Open-access drug target identification and prioritisation platform integrating genetics, genomics, transcriptomics, drugs, animal models, and scientific literature for target-disease association scoring.
homepage_url: https://platform.opentargets.org/
docs_url: https://platform-docs.opentargets.org/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC0-1.0
rate_limit: unknown
bulk_available: true
frequency: quarterly
lag: "data refresh follows quarterly release cadence; underlying sources lag per their own schedules"
geography: [global]
join_keys:
  - ENSEMBL_ID
  - GENE_SYMBOL
  - UNIPROT_ACCESSION
  - CHEMBL_ID
  - EFO_ID
  - DOI
  - PMID
primary_keys:
  - ENSEMBL_ID
  - EFO_ID
  - CHEMBL_ID
  - OPEN_TARGETS_VARIANT_ID
  - OPEN_TARGETS_STUDY_ID
join_key_fields:
  - join_key: ENSEMBL_ID
    fields: [target.id, id]
  - join_key: GENE_SYMBOL
    fields: [target.approvedSymbol, approvedSymbol]
  - join_key: UNIPROT_ACCESSION
    fields: [target.proteinIds.id, proteinIds.id]
  - join_key: CHEMBL_ID
    fields: [drug.id, id]
  - join_key: EFO_ID
    fields: [disease.id, id]
  - join_key: PMID
    fields: [evidences.rows.literature, literature]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/nickzren/opentargets-mcp
  - github.com/Augmented-Nature/OpenTargets-MCP-Server
  - github.com/pipeworx-io/mcp-opentargets
  - github.com/openpharma-org/opentargets-mcp
mcp_notes: >
  Multiple community MCPs wrap the GraphQL API; none are official. Maturity varies.
  A canonical connector should expose target, disease, drug, search, and
  association-score endpoints, and abstract over the verbose GraphQL response shape.
agent_use_cases:
  - drug target identification
  - target-disease association scoring
  - drug repurposing lookups
  - genetic evidence aggregation
  - disease ontology mapping
access_test:
  command: "curl -sf -X POST 'https://api.platform.opentargets.org/api/v4/graphql' -H 'Content-Type: application/json' -d '{\"query\":\"{ target(ensemblId: \\\"ENSG00000169083\\\") { id approvedSymbol biotype } }\"}'"
  expected_status: 200
  expected_fields: [data, target, id, approvedSymbol]
last_verified: 2026-06-08
build_priority: medium
---

# Open Targets

## Why this source matters

Open Targets is a public-private partnership between EMBL-EBI, Genentech, GSK, MSD, Pfizer, Sanofi, and others, hosted at the Wellcome Genome Campus. It integrates 40+ data sources (genetic associations, somatic mutations, drugs, pathways, expression, literature) into a single target-disease association score, with full provenance back to the evidence. For drug discovery agents, it is the cleanest free entry point to "what targets are linked to this disease, and how strong is the evidence?" Secondary relevance to `bio-genomics` (target annotations) and `academic` (literature evidence with PMID/DOI links).

## Agent use cases

- drug target identification
- target-disease association scoring
- drug repurposing lookups
- genetic evidence aggregation
- disease ontology mapping

## Join strategy

Open Targets exposes canonical IDs across its entity types: `ENSEMBL_ID` and `GENE_SYMBOL` for targets, `UNIPROT_ACCESSION` for protein annotations, `CHEMBL_ID` for drugs (drug records are keyed on ChEMBL molecule IDs), `EFO_ID` for diseases and phenotypes. Literature evidence carries `PMID` and `DOI` back to source publications.

Pairs well with ChEMBL for full chemistry, ClinicalTrials.gov / EU CTIS for trial outcomes on the same drugs (via `CHEMBL_ID` to drug name to NCT trial), and OpenAlex / Europe PMC for the underlying literature behind genetic evidence.

## Access notes

**Interactive / low-volume:** GraphQL API at `https://api.platform.opentargets.org/api/v4/graphql`, no auth, no documented rate limit. POST queries with a JSON body; request only the fields you need.

**Bulk analyses:** Quarterly Parquet releases on the EBI FTP (`ftp.ebi.ac.uk/pub/databases/opentargets/platform/`) and Google Cloud Storage (`gs://open-targets-data-releases/`). Use `rsync`, `wget`, or `gsutil`. Parquet is the only published format post-25.03; a `p2j` tool converts to JSON. File paths changed after 25.03 (snake_case, singular names) so older scripts need updating.

Verify freshness by checking the latest release version in the GraphQL `meta` field or by listing the release directory on FTP.

## MCP / connector notes

Multiple community MCPs exist (`nickzren/opentargets-mcp`, `Augmented-Nature/OpenTargets-MCP-Server`, `pipeworx-io/mcp-opentargets`, `openpharma-org/opentargets-mcp`, plus pharmacogenomics aggregators). None are official; maturity varies. Common gaps: no shared schema for association-score field trimming, no caching layer for repeated target lookups, no fallback from GraphQL to bulk Parquet for large pulls. A canonical connector should expose `search_entity`, `get_target`, `get_disease`, `get_drug`, and `get_associations` with response trimming and bulk-vs-API routing.

## Review notes

None.
