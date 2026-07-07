---
id: mondo
name: Mondo Disease Ontology
domain: bio-genomics
entry_kind: knowledge-graph
description: Open disease ontology that harmonises disease definitions across OMIM, Orphanet, DOID, EFO, ICD, MeSH, NCIt and more via precise equivalence axioms, minting a single canonical MONDO id per disease concept.
homepage_url: https://mondo.monarchinitiative.org/
docs_url: https://mondo.readthedocs.io/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "OLS API: unpublished; polite use expected"
bulk_available: true
frequency: monthly
lag: "~1 week for a Mondo release to load into OLS"
geography: [global]
join_keys:
  - EFO_ID
  - ICD_10
  - MESH_TERM
  - MEDDRA_TERM
  - MONDO_ID
  - OMIM_ID
  - ORPHA_CODE
primary_keys:
  - MONDO_ID
join_key_fields:
  - join_key: EFO_ID
    fields: [obo_xref, annotation.database_cross_reference]
  - join_key: ICD_10
    fields: [obo_xref, annotation.database_cross_reference]
  - join_key: MESH_TERM
    fields: [obo_xref, annotation.database_cross_reference]
  - join_key: MEDDRA_TERM
    fields: [obo_xref, annotation.database_cross_reference]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/seandavi/ols-mcp-server
  - "https://www.ebi.ac.uk/ols4/mcp (EBI-hosted OLS MCP)"
mcp_command:
  - "uvx ols-mcp-server (wraps EBI OLS4; ontologyId=mondo)"
mcp_notes: >
  No Mondo-specific MCP; Mondo is reached through generic ontology MCPs over the EBI
  Ontology Lookup Service (OLS4). Suggested surface: search_disease (label/synonym),
  get_term (MONDO id -> definition, synonyms, xrefs), map_external_id
  (OMIM/Orphanet/DOID/EFO/ICD -> MONDO), get_ancestors, get_descendants.
agent_use_cases:
  - disease name normalisation and de-duplication
  - crosswalk between OMIM / Orphanet / DOID / EFO / ICD-10 disease codes
  - disease term search and disambiguation
  - resolving free-text diagnoses to a canonical disease id
  - rare-disease subset filtering
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/ols4/api/ontologies/mondo' -H 'Accept: application/json'"
  expected_status: 200
  expected_fields: [ontologyId, numberOfTerms, config, version]
last_verified: 2026-07-02
build_priority: high
---

# Mondo Disease Ontology

## Why this source matters

Mondo is the open disease ontology built by the Monarch Initiative (funded by the NIH NHGRI) to harmonise disease definitions that are otherwise fragmented across OMIM, Orphanet, DOID, EFO, ICD, MeSH, NCIt, SNOMED CT, MedDRA, MedGen and GARD. Its distinguishing feature is a logic-based structure that asserts precise 1:1 equivalence axioms between terms in those source vocabularies, so a disease that appears under five different codes in five databases collapses to a single canonical `MONDO:` id. The current release carries roughly 29k disease concepts (~61k OLS terms including imports). For any agent stitching together clinical, genomic, and drug-target data, Mondo is the reference-class hub that lets an OMIM-coded record, an Orphanet-coded record, and an EFO-coded record be recognised as the same disease. Secondary relevance to `clinical-biotech` (Open Targets uses EFO/Mondo disease ids as its disease backbone) and `public-health` (ICD-10 crosswalks).

## Agent use cases

- disease name normalisation and de-duplication
- crosswalk between OMIM / Orphanet / DOID / EFO / ICD-10 disease codes
- disease term search and disambiguation
- resolving free-text diagnoses to a canonical disease id
- rare-disease subset filtering

## Join strategy

Mondo mints `MONDO_ID` (`MONDO:0000000`, 7-digit) as its native primary key and is the issuing authority for it. Every Mondo term carries cross-references (`xref` in OBO/OWL; `obo_xref[]` and `annotation.database_cross_reference` in OLS JSON) to the source vocabularies. Of those, the ones already in the canonical registry are `EFO_ID`, `ICD_10` (Mondo distinguishes `ICD10CM` and `ICD10WHO` xrefs, both map to the canonical `ICD_10`), `MESH_TERM`, and `MEDDRA_TERM`.

The load-bearing edges for cross-source disease joins are `OMIM`, `Orphanet`, and `DOID`, plus `MONDO_ID` itself, none of which are in the registry yet. They are flagged as new-key candidates in Review notes rather than invented into `join_keys`. Mondo is the natural place to resolve any of these against each other: hit a term, read its xref set, and pivot.

Use Mondo as the disease-identity spine and pair with Open Targets (disease-target-drug associations keyed on EFO/Mondo), ClinVar and ClinGen (variant-disease assertions), the GWAS Catalog (trait-disease mapping via EFO), and Orphanet (rare-disease detail).

