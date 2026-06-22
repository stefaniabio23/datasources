---
id: bindingdb
name: BindingDB
domain: clinical-biotech
entry_kind: registry
description: Public database of measured protein-small-molecule binding affinities (Ki, Kd, IC50, EC50) curated from literature, patents, PubChem bioassays, and ChEMBL.
homepage_url: https://www.bindingdb.org
docs_url: https://www.bindingdb.org/rwd/bind/BindingDBRESTfulAPI.jsp
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: CC-BY-3.0
rate_limit: "unpublished; polite use expected, heavy workloads should use bulk download"
bulk_available: true
frequency: "updated when new data are added, usually monthly (release 202606)"
lag: "weeks-to-months for newly published affinity data to be curated and released"
geography: [global]
join_keys:
  - UNIPROT_ACCESSION
  - CHEMBL_ID
  - INCHI_KEY
  - PMID
primary_keys:
  - BINDINGDB_MONOMER_ID
  - BINDINGDB_REACTANT_SET_ID
join_key_fields:
  - join_key: UNIPROT_ACCESSION
    fields: ["UniProt (SwissProt) Primary ID of Target Chain", "UniProt (TrEMBL) Primary ID of Target Chain"]
  - join_key: CHEMBL_ID
    fields: ["ChEMBL ID of Ligand"]
  - join_key: INCHI_KEY
    fields: ["Ligand InChI Key"]
  - join_key: PMID
    fields: ["PMID"]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  Clean REST API keyed by UniProt accession, PDB ID, or SMILES, but responses bundle every
  measurement for a target and need affinity-type/relation parsing. Suggested surface:
  get_ligands_by_uniprot, get_targets_by_compound, get_ligands_by_pdb, with censored-value
  flagging and affinity-type normalisation built in.
agent_use_cases:
  - binding affinity lookup
  - target-to-ligand mapping
  - ligand-to-target deorphaning
  - structure-activity dataset assembly
  - chemical-to-protein cross-referencing
access_test:
  command: "curl -sf 'https://bindingdb.org/rest/getLigandsByUniprot?uniprot=P35355;100&response=application/json'"
  expected_status: 200
  expected_fields: [getLigandsByUniprotResponse]
last_verified: 2026-06-22
build_priority: medium
---

# BindingDB

## Why this source matters

BindingDB is the reference open database of experimentally measured protein-small-molecule binding affinities, directed by Michael Gilson at the UC San Diego Skaggs School of Pharmacy and supported by NIH grants. The 2026 release covers roughly 3.2M measurements for 1.4M compounds against 11.4K targets, of which about 1.6M measurements (752K compounds, 4.8K targets) are curated directly by BindingDB staff and the remainder imported from ChEMBL, PubChem confirmatory bioassays, patents, and literature. Where ChEMBL spans bioactivity broadly, BindingDB is the deepest free collection of quantitative binding constants specifically, making it the go-to source for structure-activity relationship work, virtual-screening benchmarks, and target deorphaning. Secondary domain coverage: bio-genomics (every target carries a UniProt accession and sequence) and academic (measurements cite source publications via PMID).

## Agent use cases

- binding affinity lookup
- target-to-ligand mapping
- ligand-to-target deorphaning
- structure-activity dataset assembly
- chemical-to-protein cross-referencing

## Join strategy

BindingDB anchors targets on `UNIPROT_ACCESSION` (both SwissProt and TrEMBL primary IDs are exposed, plus the full target sequence), which makes it the natural bridge from binding data to UniProt/Ensembl sequence resources. Ligands carry `INCHI_KEY` for structure-based joins and `CHEMBL_ID` for the ChEMBL-imported subset, so an agent can stitch BindingDB affinity rows onto ChEMBL bioactivity and approved-drug metadata. Source publications attach `PMID`, enabling joins to OpenAlex, Europe PMC, and PubMed.

Source-internal identifiers (BindingDB monomer IDs for ligands, reactant-set IDs for measurement rows) live in `primary_keys` and are for direct BindingDB lookups, not cross-source joins. BindingDB also exposes PubChem CID and SID per ligand; those are flagged under Review notes because there is no canonical registry key for them yet (chembl.md already flagged `PUBCHEM_CID`).

## Access notes

**Low-volume agent queries:** REST API at `https://bindingdb.org/rest/`, no auth. Query by UniProt accession (`getLigandsByUniprot?uniprot=P35355;100` where `100` is the affinity cutoff in nM), by multiple UniProts (`getLigandsByUniprots`), by PDB ID (`getLigandsByPDBs`), or by chemical structure (`getTargetByCompound?smiles=...`). Append `&response=application/json`; default response is XML.

**Large analyses:** Bulk download from `https://www.bindingdb.org/rwd/bind/chemsearch/marvin/Download.jsp`. The all-data TSV (one row per measurement, ~560 MB) is easiest; 2D/3D SDF (structures) and a full MySQL dump (~270 MB) are also published. Files refresh roughly monthly; verify freshness by checking the release tag (e.g. `202606`) on the download page.

Data traps to handle before treating any value as a clean number:

- **Affinity type lives in a column.** Each row's measurement is tagged Ki, Kd, IC50, or EC50 in a TYPE column. These are not interchangeable: Ki/Kd are equilibrium constants, IC50/EC50 are assay-dependent. Never pool across types without intent.
- **Relation symbols encode censored data.** Values carry a relation operator (`>`, `<`, `=`). A row reading `>10000 nM` is a lower bound (inactive past the assay ceiling), not a measured affinity. Filter on the relation symbol before any quantitative use; treating censored values as point measurements corrupts SAR models and benchmarks.
- **Units.** Affinities are usually nM but the units field must be read per row, not assumed. Normalise to a common unit before comparison.

License: BindingDB-curated data is CC BY 3.0 (attribution). The ChEMBL-imported subset retains ChEMBL's CC BY-SA 3.0 share-alike obligation, so a downstream derivative dataset that includes ChEMBL-sourced rows inherits the share-alike requirement. Segregate by provenance if mixing with proprietary or differently licensed data.

## MCP / connector notes

No official MCP. High-value target: drug-discovery and cheminformatics agents are a recurring audience (overlaps ChEMBL, UniProt, PDB consumers), and the REST API is stable but returns affinity bundles that need parsing. Suggested surface: `get_ligands_by_uniprot` (trimmed to ligand SMILES/InChIKey + affinity type/value/relation/units), `get_targets_by_compound` (SMILES similarity search), `get_ligands_by_pdb`. The connector must (1) surface the affinity TYPE per row, (2) flag or filter censored values by relation symbol rather than silently dropping the operator, and (3) normalise units. Offer a bulk-vs-API switch for full SAR dataset pulls.

## Review notes

PubChem CID and SID are exposed per ligand but have no canonical registry key. `chembl.md` already flagged `PUBCHEM_CID` for review; BindingDB is a second dataset that would use it.

Potential new join key for review: PUBCHEM_CID
  Entity type: chemical
  Pattern: integer
  Other datasets that would use it: PubChem, ChEMBL cross-references, UniChem, NIH NCATS Inxight, BindingDB

Potential new join key for review: PUBCHEM_SID
  Entity type: chemical_substance
  Pattern: integer
  Other datasets that would use it: PubChem, BindingDB

License split: BindingDB-curated data is CC BY 3.0, but the ChEMBL-imported subset retains CC BY-SA 3.0. The YAML `license` field records the primary curated licence (CC-BY-3.0); the share-alike obligation on the ChEMBL subset is documented in Access notes for downstream-redistribution awareness rather than schema action.
