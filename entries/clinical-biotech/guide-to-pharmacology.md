---
id: guide-to-pharmacology
name: IUPHAR/BPS Guide to PHARMACOLOGY
domain: clinical-biotech
entry_kind: knowledge-graph
description: Expert-curated database of quantitative drug-target interactions, linking pharmacological targets (receptors, ion channels, enzymes, transporters) to ligands (approved drugs, tool compounds, endogenous molecules).
homepage_url: https://www.guidetopharmacology.org/
docs_url: https://www.guidetopharmacology.org/webServices.jsp
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: CC-BY-SA-4.0
rate_limit: "none published; unauthenticated. Large list queries (thousands of rows) take several seconds"
bulk_available: true
frequency: "roughly triennial versioned releases (e.g. 2026.1, 2026.2)"
geography: [global]
structure: registry-snapshot
join_keys:
  - UNIPROT_ACCESSION
  - CHEMBL_ID
  - ENSEMBL_ID
  - ENTREZ_GENE_ID
  - DRUGBANK_ID
  - CHEBI_ID
  - INCHI_KEY
primary_keys:
  - GTOPDB_TARGET_ID
  - GTOPDB_LIGAND_ID
  - GTOPDB_INTERACTION_ID
  - GTOPDB_FAMILY_ID
  - GTOPDB_DISEASE_ID
join_key_fields:
  - join_key: UNIPROT_ACCESSION
    fields:
      - "targets/{id}/databaseLinks.accession[database=UniProtKB]"
  - join_key: CHEMBL_ID
    fields:
      - "targets/{id}/databaseLinks.accession[database=ChEMBL Target]"
      - "ligands/{id}/databaseLinks.accession[database=ChEMBL Ligand]"
  - join_key: ENSEMBL_ID
    fields:
      - "targets/{id}/databaseLinks.accession[database=Ensembl Gene]"
  - join_key: ENTREZ_GENE_ID
    fields:
      - "targets/{id}/databaseLinks.accession[database=Entrez Gene]"
  - join_key: DRUGBANK_ID
    fields:
      - "ligands/{id}/databaseLinks.accession[database=DrugBank Ligand]"
  - join_key: CHEBI_ID
    fields:
      - "ligands/{id}/databaseLinks.accession[database=ChEBI]"
  - join_key: INCHI_KEY
    fields:
      - "ligands/{id}/structure.inchiKey"
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/longevity-genie/pharmacology-mcp"
  - "github.com/pipeworx-io/mcp-guidetopharmacology"
mcp_notes: >
  Two community MCPs wrap the REST API. Suggested surface: search_targets, get_target,
  search_ligands, get_ligand, get_interactions (target-ligand affinities), resolve_databaseLinks
  (UniProt/ChEMBL/Ensembl cross-refs). Connector should abstract the split between the core
  record endpoint and the /databaseLinks and /structure sub-endpoints where join keys live.
agent_use_cases:
  - drug-target interaction lookup
  - target-to-ligand pharmacology retrieval
  - identifier resolution across UniProt, ChEMBL, Ensembl
  - approved-drug target annotation
  - ligand binding-affinity retrieval
access_test:
  command: "curl -sf 'https://www.guidetopharmacology.org/services/targets/1/databaseLinks'"
  expected_status: 200
  expected_fields: [accession, database, url]
last_verified: 2026-07-02
build_priority: medium
---

# IUPHAR/BPS Guide to PHARMACOLOGY

## Why this source matters

GtoPdb is the expert-curated pharmacology reference of the International Union of Basic and Clinical Pharmacology (NC-IUPHAR) and the British Pharmacological Society, covering roughly 3,000 human protein targets and 9,700 ligands (approved drugs, investigational compounds, antibodies, endogenous peptides, natural products) with quantitative interaction data (Ki, IC50, EC50) sourced from the medicinal-chemistry literature. It is the authoritative naming source for receptors and drug targets and a clean bridge between drug identity and protein identity. Primary domain here is clinical-biotech (drug-target pharmacology and approved-drug annotation); it overlaps bio-genomics heavily because every target resolves to UniProt, Ensembl, and Entrez Gene identifiers.

