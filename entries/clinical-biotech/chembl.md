---
id: chembl
name: ChEMBL
domain: clinical-biotech
entry_kind: registry
description: Manually curated database of bioactive molecules with drug-like properties, integrating chemistry, bioactivity, and target/genomic data from medicinal chemistry literature and approved drugs.
homepage_url: https://www.ebi.ac.uk/chembl/
docs_url: https://chembl.gitbook.io/chembl-interface-documentation
type:
  - rest-api
  - bulk-download
  - database
auth_required: none
cost: free
license: CC-BY-SA-3.0
rate_limit: "unpublished; polite use expected, heavy workloads should use bulk download"
bulk_available: true
frequency: "approximately every 6-12 months (major releases); Release 37 May 2026"
lag: "months for newly published bioactivity literature to be curated and released"
geography: [global]
join_keys:
  - CHEMBL_ID
  - UNIPROT_ACCESSION
  - DOI
  - PMID
  - MESH_TERM
primary_keys:
  - CHEMBL_ID
join_key_fields:
  - join_key: CHEMBL_ID
    fields: [molecule_chembl_id, target_chembl_id, assay_chembl_id, document_chembl_id, cell_chembl_id]
  - join_key: UNIPROT_ACCESSION
    fields: [target_components.accession, target_components.target_component_xrefs.xref_id]
  - join_key: DOI
    fields: [doi]
  - join_key: PMID
    fields: [pubmed_id]
  - join_key: MESH_TERM
    fields: [mesh_id, mesh_heading]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  Stable REST API and a well-documented relational schema, but response shapes are verbose
  and pagination is mandatory for any non-trivial query. Suggested surface: search_molecule,
  get_molecule, get_target, search_activities_by_target, get_assay, resolve_smiles_to_chembl.
agent_use_cases:
  - drug target lookup
  - bioactivity retrieval
  - chemical structure search
  - approved-drug metadata lookup
  - target-to-compound mapping
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/chembl/api/data/molecule/CHEMBL25.json'"
  expected_status: 200
  expected_fields: [molecule_chembl_id, molecule_structures, molecule_properties, max_phase, first_approval]
last_verified: 2026-06-08
build_priority: high
---

# ChEMBL

## Why this source matters

ChEMBL is the reference open database of bioactive molecules, run by EMBL-EBI as a Global Core Biodata Resource and part of ELIXIR. Release 37 (May 2026) covers roughly 2.5M curated compounds, 15k+ targets, 1.6M assays, and 20M+ bioactivity measurements drawn from medicinal-chemistry literature, deposited datasets, and approved-drug regulatory data. For any agent working on drug discovery, target validation, or pharmacology, ChEMBL is the closest free analogue to commercial databases like GVK Excelra or Reaxys Medicinal Chemistry. Secondary domain coverage: bio-genomics (via UniProt-linked targets) and academic (every activity row cites a source publication via DOI or PMID).

## Agent use cases

- drug target lookup
- bioactivity retrieval
- chemical structure search
- approved-drug metadata lookup
- target-to-compound mapping

## Join strategy

ChEMBL exposes `CHEMBL_ID` as its native identifier across molecules (`CHEMBL25` = aspirin), targets, assays, documents, and cells. Targets carry `UNIPROT_ACCESSION` for protein cross-reference, making ChEMBL the natural bridge between bioactivity data and UniProt/Ensembl-anchored sequence resources. Source publications attach `DOI` and `PMID`, enabling joins to OpenAlex, Europe PMC, and Crossref. Targets and indications carry `MESH_TERM` tags for disease-area filtering.

UniChem (sister resource at the same FTP root) maps `CHEMBL_ID` to 40+ other chemical identifier systems (PubChem CID, DrugBank, ChEBI, InChIKey, RxNorm); use UniChem as the lookup layer when joining to non-ChEMBL chemistry sources.

Potential new join keys for review: `INCHI_KEY` (entity type: chemical_structure; pattern: `^[A-Z]{14}-[A-Z]{10}-[A-Z]$`; used by ChEMBL, PubChem, ChEBI, DrugBank, UniChem) and `PUBCHEM_CID` (entity type: chemical; integer; used by PubChem, ChEMBL cross-references, UniChem). Both would unlock chemistry-side joins that `CHEMBL_ID` alone cannot.

## Access notes

**Low-volume agent queries:** REST API at `https://www.ebi.ac.uk/chembl/api/data/`, no auth. Append `.json` (or `.xml`) to any resource path. Interactive docs at `/chembl/api/data/docs`. Pagination is mandatory: default page size 20, max 1000 via `limit=`. The Beaker utilities API at `/chembl/api/utils/` covers cheminformatics operations (SMILES standardisation, structure similarity) without needing a local RDKit install.

**Large analyses:** Bulk download from `https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/` ships SQLite, PostgreSQL, MySQL dumps, plus SDF (structures) and FASTA (target sequences). The SQLite file is the lowest-friction option for local analysis; loading into Postgres unlocks the full relational schema for cross-table queries. RDF/Turtle distribution at `/chembl/ChEMBL-RDF/latest/` for graph workflows.

License is CC BY-SA 3.0: attribution required, derivative datasets must use a compatible share-alike licence. This is more restrictive than the CC0 / CC-BY of most EBI resources; downstream products that mix ChEMBL with proprietary data should check the share-alike implications.

Known gotchas:

- Bioactivity standardisation is partial. The `standard_value` / `standard_units` / `standard_type` fields are the right join target, but ~20% of legacy rows still carry only the raw reported value.
- `max_phase` indicates highest clinical phase reached (4 = approved, 3 = Phase 3, etc.), refreshed from regulatory sources but not real-time.
- Target classification is curated by hand and lags new target discoveries by one release cycle.
- Release versions are not backwards-compatible at the row level: re-running an analysis against a newer release can produce different bioactivity counts as data is recurated.

## MCP / connector notes

No official MCP. High-value target: medicinal-chemistry and drug-discovery agents are a common audience, the REST API is stable, and the relational schema is well-documented but verbose enough that raw API responses are a poor fit for context windows. Suggested surface: `search_molecule` (by name, SMILES, InChIKey), `get_molecule` (trimmed payload with structure + key properties), `get_target`, `search_activities_by_target`, `get_assay`, `resolve_smiles_to_chembl` (via Beaker + lookup). Connector should aggressively trim `molecule_structures.molfile` and similar verbose fields by default, paginate behind the scenes, and offer a bulk-vs-API switch for large activity pulls.

## Review notes

Potential new join key for review: INCHI_KEY
  Entity type: chemical_structure
  Pattern: ^[A-Z]{14}-[A-Z]{10}-[A-Z]$
  Other datasets that would use it: PubChem, ChEBI, DrugBank, UniChem, ChemSpider, OpenFDA NDC

Potential new join key for review: PUBCHEM_CID
  Entity type: chemical
  Pattern: integer
  Other datasets that would use it: PubChem, ChEMBL cross-references, UniChem, NIH NCATS Inxight

License is CC BY-SA 3.0, more restrictive than most EBI resources (CC0 / CC-BY). Share-alike obligation may affect downstream redistribution in mixed-licence products; flagging for user awareness rather than schema action.
