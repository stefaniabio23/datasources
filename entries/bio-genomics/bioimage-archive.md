---
id: bioimage-archive
name: BioImage Archive
domain: bio-genomics
entry_kind: corpus
description: EMBL-EBI's open, cross-modality archive of life-sciences biological imaging data (light, EM, super-resolution, high-content, whole-slide) plus segmentations and AI training sets, built on BioStudies infrastructure with per-study S-BIAD accessions.
homepage_url: https://www.ebi.ac.uk/bioimage-archive/
docs_url: https://www.ebi.ac.uk/bioimage-archive/help-rest-api/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: varies-per-study
bulk_available: true
frequency: "continuous on submission; no fixed release cycle"
lag: "study appears at submitter-set release date; embargo until associated publication is common"
geography: [global]
join_keys:
  - NCBI_TAXON_ID
primary_keys:
  - BIOSTUDIES_ACCESSION
  - BIOSAMPLE_ID
  - ENA_ACCESSION
  - EMDB_ID
  - PDB_ID
join_key_fields:
  - join_key: NCBI_TAXON_ID
    fields: ["section.subsections.attributes[name=Organism]", "section.subsections.attributes[name=Taxon]"]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No official MCP. BioStudies REST is clean enough for direct use on metadata retrieval, but the
  freeform per-study section/attribute model means a connector adds value mainly by normalising
  heterogeneous acquisition/channel/resolution metadata and resolving file lists for bulk pulls.
  Suggested surface: search_studies, get_study, list_study_files, resolve_ftp_path.
agent_use_cases:
  - bioimaging dataset discovery by modality or organism
  - retrieval of AI/ML training image sets and segmentation masks
  - cross-referencing imaging studies to linked sequence/structure records
  - bulk download of imaging study files for local analysis
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BIAD7'"
  expected_status: 200
  expected_fields: [accno, attributes, section]
last_verified: 2026-06-22
build_priority: medium
---

# BioImage Archive

## Why this source matters

The BioImage Archive is EMBL-EBI's free, open archive for biological imaging data that supports any published study, run as the home for bioimaging data that has value beyond a single experiment. It is cross-modality where most image resources are not: light microscopy, electron microscopy, super-resolution, high-content screening, and whole-slide histopathology all sit alongside derived segmentations and machine-learning training sets, at petabyte scale. It implements the REMBI metadata guidelines for FAIR bioimaging and provides the archiving layer beneath specialised community resources including the Image Data Resource (IDR) and EMPIAR. For an agent assembling imaging datasets, mapping what microscopy data exists for an organism or assay, or sourcing labelled images for model training, this is the broad superset to search first. Secondary relevance to `academic` (each study cites its source publication) and `clinical-biotech` (high-content screening, histopathology); it explicitly cannot accept patient-identifiable clinical medical images.

## Agent use cases

- bioimaging dataset discovery by modality or organism
- retrieval of AI/ML training image sets and segmentation masks
- cross-referencing imaging studies to linked sequence/structure records
- bulk download of imaging study files for local analysis

## Join strategy

The archive is built on BioStudies, so every study carries a BioStudies accession in the `S-BIAD#####` namespace (`BIOSTUDIES_ACCESSION`, a primary key). That accession is the stable handle for any cross-reference back into the archive. Of the canonical registry keys, only `NCBI_TAXON_ID` is reliably exposed, and even then only when submitters populate an organism/taxon attribute. Studies frequently link out to associated records in other EBI/INSDC resources, BioSample, ENA, EMDB, and PDB, but these appear as freeform attribute links rather than enforced structured fields, so they are recorded as `primary_keys` (`BIOSAMPLE_ID`, `ENA_ACCESSION`, `EMDB_ID`, `PDB_ID`) rather than as canonical joins. Pair with IDR for the curated, queryable subset of this archive when a study has been re-published there; pair with UniProt/Ensembl via taxon for organism context.

## Access notes

Metadata is served through the BioStudies REST API: hit `https://www.ebi.ac.uk/biostudies/api/v1/studies/{accession}` (e.g. `S-BIAD7`) for a single study record, no auth. The returned JSON is a `Study > section > subsections > files` tree: top-level `accno` and `attributes` carry title and release date, subsections carry authors, organisation, and per-experiment metadata, and files are nested under experiment subsections (no enforced image-level object, the hierarchy bottoms out at study-level file lists). Bulk file access is via FTP plus Aspera and Globus for large transfers off the study's file paths. License is per study and lives on each study page, defaulting to the EMBL-EBI Terms of Use (effectively open; many studies are CC0 or CC-BY); always read the study-level license attribute before redistributing.

Metadata is freeform and inconsistent: acquisition parameters, channel definitions, and resolution are submitter-supplied with no enforced schema, and while OME-TIFF and OME-Zarr are the preferred formats they are not mandated, so file formats vary across studies. Verify freshness by checking recent accessions via the BioStudies search API rather than expecting a fixed release cadence.

## MCP / connector notes

No official or community MCP. Low-to-medium value as a dedicated connector: the BioStudies REST API is clean enough that direct calls suffice for metadata retrieval, so an MCP's main payoff is normalising the heterogeneous freeform metadata (mapping submitter-specific channel/acquisition/resolution fields onto a consistent shape) and resolving study file lists to concrete FTP/Aspera/Globus paths for bulk pulls. Suggested surface: `search_studies` (by modality, organism, keyword), `get_study` (trimmed metadata tree), `list_study_files`, `resolve_ftp_path`. The connector must abstract over the absence of an image-level object and the inconsistency of cross-reference attributes.

## Review notes

`BIOSTUDIES_ACCESSION` (the `S-BIAD#####` study accession) is flagged for review as a potential new canonical join key. IDR re-publishes curated subsets of BioImage Archive studies, so the BioStudies accession is the stable cross-resource handle linking the broad archive to its curated IDR subset and back to the source publication.

```
Potential new join key for review: BIOSTUDIES_ACCESSION
  Entity type: biostudies_study
  Pattern: ^S-[A-Z]+[0-9]+$  (BioImage Archive subspace: ^S-BIAD[0-9]+$)
  Other datasets that would use it: BioImage Archive, IDR, EMPIAR, BioStudies, ArrayExpress
```

Other identifiers BioImage Archive studies link to but that are not in the canonical registry (recorded here as primary_keys, candidates for future review): `BIOSAMPLE_ID`, `ENA_ACCESSION`, `EMDB_ID`. `PDB_ID` is already in the registry but was not confirmed as a structured field on the studies fetched; it appears only as freeform attribute links, hence kept in primary_keys rather than join_keys.

License is per-study (`varies-per-study`), not a single SPDX code; the default EMBL-EBI Terms of Use are effectively open but redistribution should be checked against the study-level license attribute case by case.
