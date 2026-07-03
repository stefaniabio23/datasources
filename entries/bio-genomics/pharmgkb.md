---
id: pharmgkb
name: PharmGKB
domain: bio-genomics
entry_kind: knowledge-graph
description: Curated pharmacogenomics knowledge base linking genes, variants, drugs, and diseases to drug-response phenotypes, clinical annotations, dosing guidelines, and annotated drug labels.
homepage_url: https://www.pharmgkb.org/
docs_url: https://api.pharmgkb.org/swagger/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC-BY-SA-4.0
bulk_available: true
geography: [global]
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: true
join_keys:
  - RSID
  - GENE_SYMBOL
  - ENSEMBL_ID
  - ENTREZ_GENE_ID
  - UNIPROT_ACCESSION
  - RXNORM_CUI
  - DRUGBANK_ID
  - CHEBI_ID
  - ATC_CODE
  - NDC
  - MESH_TERM
  - NCT_ID
  - PMID
  - PMCID
  - DOI
primary_keys:
  - PHARMGKB_ID
join_key_fields:
  - join_key: RSID
    fields: [symbol]
  - join_key: GENE_SYMBOL
    fields: [symbol]
  - join_key: ENSEMBL_ID
    fields: ["crossReferences[resource=Ensembl].resourceId"]
  - join_key: ENTREZ_GENE_ID
    fields: ["crossReferences[resource=NCBI Gene].resourceId"]
  - join_key: UNIPROT_ACCESSION
    fields: ["crossReferences[resource=UniProtKB].resourceId"]
  - join_key: RXNORM_CUI
    fields: ["linkOuts[resource=RxNorm].resourceId"]
  - join_key: DRUGBANK_ID
    fields: ["linkOuts[resource=DrugBank].resourceId"]
  - join_key: CHEBI_ID
    fields: ["linkOuts[resource=ChEBI].resourceId"]
  - join_key: ATC_CODE
    fields: ["linkOuts[resource=ATC].resourceId"]
  - join_key: NDC
    fields: ["linkOuts[resource=NDC].resourceId"]
  - join_key: MESH_TERM
    fields: ["linkOuts[resource=MeSH].resourceId"]
  - join_key: NCT_ID
    fields: ["linkOuts[resource=ClinicalTrials.gov].resourceId"]
  - join_key: PMID
    fields: ["crossReferences[resource=PubMed].resourceId"]
  - join_key: PMCID
    fields: ["crossReferences[resource=PubMed Central].resourceId"]
  - join_key: DOI
    fields: ["crossReferences[resource=DOI].resourceId"]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - pharmacogenomic variant-drug lookup
  - CPIC dosing-guideline retrieval
  - annotated drug-label search
  - gene-drug clinical annotation lookup
  - variant to drug-response phenotype mapping
access_test:
  command: "curl -sf 'https://api.pharmgkb.org/v1/data/gene?symbol=VKORC1&view=base'"
  expected_status: 200
  expected_fields: [data, status]
last_verified: 2026-07-02
build_priority: medium
---

# PharmGKB

## Why this source matters

PharmGKB is the reference pharmacogenomics knowledge base: a manually curated graph connecting genes, sequence variants, drugs, and diseases to drug-response phenotypes. Run by Stanford University and funded by the US NIH (NIGMS), it aggregates clinical annotations (variant-drug associations graded by evidence level), CPIC and other dosing guidelines, annotated FDA/EMA/PMDA drug labels with PGx information, curated pathways, and VIP (Very Important Pharmacogene) summaries. It is the bridge layer between raw genomics (dbSNP, ClinVar, Ensembl) and clinical pharmacology (drug labels, dosing decisions), so it carries a secondary `clinical-biotech` character. As of 2025 PharmGKB has been folded into the ClinPGx umbrella (with CPIC, PharmVar, PharmCAT); `pharmgkb.org` now redirects to `clinpgx.org` and the API is served from both `api.pharmgkb.org` and `api.clinpgx.org`.

## Agent use cases

- pharmacogenomic variant-drug lookup
- CPIC dosing-guideline retrieval
- annotated drug-label search
- gene-drug clinical annotation lookup
- variant to drug-response phenotype mapping

## Join strategy

