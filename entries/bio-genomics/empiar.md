---
id: empiar
name: EMPIAR
domain: bio-genomics
entry_kind: corpus
description: Public archive of raw image data underpinning 3D electron microscopy structures (cryo-EM single particle, cryo-electron tomography, volume EM), run by EMBL-EBI as a companion to EMDB.
homepage_url: https://www.ebi.ac.uk/empiar/
docs_url: https://www.ebi.ac.uk/empiar/api/documentation/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC0-1.0
rate_limit: "no published per-IP limit on the metadata REST API; bulk image transfers go via Aspera/Globus, not the API"
bulk_available: true
frequency: "continuous deposition tied to EMDB submissions; new entries released on author-set dates"
lag: "raw datasets released on the depositor's schedule, often aligned to the linked publication and EMDB release"
geography: [global]
join_keys:
  - PDB_ID
  - NCBI_TAXON_ID
primary_keys:
  - EMPIAR_ID
  - EMDB_ID
join_key_fields:
  - join_key: PDB_ID
    fields: ["cross_references (PDB IDs reachable through the linked EMDB entry)"]
  - join_key: NCBI_TAXON_ID
    fields: [imagesets.imageset.organism, sample.organism.ncbi_taxonomy_id]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Clean unauthenticated metadata REST API; the hard part is not the API but the data, raw
  EM datasets are multi-terabyte and move over Aspera/Globus, not over HTTP GET. An MCP adds
  little for metadata lookup (curl is sufficient) and cannot sensibly stream the bulk payloads.
  Narrow structural-biology audience. Suggested thin surface if built: get_entry, search_entries,
  resolve_emdb_to_empiar, list_imagesets.
agent_use_cases:
  - locate raw images behind a cryo-EM structure
  - resolve an EMDB map to its source dataset
  - find cryo-ET tilt-series for a target organism
  - retrieve dataset metadata and file manifests
  - assemble training data for cryo-EM image-processing models
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/empiar/api/entry/10002/'"
  expected_status: 200
  expected_fields: [title, cross_references, dataset_size, experiment_type, citation]
last_verified: 2026-06-22
build_priority: low
---

# EMPIAR

## Why this source matters

EMPIAR (Electron Microscopy Public Image Archive) is the public resource for the raw image data underpinning 3D electron microscopy: cryo-EM single-particle micrographs, cryo-electron tomography tilt-series, and volume EM and X-ray tomography datasets. Run by EMBL-EBI as a companion to EMDB (which holds the processed 3D maps and tomograms), it holds roughly 2,996 entries totalling about 8.73 PiB as of June 2026, making it the largest single-file-size archive at EBI. Where EMDB and PDB answer "what is the structure," EMPIAR answers "show me the original images it was reconstructed from", the audience is structural biologists reprocessing data, benchmarking new image-processing methods, or building training sets for cryo-EM machine learning. Secondary relevance to `academic` (every entry carries a primary-citation DOI) and to `clinical-biotech` (raw data behind drug-target structures).

## Agent use cases

- locate raw images behind a cryo-EM structure
- resolve an EMDB map to its source dataset
- find cryo-ET tilt-series for a target organism
- retrieve dataset metadata and file manifests
- assemble training data for cryo-EM image-processing models

## Join strategy

EMPIAR mints two source-native identifiers in `primary_keys`: `EMPIAR_ID` (`EMPIAR-#####`, CURIE `empiar:#####`) for the raw-data entry, and the linked `EMDB_ID` (`EMD-####`) it carries in `cross_references` for the processed map. Neither is in the canonical registry yet (flagged below). The registry-backed joins this source exposes are indirect: `PDB_ID` is reachable through the EMDB cross-reference (EMPIAR to EMDB to PDB crosswalk), and `NCBI_TAXON_ID` identifies the sample organism on each imageset.

The natural pivot is EMPIAR to EMDB to PDB: start from a `PDB_ID` or `EMDB_ID`, resolve to the EMDB entry, then follow its EMPIAR cross-reference back to the raw images. EMPIAR alone does not expose `PDB_ID` directly in most entries; the link runs through EMDB. Pair with the RCSB PDB and EMDB entries to complete the structure-to-raw-data chain.

## Access notes

Two distinct access paths, do not conflate them. Metadata is small and HTTP-friendly: the REST API at `https://www.ebi.ac.uk/empiar/api/` is unauthenticated, with `https://www.ebi.ac.uk/empiar/api/entry/{id}/` (numeric ID, no `EMPIAR-` prefix) returning title, authors, `cross_references` (EMDB IDs such as `EMD-2275`), `dataset_size`, `experiment_type`, organism, and the primary-citation DOI.

The raw image data is the opposite: individual entries run from tens of gigabytes to multiple terabytes (the archive totals ~8.73 PiB), so bulk transfer is via Aspera (IBM `ascp`, high-speed UDP) or Globus, with FTP and HTTPS mirrors available for smaller pulls. This is not casual `GET` territory, plan for a managed transfer client and substantial local storage before downloading a full dataset. To verify freshness, hit the entry API or check the entry-count and storage figures on the homepage.

## MCP / connector notes

No MCP exists. Low value: the metadata REST API is clean and unauthenticated enough that `curl` suffices, and the bulk payloads (multi-terabyte, Aspera/Globus) are exactly what an MCP cannot usefully stream into a context window. The audience (structural-biology reprocessing and cryo-EM ML) is narrow relative to PDB or UniProt. If a thin connector were built, it should expose `get_entry`, `search_entries`, `resolve_emdb_to_empiar`, and `list_imagesets` for metadata only, and explicitly hand off bulk retrieval to an external Aspera/Globus transfer rather than attempting it inline.

## Review notes

Potential new join key for review: EMPIAR_ID
  Entity type: em_raw_dataset
  Pattern: ^EMPIAR-[0-9]+$ (CURIE form empiar:[0-9]+)
  Other datasets that would use it: EMDB (cross-references EMPIAR), EMPIAR@PDBj, IDR

Potential new join key for review: EMDB_ID
  Entity type: em_map_or_tomogram
  Pattern: ^EMD-[0-9]+$
  Other datasets that would use it: EMDB, RCSB PDB / PDBe (3DEM entries), EMPIAR, EMICSS

These two would formalise the EMPIAR <-> EMDB <-> PDB crosswalk: an `EMDB_ID` registry key would let agents bridge EMPIAR raw data to PDB structures without ad-hoc field parsing, since the EMPIAR-to-PDB link currently runs only through EMDB. Stephanie reviews and decides whether to PR these into `schema/join-keys.yaml`.
