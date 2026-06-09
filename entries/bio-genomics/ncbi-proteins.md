---
id: ncbi-proteins
name: NCBI Protein
domain: bio-genomics
entry_kind: registry
description: NIH-maintained protein sequence database aggregating records from RefSeq, GenBank/EMBL/DDBJ translated CDS, SwissProt, PIR, PRF, and PDB into one Entrez-queryable surface.
homepage_url: https://www.ncbi.nlm.nih.gov/protein/
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
lag: "hours-to-days for new RefSeq protein annotations; matches the underlying source release cadence for SwissProt and PDB feeds"
geography: [global]
join_keys:
  - UNIPROT_ACCESSION
  - PDB_ID
  - PMID
  - NCBI_TAXON_ID
primary_keys:
  - NCBI_PROTEIN_GI
  - NCBI_PROTEIN_ACCESSION
join_key_fields:
  - join_key: UNIPROT_ACCESSION
    fields: [GBSeq_other-seqids, GBSeq_xrefs.GBXref_id]
  - join_key: PDB_ID
    fields: [GBSeq_other-seqids, GBSeq_xrefs.GBXref_id]
  - join_key: PMID
    fields: [GBSeq_references.GBReference_pubmed, linksets.linksetdbs.links]
  - join_key: NCBI_TAXON_ID
    fields: [result.<uid>.taxid, GBSeq_feature-table.GBFeature_quals.GBQualifier_value]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/Augmented-Nature/NCBI-Datasets-MCP-Server
  - github.com/vitorpavinato/ncbi-mcp-server
  - github.com/noahzeidenberg/ncbi-mcp
  - github.com/cyanheads/protein-mcp-server
mcp_notes: >
  No protein-specific official MCP. Community NCBI E-utilities MCPs cover the protein db via
  generic esearch/efetch/esummary calls. A purpose-built connector should wrap
  search_protein(term, organism), get_protein(accession_or_gi, format=fasta|gp|xml),
  get_protein_features, protein_to_pubmed, protein_to_gene, protein_to_structure, and
  resolve cross-references to UniProt and PDB without forcing the caller to parse GBSeqXML.
agent_use_cases:
  - protein sequence retrieval by accession or GI
  - GenPept feature annotation lookup
  - protein-to-publication mapping
  - cross-reference resolution to UniProt and PDB
  - taxonomy-scoped proteome retrieval
access_test:
  command: "curl -sf 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=protein&id=15718680&retmode=json'"
  expected_status: 200
  expected_fields: [header, result]
last_verified: 2026-06-09
build_priority: medium
---

# NCBI Protein

## Why this source matters

NCBI's protein archive is the consolidated landing point for protein sequences across the major contributing repositories: RefSeq (NCBI's own curated reference set), translated coding regions from GenBank/EMBL/DDBJ, SwissProt and TrEMBL feeds from UniProt, PIR, PRF, and protein chains lifted from PDB structures. Run by the National Library of Medicine at NIH, the database is exposed through Entrez search, E-utilities, and the newer NCBI Datasets toolchain. Agents working on annotation pipelines, comparative genomics, or any task that needs a sequence plus a GenPept feature table reach NCBI Protein when they want a single endpoint that covers RefSeq, UniProt-derived, and PDB-derived records without orchestrating three separate APIs. Secondary relevance to `academic` (PubMed cross-references) and `clinical-biotech` (target sequence retrieval for drug discovery work).

## Agent use cases

- protein sequence retrieval by accession or GI
- GenPept feature annotation lookup
- protein-to-publication mapping
- cross-reference resolution to UniProt and PDB
- taxonomy-scoped proteome retrieval

## Join strategy

NCBI Protein exposes `UNIPROT_ACCESSION` and `PDB_ID` in the `GBSeq_other-seqids` block and the `GBSeq_xrefs` cross-reference list (records sourced from or mirrored to SwissProt and PDB carry these directly), `PMID` via the citation block on each record and via ELink to PubMed, and `NCBI_TAXON_ID` on every record via the `taxid` summary field and the `/db_xref="taxon:<id>"` qualifier on the source feature.

NCBI's own identifiers are the integer GI number (`gi` field, e.g. `15718680`) and the accession.version (e.g. `NP_005537.3` for RefSeq protein, `AAA12345.1` for GenBank-derived, `1TUP_A` for PDB-derived chains). The accession.version is now the canonical NCBI ID; GI numbers remain supported for backward compatibility. Both are source-internal and sit outside the canonical join-key registry. See Review notes for proposed additions.

