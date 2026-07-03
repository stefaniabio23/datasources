---
id: drugcentral
name: DrugCentral
domain: clinical-biotech
entry_kind: knowledge-graph
description: Open online drug compendium of approved and off-market drugs linking structures, mechanism-of-action targets, indications, ATC classes, FAERS signals, and a dense external-identifier crosswalk.
homepage_url: https://drugcentral.org/
docs_url: https://drugcentral.org/download
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: CC-BY-SA-4.0
rate_limit: "no published limit; shared public REST API + read-only Postgres, responsiveness varies with load"
bulk_available: true
frequency: "roughly biennial major releases; latest dump 2023-11-01"
lag: "months-to-years; approvals appear at the next database release, not continuously"
geography: [global]
join_keys:
  - INCHI_KEY
  - CHEMBL_ID
  - DRUGBANK_ID
  - UNII
  - RXNORM_CUI
  - CHEBI_ID
  - ATC_CODE
  - NDC
  - MEDDRA_TERM
  - UNIPROT_ACCESSION
  - GENE_SYMBOL
primary_keys:
  - DRUGCENTRAL_STRUCT_ID
join_key_fields:
  - join_key: INCHI_KEY
    fields: [structures.inchikey]
  - join_key: CHEMBL_ID
    fields:
      - "identifier.identifier (id_type=ChEMBL_ID)"
  - join_key: DRUGBANK_ID
    fields:
      - "identifier.identifier (id_type=DRUGBANK_ID)"
  - join_key: UNII
    fields:
      - "identifier.identifier (id_type=UNII)"
  - join_key: RXNORM_CUI
    fields:
      - "identifier.identifier (id_type=RXNORM)"
  - join_key: CHEBI_ID
    fields:
      - "identifier.identifier (id_type=CHEBI)"
  - join_key: ATC_CODE
    fields: [atc.code, struct2atc.atc_code]
  - join_key: NDC
    fields: [product.ndc_product_code]
  - join_key: MEDDRA_TERM
    fields: [faers.meddra_name, faers.meddra_code]
  - join_key: UNIPROT_ACCESSION
    fields: [act_table_full.accession]
  - join_key: GENE_SYMBOL
    fields: [act_table_full.gene]
mcp_status: mcp-needed-high-value
agent_use_cases:
  - drug identifier crosswalk resolution
  - mechanism-of-action and target lookup
  - approved-drug indication retrieval
  - ATC class enrichment
  - adverse-event signal lookup
access_test:
  command: "curl -sf 'https://uxn2ycvimg.us-east-2.awsapprunner.com/structures/id/5392'"
  expected_status: 200
  expected_fields: [inchikey, smiles, name, cas_reg_no]
last_verified: 2026-07-02
build_priority: high
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: true
---

# DrugCentral

## Why this source matters

