---
id: pride
name: "PRIDE Archive"
domain: bio-genomics
entry_kind: registry
description: "EMBL-EBI repository of mass-spectrometry proteomics datasets (raw + processed + identifications), the PRIDE member of the ProteomeXchange consortium."
homepage_url: https://www.ebi.ac.uk/pride/
docs_url: https://www.ebi.ac.uk/pride/ws/archive/v2/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: EMBL-EBI-Terms-of-Use
rate_limit: "no published hard limit; EBI fair-use applies"
bulk_available: true
frequency: "continuous (new datasets published as they pass validation)"
lag: "days-to-weeks from submission to public release; private until submitter/journal releases"
geography: [global]
join_keys:
  - DOI
  - PMID
  - UNIPROT_ACCESSION
  - ORCID
  - PXD_IDENTIFIER
primary_keys:
  - PXD_ACCESSION
  - PRIDE_SUBMITTER_ID
join_key_fields:
  - join_key: DOI
    fields: [doi, references.doi]
  - join_key: PMID
    fields: [references.pubmedID]
  - join_key: ORCID
    fields: [submitters.orcid, labPIs.orcid]
  - join_key: UNIPROT_ACCESSION
    fields: [proteinevidences.accession]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/PRIDE-Archive/mcp_pride_archive_search"
mcp_notes: >
  Official PRIDE-Archive-org MCP wrapping the Archive search API: keyword search,
  pagination, sort by date/popularity. Read-only; covers project discovery, not
  protein/peptide-level identification retrieval.
agent_use_cases:
  - proteomics dataset discovery
  - protein-to-experiment lookup
  - disease/organism cohort assembly
  - publication-to-rawdata linkage
  - MS instrument/method survey
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD000001' -H 'Accept: application/json'"
  expected_status: 200
  expected_fields: [accession, title, doi, references, organisms]
last_verified: 2026-07-02
build_priority: medium
---

# PRIDE Archive

## Why this source matters

PRIDE (PRoteomics IDEntifications Database) is EMBL-EBI's repository for mass-spectrometry-based proteomics data and the world's largest such archive. It is the UK founding member of the ProteomeXchange consortium (alongside PeptideAtlas/PASSEL, MassIVE, jPOST, iProX), so every complete submission carries a shared ProteomeXchange `PXD` accession that resolves across all member repositories. Each project bundles raw MS files, processed result files, and identification evidence with rich metadata: organism, disease, instrument, experiment type, submitter, and linked publications. For an agent, PRIDE is the entry point for turning a protein, disease, or paper into the underlying experimental proteomics evidence. Secondary relevance to `clinical-biotech` (biomarker and drug-target proteomics) and `academic` (publication-linked datasets).

## Agent use cases

- proteomics dataset discovery
- protein-to-experiment lookup
- disease/organism cohort assembly
- publication-to-rawdata linkage
- MS instrument/method survey

## Join strategy

Project-level metadata exposes `DOI` (both the dataset DOI at `doi`, e.g. `10.6019/PXD000001`, and the associated-publication DOI at `references.doi`), `PMID` (`references.pubmedID`), and `ORCID` for submitters and lab PIs (`submitters.orcid`, `labPIs.orcid`; frequently blank on older records). `UNIPROT_ACCESSION` is the strongest biological join but lives at the protein/peptide identification level, not in the project record; reach it via the identification-evidence data rather than the project endpoint, so treat it as a per-molecule join within a resolved project.

The project accession is the ProteomeXchange `PXD` identifier (`PXD` + six digits; legacy submissions used `PRD`). This is the natural cross-repository join to PeptideAtlas, MassIVE, jPOST, and ProteomeCentral, but there is no canonical `PXD_IDENTIFIER` key in the registry yet. It is flagged below and held in `primary_keys` as `PXD_ACCESSION` for now. Pair PRIDE with UniProt (protein annotation), Europe PMC / PubMed (the linked publications), and the other ProteomeXchange members via the shared PXD accession.

## Access notes

Start at the REST API: `GET https://www.ebi.ac.uk/pride/ws/archive/v2/projects/{accession}` for a single project, `GET .../v2/search/projects?keyword=...&pageSize=...` for search. No auth for public data. A parallel `v3` API is live (`.../v3/projects/{accession}`). Bulk raw/result files are served from the PRIDE FTP tree (`ftp://ftp.pride.ebi.ac.uk/pride/data/archive/YYYY/MM/{accession}/`) and via Globus/Aspera for large transfers; file lists come from the project's files endpoint. No documented hard rate limit, apply EBI fair-use and paginate rather than hammer. Private/embargoed datasets require the submitter's reviewer credentials and are out of scope for anonymous access.

## MCP / connector notes

`mcp-exists`: `github.com/PRIDE-Archive/mcp_pride_archive_search`, published by the PRIDE-Archive org (treated as community maturity, not a modelcontextprotocol official server). It wraps the Archive search API with keyword search, pagination, and sort by date/popularity, over both HTTP/SSE and stdio. Gap: it covers project discovery only. It does not expose file listing, download URL construction, or protein/peptide-level identification retrieval, so an agent still drops to the raw REST/FTP endpoints for those. A fuller connector would add `get_project`, `list_project_files`, and a protein-accession-to-projects reverse lookup.

## Review notes

- New license short name used: `EMBL-EBI-Terms-of-Use`. Not in SCHEMA.md's known-license list and no SPDX code exists. Per-dataset licenses vary (the `license` field returns "EBI terms of use" by default; some datasets are marked otherwise, and PRIDE documentation references Apache-2.0 for certain project software/content). Confirm the canonical short name before merge.
- Potential new join key for review: PXD_IDENTIFIER
  Entity type: proteomics_dataset
  Pattern: "^(PXD|PRD)[0-9]{6}$"
  Other datasets that would use it: PeptideAtlas, MassIVE, jPOST, iProX, ProteomeCentral (all ProteomeXchange members share the PXD accession). Also listed in the peptideatlas and proteomexchange candidate hints. Held in primary_keys as PXD_ACCESSION until a canonical key is PR'd.
- `UNIPROT_ACCESSION` field path `proteinevidences.accession` is inferred from PRIDE's identification data model; the project-level endpoints probed (v2/v3 proteinevidences/proteins) returned 404 at the paths tried, so the exact route to protein identifications was not verified in this session. Confirm the live identification endpoint before relying on the field path.
