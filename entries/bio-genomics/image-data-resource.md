---
id: image-data-resource
name: Image Data Resource (IDR)
domain: bio-genomics
entry_kind: corpus
description: Public repository of curated, richly annotated reference bioimaging datasets from published scientific studies, served on OMERO with a session-based JSON API, search engine, and bulk download.
homepage_url: https://idr.openmicroscopy.org/
docs_url: https://idr.openmicroscopy.org/about/api.html
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: account-required
cost: free
license: CC-BY-4.0
rate_limit: "unpublished; OMERO.web is session-backed, throttle politely and route large pulls to Globus/FTP"
bulk_available: true
frequency: "rolling; new studies curated and added on an ongoing basis"
lag: "months between a study's publication and curation into IDR"
geography: [global]
join_keys:
  - NCBI_TAXON_ID
  - GENE_SYMBOL
  - PDB_ID
primary_keys:
  - IDR_STUDY_ID
  - OMERO_SCREEN_ID
  - OMERO_PLATE_ID
  - OMERO_WELL_ID
  - OMERO_IMAGE_ID
  - OMERO_PROJECT_ID
  - OMERO_DATASET_ID
  - BIOSTUDIES_ACCESSION
join_key_fields:
  - join_key: NCBI_TAXON_ID
    fields: ["annotations[ns=mapr/organism].values", "map-annotation.Organism"]
  - join_key: GENE_SYMBOL
    fields: ["annotations[ns=mapr/gene].values", "map-annotation.Gene Symbol"]
  - join_key: PDB_ID
    fields: ["map-annotation.PDB", "annotations.values"]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No official or community MCP. OMERO.web is session-backed (cookie from a GET index call must be
  carried before API calls), the data model is a deep study>screen>plate>well>image hierarchy, and
  payloads are image-centric rather than text. A connector would mostly serve specialised bioimaging
  agents; narrow audience. Suggested surface: search_studies, get_study, list_map_annotation_values,
  search_images_by_annotation, get_image_metadata, resolve_study_to_biostudies.
agent_use_cases:
  - find imaging studies by organism, gene, phenotype, or compound
  - retrieve study and screen metadata
  - enumerate map-annotation values for a key (e.g. Gene Symbol)
  - resolve a study to its BioStudies / S-BIAD source accession
  - pull image-level metadata for a screen
access_test:
  command: "curl -sf -c /tmp/idr_cookies.txt 'https://idr.openmicroscopy.org/webclient/?experimenter=-1' >/dev/null && curl -sf -b /tmp/idr_cookies.txt 'https://idr.openmicroscopy.org/api/v0/m/screens/'"
  expected_status: 200
  expected_fields: [data, meta]
last_verified: 2026-06-22
build_priority: low
notes: "access_test constructed (session-cookie two-step), not executed in this environment"
---

# Image Data Resource (IDR)

## Why this source matters

IDR is the reference public repository of curated bioimaging data, run by the Open Microscopy Environment (OME) team and EMBL-EBI. It is an added-value subset: rather than mirroring everything published, IDR curators select imaging studies, normalise their metadata against controlled vocabularies (EFO for experimental factors, CMPO for phenotypes), and re-serve them on OMERO so they are searchable and reanalysable. Coverage spans high-content screens (RNAi, compound, and CRISPR), light and tissue microscopy across human, model-organism, and environmental samples, and a selection of electron microscopy. For an agent reasoning about gene function, phenotype, or compound effect at the image level, IDR is the place where "show me images of cells where this gene is knocked down and this phenotype appears" is actually answerable. Secondary relevance to `clinical-biotech` (compound screens, cell-line annotations) and `academic` (every study links back to its publication and a BioStudies source record).

## Agent use cases

- find imaging studies by organism, gene, phenotype, or compound
- retrieve study and screen metadata
- enumerate map-annotation values for a key (e.g. Gene Symbol)
- resolve a study to its BioStudies / S-BIAD source accession
- pull image-level metadata for a screen

## Join strategy

