---
id: orphanet
name: Orphanet
domain: clinical-biotech
entry_kind: knowledge-graph
description: Reference knowledge base of rare diseases and orphan drugs, minting the ORPHAcode nomenclature and cross-referencing it to ICD-10/11, OMIM, MONDO, UMLS, MeSH, MedDRA, genes, and phenotypes.
homepage_url: https://www.orpha.net/
docs_url: https://api.orphadata.com/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "not published; keyless public API, be polite"
bulk_available: true
frequency: "Orphadata Science files bi-annual (Jul + Dec); nomenclature pack annual (Jul)"
lag: "curation lag of months; refreshed on the fixed release cadence above"
geography: [global]
join_keys:
  - ICD_10
  - MESH_TERM
  - MEDDRA_TERM
  - GENE_SYMBOL
  - ENSEMBL_ID
  - UNIPROT_ACCESSION
primary_keys:
  - ORPHA_CODE
join_key_fields:
  - join_key: ICD_10
    fields:
      - "data.results.ExternalReference[Source=ICD-10].Reference"
  - join_key: MESH_TERM
    fields:
      - "data.results.ExternalReference[Source=MeSH].Reference"
  - join_key: MEDDRA_TERM
    fields:
      - "data.results.ExternalReference[Source=MedDRA].Reference"
  - join_key: GENE_SYMBOL
    fields:
      - data.results.DisorderGeneAssociation.Gene.Symbol
  - join_key: ENSEMBL_ID
    fields:
      - "data.results.DisorderGeneAssociation.Gene.ExternalReference[Source=Ensembl].Reference"
  - join_key: UNIPROT_ACCESSION
    fields:
      - "data.results.DisorderGeneAssociation.Gene.ExternalReference[Source=SwissProt].Reference"
mcp_status: mcp-needed-high-value
agent_use_cases:
  - rare disease name normalization
  - disease code cross-referencing
  - disease-gene lookup
  - orphan drug context
  - epidemiology and prevalence lookup
access_test:
  command: "curl -sf 'https://api.orphadata.com/rd-cross-referencing/orphacodes/558?lang=en'"
  expected_status: 200
  expected_fields:
    - data.results.ORPHAcode
    - data.results.ExternalReference
last_verified: 2026-07-02
build_priority: medium
---

# Orphanet

## Why this source matters

Orphanet is the reference knowledge base for rare diseases and orphan drugs, run by INSERM (US14) in Paris and co-funded by the EU4Health programme; it is an ELIXIR Core Data Resource. It mints the ORPHAcode, a time-stable numeric identifier for each of ~6,000+ rare clinical entities, and curates a standardised multilingual nomenclature that is the de facto vocabulary for rare-disease coding in European health systems. Each entity is aligned to ICD-10, ICD-11, OMIM, MONDO, UMLS, MeSH, and MedDRA (with the mapping precision qualified: exact, broader-than, narrower-than) and linked to associated genes, phenotypes (HPO), epidemiology, natural history, and functional consequences. Secondary domains: bio-genomics (disease-gene associations carrying HGNC, Ensembl, UniProt) and public-health (prevalence and epidemiology datasets).

## Agent use cases

- rare disease name normalization
- disease code cross-referencing
- disease-gene lookup
- orphan drug context
- epidemiology and prevalence lookup

## Join strategy

Orphanet's value is as a rare-disease crosswalk hub. The cross-referencing API returns, per ORPHAcode, an `ExternalReference` array whose `Source`/`Reference` pairs carry `ICD_10` plus several identifiers not yet canonical here (ICD-11, OMIM, MONDO, UMLS). The gene-association product carries `GENE_SYMBOL` (HGNC symbol), `ENSEMBL_ID`, and `UNIPROT_ACCESSION` (Orphanet labels UniProt as `SwissProt`), alongside HGNC and OMIM gene IDs. `MESH_TERM` and `MEDDRA_TERM` are also exposed as disease cross-references.

The native `ORPHA_CODE` is Orphanet's own primary key and is referenced back by OMIM, MONDO, Open Targets, ClinVar, and GARD, so it is a strong new-canonical-key candidate (flagged below). Pair Orphanet with Open Targets and ClinVar (gene/variant to disease), OMIM (Mendelian detail), and the HPO ecosystem (phenotype-driven retrieval). Reverse-lookup endpoints exist (`/rd-cross-referencing/icd-10s/{icd}`, `/omims/{omim}`, `/rd-phenotypes/hpoids/{hpo}`), so you can enter from an ICD-10, OMIM, or HPO code and resolve back to ORPHAcodes.

