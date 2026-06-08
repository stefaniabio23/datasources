---
id: string-db
name: STRING
domain: bio-genomics
description: Database of known and predicted protein-protein interactions across ~12,500 organisms, covering ~59M proteins and 20B+ functional associations from experiments, co-expression, text-mining, and genomic context.
homepage_url: https://string-db.org/
docs_url: https://string-db.org/help/api/
type:
  - rest-api
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "no published quota; docs ask that the API only be used for limited or occasional access (use bulk dumps for analysis-scale pulls)"
bulk_available: true
frequency: "major version every 1-2 years (v12.0 current)"
lag: "months between releases; underlying source data refresh varies"
geography: [global]
join_keys:
  - UNIPROT_ACCESSION
  - ENSEMBL_ID
  - GENE_SYMBOL
primary_keys:
  - STRING_PROTEIN_ID
join_key_fields:
  - join_key: ENSEMBL_ID
    fields: [stringId, stringId_A, stringId_B]
  - join_key: GENE_SYMBOL
    fields: [preferredName, preferredName_A, preferredName_B]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/Augmented-Nature/STRING-db-MCP-Server
  - github.com/MCPmed/STRINGmcp
  - github.com/pipeworx-io/mcp-string-db
mcp_notes: >
  Three community MCPs exist (JS, Python, TS); no official server. All wrap the REST
  API; none documents the bulk-snapshot path. A good MCP routes small queries
  through the API and warns the agent to switch to bulk dumps past ~1k network calls.
agent_use_cases:
  - protein interaction lookup
  - pathway and complex discovery
  - functional enrichment
  - gene-set network construction
  - homology mapping across species
access_test:
  command: "curl -sf 'https://string-db.org/api/json/network?identifiers=TP53&species=9606'"
  expected_status: 200
  expected_fields: [stringId_A, stringId_B, preferredName_A, preferredName_B, ncbiTaxonId, score]
last_verified: 2026-06-08
build_priority: medium
---

# STRING

## Why this source matters

Functional protein-association network covering ~59M proteins across ~12,500 organisms, with ~20B scored interactions integrated from experiments, curated databases, co-expression, conserved genomic context, and literature text-mining. Maintained by the STRING Consortium (SIB, CPR, EMBL). For any agent reasoning about protein function, pathway membership, drug-target context, or gene-set biology, STRING is the canonical first stop for "what does this protein interact with, and how confident are we." CC-BY-4.0 with both a REST API and full bulk dumps (per-organism TSVs plus SQL schema). Secondary use as a bridge resource: STRING normalises across UniProt, Ensembl, and gene symbols, so it works well as a join hub in multi-source protein analyses.

## Agent use cases

- protein interaction lookup
- pathway and complex discovery
- functional enrichment
- gene-set network construction
- homology mapping across species

## Join strategy

STRING accepts and normalises three canonical identifier families: `UNIPROT_ACCESSION` (e.g. P04637), `ENSEMBL_ID` (protein IDs like ENSP00000269305), and `GENE_SYMBOL` (e.g. TP53). The `/get_string_ids` endpoint resolves messy inputs to canonical STRING IDs first; downstream calls expect those.

STRING-internal IDs follow the form `<taxon>.<ENSP>` (e.g. `9606.ENSP00000269305` for human TP53). These are best treated as STRING-local handles for follow-up calls, not as cross-source join keys. NCBI taxon IDs (`species=9606`) parameterise nearly every call but are out of scope for the current join-key registry.

Pair with UniProt for canonical protein metadata and sequence, Ensembl for gene-to-transcript-to-protein mapping, ChEMBL for drug-target context, and OpenAlex / Europe PMC for citing literature behind text-mined edges.

## Access notes

**Single-protein and small-network queries:** REST API at `https://string-db.org/api/<format>/<method>`. Formats: `tsv`, `tsv-no-header`, `json`, `xml`, `psi-mi`, `psi-mi-tab`, plus `image` / `svg` for network plots. Core methods: `get_string_ids`, `network`, `interaction_partners`, `enrichment`, `ppi_enrichment`, `homology`. Always pass `species=<taxon>` (NCBI taxonomy ID) to avoid cross-organism mismatches.

**Anything analysis-scale:** Switch to bulk downloads from the per-organism downloads page. Key files per species: `protein.links.full.<v>.txt.gz` (all edges with sub-scores), `protein.info.<v>.txt.gz` (annotations and preferred names), `protein.aliases.<v>.txt.gz` (cross-references to UniProt, Ensembl, RefSeq, etc.). Full SQL dumps available for local installs. The docs explicitly ask not to hammer the API for bulk analyses.

Known gotchas:

- API has no published rate-limit number; behaviour at scale is undefined. Treat as "be polite, cache, and move to bulk past ~hundreds of calls."
- Confidence score is a 0-1000 integer in bulk files but 0-1 float in API JSON. Normalise before merging.
- A `score` of 0.400 (medium) is the default UI threshold; do not assume edges below that are meaningful.
- Major releases (v11 → v12) renumber STRING-internal IDs. Pin the version in any reproducible analysis.

## MCP / connector notes

Three community MCPs exist (none official): `Augmented-Nature/STRING-db-MCP-Server` (JS), `MCPmed/STRINGmcp` (Python), `pipeworx-io/mcp-string-db` (TypeScript). All wrap the REST surface (`get_string_ids`, `network`, `interaction_partners`, `enrichment`) and none documents a bulk-snapshot path. A production-grade MCP should: route small per-protein queries to the API, intercept gene-set-scale requests and either advise switching to bulk or stream from a cached snapshot, normalise the 0-1 vs 0-1000 score scaling, and resolve aliases via `get_string_ids` before any downstream call. Maturity is community, so pick one and pin a commit.

## Review notes

- `mcp_package` lists three community MCPs; consider promoting one as the recommended pick after a brief comparison (none looks clearly canonical from a search alone).
- STRING-internal identifiers (`STRING_PROTEIN_ID`, format `<taxon>.<ENSP>`) are not in `schema/join-keys.yaml`; they are intentionally local to STRING and probably should not be promoted unless another source begins exporting them.
- NCBI taxon IDs (`NCBI_TAXON_ID`) recur across STRING, NCBI Gene, UniProt, Ensembl, and most bio-genomics sources. Potential new canonical join key:
  - Entity type: organism
  - Pattern: `^[0-9]+$`
  - Other datasets that would use it: NCBI Gene, UniProt, Ensembl, NCBI SRA, NCBI GEO (all already in `entries/bio-genomics/`).