Pair with UniProt for richer functional annotation, PDB for structure, NCBI Gene (via ELink `protein<->gene`) for gene-level context, and Ensembl for transcript-to-protein resolution in a genomic frame.

## Access notes

**Programmatic access:** E-utilities REST at `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` with `db=protein`. First endpoints to hit are `esummary.fcgi?db=protein&id=<gi-or-accession>&retmode=json` for lightweight metadata, `efetch.fcgi?db=protein&id=<id>&rettype=fasta&retmode=text` for sequence, and `efetch.fcgi?db=protein&id=<id>&rettype=gp&retmode=text` for the GenPept flat file. `rettype=gp&retmode=xml` returns GBSeqXML with the full feature table and cross-reference list. Anonymous: 3 req/sec. Register a free NCBI account and pass `&api_key=${NCBI_API_KEY}` for 10 req/sec; higher limits available on request. Always include `&tool=` and `&email=` to avoid IP blocks. Large jobs should run weekends or 9pm-5am US Eastern.

**Bulk:** `ftp.ncbi.nlm.nih.gov/refseq/release/` ships RefSeq protein in `.faa.gz` (FASTA) and `.gpff.gz` (GenPept flat file) split by division (vertebrate_mammalian, bacteria, viral, etc.), refreshed daily for incrementals and on the RefSeq release cycle for full snapshots. The newer `https://ftp.ncbi.nlm.nih.gov/genomes/all/` tree provides per-assembly protein FASTAs alongside genome assemblies. For any analysis over more than a few thousand proteins, prefer bulk over E-utilities pagination.

**License:** US government work, public domain in the US under 17 USC 105. NLM requests attribution but does not require it. Third-party records aggregated from SwissProt (CC-BY-4.0) and PDB (CC0) carry the contributing source's licence; verify per-record provenance via `sourcedb` and the `GBSeq_other-seqids` block before redistributing.

## MCP / connector notes

No NCBI Protein-specific MCP. Generic NCBI E-utilities community MCPs cover the protein db via parameterised esearch/efetch/esummary calls: `Augmented-Nature/NCBI-Datasets-MCP-Server` (wraps the newer NCBI Datasets API including protein endpoints), `vitorpavinato/ncbi-mcp-server` (Python, E-utilities), `noahzeidenberg/ncbi-mcp` (broader NCBI adapter), `cyanheads/protein-mcp-server` (multi-source protein server that includes NCBI alongside UniProt and PDB). Quality and feature-table parsing depth vary.

A purpose-built connector should expose `search_protein(term, organism)`, `get_protein(accession_or_gi, format=fasta|gp|xml)`, `get_protein_features(accession)`, `protein_to_pubmed(id)`, `protein_to_gene(id)`, `protein_to_structure(id)`. The MCP must abstract over GBSeqXML feature-table parsing (verbose nested qualifier structure), handle the `WebEnv`/`query_key` history server for batches over a few hundred IDs, route large pulls to FTP snapshots, and disambiguate between RefSeq (`NP_`, `XP_`, `WP_`, `YP_`), GenBank-derived (`AAA-AZZ`, 3-letter + digits), SwissProt-imported, and PDB-chain accessions.

## Review notes

Potential new join keys for review:

- `NCBI_PROTEIN_GI`
  Entity type: protein
  Pattern: `^[0-9]+$`
  Other datasets that would use it: NCBI databases (Nuccore, Gene via gene2refseq, BioProject), UniProt (cross-references include NCBI GI), older bioinformatics pipelines. Stable but deprecated in favour of accession.version; still appears widely in legacy data.

- `NCBI_PROTEIN_ACCESSION`
  Entity type: protein
  Pattern: covers RefSeq (`^[NXWY]P_[0-9]+(\.[0-9]+)?$`), GenBank-derived (`^[A-Z]{3}[0-9]{5,7}(\.[0-9]+)?$`), and PDB-derived (`^[0-9][A-Z0-9]{3}_[A-Z]$`) forms
  Other datasets that would use it: NCBI Gene, UniProt (RefSeq cross-references), Ensembl (Xref), ClinVar (HGVS protein-level changes reference RefSeq protein accessions), variant calling and annotation pipelines. More universal than GI for cross-database joins; arguably worth its own canonical entry rather than overloading the existing `UNIPROT_ACCESSION` registry slot.

- `REFSEQ_ID` (already flagged in `uniprot.md` review notes)
  Same proposal applies here; NCBI Protein is the issuing authority for the `NP_`/`XP_`/`WP_`/`YP_` protein subset of RefSeq.

Stephanie reviews and decides whether to PR these into `schema/join-keys.yaml`.
