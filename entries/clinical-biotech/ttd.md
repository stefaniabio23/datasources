---
id: ttd
name: Therapeutic Target Database (TTD)
domain: clinical-biotech
entry_kind: knowledge-graph
description: Curated database of therapeutic protein and nucleic-acid targets linked to their drugs, diseases, biomarkers and pathways, classified by target druggability and development status.
homepage_url: https://db.idrblab.net/ttd/
docs_url: https://db.idrblab.net/ttd/help
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free-non-commercial
license: CC-BY-NC-4.0
bulk_available: true
frequency: biennial
lag: "curated release cadence; major versions roughly every two years (2018, 2020, 2022, 2024)"
geography: [global]
join_keys:
  - UNIPROT_ACCESSION
  - GENE_SYMBOL
  - PDB_ID
  - CHEBI_ID
  - ATC_CODE
primary_keys:
  - TTD_TARGET_ID
  - TTD_DRUG_ID
join_key_fields:
  - join_key: UNIPROT_ACCESSION
    fields: [UNIPROID]
  - join_key: GENE_SYMBOL
    fields: [GENENAME]
  - join_key: PDB_ID
    fields: [PDBSTRUC]
  - join_key: CHEBI_ID
    fields: [CHEBI_ID]
  - join_key: ATC_CODE
    fields: [SUPDRATC]
mcp_status: mcp-needed-high-value
mcp_notes: >
  No API to wrap; an MCP should ingest the flat P1/P2 download files and serve
  target-by-druggability-class, drug-by-target and target-to-disease lookups.
  Suggested surface: search_target, get_target_drugs, get_target_diseases,
  get_drug_crossrefs, list_targets_by_status.
agent_use_cases:
  - target druggability triage
  - drug-to-target lookup
  - target-disease association
  - drug cross-reference resolution
  - biomarker-disease lookup
access_test:
  command: "curl -sfL 'https://ttd.idrblab.cn/files/download/P2-01-TTD_uniprot_all.txt' | head"
  expected_status: 200
  expected_fields: [TARGETID, UNIPROID]
last_verified: 2026-07-02
structure: registry-snapshot
build_priority: medium
---

# Therapeutic Target Database (TTD)

## Why this source matters

TTD is a curated repository of known and explored therapeutic protein and nucleic-acid targets, the diseases they address, the pathways they sit in, and the drugs directed at each. It is built by the Innovative Drug Research and Bioinformatics (IDRB) Lab at Zhejiang University with the Bioinformatics and Drug Design Group at the National University of Singapore. The 2024 release covers 3,730 targets and 39,862 drugs. Its distinctive axis is target druggability status: every target is graded as successful, clinical-trial, preclinical/patented, or literature-reported, and every drug carries a highest-clinical-status. That development-stage lens complements the bioactivity focus of ChEMBL and the genetics-evidence focus of Open Targets, both also in `clinical-biotech`. Access is free without login; the associated Nucleic Acids Research paper is released under a Creative Commons Attribution-NonCommercial licence.

## Agent use cases

- target druggability triage
- drug-to-target lookup
- target-disease association
- drug cross-reference resolution
- biomarker-disease lookup

## Join strategy

Targets carry a UniProt identifier (`UNIPROID`, exposed as the UniProt entry-name/mnemonic form such as `FGFR1_HUMAN`, not the accession) and an HGNC gene symbol (`GENENAME`), plus PDB structure IDs (`PDBSTRUC`). Join on `UNIPROT_ACCESSION` after a one-step UniProt entry-name-to-accession resolution, or join directly on `GENE_SYMBOL` and `PDB_ID`. The drug cross-matching file (`P1-03`) resolves TTD drugs to `CHEBI_ID` and SuperDrug ATC codes (`SUPDRATC`, mapped to `ATC_CODE`), alongside PubChem CID/SID and CAS numbers that have no canonical key yet (flagged below).

Source-internal identifiers are TTD Target ID (`TARGETID`, `T`-prefix) and TTD Drug ID (`TTDDRUID`, `D`-prefix); both live in `primary_keys`. Pair TTD with ChEMBL/BindingDB for potency data on the same targets, with Open Targets for genetic-association evidence, and with DrugBank for approval and pharmacology detail.

## Access notes

There is no documented public REST API; the web batch-search form and per-record pages are JS-rendered. The reliable programmatic path is the flat download files under `https://ttd.idrblab.cn/files/download/` (the `db.idrblab.net/ttd/` host 302-redirects there). Key files: `P1-01-TTD_target_download.txt` (targets, UniProt, gene, PDB, drug list), `P1-03-TTD_crossmatching.txt` (drug cross-references: PubChem, CAS, ChEBI, ATC), `P1-06-Target_disease.txt`, `P1-08-Biomarker_disease.txt`, `P2-01-TTD_uniprot_all.txt`. Files are colon-free key-value plain text with a header abbreviation index; parse per-record blocks keyed by the leading ID column. Check the `Version` line in any file header (currently `10.1.01 (2024.01.10)`) to confirm freshness. The database itself does not publish an explicit machine-readable licence file; the non-commercial term is inferred from the NAR article and TTD's historical academic-use terms.

## MCP / connector notes

No MCP exists. High value because target/drug resolution overlaps several `clinical-biotech` and `bio-genomics` entries (ChEMBL, DrugBank, Open Targets, Guide to Pharmacology, UniProt). Since there is no live API, the connector should ingest the P1/P2 bulk files into a local store and expose `search_target`, `get_target_drugs`, `get_target_diseases`, `get_drug_crossrefs`, and `list_targets_by_status`. The MCP must abstract over the idiosyncratic key-value block format and normalise the UniProt entry-name field to accessions.

## Review notes

- License uncertainty: the `CC-BY-NC-4.0` value is inferred from the associated NAR 2024 article and TTD's stated free/non-commercial academic access; the database publishes no explicit licence file or version. Confirm exact terms before any redistribution.
- `CHEMBL_ID` was hinted but NOT included: the target file's `SCHEMBL...` values are SureChEMBL (patent-extracted structure) IDs, not ChEMBL molecule IDs, and no true `CHEMBL[0-9]+` identifier was found in the bulk files. ChEMBL cross-links may appear only on web pages.
- Potential new join keys for review (present in TTD, absent from `schema/join-keys.yaml`):
  - `PUBCHEM_CID` — entity: chemical_compound; pattern `^[0-9]+$` (field `PUBCHCID`); also used by DrugBank, DrugCentral, PubChem, GtoPdb. High cross-source value.
  - `CAS_NUMBER` — entity: chemical_substance; pattern `^[0-9]{2,7}-[0-9]{2}-[0-9]$` (field `CASNUMBE`); used by many drug/chemical sources.
  - `ICD_11` — entity: condition_code; TTD classifies diseases by WHO ICD-11, while the registry only has `ICD_10`.
  - `TTD_TARGET_ID` / `TTD_DRUG_ID` — currently in `primary_keys`; promote to canonical keys if other datasets reference them.
- `UNIPROID` carries the UniProt entry name (mnemonic), not the accession; `UNIPROT_ACCESSION` is listed because the linkage is genuine and 1:1-resolvable, but joins need a mnemonic-to-accession mapping step.
