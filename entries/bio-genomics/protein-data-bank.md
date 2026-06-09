---
id: protein-data-bank
name: RCSB Protein Data Bank
domain: bio-genomics
entry_kind: registry
description: Public repository of experimentally-determined 3D structures of proteins, nucleic acids, and complexes plus integrative and computed structure models, run by the RCSB consortium as the US member of the worldwide PDB.
homepage_url: https://www.rcsb.org/
docs_url: https://data.rcsb.org/
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: CC0-1.0
rate_limit: "no published per-IP limit; Data API caps batch requests at 1000 IDs per call. Search API has no published limit; contact info@rcsb.org for heavy use."
bulk_available: true
frequency: "weekly release every Wednesday (00:00 UTC)"
lag: "experimental structures appear ~1-2 weeks after authors release; computed model snapshots refreshed periodically from AlphaFold and ModelArchive"
geography: [global]
join_keys:
  - PDB_ID
  - UNIPROT_ACCESSION
  - DOI
  - PMID
  - NCBI_TAXON_ID
primary_keys:
  - PDB_ID
  - PDB_ENTITY_ID
  - PDB_ASSEMBLY_ID
  - PDB_CHAIN_ID
  - PDB_CSM_ID
join_key_fields:
  - join_key: PDB_ID
    fields: [rcsb_id, entry.id, rcsb_entry_container_identifiers.entry_id]
  - join_key: UNIPROT_ACCESSION
    fields: [rcsb_polymer_entity_container_identifiers.uniprot_ids, "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers[database_name=UniProt].database_accession"]
  - join_key: DOI
    fields: [citation.pdbx_database_id_DOI, rcsb_primary_citation.pdbx_database_id_doi]
  - join_key: PMID
    fields: [citation.pdbx_database_id_PubMed, rcsb_primary_citation.pdbx_database_id_pub_med]
  - join_key: NCBI_TAXON_ID
    fields: [rcsb_entity_source_organism.ncbi_taxonomy_id, rcsb_entity_host_organism.ncbi_taxonomy_id]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/pipeworx-io/mcp-rcsb-pdb
  - github.com/cnyambura/rcsb-mcp
  - github.com/r0bin2u/pdb-mcp
  - github.com/cyanheads/protein-mcp-server
mcp_notes: >
  Several overlapping community MCPs, none official from RCSB. Most wrap the Data API
  entry/polymer-entity endpoints plus a subset of Search API queries. A consolidated
  connector should expose search_structures, get_entry, get_polymer_entity,
  get_uniprot_mappings, fetch_coordinates (mmCIF or BinaryCIF), search_by_sequence,
  with response trimming for verbose audit-revision history and routing of large
  coordinate pulls to the files.rcsb.org HTTPS or rsync mirror.
agent_use_cases:
  - structure lookup by PDB ID
  - resolve UniProt accession to experimentally-solved structures
  - coordinate file retrieval (mmCIF, BinaryCIF, legacy PDB)
  - sequence and structure similarity search
  - ligand and binding-site queries
access_test:
  command: "curl -sf 'https://data.rcsb.org/rest/v1/core/entry/4HHB'"
  expected_status: 200
  expected_fields: [rcsb_id, rcsb_entry_container_identifiers, rcsb_accession_info, citation, exptl]
last_verified: 2026-06-09
build_priority: medium
---

# RCSB Protein Data Bank

## Why this source matters

The US member of the Worldwide Protein Data Bank (wwPDB) and the canonical public archive of experimentally-determined 3D macromolecular structures: ~255K experimental entries (X-ray crystallography, cryo-EM, NMR, neutron diffraction), ~390 integrative structures, plus over a million computed structure models federated in from AlphaFold and ModelArchive. Hosted by Rutgers University, UC San Diego (with the San Diego Supercomputer Center), and UC San Francisco, funded primarily by NSF, NIH, and DOE. Any agent answering "does this protein have a solved structure, what does it bind, what's the resolution, what ligands sit in the active site" should hit RCSB PDB first. The other wwPDB partners (PDBe at EMBL-EBI, PDBj in Osaka, BMRB for NMR, EMDB for electron microscopy maps) share the same underlying archive but differ in API surface and value-added annotations. Secondary relevance to `clinical-biotech` (drug-target structure for medicinal chemistry) and `academic` (every structure carries a primary citation DOI/PMID).

## Agent use cases

- structure lookup by PDB ID
- resolve UniProt accession to experimentally-solved structures
- coordinate file retrieval (mmCIF, BinaryCIF, legacy PDB)
- sequence and structure similarity search
- ligand and binding-site queries

## Join strategy

