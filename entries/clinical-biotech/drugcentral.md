---
id: drugcentral
name: DrugCentral
domain: clinical-biotech
entry_kind: registry
description: Open online drug compendium of approved and off-market drugs with structures, targets, indications, pharmacologic action, regulatory approvals, and a dense external-identifier crosswalk.
homepage_url: https://drugcentral.org/
docs_url: https://drugcentral.org/download
type:
  - database
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-SA-4.0
rate_limit: "public read-only PostgreSQL instance; no published cap; polite use expected"
bulk_available: true
frequency: "irregular major releases (roughly every 1-2 years); latest dump 2023-11-01"
lag: "months-to-years; approvals appear at the next database release, not continuously"
geography: [global]
join_keys:
  - INCHI_KEY
  - CHEMBL_ID
  - ATC_CODE
  - RXNORM_CUI
  - UNII
  - DRUGBANK_ID
  - CHEBI_ID
  - MESH_TERM
  - UNIPROT_ACCESSION
  - GENE_SYMBOL
primary_keys:
  - DRUGCENTRAL_STRUCT_ID
join_key_fields:
  - join_key: INCHI_KEY
    fields: [structures.inchikey]
  - join_key: CHEMBL_ID
    fields: ["identifier (id_type=ChEMBL_ID)"]
  - join_key: ATC_CODE
    fields: [struct2atc.atc_code, atc.code]
  - join_key: RXNORM_CUI
    fields: ["identifier (id_type=RxNorm)"]
  - join_key: UNII
    fields: [structures.unii, "identifier (id_type=UNII)"]
  - join_key: DRUGBANK_ID
    fields: ["identifier (id_type=DRUGBANK_ID)"]
  - join_key: CHEBI_ID
    fields: ["identifier (id_type=ChEBI)"]
  - join_key: MESH_TERM
    fields: [pharma_class, omop_relationship]
  - join_key: UNIPROT_ACCESSION
    fields: [act_table_full.accession]
  - join_key: GENE_SYMBOL
    fields: [act_table_full.gene]
mcp_status: mcp-needed-high-value
agent_use_cases:
  - drug identifier crosswalk resolution
  - mechanism-of-action and target lookup
  - approved-drug indication retrieval
  - substructure and similarity chemical search
  - drug repositioning candidate discovery
access_test:
  command: "PGPASSWORD=dosage psql -h unmtid-dbs.net -p 5433 -U drugman -d drugcentral -c \"SELECT id, name, inchikey FROM structures LIMIT 1;\""
  expected_fields: [id, name, inchikey]
last_verified: 2026-07-02
build_priority: medium
notes: "access_test constructed but not executed (no psql client in this environment). Uses DrugCentral's published public read-only credentials (drugman/dosage) against unmtid-dbs.net:5433."
---

# DrugCentral

## Why this source matters