## Access notes

Hit `https://api.orphadata.com/rd-cross-referencing/orphacodes/{orphacode}?lang=en` first; it is keyless and returns the entity plus its full cross-reference set (verified 200 on ORPHA 558, Marfan syndrome). Companion namespaces on the same host: `rd-associated-genes`, `rd-phenotypes`, `rd-epidemiology`, `rd-natural_history`, `rd-classification`, `rd-medical-specialties`. The OpenAPI spec is at `https://api.orphadata.com/openapi.json`. Not every ORPHAcode has every product (a gene query on a non-genetic entity returns a 404 "Query not found" rather than an empty body). For bulk work, download the Orphadata Science files (XML/JSON) and the Orphanet Nomenclature Pack from orphadata.com rather than paginating the API; releases are fixed (nomenclature yearly in July, science files July + December), so pin the release date you used.

## MCP / connector notes

No dedicated Orphanet MCP server was found (the DeepRare agentic system is MCP-inspired but not a published server). The API is clean and keyless, but a connector is high-value because disease-name to ORPHAcode normalization plus code cross-referencing is a shared need across most biomedical entries in this registry (Open Targets, ClinVar, ClinicalTrials.gov, OMIM-adjacent sources). Suggested surface: `resolve_disease(name) -> orphacode`, `get_cross_references(orphacode)`, `get_associated_genes(orphacode)`, `get_phenotypes(orphacode)`, `reverse_lookup(icd10|omim|hpo) -> orphacodes`. The connector should abstract over the per-product 404-means-none behaviour and the `Source` string enum used inside `ExternalReference`.

## Review notes

Potential new join keys for review (exposed by Orphanet, not yet in `schema/join-keys.yaml`; do not invent into `join_keys` until PR'd):

- ORPHA_CODE
  - Entity type: rare_disease
  - Pattern: numeric string, often prefixed (e.g. `558` or `ORPHA:558`)
  - Other datasets that would use it: OMIM, MONDO, Open Targets, ClinVar, GARD, ClinicalTrials.gov condition mapping
- OMIM_ID
  - Entity type: mendelian_disease_or_gene (Orphanet exposes both disease-MIM and gene-MIM)
  - Pattern: `^[0-9]{6}$`
  - Other datasets that would use it: OMIM, ClinVar, Open Targets, MONDO, MyVariant
- ICD_11
  - Entity type: condition_code
  - Pattern: alphanumeric MMS code (e.g. `LD28.01`)
  - Other datasets that would use it: WHO ICD-11, national health information systems
- MONDO_ID
  - Entity type: disease
  - Pattern: `^(MONDO:)?[0-9]{7}$` (Orphanet returns the bare 7-digit form, e.g. `0007947`)
  - Other datasets that would use it: Open Targets, MONDO, EBI OLS
- UMLS_CUI
  - Entity type: biomedical_concept
  - Pattern: `^C[0-9]{7}$`
  - Other datasets that would use it: UMLS Metathesaurus, MedGen, DisGeNET
- HPO_ID
  - Entity type: phenotype
  - Pattern: `^HP:[0-9]{7}$`
  - Other datasets that would use it: Human Phenotype Ontology, ClinVar, DECIPHER, GA4GH phenopackets
- HGNC_ID
  - Entity type: gene
  - Pattern: `^(HGNC:)?[0-9]+$` (Orphanet returns the bare numeric form, e.g. `8941`)
  - Other datasets that would use it: HGNC, Ensembl, Open Targets, ClinVar

License note: the Orphanet Nomenclature / ORPHAcodes and the Orphadata Science files are CC-BY-4.0 (the cross-referencing API self-declares `CC-BY-4.0` in the `__licence` block of every response). Orphanet states "conditions may apply" to some other products, so a downstream commercial redistributor should confirm per-product terms. Required citation form: "Orphanet: an online rare disease and orphan drug data base. (c) INSERM 1999. Available at https://www.orpha.net" plus access date.