PharmGKB is a dense cross-reference hub. Variant objects carry the dbSNP `RSID` as their symbol; gene objects carry the HGNC `GENE_SYMBOL` plus cross-references to `ENSEMBL_ID` (Ensembl), `ENTREZ_GENE_ID` (NCBI Gene), and `UNIPROT_ACCESSION` (UniProtKB). Chemical/drug objects expose `linkOuts` to `RXNORM_CUI`, `DRUGBANK_ID`, `CHEBI_ID`, `ATC_CODE`, `NDC`, and `MESH_TERM`, and even link out to trials via `NCT_ID`. Literature and annotation objects carry `PMID`, `PMCID`, and `DOI`.

Cross-references live in two array fields: `crossReferences` (genes, literature) and `linkOuts` (chemicals), each element an object with `resource` + `resourceId`. The `join_key_fields` paths use a `[resource=X]` filter to name the element that carries each canonical key.

Every PharmGKB entity has a native `PA####` accession (`PHARMGKB_ID`) that spans genes, variants, drugs, guidelines, and pathways. It is heavily reused by CPIC, PharmVar, and PharmCAT, so it is a strong candidate for promotion to a canonical join key (flagged below). Use it for direct PharmGKB record fetches; use the canonical keys above to stitch PharmGKB into ClinVar (RSID), Open Targets / Ensembl (ENSEMBL_ID), and openFDA / DrugBank / ChEMBL (drug identifiers).

## Access notes

Hit the REST API first: base URL `https://api.pharmgkb.org/v1`, JSON responses, no authentication. Useful entry points are `/data/gene?symbol=...`, `/data/variant?symbol=rs...`, `/data/chemical?name=...`, `/data/clinicalAnnotation/{id}`, and `/data/label/{id}`. Add `view=base|max` to control payload verbosity (`max` pulls linkOuts and cross-references). The Swagger UI at `https://api.pharmgkb.org/swagger/` and the OpenAPI spec at `https://api.pharmgkb.org/openapi.json` are the authoritative reference; PharmGKB warns that endpoint parameters and response shapes may change without notice.

For anything analytical, prefer the bulk downloads (`clinpgx.org/downloads`): TSV/zip archives of clinical annotations, variant annotations, drug labels, relationships, genes, chemicals, phenotypes, and pathways, refreshed on a periodic (roughly monthly) cadence. Check the download page's file dates to confirm freshness; the registry does not track a fixed release schedule.

License is CC-BY-SA-4.0, but the ClinPGx Data Usage Policy adds terms: attribution is required, redistribution must preserve ShareAlike, and CPIC dosing content plus some third-party cross-referenced data (e.g. DrugBank) carry their own upstream restrictions. Commercial redistribution should be checked against the policy rather than assumed from the SPDX code alone. No documented hard rate limit; be polite on the API.

## MCP / connector notes

No MCP server exists. Audience is narrower than a general biomedical connector, so this is a low-value build for now, though it converges with clinical-trial and drug-safety agents already in the directory. A useful surface would abstract the drug+gene -> clinical-annotation lookup, CPIC guideline retrieval by drug or gene, drug-label PGx extraction, and variant-to-phenotype resolution, while trimming the verbose `crossReferences`/`linkOuts` arrays down to the canonical identifiers an agent actually joins on. The connector must abstract over the two-field cross-reference model (`crossReferences` vs `linkOuts`) and the `view=base|max` verbosity switch. Until then the API is clean enough to call directly.

## Review notes

Potential new join key for review: PHARMGKB_ID
  Entity type: pharmacogenomic entity (gene, variant, drug, guideline, pathway, phenotype)
  Pattern: ^PA[0-9]+$
  Other datasets that would use it: CPIC, PharmVar, PharmCAT, and PharmGKB-derived annotations reference PA accessions directly; strong cross-source utility within pharmacogenomics.

License nuance: SPDX `CC-BY-SA-4.0` is recorded, but the ClinPGx Data Usage Policy layers attribution/ShareAlike and third-party (CPIC, DrugBank) restrictions on top. Confirm the canonical short-name convention if a "ClinPGx-Data-Usage-Policy" qualifier is wanted; kept as the SPDX code with nuance in Access notes per SCHEMA.md guidance.

Rebrand: PharmGKB is now part of ClinPGx; `pharmgkb.org` 301-redirects to `clinpgx.org`. `homepage_url` kept as the requested `pharmgkb.org`. Consider whether the canonical homepage should migrate to `clinpgx.org`.
