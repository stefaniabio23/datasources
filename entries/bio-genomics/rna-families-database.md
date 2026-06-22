---
id: rna-families-database
name: Rfam
domain: bio-genomics
entry_kind: knowledge-graph
description: EMBL-EBI database of RNA families, each represented by a curated seed alignment, consensus secondary structure, and covariance model used for genome annotation.
homepage_url: https://rfam.org/
docs_url: https://docs.rfam.org/
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: CC0
rate_limit: "unpublished; polite use expected (push heavy work to FTP or the public MySQL mirror)"
bulk_available: true
frequency: "annual or semi-annual major releases"
lag: "months between sequence-database freezes and the next Rfam release"
geography: [global]
join_keys:
  - PDB_ID
  - MIRBASE_ID
  - NCBI_TAXON_ID
  - GO_ID
  - PMID
primary_keys:
  - RFAM_ACCESSION
  - RFAM_FAMILY_ID
  - RFAM_CLAN_ACCESSION
join_key_fields:
  - join_key: PDB_ID
    fields: [pdb_id, structures.pdb_id]
  - join_key: MIRBASE_ID
    fields: [database_link.db_id]
  - join_key: NCBI_TAXON_ID
    fields: [rfamseq.ncbi_id, taxonomy.ncbi_id]
  - join_key: GO_ID
    fields: [database_link.db_id]
  - join_key: PMID
    fields: [curation.seed_source, curation.structure_source, literature_reference.pmid]
mcp_status: mcp-needed-low-value
mcp_maturity: none
agent_use_cases:
  - non-coding RNA family lookup
  - genome annotation with covariance models
  - sequence search for structural RNAs
  - cross-reference RNA structures to PDB and miRBase
  - phylogenetic distribution of RNA families
access_test:
  command: "curl -sf 'https://rfam.org/family/RF00177?content-type=application/json'"
  expected_status: 200
  expected_fields: [rfam.acc, rfam.id, rfam.description, rfam.curation, rfam.release]
last_verified: 2026-06-09
build_priority: low
---

# Rfam

## Why this source matters

Curated collection of RNA families covering non-coding RNA genes (tRNA, rRNA, snoRNA, microRNA, lncRNA), cis-regulatory elements (riboswitches, IRES, frameshift signals), and self-splicing introns. Run by EMBL-EBI as part of ELIXIR, funded by BBSRC and Wellcome. Release 15.1 (January 2026) holds 4,227 families, each with a hand-curated seed alignment, consensus secondary structure, and a covariance model (Infernal CM) used to scan genomes for new family members. Rfam is the canonical reference for structural RNA annotation in the same way Pfam is for protein domains. Any agent answering "what RNA is encoded at these coordinates", "what families does this sequence belong to", or "what's the conserved secondary structure of this ncRNA" should hit Rfam.

## Agent use cases

- non-coding RNA family lookup
- genome annotation with covariance models
- sequence search for structural RNAs
- cross-reference RNA structures to PDB and miRBase
- phylogenetic distribution of RNA families

## Join strategy

Rfam mints its own stable identifiers: family accessions of the form `RF[0-9]{5}` (e.g. `RF00177` for bacterial SSU rRNA), short family IDs (`SSU_rRNA_bacteria`), and clan accessions (`CL[0-9]{5}`). These are source-internal primary keys.

For cross-source joining, Rfam exposes `PDB_ID` (3D-structure mappings via the `/family/{id}/structures` endpoint and the `pdb_full_region` MySQL table), `MIRBASE_ID` (microRNA families cross-referenced through the `database_link` table), `NCBI_TAXON_ID` (every sequence in `rfamseq` carries the NCBI taxon ID of its source organism), `GO_ID` (functional annotation per family via `database_link`), and `PMID` (curation provenance and structure source). INSDC nucleotide accessions appear in `rfamseq.rfamseq_acc` but the canonical registry has no ENA/INSDC key yet, see Review notes.

Pair with miRBase for mature microRNA sequences, PDB for 3D RNA structures, Ensembl or NCBI for genome coordinates of annotated families, and the NCBI Taxonomy entry for taxon-scoped queries. The covariance models themselves pair with Infernal (`cmsearch`) for de novo annotation of new genomes.

## Access notes

**Single-family lookups:** REST at `https://rfam.org/family/{ID_or_accession}` with `?content-type=application/json` or an `Accept: application/json` header. Stable, no auth, returns curation metadata, gathering/trusted/noise thresholds, release info, and clan membership. Sub-resources include `/cm` (covariance model), `/alignment/{stockholm|pfam|fasta|fastau}`, `/structures` (PDB mappings), `/tree/`, `/regions` (may 403 if too large).

**Sequence search:** Two-step async at `https://batch.rfam.org`. `POST /submit-job` with a FASTA payload returns a job ID; `GET /result/{jobId}` polls (202 while running, 200 with JSON/XML hits when done, 410 after the one-week retention window). Service occasionally returns 503 under load.

**Bulk:** FTP at `https://ftp.ebi.ac.uk/pub/databases/Rfam/CURRENT/` ships every release as covariance models, seed alignments (Stockholm), full alignments, FASTA sequences, phylogenetic trees, and full MySQL dumps. Prefer FTP for any analysis spanning more than a handful of families.

**Public MySQL:** read-only mirror at `mysql-rfam-public.ebi.ac.uk:4497`, user `rfamro`, no password, database `Rfam`. Core tables: `family`, `rfamseq`, `full_region`, `clan`, `clan_membership`, `taxonomy`, `database_link`, `pdb_full_region`. Best path for cross-family aggregate queries (e.g. "all snoRNA families annotated in human").

**Rate limits:** not publicly documented. Behave politely on the REST API; push heavy work to FTP or MySQL.

**License:** all Rfam data is CC0 (public domain dedication). No attribution required, though citing the latest Rfam paper (Ontiveros-Palacios et al., NAR 2024) is conventional in publications.

## MCP / connector notes

No MCP server exists for Rfam as of June 2026 (GitHub search returns zero hits). Demand is narrower than Ensembl or UniProt, so this sits at `mcp-needed-low-value`.

Suggested connector surface if built: `get_family(id_or_acc)`, `list_families(filter)`, `get_secondary_structure(id, type)` returning the SVG or CT, `get_covariance_model(id)`, `get_pdb_mappings(id)`, `search_sequence(fasta)` abstracting the two-step batch.rfam.org submit/poll flow, `resolve_external_id(MIRBASE|PDB|GO -> RF accession)`. The covariance-model files are bulky binary-ish text; the MCP should expose a download URL rather than streaming them inline. Sequence search needs explicit job-state handling (202 vs 410 vs 503) and probably a synchronous wrapper with a configurable timeout.

## Review notes

Potential new join key for review:

- `INSDC_ACCESSION` (ENA/GenBank/DDBJ nucleotide accession; appears across Rfam `rfamseq.rfamseq_acc`, NCBI nucleotide, ENA, Ensembl, BOLD, and many other bio-genomics sources)
  Entity type: nucleotide_sequence
  Pattern: roughly `^[A-Z]{1,6}[0-9]{5,8}(\.[0-9]+)?$` (covers GenBank-style, ENA WGS, RefSeq-style with prefix)
  Other datasets that would use it: ENA, NCBI Nucleotide, Ensembl, miRBase, GBIF (via barcode references)

Other items:

- Rate-limit guidance is not published; marked `rate_limit: unknown`.
- Frequency field is approximate: Rfam major releases land annually or semi-annually rather than on a fixed cadence. 15.1 dated 2026-01-16.