## Access notes

Mondo publishes no first-party REST API; programmatic access goes through the EBI Ontology Lookup Service (OLS4), which loads each Mondo release about a week after it ships.

- Ontology metadata: `https://www.ebi.ac.uk/ols4/api/ontologies/mondo`
- Term lookup by id: `https://www.ebi.ac.uk/ols4/api/ontologies/mondo/terms?obo_id=MONDO:0007739`
- Text search: `https://www.ebi.ac.uk/ols4/api/search?q=huntington&ontology=mondo`

No auth. Rate limits are undocumented on OLS; behave politely.

Bulk downloads (the canonical source, refreshed roughly monthly) via OBO Foundry PURLs from `github.com/monarch-initiative/mondo` releases:

- `https://purl.obolibrary.org/obo/mondo.owl` — full OWL
- `https://purl.obolibrary.org/obo/mondo.obo` — OBO with xrefs (simplest for crosswalk extraction)
- `https://purl.obolibrary.org/obo/mondo.json` — OBO Graphs JSON
- `https://purl.obolibrary.org/obo/mondo/subsets/mondo-rare.owl` — rare-disease subset
- `https://purl.obolibrary.org/obo/mondo/mondo-international.owl` — international edition

For any crosswalk task touching more than a few hundred diseases, pull `mondo.obo` and read xrefs locally rather than paginating OLS.

**License nuance:** CC-BY 4.0. Attribution should cite the Mondo/Monarch Initiative publications and the specific release version (OLS exposes it in the `version` field). Note that some third-party source vocabularies Mondo cross-references (SNOMED CT, ICD) carry their own licensing; Mondo distributes only the xref mapping, not the source content, but redistributing derived SNOMED/ICD detail may still require respecting the upstream terms.

## MCP / connector notes

No Mondo-specific MCP server. Mondo is reachable through generic ontology MCPs that wrap the EBI OLS:

- `github.com/seandavi/ols-mcp-server` — community MCP over OLS4 (search terms, list ontologies, get term detail, hierarchy walks, embedding-based similarity); set `ontologyId=mondo`.
- EBI hosts an OLS4 MCP endpoint at `https://www.ebi.ac.uk/ols4/mcp` covering all OLS ontologies including Mondo.

A purpose-built disease connector should expose `search_disease` (label/synonym), `get_term` (MONDO id -> definition, synonyms, full xref set), `map_external_id` (OMIM/Orphanet/DOID/EFO/ICD/MeSH -> MONDO and back), `get_ancestors`, and `get_descendants`. The tricky part the MCP must abstract over is xref semantics: Mondo distinguishes exact/equivalent matches from close/broad/narrow matches, and a naive crosswalk that treats all xrefs as 1:1 will over-merge diseases. Surface the match predicate alongside every mapping.

## Review notes

Potential new join keys for review (Mondo is the canonical crosswalk hub for all of these, so they have broad cross-source utility):

- `MONDO_ID` — Mondo disease concept id.
  Entity type: disease
  Pattern: `^MONDO:[0-9]{7}$`
  Other datasets that would use it: Open Targets, HPO annotations, ClinGen, Monarch KG, EFO (EFO imports Mondo). Currently placed in `primary_keys` only.

- `OMIM_ID` — OMIM / OMIM phenotype-series identifier for Mendelian disease.
  Entity type: disease
  Pattern: `^(OMIM:)?[0-9]{6}$` (also `PS[0-9]{6}` for phenotypic series)
  Other datasets that would use it: OMIM, ClinVar, ClinGen, Orphanet, GARD, Open Targets.

- `ORPHA_CODE` — Orphanet rare-disease identifier.
  Entity type: rare_disease
  Pattern: `^(Orphanet:|ORPHA:)?[0-9]+$`
  Other datasets that would use it: Orphanet, OrphaData, GARD, EU rare-disease registries, Open Targets.

Also present as Mondo xrefs and worth considering later: `DOID` (Disease Ontology id, `^DOID:[0-9]+$`), `UMLS_CUI` (`^C[0-9]{7}$`), `NCIT_ID` (`^NCIT:C[0-9]+$`), `MEDGEN_ID`, `GARD_ID`, and `SNOMED_CT` (licensing-restricted). None invented into `join_keys`.

`EFO_ID`, `ICD_10`, `MESH_TERM`, and `MEDDRA_TERM` were placed in `join_keys` as they already exist in the registry and Mondo exposes them via xrefs. Domain choice is `bio-genomics` (alongside gene-ontology and the EFO-aligned genomics sources); a case exists for `clinical-biotech` given the Open Targets dependency. Flag for a maintainer call.
