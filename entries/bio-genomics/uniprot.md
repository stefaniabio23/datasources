---
id: uniprot
name: UniProt
domain: bio-genomics
entry_kind: registry
description: Comprehensive, freely accessible protein sequence and functional annotation resource maintained by the UniProt Consortium (EMBL-EBI, SIB, PIR), with REST API, FTP bulk downloads, and rich cross-references to genomic, structural, and clinical databases.
homepage_url: https://www.uniprot.org/
docs_url: https://www.uniprot.org/help/api
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "soft; large queries should paginate or use the streaming endpoint. EBI Proteins API caps at 200 req/sec per user."
bulk_available: true
frequency: "8-week release cycle"
lag: "weeks-to-months for newly published proteins to enter Swiss-Prot manual curation; TrEMBL ingests computationally within a release cycle"
geography: [global]
join_keys:
  - UNIPROT_ACCESSION
  - GENE_SYMBOL
  - ENSEMBL_ID
  - PMID
  - DOI
  - CHEMBL_ID
primary_keys:
  - UNIPROT_ACCESSION
  - UNIPROTKB_ID
  - UNIPARC_UPI
  - UNIREF_ID
join_key_fields:
  - join_key: UNIPROT_ACCESSION
    fields: [primaryAccession, secondaryAccessions]
  - join_key: GENE_SYMBOL
    fields: [genes.geneName.value, genes.synonyms.value]
  - join_key: ENSEMBL_ID
    fields: ["uniProtKBCrossReferences[database=Ensembl].id"]
  - join_key: PMID
    fields: [references.citation.id, "references.citation.citationCrossReferences[database=PubMed].id"]
  - join_key: DOI
    fields: ["references.citation.citationCrossReferences[database=DOI].id"]
  - join_key: CHEMBL_ID
    fields: ["uniProtKBCrossReferences[database=ChEMBL].id"]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/Augmented-Nature/Augmented-Nature-UniProt-MCP-Server
  - github.com/TakumiY235/uniprot-mcp-server
  - github.com/smaniches/uniprot-mcp
  - github.com/cyanheads/protein-mcp-server
  - github.com/pipeworx-io/mcp-uniprot
  - github.com/josefdc/Uniprot-MCP
mcp_notes: >
  Several overlapping community MCPs, none official. Most wrap a subset of search/lookup
  endpoints. A consolidated connector should expose search_proteins, get_protein,
  get_sequence_fasta, get_features, get_cross_references, resolve_gene_to_protein,
  with response trimming for verbose comment/feature trees and routing of large pulls
  to the streaming endpoint or FTP snapshot.
agent_use_cases:
  - protein lookup by accession or gene symbol
  - sequence retrieval (FASTA)
  - functional annotation and domain features
  - cross-reference resolution to genomic and structural databases
  - proteome-wide queries by organism
access_test:
  command: "curl -sf 'https://rest.uniprot.org/uniprotkb/P12345.json'"
  expected_status: 200
  expected_fields: [primaryAccession, uniProtkbId, organism, proteinDescription, sequence, uniProtKBCrossReferences]
last_verified: 2026-06-08
build_priority: high
---

# UniProt

## Why this source matters

The canonical open protein knowledgebase, run by the UniProt Consortium (EMBL-EBI in Hinxton, SIB in Geneva, PIR at Georgetown), formally federated in 2002 with funding from NIH, NHGRI, the European Commission, and the Swiss Federal Government. UniProtKB has two sections: Swiss-Prot (manually curated, ~570K entries) and TrEMBL (computationally annotated, ~250M+ entries). Any agent answering "what does this protein do, what's its sequence, what variants are known, what genes encode it, what structures exist" should hit UniProt first. Secondary relevance to `clinical-biotech` (drug target annotation, disease associations) and `academic` (literature cross-references via PMID/DOI).

## Agent use cases

- protein lookup by accession or gene symbol
- sequence retrieval (FASTA)
- functional annotation and domain features
- cross-reference resolution to genomic and structural databases
- proteome-wide queries by organism

## Join strategy