IDR's value for cross-source joining sits in its curated map-annotations: each study and image carries key-value pairs for organism, gene symbol, phenotype, compound, and cell line. From the canonical registry, IDR exposes `NCBI_TAXON_ID` (organism annotations), `GENE_SYMBOL` (gene annotations, HGNC for human studies), and `PDB_ID` for the subset of EM-derived structural studies that cross-reference a deposited structure. Phenotype and compound annotations are controlled-vocabulary terms (CMPO, ChEBI-adjacent) but do not map cleanly onto an existing canonical key, so they stay descriptive for now.

Native identifiers are study-internal: the `idr####` study accession (e.g. `idr0001`, where the number is the curation order) plus the OMERO numeric IDs for the screen/plate/well/image (HCS path) or project/dataset/image (standard path) objects. These live in `primary_keys`, not `join_keys`, since they are IDR/OMERO-internal. Every study links back to its source BioStudies record via an `S-BIAD` accession (`BIOSTUDIES_ACCESSION`), which is the bridge to the BioImage Archive; EM-derived studies additionally cross-reference EMDB and PDB.

Recommended pivot: resolve a study to its `S-BIAD` accession to reach the raw deposited data in the BioImage Archive, or use the gene/organism map-annotations to join image phenotypes back to UniProt/Ensembl-anchored gene context.

## Access notes

OMERO.web is session-backed, this is the load-bearing access gotcha. There is no stateless API key. You must first issue a GET to an index endpoint (e.g. `https://idr.openmicroscopy.org/webclient/?experimenter=-1`) to obtain a session cookie, then carry that cookie on every subsequent API call. The JSON API base is `https://idr.openmicroscopy.org/webclient/api/` (and the OMERO JSON API at `/api/v0/m/`); map-annotations come back from the annotations endpoints with `type=map`.

The data model is a deep hierarchy: study/screen > plate > well > image for high-content screens, and project > dataset > image for standard microscopy. Navigating from a study down to individual images is several API calls deep, plan traversal rather than expecting flat result sets. The search engine API surfaces all values for a given annotation key (e.g. every "Gene Symbol" present) and returns images matching a key-value filter.

For anything beyond metadata browsing, use bulk: IDR offers Globus and FTP/Aspera download of raw image data, which is large. Freshness can be checked by listing studies (new `idr####` accessions appear as curation completes). Data is CC-BY-4.0 (attribution required); note the distinction between the data licence and the OMERO software, which is GPL.

## MCP / connector notes

No official or community MCP. Suggested surface if built: `search_studies` (by organism / gene / phenotype / compound), `get_study`, `list_map_annotation_values` (enumerate values for an annotation key), `search_images_by_annotation`, `get_image_metadata`, `resolve_study_to_biostudies`. The connector must abstract over two hard parts: (1) the session-cookie handshake (GET index, persist cookie, attach to all calls), and (2) the deep object hierarchy, exposing study-level and annotation-level queries rather than forcing callers to walk plate>well>image themselves. Image payloads are large and binary-adjacent; default to returning metadata and annotation values, not pixel data. Narrow audience (specialised bioimaging agents), hence low-value rather than high-value.

## Review notes

Potential new primary/join keys for review (flagged, not added to the registry):

Potential new join key for review: IDR_STUDY_ID
  Entity type: bioimaging_study
  Pattern: ^idr[0-9]{4}$
  Other datasets that would use it: IDR-internal; cross-referenced from BioStudies / BioImage Archive

Potential new join key for review: BIOSTUDIES_ACCESSION
  Entity type: biostudies_submission
  Pattern: ^S-[A-Z]{4}[0-9]+$ (S-BIAD form for BioImage Archive submissions)
  Other datasets that would use it: BioStudies, BioImage Archive, EMPIAR-adjacent EM deposits, IDR

Both are currently in `primary_keys` (source-native). They are flagged here because BioStudies/BioImage Archive and EMPIAR-adjacent EM resources would reference the same accessions, so they may have cross-source utility if those sources are later added. Stephanie reviews and decides whether to PR them into `schema/join-keys.yaml`.