DrugCentral is an open online drug compendium maintained by the Translational Informatics Division at the University of New Mexico (Tudor Oprea's group, with Oleg Ursu and collaborators), part of the NIH IDG "Illuminating the Druggable Genome" program and published/updated in Nucleic Acids Research (2017, 2019, 2021, 2023). It covers ~5,000 active pharmaceutical ingredients and ~150,000 pharmaceutical products spanning FDA-, EMA-, and PMDA-approved drugs plus off-market and (as of 2023) veterinary agents. Each drug fuses chemical structure (SMILES/InChI), regulatory approval status, ATC classification, mechanism-of-action targets with UniProt accessions and gene symbols, disease indications (SNOMED-CT / OMOP vocabularies), FAERS adverse-event signals stratified by sex and age, and a dense crosswalk of external identifiers. Where ChEMBL centres on bioactivity assays and DrugBank sits behind a license wall, DrugCentral is fully open (CC-BY-SA-4.0, no registration) and ships a complete PostgreSQL database plus a public REST API, which makes it the cheapest open hub for resolving one drug identifier into all the others. Secondary relevance to `bio-genomics` (drug-target act tables) and `public-health` (FAERS demographic slices).

## Agent use cases

- drug identifier crosswalk resolution
- mechanism-of-action and target lookup
- approved-drug indication retrieval
- ATC class enrichment
- adverse-event signal lookup

## Join strategy

DrugCentral's load-bearing value is its identifier crosswalk. Structures carry `INCHI_KEY` (`structures.inchikey`, alongside InChI/SMILES). The `identifier` xref table maps each structure to `CHEMBL_ID`, `DRUGBANK_ID`, `UNII`, `RXNORM_CUI`, and `CHEBI_ID` (source-side `id_type` values `ChEMBL_ID`, `DRUGBANK_ID`, `UNII`, `RXNORM`, `CHEBI`), plus PubChem CID, KEGG, UMLS CUI, SNOMED CT, INN, and CAS RN. `ATC_CODE` comes from the `atc` / `struct2atc` tables, `NDC` from the `product` table, and `MEDDRA_TERM` from the `faers` adverse-event tables. The `act_table_full` drug-target table resolves targets to `UNIPROT_ACCESSION` (`accession`) and `GENE_SYMBOL` (`gene`).

The DrugCentral-internal primary key is `struct_id` (`DRUGCENTRAL_STRUCT_ID`, exposed as `structures.id` / `struct_id` across tables), which uniquely identifies each active-ingredient structure; it is intentionally outside the canonical registry, so use it for direct DrugCentral lookups, not cross-source joins.

Common pairings: ChEMBL (bioactivity for the same `CHEMBL_ID`), DrugBank (`DRUGBANK_ID`), openFDA / DailyMed (`UNII`, `NDC`, `RXNORM_CUI`), Open Targets (`UNIPROT_ACCESSION` / `GENE_SYMBOL` target-disease evidence), PubChem (structure via `INCHI_KEY`). DrugCentral is the recommended free resolver to seed any of these joins.

Note: the task hint flagged `RXNORM_CUI` as a candidate, but it already exists in `schema/join-keys.yaml`, so it is mapped directly here rather than flagged. New-key candidates DrugCentral also carries but the registry lacks (`PUBCHEM_CID`, `CAS_RN`, `UMLS_CUI`, `SNOMED_CT_ID`, `KEGG_DRUG_ID`) are flagged in Review notes.

## Access notes

Three access paths, all no-auth:

1. **Public REST API (DrugCentral DRS API):** base `https://uxn2ycvimg.us-east-2.awsapprunner.com`, interactive OpenAPI docs at `/docs`. Table-shaped endpoints: `/structures/id/{id}` and `/structures/inchikey/{inchikey}` for chemistry, `/identifier/struct_id/{struct_id}` for the full cross-reference set, `/struct2atc/struct_id/{struct_id}` for ATC, `/act_table_full/struct_id/{struct_id}` for drug-target rows (UniProt/gene/affinity), `/faers/struct_id/{struct_id}` for adverse events. Supports `skip`/`limit` paging and `/csv` + `/tsv` variants. This is an AWS App Runner deployment, so treat availability as best-effort.
2. **Public read-only PostgreSQL:** host `unmtid-dbs.net`, port `5433`, database `drugcentral`, user `drugman`, password `dosage` (DrugCentral's own published public credentials, not secrets; responsiveness varies with load). Best for relational joins and bulk pulls; query with `psql` or any Postgres driver.
3. **Bulk download** at `https://drugcentral.org/download`: full PostgreSQL v14.5 dump (latest 2023-11-01), drug-target interaction TSVs, FDA/EMA/PMDA approvals CSVs, SMILES/InChI TSV, and SDF (MOL V2000/V3000). A DockerHub image of the Postgres backend is also published.

No documented rate limit. Verify freshness via the dump date on the download page or `SELECT * FROM dbversion;` on the live instance. The `access_test` REST call was executed and returned HTTP 200.

## MCP / connector notes

No dedicated DrugCentral MCP found (searched modelcontextprotocol org/registry, GitHub, npm, PyPI as of 2026-07). Nearest neighbours are the unofficial `openpharma-org/drugbank-mcp-server` and general healthcare MCPs, none of which wrap DrugCentral.

High-value connector target: three or more drug-data entries in this registry (ChEMBL, DrugBank, RxNorm, openFDA) want the same identifier-resolution surface, and DrugCentral is the open one that can back it. Suggested surface: `resolve_identifier` (any of InChIKey/ChEMBL/RxCUI/UNII/DrugBank/ChEBI/ATC to struct_id), `get_drug` (full record by struct_id or name), `get_targets` (act rows with UniProt/gene/affinity), `get_indications` (SNOMED/OMOP disease links), `get_adverse_events` (FAERS, sex/age strata), `substructure_search` (SMILES). The connector should abstract over the two backends (REST API vs direct Postgres), normalise the wide `identifier` `id_type` vocabulary into a clean canonical-key map, trim verbose `structures` rows (molfile/descriptor columns) by default, and cache aggressively since data changes only at release boundaries.

## Review notes

- License is `CC-BY-SA-4.0` (SPDX). ShareAlike means derivative datasets that redistribute DrugCentral content must carry the same license; note for any downstream product that embeds it.
- `RXNORM_CUI` is already in `schema/join-keys.yaml`, so it is placed in `join_keys` (the task hint marked it a candidate, but the registry already has it).
- `MESH_TERM` was deliberately NOT added: DrugCentral exposes MeSH Descriptor / Supplemental Record UIDs (`id_type` `MESH_DESCRIPTOR_UI`, `MESH_SUPPLEMENTAL_RECORD_UI`), not MeSH term strings, so it does not cleanly match the registry's `MESH_TERM` (term text). See MeSH-UID candidate below.
- Potential new join key for review: PUBCHEM_CID
  - Entity type: chemical_compound
  - Pattern: `^[0-9]+$` (PubChem Compound ID; identifier id_type `PUBCHEM_CID`)
  - Other datasets that would use it: PubChem, ChEMBL, DrugBank, openFDA, most cheminformatics sources (already noted in the DrugBank entry; consolidate on promotion)
- Potential new join key for review: CAS_RN
  - Entity type: chemical_substance
  - Pattern: `^[0-9]{2,7}-[0-9]{2}-[0-9]$` (CAS Registry Number; `structures.cas_reg_no`)
  - Other datasets that would use it: DrugBank, ChemIDplus, CompTox, PubChem
- Potential new join key for review: UMLS_CUI
  - Entity type: biomedical_concept
  - Pattern: `^C[0-9]{7}$` (UMLS Concept Unique Identifier; `omop_relationship.umls_cui`, identifier id_type `UMLSCUI`)
  - Other datasets that would use it: OMOP-vocabulary sources, MeSH crosswalks, indication datasets
- Potential new join key for review: SNOMED_CT_ID
  - Entity type: clinical_concept
  - Pattern: `^[0-9]{6,18}$` (SNOMED CT concept id; `omop_relationship.snomed_conceptid`, id_type `SNOMEDCT_US`)
  - Other datasets that would use it: OHDSI/OMOP vocabularies, EHR/claims indication mapping
- Potential new join key for review: KEGG_DRUG_ID
  - Entity type: drug
  - Pattern: `^D[0-9]{5}$` (KEGG DRUG identifier; id_type `KEGG_DRUG`)
  - Other datasets that would use it: KEGG, pathway/MoA sources
- Potential new join key for review: MESH_UID (MeSH Descriptor/Supplemental Unique ID, e.g. `D010975` / `C000613976`), distinct from the registry's term-text `MESH_TERM`. Other datasets that would use it: PubMed/MeSH-indexed sources, CTD.
- `join_key_fields` paths use DrugCentral relational table.column names (with an `id_type` parenthetical for the shared `identifier` table) rather than JSON paths, since the source is relational. All paths were confirmed against the live public REST API on 2026-07-02.
