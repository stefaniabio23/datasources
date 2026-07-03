---
id: hmdb
name: HMDB (Human Metabolome Database)
domain: bio-genomics
entry_kind: knowledge-graph
description: Curated knowledgebase of small-molecule human metabolites with chemical, clinical, and biochemical annotation cross-linked to major chemistry and biology databases.
homepage_url: https://hmdb.ca/
docs_url: https://hmdb.ca/downloads
type:
  - bulk-download
  - dataset-dump
  - rest-api
  - web-ui
auth_required: none
cost: free-non-commercial
license: CC-BY-NC-4.0
bulk_available: true
frequency: irregular
lag: "major versions every few years (v5.0 released 2022)"
geography: [global]
join_keys:
  - CHEBI_ID
  - INCHI_KEY
  - DRUGBANK_ID
  - UNIPROT_ACCESSION
  - GENE_SYMBOL
primary_keys:
  - HMDB_ID
join_key_fields:
  - join_key: CHEBI_ID
    fields: [metabolite.chebi_id]
  - join_key: INCHI_KEY
    fields: [metabolite.inchikey]
  - join_key: DRUGBANK_ID
    fields: [metabolite.drugbank_id]
  - join_key: UNIPROT_ACCESSION
    fields: [metabolite.protein_associations.protein.uniprot_id]
  - join_key: GENE_SYMBOL
    fields: [metabolite.protein_associations.protein.gene_name]
mcp_status: mcp-exists
mcp_maturity: experimental
mcp_package:
  - "github.com/QuentinCody/hmdb-mcp-server"
mcp_command:
  - "npx mcp-remote https://hmdb-mcp-server.quentincody.workers.dev/mcp"
mcp_notes: >
  Single community MCP (Cloudflare Worker, remote). Exposes hmdb_search (endpoint
  discovery), hmdb_execute (API call), hmdb_query_data (SQL over staged SQLite),
  hmdb_get_schema. Wraps the request-gated HMDB API; large responses staged to SQLite.
agent_use_cases:
  - metabolite identity resolution
  - metabolite-to-gene/protein mapping
  - biomarker and disease-association lookup
  - pathway annotation
  - chemical cross-reference bridging
last_verified: 2026-07-02
build_priority: medium
notes: "All endpoints sit behind Cloudflare; curl/non-browser clients get 403. Bulk XML downloads are free without an account; programmatic REST API access is granted per-request by emailing the HMDB team. access_test omitted because no no-auth endpoint is reliably executable outside a browser."
---

# HMDB (Human Metabolome Database)

## Why this source matters

HMDB is the reference knowledgebase for the human metabolome, run by the Wishart lab at the University of Alberta. Version 5.0 (2022) holds ~220k metabolite entries (~217k annotated plus large GC-MS derivatized sets) and ~8,600 linked protein sequences, each MetaboCard carrying up to ~130 fields split across chemical, clinical, and enzymatic/biochemical annotation. For any agent working in metabolomics, biomarker discovery, or clinical chemistry, HMDB is the canonical entity table that ties a metabolite to its structure, its associated proteins and genes, its disease associations, and its identifiers in every other major chemistry database. It secondarily touches `clinical-biotech` through biomarker and disease-association fields.

## Agent use cases

- metabolite identity resolution
- metabolite-to-gene/protein mapping
- biomarker and disease-association lookup
- pathway annotation
- chemical cross-reference bridging

## Join strategy

HMDB is a cross-reference hub for small molecules. It exposes `INCHI_KEY` (structure hash) and `CHEBI_ID` (EBI chemical ontology) as the primary chemistry joins, `DRUGBANK_ID` where a metabolite is also a drug, and, via each metabolite's `protein_associations`, `UNIPROT_ACCESSION` and `GENE_SYMBOL` for the enzymes and transporters that act on it. Pair with ChEBI/ChEMBL for chemistry, UniProt/Ensembl for the protein and gene side, and DrugBank for pharmacology.

The source-internal `HMDB_ID` (accession form `HMDB` + digits, e.g. `HMDB0000001`) is the primary key; it is widely referenced by other metabolomics resources (MetaboLights, Metabolomics Workbench, KEGG, PubChem) and is a strong candidate for the canonical registry (flagged below). HMDB also carries KEGG, PubChem CID, and CAS identifiers that are not yet canonical keys (flagged below). InChIKey is the most reliable structure-level join because it is provider-independent.

## Access notes

Two access paths. First, bulk downloads at `https://hmdb.ca/downloads` (full-database XML plus per-category TXT/CSV/JSON/XML, and SDF/MOL structure files) are free and need no account. Second, a programmatic REST API exists but access is granted per request: academic groups email the HMDB team (contacts on `https://hmdb.ca/simple/api`) and commercial groups arrange customized API access. The whole site is behind Cloudflare, so plain curl or server-side fetchers get HTTP 403; downloads and API calls in practice run from a browser or an approved client with a real user agent. To check freshness without downloading, read `https://hmdb.ca/release-notes` (last major release: v5.0, 2022; updates are irregular, not on a fixed cadence). Parse the full XML with a streaming parser (the complete dump is large); community parsers exist (HMDBParser, OmnipathR `hmdb_table`, Bioconductor `hmdbQuery`).

## MCP / connector notes

One community MCP exists: `github.com/QuentinCody/hmdb-mcp-server`, a remote Cloudflare-Worker server (TypeScript) exposing `hmdb_search`, `hmdb_execute`, `hmdb_query_data` (SQL over staged SQLite), and `hmdb_get_schema`. It wraps the request-gated HMDB API and stages large responses (>30KB) into queryable SQLite. Maturity is experimental (single maintainer, remote-hosted worker; depends on upstream API access). A more robust connector would abstract over the Cloudflare gate and the bulk-XML-vs-API split, and expose typed lookups: `get_metabolite`, `search_by_name`, `resolve_inchikey`, `metabolite_to_proteins`, `disease_associations`.

## Review notes

License is CC-BY-NC-4.0 (non-commercial; commercial reuse or redistribution requires explicit permission and acknowledgment of HMDB plus the original publication). SPDX code used directly.

Potential new join keys for review:

Potential new join key for review: HMDB_ID
  Entity type: metabolite
  Pattern: "^HMDB[0-9]+$" (v5 zero-pads to 7 digits, e.g. HMDB0000001; legacy 5-digit form HMDB00001 also circulates)
  Other datasets that would use it: MetaboLights, Metabolomics Workbench, KEGG, PubChem, FooDB, MarkerDB, NP-MRD

Potential new join key for review: KEGG_COMPOUND_ID
  Entity type: metabolite_or_compound
  Pattern: "^C[0-9]{5}$"
  Other datasets that would use it: KEGG, ChEBI, PubChem, MetaCyc, Reactome

Potential new join key for review: PUBCHEM_CID
  Entity type: chemical_compound
  Pattern: "^[0-9]+$"
  Other datasets that would use it: PubChem, ChEBI, ChEMBL, DrugBank, most chemistry sources

Potential new join key for review: CAS_RN
  Entity type: chemical_substance
  Pattern: "^[0-9]{2,7}-[0-9]{2}-[0-9]$"
  Other datasets that would use it: PubChem, ChEBI, DrugBank, DSSTox
