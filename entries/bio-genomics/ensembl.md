---
id: ensembl
name: Ensembl
domain: bio-genomics
entry_kind: knowledge-graph
description: Open genome annotation project from EMBL-EBI covering 4,700+ genomes with REST API, BioMart, FTP downloads, and MySQL access.
homepage_url: https://www.ensembl.org/
docs_url: https://rest.ensembl.org/
type:
  - rest-api
  - bulk-download
  - database
auth_required: none
cost: free
license: Apache-2.0
rate_limit: "15 req/sec per IP soft limit; server returns 429 with Retry-After when exceeded"
bulk_available: true
frequency: quarterly
lag: "weeks-to-months between assembly publication and inclusion in a release"
geography: [global]
join_keys:
  - ENSEMBL_ID
  - GENE_SYMBOL
  - UNIPROT_ACCESSION
primary_keys:
  - ENSEMBL_ID
  - ENSEMBL_GENE_ID
  - ENSEMBL_TRANSCRIPT_ID
  - ENSEMBL_PROTEIN_ID
  - ENSEMBL_EXON_ID
  - ENSEMBL_REGULATORY_ID
join_key_fields:
  - join_key: ENSEMBL_ID
    fields: [id, canonical_transcript, Parent, Transcript.id, Transcript.Parent, Transcript.Exon.id, Transcript.Translation.id, Transcript.Translation.Parent]
  - join_key: GENE_SYMBOL
    fields: [display_name, xrefs.display_id, xrefs.primary_id]
  - join_key: UNIPROT_ACCESSION
    fields: [xrefs.primary_id]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cyanheads/ensembl-mcp-server
  - github.com/effieklimi/ensembl-mcp-server
  - github.com/Augmented-Nature/Ensembl-MCP-Server
  - github.com/munch-group/ensembl-mcp
  - github.com/pipeworx-io/mcp-ensembl
mcp_notes: >
  Several overlapping community MCPs; none official. Most wrap a subset of REST endpoints
  (lookup, sequence, variation, comparative). A consolidated connector should expose
  lookup_by_id, lookup_by_symbol, get_sequence, get_variants, get_orthologs, with
  species disambiguation and response trimming for verbose Transcript/Exon trees.
agent_use_cases:
  - gene lookup by Ensembl ID or symbol
  - sequence retrieval
  - variant effect prediction
  - ortholog discovery
  - cross-species comparative genomics
access_test:
  command: "curl -sf -H 'Content-Type: application/json' 'https://rest.ensembl.org/lookup/id/ENSG00000157764?expand=1'"
  expected_status: 200
  expected_fields: [id, biotype, seq_region_name, Transcript]
last_verified: 2026-06-08
build_priority: medium
---

# Ensembl

## Why this source matters

Genome annotation project run by EMBL-EBI, covering 4,700+ genomes (4,100 animal, 470 plant, 100 fungal) plus pangenomes for human (565 haplotypes), barley, and pig. The canonical source for vertebrate gene models, sequence, variation, and comparative genomics. Any agent answering "what does this gene do, where is it on the genome, what variants exist, what's its ortholog in mouse" should hit Ensembl first. Stable, free, programmatically accessible via REST, BioMart, and MySQL.

## Agent use cases

- gene lookup by Ensembl ID or symbol
- sequence retrieval
- variant effect prediction
- ortholog discovery
- cross-species comparative genomics

## Join strategy

Ensembl is the issuing authority for `ENSEMBL_ID` (genes `ENSG`, transcripts `ENST`, proteins `ENSP`, regulatory `ENSR`). It also resolves HGNC `GENE_SYMBOL` via `/lookup/symbol/{species}/{symbol}` and cross-references `UNIPROT_ACCESSION` through `/xrefs/id/{ensembl_id}`.

For broader joins, the xrefs endpoint returns RefSeq, NCBI Entrez Gene, HGNC, MIM, ChEMBL, and many other identifiers per Ensembl ID, making it a useful pivot when a downstream source uses a different identifier vocabulary. Pair with UniProt for protein-level annotation, ClinVar for clinical variant interpretation, and Open Targets for target-disease evidence.

## Access notes

**Low-volume queries:** REST at `https://rest.ensembl.org` with `Content-Type: application/json`. No auth. First endpoint to try is `/lookup/id/{ensembl_id}?expand=1` or `/lookup/symbol/{species}/{symbol}`.

**Large analyses:** FTP at `https://ftp.ensembl.org/pub/release-N/` ships FASTA, GTF, GFF3, VCF, and full MySQL dumps per release. BioMart at `https://www.ensembl.org/biomart/martview` handles cross-database joins for tabular pulls. Public MySQL server at `ensembldb.ensembl.org` (port 3306, anonymous) for direct SQL.

Known gotchas:

- Rate limit is soft (~15 req/sec per IP); server returns 429 with `Retry-After` when exceeded. Honour it or get temporarily blocked.
- `expand=1` returns deeply nested Transcript/Exon/Translation trees; payload can be 100+ KB per gene.
- Release cadence is quarterly; assembly versions matter (`GRCh38.p14` vs older). Always pin the release when reproducing analyses.
- A new platform transition is in progress as of late 2025; some endpoints may move. Check `ensembl.info` blog for migration notices.
- Ensembl Genomes (plants, fungi, metazoa, protists, bacteria) lives at separate subdomains (`plants.ensembl.org`, etc.) with parallel REST APIs.

## MCP / connector notes

Multiple community MCPs exist (`cyanheads/ensembl-mcp-server`, `effieklimi/ensembl-mcp-server`, `Augmented-Nature/Ensembl-MCP-Server`, `munch-group/ensembl-mcp`, `pipeworx-io/mcp-ensembl`); none official from EMBL-EBI. Overlap is high and quality varies. A consolidated connector should expose `lookup_by_id`, `lookup_by_symbol`, `get_sequence`, `get_variants`, `get_orthologs`, with species disambiguation, response trimming for deeply nested Transcript trees, and bulk-vs-API routing for analyses spanning thousands of genes (push those to FTP or MySQL).

## Review notes

None.