DrugCentral is an open online drug compendium maintained by the Translational Informatics Division at the University of New Mexico (Tudor Oprea's group, with Oleg Ursu and collaborators), published and updated in Nucleic Acids Research (2017, 2019, 2021, 2023). It covers ~5,000 active pharmaceutical ingredients and ~150,000 pharmaceutical products, spanning FDA-, EMA-, and PMDA-approved drugs plus off-market and veterinary agents. Each drug fuses chemical structure (SMILES/InChI), regulatory approval status, ATC classification, mechanism-of-action targets with UniProt accessions and gene symbols, disease indications (mapped to SNOMED-CT and OMOP vocabularies), pharmacologic action (MeSH, ChEBI), FAERS adverse-event signals stratified by sex and age, and a dense crosswalk of external identifiers. Where ChEMBL centres on bioactivity assays and DrugBank sits behind a license wall, DrugCentral is fully open (CC-BY-SA-4.0, no registration) and ships as a complete PostgreSQL database, which makes it the cheapest open hub for resolving one drug identifier into all the others. Secondary relevance to `bio-genomics` (drug-target act tables) and `public-health` (FAERS demographic slices).

## Agent use cases

- drug identifier crosswalk resolution
- mechanism-of-action and target lookup
- approved-drug indication retrieval
- substructure and similarity chemical search
- drug repositioning candidate discovery

## Join strategy

DrugCentral's load-bearing value is its identifier crosswalk. Structures carry `INCHI_KEY` (and InChI/SMILES). The `identifier` xref table maps each structure to `CHEMBL_ID`, `RXNORM_CUI`, `UNII`, `DRUGBANK_ID`, `CHEBI_ID`, plus PubChem CID, KEGG, UMLS CUI, INN, and CAS RN. `ATC_CODE` comes from the `struct2atc`/`atc` tables. The `act_table_full` drug-target table resolves targets to `UNIPROT_ACCESSION` and `GENE_SYMBOL`. Pharmacologic action and indications surface `MESH_TERM`.

The DrugCentral-internal primary key is `struct_id` (`DRUGCENTRAL_STRUCT_ID`), which uniquely identifies each active ingredient structure; it is intentionally outside the canonical registry, so use it for direct DrugCentral lookups, not cross-source joins.

Common pairings: ChEMBL (bioactivity for the same `CHEMBL_ID`), DrugBank (`DRUGBANK_ID` for licensed pharmacology detail), openFDA / RxNorm (`RXNORM_CUI` to FAERS and clinical drug concepts), Open Targets (`UNIPROT_ACCESSION`/`GENE_SYMBOL` target-disease evidence), PubChem (structure via `INCHI_KEY`). DrugCentral is the recommended free resolver to seed any of these joins.

New-key candidates that DrugCentral also carries but are not yet in the registry: `PUBCHEM_CID`, `SNOMED_CT` (indication mapping), `CAS_RN`. Flagged in Review notes.

## Access notes

Primary programmatic path is the public read-only PostgreSQL instance: host `unmtid-dbs.net`, port `5433`, database `drugcentral`, user `drugman`, password `dosage` (these are DrugCentral's own published public credentials, documented on the download page and in the BioClients client, not secrets). Query it directly with `psql` or any Postgres driver; the full relational schema (structures, identifier, act_table_full, struct2atc, omop_relationship, faers) is queryable without registration.

Bulk path: the complete database dump (`.sql.gz`, v14.5, dated 2023-11-01) plus TSV drug-target interactions, SDF (MOL V2000/V3000), SMILES/InChI structure files, and FDA/EMA/PMDA approved-drug CSVs from `https://drugcentral.org/download`. A DockerHub image of the Postgres backend is also published for local deployment.

There is no clean public REST API; the BioClients Python client (`BioClients.drugcentral.Client`) wraps SQL queries against the public Postgres instance rather than an HTTP endpoint. Verify freshness by checking the dump date on the download page (currently 2023-11-01) or `SELECT * FROM dbversion;` on the live instance. The `access_test` psql command was constructed but not executed here (no psql client available).

## MCP / connector notes

No dedicated DrugCentral MCP found (searched modelcontextprotocol org/registry, GitHub, npm, PyPI as of 2026-07). The nearest neighbours are the unofficial `openpharma-org/drugbank-mcp-server` and general healthcare MCPs, none of which wrap DrugCentral.

High-value connector target: three or more drug-data entries in this registry (ChEMBL, DrugBank, RxNorm, openFDA) want the same identifier-resolution surface, and DrugCentral is the open one that can back it. Suggested surface: `resolve_identifier` (any of InChIKey/ChEMBL/RxCUI/UNII/DrugBank/ATC to struct_id), `get_drug` (full record by struct_id or name), `get_targets` (drug-target act rows with UniProt/gene/affinity), `get_indications` (SNOMED/OMOP disease links), `substructure_search` (SMILES). The connector must abstract over raw SQL against the public Postgres (parameterised, read-only, injection-safe), normalise the wide `identifier` xref table into a clean id-type map, and cache aggressively since the underlying data changes only at release boundaries.

## Review notes

- License is `CC-BY-SA-4.0` (SPDX). ShareAlike means derivative datasets that redistribute DrugCentral content must carry the same license; note for any downstream product that embeds it.
- Potential new join key for review: `PUBCHEM_CID`. Entity type: `chemical_compound`. Pattern: `^[0-9]+$`. Other datasets that would use it: PubChem, ChEMBL, ChEBI, DrugBank, every cheminformatics source. Already flagged in the DrugBank entry; consolidate when promoting.
- Potential new join key for review: `SNOMED_CT`. Entity type: `clinical_finding_or_disease`. Pattern: `^[0-9]{6,18}$` (SNOMED CT concept id). Other datasets that would use it: OHDSI/OMOP vocabularies, DrugCentral indications, UMLS crosswalks, NHS/clinical coding sources.
- Potential new join key for review: `CAS_RN`. Entity type: `chemical_substance`. Pattern: `^[0-9]{2,7}-[0-9]{2}-[0-9]$`. Other datasets that would use it: PubChem, ChemIDplus, CompTox, EPA, most chemistry registries.
- `RXNORM_CUI` is already in `schema/join-keys.yaml`, so it is placed in `join_keys` (the task hint marked it a candidate, but the registry already has it).
- `type` omits `rest-api`: DrugCentral's programmatic access is the public PostgreSQL instance and bulk dumps, not a documented HTTP API. Modelled as `database` + `bulk-download` + `web-ui`. Revisit if an official REST/OpenAPI endpoint is confirmed live.
- `access_test` uses DrugCentral's published public Postgres credentials and was not executed (no psql client in this environment). It is a database query, not an HTTP call, so `expected_status` is omitted.
- `join_key_fields` paths use DrugCentral table names with an `id_type` parenthetical (e.g. `identifier (id_type=ChEMBL_ID)`) rather than JSON paths, since the source is relational. Exact column names for a few xref types were inferred from the documented schema; verify against `list_xref_types` on the live instance before relying on precise column paths.