UniProt is the issuing authority for `UNIPROT_ACCESSION` (e.g. `P12345`, `Q9Y6K1`). Every entry exposes `uniProtKBCrossReferences` linking out to `ENSEMBL_ID`, `GENE_SYMBOL` (HGNC), `CHEMBL_ID`, plus literature `PMID` and `DOI` references. Other cross-refs present in entries but outside the current canonical registry include RefSeq, PDB, InterPro, Pfam, KEGG, Reactome, OMIM, GO, taxonomy IDs (NCBI Taxon), and DrugBank.

UniProt-internal IDs (`uniProtkbId` entry names like `AATM_RABIT`, `UniRef` cluster IDs, `UniParc` UPI identifiers) sit outside the canonical registry; use them for direct UniProt lookups, not cross-source joins.

Recommended pivot pattern: resolve any protein-bearing identifier to `UNIPROT_ACCESSION` first, then fan out to Ensembl for genomic context, ChEMBL for bioactivity, ClinVar for variant pathogenicity, AlphaFold or PDB for structure.

## Access notes

**Low-volume queries:** REST at `https://rest.uniprot.org`. No auth. First endpoint to try is `/uniprotkb/{accession}.json` for single-entry fetch, or `/uniprotkb/search?query=...&format=json` for search. Supported formats include JSON, XML, FASTA, GFF, TSV, and the legacy flat-file format via `?format=txt`.

**Large analyses:** FTP at `https://ftp.uniprot.org/pub/databases/uniprot/current_release/` ships Swiss-Prot and TrEMBL in FASTA, XML, and flat-file formats per 8-week release. UniRef (clustered at 100/90/50% identity) and UniParc snapshots live alongside. The streaming endpoint (`/stream?...`) returns full result sets without pagination for medium pulls.

The companion EBI Proteins API at `https://www.ebi.ac.uk/proteins/api` adds variation, proteomics, and large-scale-study integrations (1000 Genomes, ExAC, ClinVar, TCGA, COSMIC, gnomAD) on top of UniProtKB and caps at 200 req/sec/user.

Known gotchas:

- TrEMBL is huge and noisy; for most agent use cases filter to Swiss-Prot (`reviewed:true`) unless TrEMBL coverage is specifically needed.
- The accession pattern `[A-NR-Z][0-9][A-Z0-9]{3}[0-9]` covers most accessions but a longer 10-character form also exists.
- Cross-reference lists can be very long for well-studied proteins (hundreds of PDB/PMID entries); trim before passing to an LLM.
- Releases are versioned; reproducible analyses should pin to a release number from the FTP `release-YYYY_NN` folders.

## MCP / connector notes

Multiple community MCPs exist (`Augmented-Nature/Augmented-Nature-UniProt-MCP-Server`, `TakumiY235/uniprot-mcp-server`, `smaniches/uniprot-mcp`, `cyanheads/protein-mcp-server`, `pipeworx-io/mcp-uniprot`, `josefdc/Uniprot-MCP`); none official from the consortium. Quality and surface coverage vary. A consolidated connector should expose `search_proteins`, `get_protein`, `get_sequence_fasta`, `get_features`, `get_cross_references`, `resolve_gene_to_protein`, with response trimming for verbose comment/feature trees, organism disambiguation, and bulk-vs-API routing (push proteome-wide pulls to the streaming endpoint or FTP snapshot).

## Review notes

Potential new join keys for review that UniProt cross-references natively and would be useful across bio-genomics and clinical-biotech entries:

- `PDB_ID` — RCSB Protein Data Bank structure identifier (e.g. `1A2K`); pattern `^[0-9][A-Z0-9]{3}$`. Used by PDB, AlphaFold, UniProt, ChEMBL.
- `REFSEQ_ID` — NCBI RefSeq accession (e.g. `NP_000537`, `NM_007294`); pattern varies by molecule type. Used by NCBI, UniProt, Ensembl.
- `INTERPRO_ID` — InterPro protein family/domain identifier (e.g. `IPR000001`); pattern `^IPR[0-9]{6}$`. Used by InterPro, UniProt, Pfam.
- `NCBI_TAXON_ID` — NCBI Taxonomy identifier (e.g. `9606` for human); pattern `^[0-9]+$`. Used by virtually every bio-genomics source.
- `GO_TERM` — Gene Ontology identifier (e.g. `GO:0005515`); pattern `^GO:[0-9]{7}$`. Used by GO, UniProt, Ensembl, MGI.

Stephanie reviews and decides whether to PR these into `schema/join-keys.yaml`.
