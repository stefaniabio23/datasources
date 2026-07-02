---
id: proteomexchange
name: ProteomeXchange
domain: bio-genomics
entry_kind: registry
description: Consortium and central index coordinating proteomics data deposition across the main repositories, minting PXD dataset accessions and exposing dataset metadata through ProteomeCentral.
homepage_url: https://www.proteomexchange.org/
docs_url: https://proteomecentral.proteomexchange.org/
type:
  - rest-api
  - web-ui
auth_required: none
cost: free
license: ProteomeXchange-Open-Data
rate_limit: "fair-use; ProteomeCentral GET/PROXI API"
bulk_available: true
frequency: "continuous; new datasets announced as they are made public"
lag: "days; datasets go public on associated publication"
geography: [global]
is_directory: true
join_keys:
  - PMID
  - DOI
primary_keys:
  - PXD_IDENTIFIER
  - PRIDE_PROJECT_ID
mcp_status: mcp-needed-low-value
agent_use_cases:
  - proteomics dataset discovery
  - finding raw mass-spec data by publication or keyword
  - publication-to-dataset linking
  - dataset provenance and cross-repository search
access_test:
  command: "curl -sf 'https://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=PXD000001&outputMode=JSON' -o /dev/null"
  expected_status: 200
last_verified: 2026-07-02
build_priority: low
notes: "access_test executed 2026-07-02 (GetDataset JSON → 200). ProteomeXchange federates PRIDE (EBI), PeptideAtlas (ISB), MassIVE (UCSD), jPOST, iProX, and Panorama Public; it is the discovery layer over those repositories (is_directory: true). PXD accessions are the canonical proteomics dataset id; now exposed by two entries (this and peptideatlas), so PXD_IDENTIFIER is worth promoting to the canonical join-key registry (Review notes)."
---

# ProteomeXchange

## Why this source matters

ProteomeXchange is the coordinating consortium for public proteomics data: it standardises how mass-spectrometry datasets are deposited and disseminated across the field's main repositories, PRIDE (EMBL-EBI), PeptideAtlas (ISB), MassIVE (UCSD), jPOST (Japan), iProX (China), and Panorama Public, and mints the `PXD` accession that uniquely identifies each dataset. Its ProteomeCentral portal is the single place to search and resolve any public proteomics dataset regardless of which repository actually hosts the files. For an agent, ProteomeXchange is the entry point to raw and processed proteomics experiments: given a paper or a topic, find the underlying MS datasets and route to the hosting repository for the files.

## Agent use cases

- proteomics dataset discovery
- finding raw mass-spec data by publication or keyword
- publication-to-dataset linking
- dataset provenance and cross-repository search

## Join strategy

Dataset metadata links to the associated publication, so the canonical join keys are `PMID` and `DOI`, use these to go from a paper to its deposited data (or vice versa) and to join into `pubmed`, `europe-pmc`, and `openalex`. The native primary key is the ProteomeXchange accession (`PXD_IDENTIFIER`, e.g. `PXD000001`), plus the hosting repository's own id (`PRIDE_PROJECT_ID` and equivalents). `PXD_IDENTIFIER` is the load-bearing cross-source key in proteomics: it is how `peptideatlas` and papers reference the source experiments, so it is the natural bridge from a reprocessed protein-evidence build back to the raw deposit.

## Access notes

Free, no authentication. Two API paths on ProteomeCentral: the legacy `GetDataset` endpoint (`/cgi/GetDataset?ID=PXD######&outputMode=JSON|XML`) for a single dataset, and the community PROXI REST API (`/api/proxi/v1/`) for programmatic dataset and spectrum queries shared across member repositories. An RSS feed announces new datasets. ProteomeCentral holds metadata and pointers; the actual data files are downloaded from the hosting repository (PRIDE FTP, MassIVE, etc.), so a full-data pull is a two-step resolve-then-fetch.

## MCP / connector notes

No MCP exists; proteomics is a specialised audience, so it is low priority. A useful connector would wrap ProteomeCentral: search datasets by keyword/PMID/species, resolve a PXD accession to its metadata and hosting repository, and hand off file URLs. It should abstract over the GetDataset-vs-PROXI split and the per-repository file layouts.

## Review notes

- New non-SPDX license short name `ProteomeXchange-Open-Data`. Dataset metadata is openly accessible; the underlying data files carry each submission's own terms. Confirm the convention.
- **Promote `PXD_IDENTIFIER` to the canonical join-key registry.** It is now exposed by two entries (`proteomexchange`, `peptideatlas`) and is the standard proteomics dataset id, which meets the "second source exposes it" bar flagged in the peptideatlas entry. Separate `join-keys.yaml` PR.
- Member repositories (PRIDE, MassIVE, jPOST, iProX, Panorama Public) are candidate future entries; `peptideatlas` is already in. `is_directory: true` marks this as the discovery layer over them.
- `join_key_fields` omitted: PROXI/GetDataset payload paths for PMID/DOI not verified against a live response; add once confirmed.
