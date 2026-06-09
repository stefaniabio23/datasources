---
id: ncbi-taxonomy
name: NCBI Taxonomy
domain: bio-genomics
entry_kind: knowledge-graph
description: NCBI-curated classification and nomenclature for every organism represented in the public sequence databases, with a stable integer taxon ID linking nucleotide, protein, gene, assembly, BioSample, and PubMed records across NCBI and downstream resources.
homepage_url: https://www.ncbi.nlm.nih.gov/taxonomy
docs_url: https://www.ncbi.nlm.nih.gov/books/NBK53758/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free
license: US-Government-Public-Domain
rate_limit: "3 req/sec anon; 10 req/sec with free api_key (higher on request)"
bulk_available: true
frequency: daily
lag: "hours for new taxon additions to appear via E-utilities; daily taxdump snapshots on FTP"
geography: [global]
join_keys:
  - NCBI_TAXON_ID
  - PMID
primary_keys:
  - NCBI_TAXON_ID
join_key_fields:
  - join_key: NCBI_TAXON_ID
    fields: [result.<uid>.taxid, result.<uid>.uid, result.<uid>.akataxid]
  - join_key: PMID
    fields: [linksets.linksetdbs.links]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/Augmented-Nature/NCBI-Datasets-MCP-Server
  - github.com/noahzeidenberg/ncbi-mcp
  - github.com/vitorpavinato/ncbi-mcp-server
mcp_notes: >
  No official MCP. Augmented-Nature/NCBI-Datasets-MCP-Server exposes dedicated
  search_taxonomy, get_taxonomy_info, and get_organism_info tools alongside its
  genome/gene/assembly coverage. The other E-utilities-based community servers
  can hit db=taxonomy generically via esearch/esummary/efetch but typically lack
  taxonomy-specific helpers (lineage walking, rank filtering, name-to-ID
  resolution with synonym handling).
agent_use_cases:
  - organism name to taxon ID resolution
  - lineage and rank lookup for a taxon
  - taxonomic subtree enumeration (all descendants of a clade)
  - cross-database joins via NCBI_TAXON_ID
  - genetic code and division lookup per organism
access_test:
  command: "curl -sf 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy&id=9606&retmode=json'"
  expected_status: 200
  expected_fields: [header, result]
last_verified: 2026-06-09
build_priority: high
---

# NCBI Taxonomy

## Why this source matters

The de facto reference classification for every organism represented in GenBank, RefSeq, SRA, BioSample, and the rest of the NCBI ecosystem. Curated by the National Library of Medicine (part of NIH), it assigns a stable integer taxon ID to each node in a single hierarchical tree spanning archaea, bacteria, eukaryotes, viruses, and unclassified sequences, currently covering roughly 10% of described species on Earth. Any agent that needs to resolve an organism name (with synonyms, misspellings, and rank variation) to a single canonical ID, walk lineage, enumerate descendants of a clade, or join across NCBI databases passes through this resource. Secondary relevance to `clinical-biotech` (pathogen and host-organism resolution) and `public-health` (surveillance pipelines keyed on taxon IDs).

## Agent use cases

- organism name to taxon ID resolution
- lineage and rank lookup for a taxon
- taxonomic subtree enumeration (all descendants of a clade)
- cross-database joins via NCBI_TAXON_ID
- genetic code and division lookup per organism

## Join strategy

NCBI Taxonomy is the issuing authority for `NCBI_TAXON_ID` (integer, e.g. `9606` for Homo sapiens, `10090` for mouse, `562` for E. coli). The taxon ID is the most universally recognised cross-source organism key in bio-genomics: UniProt, Ensembl, NCBI Gene, NCBI Nucleotide, NCBI Protein, NCBI SRA, BioSample, BioProject, ENA, DDBJ, GBIF, Open Tree of Life, and most genome-assembly pipelines all expose or accept it. `PMID` is reachable via ELink (db=taxonomy -> db=pubmed) for taxonomy-tagged literature.

Pair with NCBI Gene, UniProt, and Ensembl to fan out from a taxon to its genes and proteins; with NCBI SRA, BioSample, and BioProject to find sequencing experiments by organism; with GBIF for occurrence records by species (GBIF carries `taxonKey` separately but also stores the NCBI taxon ID where mapped). For non-NCBI taxonomic backbones (GBIF, Catalogue of Life, ITIS, OTT), expect partial overlap and unmapped taxa at the edges.

## Access notes

**Programmatic access:** E-utilities REST API at `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` with `db=taxonomy`. Core endpoints: `esearch.fcgi?db=taxonomy&term=...` (name to taxon ID), `esummary.fcgi?db=taxonomy&id=...` (compact lineage, rank, division, common name, genetic code), `efetch.fcgi?db=taxonomy&id=...&rettype=xml` (full record with synonyms and lineage path), `elink.fcgi?dbfrom=taxonomy&db=...` (jump to nuccore, protein, gene, pubmed, assembly, biosample, sra). Anonymous: 3 req/sec. Register a free NCBI account and pass `&api_key=${NCBI_API_KEY}` for 10 req/sec; higher limits available on request. Always include `&tool=` and `&email=`. Schedule large jobs for weekends or 9pm-5am US Eastern.

The newer NCBI Datasets API at `https://api.ncbi.nlm.nih.gov/datasets/v2/` exposes structured taxonomy endpoints (organism name resolution, taxonomic tree download) and is generally cleaner than E-utilities for modern integrations, though E-utilities remains canonical for joins.

**Bulk:** `https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/` refreshed daily. Core archives: `taxdump.tar.gz` (~71 MB, classic dump format with `names.dmp`, `nodes.dmp`, `merged.dmp`, `delnodes.dmp`, `division.dmp`, `gencode.dmp`), `new_taxdump/` (newer richer format with rank columns and host metadata), `taxcat.tar.gz` (taxonomic categories for high-level filtering), `accession2taxid/` (mapping from any GenBank accession to its taxon ID, large files). For any pipeline that joins millions of sequences or accessions to organisms, load the dump locally and skip the API entirely.

**Identifier stability:** taxon IDs are persistent; when a taxon is merged or deprecated, the old ID stays resolvable and points at the surviving node via `merged.dmp`. Always resolve through the merge map before treating a taxon ID as missing.

**License:** US government work, public domain in the US under 17 USC 105. NLM requests attribution ("Source: National Library of Medicine") but does not require it for redistribution.

## MCP / connector notes

Augmented-Nature/NCBI-Datasets-MCP-Server (community, JavaScript) exposes dedicated `search_taxonomy`, `get_taxonomy_info`, and `get_organism_info` tools and is the most direct fit. noahzeidenberg/ncbi-mcp and vitorpavinato/ncbi-mcp-server (Python, E-utilities wrappers) can hit `db=taxonomy` through generic esearch/esummary/efetch calls but lack taxonomy-specific helpers; expect to handle synonym resolution, rank filtering, and lineage walking in the caller.

A purpose-built Taxonomy MCP would expose `resolve_organism(name, fuzzy=true)`, `get_taxon(taxid)`, `get_lineage(taxid)`, `get_children(taxid, rank=null)`, `get_descendants(taxid)`, `accession_to_taxid(accession)`, `merged_id_lookup(old_taxid)`. The connector must handle synonym and misspelling resolution (NCBI names include authorities, common names, equivalents, includes, and acronyms), the merged/deleted ID map, and rank-filtered subtree traversal without round-tripping the full taxdump per call. For high-volume pipelines it should route to a locally cached taxdump rather than E-utilities.

## Review notes

None.
