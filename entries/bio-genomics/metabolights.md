---
id: metabolights
name: MetaboLights
domain: bio-genomics
entry_kind: registry
description: EMBL-EBI open repository of metabolomics studies, raw and derived experimental data, metabolite structures, and reference spectra.
homepage_url: https://www.ebi.ac.uk/metabolights/
docs_url: https://www.ebi.ac.uk/metabolights/ws/api/spec.html
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC0
rate_limit: "no documented hard limit; polite use expected on the public web service"
bulk_available: true
frequency: continuous
lag: "days-to-weeks between submission acceptance/curation and public release"
geography: [global]
join_keys:
  - CHEBI_ID
  - PMID
  - DOI
  - HMDB_ID
primary_keys:
  - MTBLS_ID
join_key_fields:
  - join_key: CHEBI_ID
    fields:
      - "compound.chebiId"
      - "metaboliteAssignment.database_identifier"
  - join_key: PMID
    fields:
      - "publications.pubMedID"
  - join_key: DOI
    fields:
      - "publications.doi"
mcp_status: mcp-needed-high-value
agent_use_cases:
  - metabolomics study retrieval
  - metabolite-to-study lookup
  - reference spectra retrieval
  - cross-omics compound joining via ChEBI
  - publication-linked dataset discovery
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/metabolights/ws/studies/MTBLS1'"
  expected_status: 200
  expected_fields: [mtblsStudy, studyStatus, studyFtpUrl]
last_verified: 2026-07-02
build_priority: medium
---

# MetaboLights

## Why this source matters

MetaboLights is EMBL-EBI's open, cross-species, cross-technique repository for metabolomics experiments: raw and derived data files, ISA-Tab study metadata, metabolite assignment files, and metabolite structures with reference spectra. It is the ELIXIR-recommended metabolomics deposition database and the metabolomics counterpart to ProteomeXchange (proteomics) and ArrayExpress/GEO (transcriptomics). Each study carries a stable `MTBLS` accession usable as a publication reference. For an agent, it is the canonical entry point for finding which metabolites were measured in which biological context, with the raw instrument data attached.

## Agent use cases

- metabolomics study retrieval
- metabolite-to-study lookup
- reference spectra retrieval
- cross-omics compound joining via ChEBI
- publication-linked dataset discovery

## Join strategy

MetaboLights exposes `CHEBI_ID` on curated metabolites (it is itself a major submitter of new entries to ChEBI) and, in metabolite assignment files (`m_*.tsv`), the `database_identifier` column carries ChEBI accessions for measured compounds. This makes ChEBI the primary bridge to ChEMBL, Reactome, KEGG, and other chemistry-aware sources. Study metadata links to source literature via `PMID` and `DOI` (ISA `publications`), so it pairs with OpenAlex, Europe PMC, and PubMed for provenance and with any DOI-keyed source for the dataset citation.

The source-native study accession (`MTBLS` prefix, e.g. `MTBLS1`) is the internal primary key. It is not yet a canonical registry key; it is flagged below as a new-key candidate because it appears in the literature and in cross-database links (ELIXIR, MetabolomicsWorkbench mirrors, journal data-availability statements).

## Access notes

Hit the public REST web service first: base `https://www.ebi.ac.uk/metabolights/ws/`. `GET /studies` returns every public accession; `GET /studies/{MTBLS_ID}` returns study status plus FTP/HTTP/Globus data URLs. Swagger UI at the `docs_url`. No auth for public read; submitter/curator operations require an API token, not needed for retrieval. Bulk data lives on the EBI FTP tree (`ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/<MTBLS_ID>`) with Globus for large transfers; use FTP/Globus rather than the API for raw instrument files.

License nuance: CC0 is the default for datasets submitted from April 2025 and is the recommended license; some older studies may carry different terms, so check the per-study `revisionComment`/license field before redistributing pre-2025 raw data. All access is governed by EMBL-EBI Terms of Use.

## MCP / connector notes

No MCP server exists yet (community discussion lists MetaboLights as a planned metabolomics connector). High value: it overlaps with the omics-repository audience already served by several bio-genomics entries (ProteomeXchange, ArrayExpress, GEO, Expression Atlas), so one connector serves multiple agents. Suggested surface: `search_studies` (by compound / organism / technique), `get_study` (metadata + data URLs), `get_study_publications`, `get_study_metabolites` (ChEBI-resolved), `get_reference_spectrum`. The connector must abstract over the split between the JSON web service (metadata) and the FTP/Globus tree (raw files), and over ISA-Tab parsing for assignment files.

## Review notes

Potential new join key for review: MTBLS_ID
  Entity type: metabolomics_study
  Pattern: ^MTBLS[0-9]+$
  Other datasets that would use it: MetabolomicsWorkbench (cross-links), Europe PMC / journal data-availability statements, ELIXIR deposition records.

License is CC0 for the modern default but heterogeneous across pre-April-2025 studies; captured as `CC0` in YAML with the caveat in Access notes. No new domain or enum values required.
