---
id: ncbi-gene
name: NCBI Gene
domain: bio-genomics
entry_kind: registry
description: NIH-maintained reference database of gene-specific information across all sequenced species, with nomenclature, sequences, maps, pathways, and cross-references.
homepage_url: https://www.ncbi.nlm.nih.gov/gene
docs_url: https://www.ncbi.nlm.nih.gov/books/NBK25501/
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
lag: "hours-to-days for new RefSeq annotations; weeks for new species curation"
geography: [global]
join_keys:
  - GENE_SYMBOL
  - ENSEMBL_ID
  - PMID
  - MESH_TERM
primary_keys:
  - NCBI_GENE_ID
join_key_fields:
  - join_key: GENE_SYMBOL
    fields: [result.<uid>.nomenclaturesymbol, result.<uid>.name]
  - join_key: ENSEMBL_ID
    fields: [gene2ensembl.Ensembl_gene_identifier, gene2ensembl.Ensembl_rna_identifier, gene2ensembl.Ensembl_protein_identifier]
  - join_key: PMID
    fields: [linksets.linksetdbs.links]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/Augmented-Nature/NCBI-Datasets-MCP-Server
  - github.com/vitorpavinato/ncbi-mcp-server
  - github.com/noahzeidenberg/ncbi-mcp
  - github.com/mohammadnajeeb/ncbi_gene_mcp_client
mcp_notes: >
  Multiple community MCPs wrap E-utilities; none official. Common surface: esearch(db=gene),
  esummary(db=gene), efetch(db=gene), elink(gene<->pubmed/protein/nuccore). MCPs vary in
  whether they normalise the noisy E-utilities response shapes or pass raw XML/JSON.
agent_use_cases:
  - gene symbol lookup
  - gene-to-publication mapping
  - cross-species ortholog discovery
  - gene-to-pathway annotation
  - RefSeq/Ensembl ID cross-referencing
access_test:
  command: "curl -sf 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=7157&retmode=json'"
  expected_status: 200
  expected_fields: [header, result]
last_verified: 2026-06-08
build_priority: medium
---

# NCBI Gene

## Why this source matters

Authoritative reference index for gene-specific information across every sequenced species curated by NCBI, run by the National Library of Medicine. Records integrate official nomenclature (HGNC for human), RefSeq sequences, chromosomal maps, GO annotations, OMIM links, pathway memberships, and PubMed citations into one queryable surface. For agents working in functional genomics, variant interpretation, or biomedical literature mining, NCBI Gene is the canonical bridge between a gene symbol and everything else NCBI knows about it. Secondary relevance to `academic` (PubMed cross-links) and `clinical-biotech` (OMIM and ClinVar associations).

## Agent use cases

- gene symbol lookup
- gene-to-publication mapping
- cross-species ortholog discovery
- gene-to-pathway annotation
- RefSeq/Ensembl ID cross-referencing

## Join strategy

NCBI Gene exposes `GENE_SYMBOL` (HGNC for human, MGI for mouse, etc.), `ENSEMBL_ID` via the `gene2ensembl` bulk file and ELink, `PMID` via `gene2pubmed` and ELink to PubMed, and `MESH_TERM` via indexed concept tagging.

NCBI's own Entrez Gene ID (the integer `id` field, e.g. `7157` for TP53) is the source-internal primary key and the most stable identifier across NCBI databases. It is not in the canonical join-key registry. See Review notes for the proposed addition.

Pair with Ensembl/Ensembl REST for transcript-level detail, UniProt for protein-centric joins (via `gene2refseq` -> RefSeq protein -> UniProt mapping), and ClinVar for variant-level clinical significance. For human GWAS work, the gene symbol joins out to GWAS Catalog and OpenTargets.

## Access notes

**Programmatic access:** E-utilities REST API at `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` with `db=gene`. Anonymous: 3 req/sec. Register a free NCBI account and pass `&api_key=${NCBI_API_KEY}` for 10 req/sec; higher limits available on request. Always include `&tool=` and `&email=` to avoid IP blocks. Schedule large jobs for weekends or 9pm-5am US Eastern.

**Bulk:** `ftp.ncbi.nlm.nih.gov/gene/DATA/` refreshed daily. Core files: `gene_info.gz` (1.4 GB), `gene2pubmed.gz` (254 MB), `gene2refseq.gz` (2.1 GB), `gene2go.gz` (1.2 GB), `gene2accession.gz` (4.2 GB), `gene2ensembl.gz` (276 MB), `gene_history.gz` (retired/replaced IDs). For any join across millions of genes, prefer bulk over E-utilities pagination.

**License:** US government work, public domain in the US under 17 USC 105. NLM requests attribution ("Source: National Library of Medicine") but does not require it for redistribution. Some linked third-party content (e.g. embedded OMIM excerpts) may carry separate licences; check the per-resource policy if redistributing.

## MCP / connector notes

Multiple community MCPs exist; none official. Notable: `Augmented-Nature/NCBI-Datasets-MCP-Server` (wraps the newer NCBI Datasets API, JavaScript), `vitorpavinato/ncbi-mcp-server` (Python, E-utilities-focused), `noahzeidenberg/ncbi-mcp` (Python, broader NCBI adapter), `mohammadnajeeb/ncbi_gene_mcp_client` (Gene-specific). Quality and coverage vary; expect to evaluate before adopting.

A purpose-built Gene MCP would expose `search_gene(term, organism)`, `get_gene(id_or_symbol)`, `gene_to_pubmed(id)`, `gene_to_ortholog(id, target_taxid)`, `gene_to_refseq(id)`. The connector must abstract over E-utilities' noisy multi-format response shapes (XML, JSON, text), handle the `WebEnv`/`query_key` history server for large batches, and route bulk-file lookups for queries over a few hundred genes.

## Review notes

Potential new join key for review: `NCBI_GENE_ID`
  Entity type: gene
  Pattern: `^[0-9]+$` (integer)
  Other datasets that would use it: NCBI databases (PubMed via gene2pubmed, Protein, Nuccore, ClinVar, dbSNP, OMIM), Ensembl (via Xref), UniProt (via cross-references), HGNC, OpenTargets, MyGene.info. Most gene-centric resources expose it; arguably more universal than `ENSEMBL_ID` for cross-database joins.
