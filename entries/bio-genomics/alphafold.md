---
id: alphafold
name: AlphaFold Protein Structure Database
domain: bio-genomics
entry_kind: registry
description: Open database of AlphaFold-predicted 3D protein structures for 214M+ UniProt sequences, run by EMBL-EBI with Google DeepMind, served per-accession via JSON API and in bulk per-proteome on Google Cloud Storage and the EBI FTP.
homepage_url: https://alphafold.ebi.ac.uk
docs_url: https://alphafold.ebi.ac.uk/api-docs
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "unpublished; polite use expected, large pulls should use the GCS bucket or EBI FTP rather than the per-accession API"
bulk_available: true
frequency: "periodic, tracking UniProt releases; synced to UniProt release 2025_03"
lag: "structures regenerated to track UniProt releases; new UniProt sequences appear after a prediction/release cycle"
geography: [global]
join_keys:
  - UNIPROT_ACCESSION
  - PDB_ID
primary_keys:
  - ALPHAFOLD_MODEL_ID
join_key_fields:
  - join_key: UNIPROT_ACCESSION
    fields: [uniprotAccession]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  Clean per-accession JSON API keyed on UniProt accession, but responses embed full sequence
  and several large coordinate/confidence file URLs, and structure/PAE files are megabyte-scale.
  Suggested surface: get_prediction (trimmed metadata + file URLs), get_confidence (pLDDT summary),
  get_pae, resolve_uniprot_to_structure, with routing of bulk per-proteome pulls to GCS/FTP.
agent_use_cases:
  - predicted structure lookup by UniProt accession
  - per-residue confidence (pLDDT) retrieval
  - predicted aligned error (PAE) retrieval
  - proteome-wide structure download
  - structure coverage check for an unstudied protein
access_test:
  command: "curl -sf 'https://alphafold.ebi.ac.uk/api/prediction/P00520'"
  expected_status: 200
  expected_fields: [uniprotAccession, modelEntityId, globalMetricValue, cifUrl, sequence]
last_verified: 2026-06-22
build_priority: medium
---

# AlphaFold Protein Structure Database

## Why this source matters

The reference open database of computationally predicted protein structures, run by EMBL-EBI in partnership with Google DeepMind. It covers 214M+ UniProt sequences, synced to UniProt release 2025_03, and now includes isoforms in addition to canonical sequences. Where the PDB holds experimentally determined structures for a small, well-studied slice of the proteome, AlphaFold offers a predicted 3D model for almost any protein with a UniProt accession, making it the first stop for an agent that needs a structure for a protein no crystallographer has touched. Every entry is a prediction, not an experimental observation, which is the defining caveat for any downstream use. Secondary relevance to `clinical-biotech` (structure-guided target assessment and druggability) and `academic` (the underlying AlphaFold methods papers).

## Agent use cases

- predicted structure lookup by UniProt accession
- per-residue confidence (pLDDT) retrieval
- predicted aligned error (PAE) retrieval
- proteome-wide structure download
- structure coverage check for an unstudied protein

## Join strategy

AlphaFold is keyed entirely on `UNIPROT_ACCESSION`: the API endpoint takes the accession directly (`/api/prediction/P00520`) and the response carries it in `uniprotAccession`. This makes UniProt the canonical pivot. Resolve any protein-bearing identifier to a `UNIPROT_ACCESSION` first (via UniProt or Ensembl), then fetch the predicted structure here. AlphaFold cross-references `PDB_ID` only indirectly: both AlphaFold and the PDB anchor to the same UniProt accession, so the join to experimental structures runs through `UNIPROT_ACCESSION` rather than a direct PDB field in the AlphaFold payload. This makes AlphaFold the predicted-structure complement to the PDB entry: pair the two on shared UniProt accession to compare predicted vs experimental coverage for a target.

Source-native identifier: the AlphaFold model ID (`primary_keys: ALPHAFOLD_MODEL_ID`), format `AF-<UniProt accession>-F<fragment>-model_v<version>` (e.g. `AF-P00520-F1-model_v4`). The `F<n>` fragment index handles proteins long enough to be split across multiple models. This ID is AlphaFold-internal and derives mechanically from the UniProt accession, so it is not a cross-source join key; use the accession for joins and the model ID only for addressing a specific AlphaFold file.

## Access notes

**Low-volume queries:** REST/JSON API at `https://alphafold.ebi.ac.uk/api`, no auth. First endpoint: `/api/prediction/{accession}` returns an array of model summaries with `globalMetricValue` (mean pLDDT), per-confidence-band fractions, the full sequence, and URLs to the structure (`cifUrl`, `bcifUrl`, `pdbUrl`), confidence, and PAE files. The legacy API retires June 2026; build against the current `api-docs` surface, not older endpoint shapes.

**Large analyses:** Bulk per-proteome tar archives (compressed mmCIF and PDB) at the EBI FTP `https://ftp.ebi.ac.uk/pub/databases/alphafold`, plus the Swiss-Prot subset. The Google Cloud Storage mirror `gs://public-datasets-deepmind-alphafold-v4` holds three files per protein: `*-model_v4.cif` (coordinates), `*-confidence_v4.json` (per-residue pLDDT), and `*-predicted_aligned_error_v4.json` (PAE). Use GCS or FTP for any proteome-wide pull rather than iterating the per-accession API. Freshness check: confirm the UniProt release the current build tracks against `2025_03` on the homepage, and note the file-version suffix (the EBI API currently serves `model_v6` models while the GCS bucket above is the `v4` snapshot).

**Confidence interpretation, the load-bearing caveat.** Two per-prediction metrics ship with every model. pLDDT is a per-residue confidence score on a 0-100 scale: above 90 is high accuracy, 70-90 is a confident backbone, 50-70 is low, and below 50 should be treated as a likely-disordered or unreliable region rather than a real fold. PAE (predicted aligned error) is a residue-pair matrix expressing confidence in the relative position of domains, the metric to consult before trusting inter-domain geometry. Every structure here is predicted, not experimental, the inverse of the PDB: do not treat a high-pLDDT model as an experimental fact, and always surface the confidence band alongside any structural claim.

## MCP / connector notes

No official MCP. High-value target: structural-biology, target-assessment, and protein-engineering agents are a common audience, and the API is clean but its responses embed full sequences and several large file URLs, with the actual structure/PAE files running to megabytes. Suggested surface: `get_prediction` (trimmed metadata plus file URLs, no inline sequence by default), `get_confidence` (pLDDT summary and per-residue band breakdown), `get_pae`, `resolve_uniprot_to_structure`, with proteome-wide pulls routed to the GCS bucket or EBI FTP. The connector must abstract over file-version drift (`v4` on GCS vs `v6` on the live API) and never load raw mmCIF or PAE matrices into the context window.

## Review notes

Native model identifier `ALPHAFOLD_MODEL_ID` (format `AF-<UniProt accession>-F<fragment>-model_v<version>`) is recorded in `primary_keys` only. It is not proposed as a canonical join key because it derives mechanically from the UniProt accession and carries no cross-source utility that `UNIPROT_ACCESSION` does not already provide.

`PDB_ID` is listed in `join_keys` as a cross-reference that runs through the shared `UNIPROT_ACCESSION` rather than a direct field in the AlphaFold payload, so it has no `join_key_fields` entry. Flagging in case the registry convention prefers join keys be limited to identifiers that appear directly in the source payload.

File-version skew observed at verification: the EBI per-accession API returns `model_v6` while the documented and GCS-published snapshot is `model_v4`. Not a schema issue, noted for consumer awareness.