RCSB PDB is the issuing authority for `PDB_ID` (e.g. `4HHB`, `1TUP`, pattern `^[0-9][A-Z0-9]{3}$`), the canonical four-character identifier referenced by UniProt, AlphaFold, ChEMBL, DrugBank, InterPro, and most structural-biology tooling. Polymer-entity records expose `UNIPROT_ACCESSION` via SIFTS-derived `rcsb_polymer_entity_container_identifiers.uniprot_ids` and the richer `reference_sequence_identifiers` block; one entry can map to multiple UniProt accessions (one per chain or chimera). Primary-citation blocks expose `DOI` and `PMID` for the publication describing the structure. Source-organism and host-organism blocks expose `NCBI_TAXON_ID`.

PDB-internal IDs that sit outside the canonical registry: entity IDs (`{PDB_ID}_{entity_number}`, e.g. `4HHB_1`), assembly IDs (`{PDB_ID}-{assembly_number}`), chain IDs (label_asym_id and auth_asym_id), and computed-structure-model identifiers (AF-{UniProt}-F{frag}-model_v{N} for AlphaFold). Use these for direct PDB lookups, not cross-source joins.

Recommended pivot pattern: resolve any protein identifier to `UNIPROT_ACCESSION` first via UniProt, then query PDB's Search API with `rcsb_polymer_entity_container_identifiers.uniprot_ids` to discover all structures for that protein, then fan out to fetch coordinates or pair with ChEMBL for bound ligand bioactivity.

## Access notes

**Low-volume metadata queries:** Data REST at `https://data.rcsb.org/rest/v1/core` with no auth. First endpoint to try is `/entry/{pdb_id}` for entry-level metadata or `/polymer_entity/{pdb_id}/{entity_id}` for chain-level data including UniProt mappings. A GraphQL endpoint at `https://data.rcsb.org/graphql` lets agents fetch a tailored projection in one round trip; preferred over chaining REST calls when the response shape is known in advance.

**Search:** Search API at `https://search.rcsb.org/rcsbsearch/v2/query` accepts JSON POST queries combining attribute, full-text, sequence (mmseqs2), sequence-motif, structure-similarity, structural-motif, and chemical searches. Specify `return_type` (`entry`, `polymer_entity`, `polymer_instance`, `assembly`, `non_polymer_entity`, `mol_definition`) to control granularity.

**Coordinate files:** HTTPS at `https://files.rcsb.org/download/{pdb_id}.cif.gz` (mmCIF, current canonical format), `.pdb.gz` (legacy 80-column format, deprecated for >62-chain entries but still produced where possible), or `https://models.rcsb.org/{pdb_id}.bcif.gz` for BinaryCIF (compact binary mmCIF, recommended for programmatic pipelines). FASTA sequences at `/fasta/entry/{pdb_id}/download`. Full archive snapshots via `rsync://rsync.rcsb.org` or the wwPDB FTP at `https://files.wwpdb.org`.

Known gotchas:

- Data API caps batch endpoints at 1000 IDs per call; chunk larger lists.
- Legacy PDB format cannot represent structures with >99,999 atoms or >62 chains; for those entries only mmCIF or BinaryCIF are produced. Agents should prefer mmCIF/BinaryCIF for new pipelines.
- Sequence clusters at `https://cdn.rcsb.org/resources/sequence/clusters/` are pre-computed at 30/40/50/70/90/95/100% identity and useful for de-duplicating redundant structures.
- The `pdbx_audit_revision_*` blocks are verbose (every structure revision is logged); trim before passing to an LLM.
- Computed structure models (AlphaFold + ModelArchive) share Data API endpoints but carry different identifier patterns and quality metadata; check `rcsb_comp_model_provenance` to distinguish from experimental entries.
- Holdings endpoints (`/holdings/current/entry_ids`, `/holdings/unreleased/entry_ids`, `/holdings/removed/entry_ids`) give the authoritative list of live entries; useful for delta sync.

## MCP / connector notes

Multiple community MCPs exist (`pipeworx-io/mcp-rcsb-pdb`, `cnyambura/rcsb-mcp`, `r0bin2u/pdb-mcp`, plus the multi-source `cyanheads/protein-mcp-server` which covers PDB alongside UniProt and AlphaFold); none official from RCSB. Coverage and quality vary. A consolidated connector should expose `search_structures`, `get_entry`, `get_polymer_entity`, `get_uniprot_mappings`, `fetch_coordinates` (with format and compression options), `search_by_sequence`, with response trimming for verbose audit-revision history, cross-reference flattening (SIFTS UniProt mappings, citation DOIs, source organism taxonomy), and routing of bulk coordinate pulls to `files.rcsb.org` HTTPS or the rsync mirror instead of through the API.

## Review notes

Potential new join key for review that PDB cross-references natively and would be useful across bio-genomics entries:

- `SCOP_ID` or `CATH_ID` for structural-classification hierarchies (Class/Architecture/Topology/Homology). Used by SCOP, CATH, PDB; would let agents pivot between sequence-based and fold-based similarity. Patterns vary by version.

Stephanie reviews and decides whether to PR these into `schema/join-keys.yaml`.