## Agent use cases

- drug-target interaction lookup
- target-to-ligand pharmacology retrieval
- identifier resolution across UniProt, ChEMBL, Ensembl
- approved-drug target annotation
- ligand binding-affinity retrieval

## Join strategy

Targets carry `UNIPROT_ACCESSION`, `ENSEMBL_ID`, `ENTREZ_GENE_ID`, and a `CHEMBL_ID` (ChEMBL Target) via the `/targets/{id}/databaseLinks` endpoint. Ligands carry `CHEMBL_ID` (ChEMBL Ligand), `DRUGBANK_ID`, and `CHEBI_ID` via `/ligands/{id}/databaseLinks`, plus a structure-derived `INCHI_KEY` from `/ligands/{id}/structure`. This makes GtoPdb a strong resolver hub: pair with ChEMBL for full bioactivity matrices, with UniProt for protein annotation, with Open Targets for target-disease evidence, and with DrugBank for pharmacology/pharmacokinetics.

Source-internal numeric IDs (`GTOPDB_TARGET_ID`, `GTOPDB_LIGAND_ID`, `GTOPDB_INTERACTION_ID`, `GTOPDB_FAMILY_ID`, `GTOPDB_DISEASE_ID`) are used for direct record fetches, not cross-source joins. Note that GtoPdb also exposes `PubChem CID` on ligands, which is not yet a canonical key here (flagged below), and its own target/ligand IDs are back-referenced by ChEMBL, Open Targets, and DrugCentral (also flagged).

## Access notes

REST API base is `https://www.guidetopharmacology.org/services/`, JSON, no auth, no published rate limit. Join keys do not live on the core record; hit the `/{id}/databaseLinks` sub-endpoint (targets and ligands) and `/{id}/structure` (ligands, for InChIKey/SMILES). Empty results return HTTP 204. For bulk work, full CSV and SQL database dumps are published per release on the downloads page and archived on Zenodo, better than paginating the API for whole-database pulls. Licensing is dual: database contents under CC-BY-SA-4.0, the database structure under the Open Data Commons Open Database License (ODbL-1.0); attribution and share-alike apply to redistribution.

## MCP / connector notes

Two community MCP servers exist: `longevity-genie/pharmacology-mcp` and `pipeworx-io/mcp-guidetopharmacology` (listed on Glama). Neither is official. A connector should expose target/ligand search plus interaction retrieval and, critically, abstract over the multi-endpoint shape: core record, `databaseLinks` for cross-references, and `structure` for chemical identifiers all sit at different paths. Response trimming helps since interaction lists for well-studied targets run to thousands of rows.

## Review notes

Potential new join keys for review:

- `PUBCHEM_CID` — PubChem Compound identifier. Entity type: chemical_compound. Pattern: `^[0-9]+$`. Exposed by GtoPdb ligands (`ligands/{id}/databaseLinks.accession[database=PubChem CID]`); also emitted by ChEMBL, DrugBank, ChEBI, PubChem itself. High cross-source utility; strong candidate.
- `GTOPDB_TARGET_ID` / `GTOPDB_LIGAND_ID` — GtoPdb native numeric target and ligand IDs. Entity types: pharmacological_target, ligand. Pattern: `^[0-9]+$`. Currently in `primary_keys`, but ChEMBL, Open Targets, and DrugCentral back-reference them, so they may warrant promotion to canonical join keys. Flagged per the join-key hint; not invented into `join_keys`.

License nuance (dual CC-BY-SA-4.0 / ODbL-1.0) is captured in Access notes; `license` field carries the content license CC-BY-SA-4.0. Confirm which the registry prefers for dual-licensed data sources.
