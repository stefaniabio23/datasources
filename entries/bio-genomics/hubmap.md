---
id: hubmap
name: HuBMAP Data Portal
domain: bio-genomics
entry_kind: registry
description: NIH Human BioMolecular Atlas Program portal of multi-modal spatial and single-cell datasets from healthy human tissue, with donor/sample/dataset provenance.
homepage_url: https://portal.hubmapconsortium.org/
docs_url: https://docs.hubmapconsortium.org/apis.html
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
frequency: "continuous (new datasets published on a rolling basis)"
geography: [USA]
join_keys:
  - UBERON_ID
  - DOI
primary_keys:
  - HUBMAP_ID
  - HUBMAP_UUID
join_key_fields:
  - join_key: UBERON_ID
    fields:
      - ancestors.rui_location.ccf_annotations
      - origin_samples.rui_location.ccf_annotations
  - join_key: DOI
    fields:
      - registered_doi
      - doi_url
mcp_status: mcp-needed-low-value
agent_use_cases:
  - find spatial and single-cell datasets by organ
  - retrieve tissue sample and donor provenance
  - cross-reference anatomy via UBERON
  - download processed single-cell matrices
  - map donor demographics to tissue datasets
access_test:
  command: "curl -sf -X POST 'https://search.api.hubmapconsortium.org/v3/search' -H 'Content-Type: application/json' -d '{\"size\":1,\"query\":{\"term\":{\"entity_type.keyword\":\"Dataset\"}}}'"
  expected_status: 200
  expected_fields: [hits, _source, hubmap_id, entity_type]
last_verified: 2026-07-02
build_priority: low
structure: registry-snapshot
pit_reconstructable: false
---

# HuBMAP Data Portal

## Why this source matters

The Human BioMolecular Atlas Program (HuBMAP) is an NIH Common Fund consortium building a multi-scale spatial atlas of healthy human tissue. The Data Portal indexes datasets generated on emerging single-cell and spatial assays (CODEX, scRNA-seq, snRNA-seq, Visium, imaging mass cytometry, MALDI, and more) together with their donor, tissue-sample, and processing provenance. Every biological entity (donor, sample, dataset, collection) carries a stable HuBMAP ID and UUID, and published datasets are DOI-minted. An agent building or querying a reference of healthy human tissue biology, anatomy-anchored expression, or spatial-omics benchmarks treats HuBMAP as the canonical open source. Secondary relevance to `clinical-biotech` (tissue reference for disease comparison) and `geospatial` in the anatomical sense (Common Coordinate Framework spatial registration of samples within organs).

## Agent use cases

- find spatial and single-cell datasets by organ
- retrieve tissue sample and donor provenance
- cross-reference anatomy via UBERON
- download processed single-cell matrices
- map donor demographics to tissue datasets

## Join strategy

Two canonical join keys are exposed. `UBERON_ID` anchors every registered sample to cross-species anatomy through the Common Coordinate Framework: the `rui_location.ccf_annotations` arrays on ancestor and origin-sample records list UBERON terms as full OBO PURLs (e.g. `http://purl.obolibrary.org/obo/UBERON_0002113`), so an agent must strip the PURL prefix and rewrite `UBERON_NNNNNNN` to the canonical `UBERON:NNNNNNN` form before joining to GTEx, Ensembl tissue expression, or any UBERON-keyed source. `DOI` (`registered_doi`, `doi_url`) identifies the ~8,300 published datasets and joins to OpenAlex, Crossref, and Europe PMC for citing literature.

Source-internal identifiers are the HuBMAP ID (human-readable, e.g. `HBM638.SMWG.276`) and the 32-character UUID; both live in `primary_keys` and are the handles for direct Entity API lookups, not for cross-source joins. Cell-type annotations use Cell Ontology (CL) terms through the Cells / scFind services, but CL is not yet a canonical registry key (see Review notes).

## Access notes

Public (published) data is fully queryable with no auth. Hit the Search API first: `POST https://search.api.hubmapconsortium.org/v3/search` with an Elasticsearch query DSL body against the `hm_prod_public_entities` index. Filter on `entity_type.keyword` (`Donor` / `Sample` / `Dataset` / `Collection`). Protected and consortium-internal entities require a Globus Nexus bearer token (`Authorization: Bearer <token>`) and a HuBMAP/Globus account; unauthenticated calls simply return the public subset. Bulk file downloads go through Globus or the HuBMAP Command Line Transfer (CLT) tool; the Search API can emit a CLT manifest with `?produce-clt-manifest=true`. Companion Entity, UUID, and Ontology (UBKG) APIs cover provenance and vocabulary lookups. Community client libraries exist: `HuBMAPR` (R/Bioconductor) and Python helpers. Rate limits are not documented; be polite on the ES endpoint.

## MCP / connector notes

No MCP server exists. A connector would abstract over the raw Elasticsearch query DSL, which is the main friction for agents. Suggested surface: `search_datasets(organ, assay_type, ...)`, `get_entity(hubmap_id)`, `get_provenance(uuid)`, `list_files(uuid)` / `build_clt_manifest(query)`, and `resolve_anatomy(uberon)`. The connector must normalise UBERON PURLs to canonical `UBERON:` form, page ES results, and route large file pulls to Globus/CLT rather than inlining them. Audience is fairly narrow (spatial / single-cell researchers), hence low build priority.

## Review notes

Potential new join keys for review:

- Proposed key: `HUBMAP_ID`
  - Entity type: tissue_biosample_or_dataset
  - Pattern: `^HBM[0-9]{3}\.[A-Z]{4}\.[0-9]{3}$` (e.g. `HBM638.SMWG.276`)
  - Other datasets that would use it: SenNet, CCF/HRA reference atlas, and cross-references from GEO/dataset citations. Currently held in `primary_keys` only.

- Proposed key: `CL_ID` (Cell Ontology)
  - Entity type: cell_type
  - Pattern: `^CL:[0-9]{7}$`
  - Other datasets that would use it: CellxGene, Azimuth references, Human Cell Atlas, Tabula Sapiens, and any single-cell atlas with cell-type annotations. Broad cross-source utility; strong candidate for the registry. HuBMAP exposes CL terms via the Cells / scFind and UBKG services rather than the core entity index.

License note: HuBMAP data, APIs, and the CCF 3D Reference Object Library are released under CC BY 4.0 (attribution required, commercial use allowed). Confirmed against the HuBMAP FAQ and APIs pages; SPDX `CC-BY-4.0` used.
