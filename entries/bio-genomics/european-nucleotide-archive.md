---
id: european-nucleotide-archive
name: European Nucleotide Archive (ENA)
domain: bio-genomics
entry_kind: corpus
description: EMBL-EBI's open archive of nucleotide sequence and raw read data; the European INSDC node mirroring NCBI SRA and DDBJ.
homepage_url: https://www.ebi.ac.uk/ena/browser/
docs_url: https://ena-docs.readthedocs.io/en/latest/retrieval/programmatic-access.html
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: EMBL-EBI-Terms-of-Use
rate_limit: "50 req/sec; requests above the threshold return HTTP 429"
bulk_available: true
frequency: continuous
lag: "hours-to-days after submitter release; embargoed studies appear on the disclosed release date"
geography: [global]
join_keys:
  - NCBI_TAXON_ID
primary_keys:
  - ERR
  - ERX
  - ERS
  - ERP
  - SRR
  - SRX
  - SRS
  - SRP
  - DRR
  - DRX
  - DRS
  - DRP
  - PRJEB
  - PRJNA
  - PRJDB
  - SAMEA
  - SAMN
  - SAMD
join_key_fields:
  - join_key: NCBI_TAXON_ID
    fields: [tax_id]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No dedicated ENA MCP exists. The Portal API (search/filereport/results) and Browser API
  (xml/fasta/fastq) are clean and stable, but the load-bearing workflow (resolve a study or
  run to FASTQ download URLs at scale via /filereport) needs an opinionated surface that
  abstracts field selection, pagination, INSDC prefix-swap, and the FTP/Aspera handoff.
  Shares audience with ncbi-sra, ncbi-geo, and ensembl.
agent_use_cases:
  - resolve study or run accessions to FASTQ download URLs
  - bulk metadata search across reads and assemblies
  - cross-reference INSDC accessions with NCBI SRA and DDBJ
  - locate raw reads for an organism by NCBI taxon id
  - retrieve sequence records as XML or FASTA
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJEB1787&result=read_run&fields=run_accession,fastq_ftp&format=tsv&limit=2'"
  expected_status: 200
  expected_fields: [run_accession, fastq_ftp]
last_verified: 2026-06-22
build_priority: high
notes: "Access test executed 2026-06-22, returned 200 with run_accession + fastq_ftp columns and live FTP URLs (e.g. ERR1701760). Anonymous query worked; no key required."
---

# European Nucleotide Archive (ENA)

## Why this source matters

ENA is the European node of the International Nucleotide Sequence Database Collaboration (INSDC), run by EMBL-EBI as a Global Core Biodata Resource. INSDC means ENA, NCBI SRA, and DDBJ mirror the same underlying objects: a run submitted to any one partner is propagated to the other two and is retrievable under each centre's accession space. ENA's surface is the cleanest of the three for programmatic FASTQ retrieval at scale, the `/filereport` endpoint turns a single study or run accession into download URLs for every file underneath it. For any agent that needs to go from a publication, organism, or BioProject to raw reads or assembled sequence, ENA is the default European substrate and a drop-in mirror when NCBI SRA is rate-limited or down. Secondary relevance to `public-health` (pathogen surveillance submissions) and `academic` (every study links back to source publications).

## Agent use cases

- resolve study or run accessions to FASTQ download URLs
- bulk metadata search across reads and assemblies
- cross-reference INSDC accessions with NCBI SRA and DDBJ
- locate raw reads for an organism by NCBI taxon id
- retrieve sequence records as XML or FASTA

## Join strategy

ENA exposes one canonical registry join key in its records: `NCBI_TAXON_ID` (the `tax_id` field, shared verbatim with NCBI Taxonomy and used to filter reads by organism).

The load-bearing identifiers are INSDC accessions, intentionally outside the canonical registry. ENA's native data hierarchy is study > experiment > run with a sample attached: `ERP` (study), `ERX` (experiment), `ERR` (run), `ERS` (sample), plus the `PRJEB` BioProject and `SAMEA` BioSample prefixes. Because INSDC mirrors objects across the three partners, ENA also resolves the NCBI forms (`SRP`/`SRX`/`SRR`/`SRS`, `PRJNA`, `SAMN`) and the DDBJ forms (`DRP`/`DRX`/`DRR`/`DRS`, `PRJDB`, `SAMD`). The prefix swap is the key fact: `ERR`, `SRR`, and `DRR` for the same run are the same object, so an agent holding an `SRR` from NCBI SRA can query ENA directly without re-resolving. Use these accessions for direct lookups; map to NCBI SRA or DDBJ when a downstream tool wants a specific centre's space. Pair with Ensembl or RefSeq for genome context, and with GEO for processed expression matrices that often share the same BioProject.

Potential new join keys flagged in `## Review notes` (INSDC_RUN, INSDC_EXPERIMENT, INSDC_STUDY, BIOPROJECT, BIOSAMPLE), as ncbi-sra and ncbi-geo would also use them.

## Access notes

**Metadata search:** Portal API at `https://www.ebi.ac.uk/ena/portal/api/`. `/search` runs Advanced Search queries with field/result-type filters; `/filereport` is the workhorse, given an accession and `result=read_run` plus a `fields=` list (e.g. `run_accession,fastq_ftp,fastq_aspera,sample_accession`) it returns one row per file with download URLs; `/results` lists available result types and `/returnFields` lists queryable fields per result type. Default `format` is TSV; set `format=json` for structured output. No auth, no key. Rate limit is 50 req/sec, requests above it return HTTP 429.

**Record retrieval:** Browser API at `https://www.ebi.ac.uk/ena/browser/api/`. Append the format to the accession path: `/xml/{accession}`, `/fasta/{accession}`, `/fastq/{accession}`, `/text/{accession}`. Good for single-record pulls; use the Portal API for anything that touches more than one study.

**Reads in bulk:** `/filereport` returns `fastq_ftp` (FTP under `ftp.sra.ebi.ac.uk`) and `fastq_aspera` (Aspera, much faster for large transfers) columns. The `enaBrowserTools` CLI wraps accession-or-study bulk download over both protocols. Anonymous for public data; human controlled-access data follows a Data Access Committee mechanism.

## MCP / connector notes

No dedicated ENA MCP. High-value target: read-archive and sequence retrieval agents are a recurring audience (overlaps ncbi-sra, ncbi-geo, ensembl), and the FASTQ-resolution workflow is fiddly enough that raw API responses are a poor fit for context windows. Suggested surface: `search_records(query, result_type, organism)`, `get_filereport(accession, fields)` returning a trimmed run > file table, `resolve_to_fastq_urls(study_or_run)`, `get_sequence(accession, format)`, and `to_insdc_centre(accession, centre)` for the ERR/SRR/DRR prefix swap. The connector must abstract Portal-API field selection and pagination, default to Aspera URLs for large pulls, and translate freely between the three INSDC accession spaces.

## Review notes

Potential new join keys for review (all INSDC-shared; ncbi-sra and ncbi-geo would also use them, and ncbi-sra already flagged the SRA_RUN_ID / BIOPROJECT_ID / BIOSAMPLE_ID variants):

```
Potential new join key for review: INSDC_RUN
  Entity type: sequencing_run
  Pattern: ^(ERR|SRR|DRR)[0-9]+$
  Other datasets that would use it: ENA, NCBI SRA, DDBJ, GEO (via SRA-linked runs)

Potential new join key for review: INSDC_EXPERIMENT
  Entity type: sequencing_experiment
  Pattern: ^(ERX|SRX|DRX)[0-9]+$
  Other datasets that would use it: ENA, NCBI SRA, DDBJ

Potential new join key for review: INSDC_STUDY
  Entity type: study
  Pattern: ^(ERP|SRP|DRP)[0-9]+$
  Other datasets that would use it: ENA, NCBI SRA, DDBJ

Potential new join key for review: BIOPROJECT
  Entity type: study
  Pattern: ^(PRJEB|PRJNA|PRJDB)[0-9]+$
  Other datasets that would use it: ENA, NCBI SRA, DDBJ, GEO, NCBI BioProject

Potential new join key for review: BIOSAMPLE
  Entity type: biological_sample
  Pattern: ^SAM(N|EA|D)[0-9]+$
  Other datasets that would use it: ENA, NCBI SRA, DDBJ, GEO, NCBI BioSample
```

Note the naming overlap with ncbi-sra's existing flags: ncbi-sra proposed `SRA_RUN_ID`, `BIOPROJECT_ID`, `BIOSAMPLE_ID` for the same identifier families. These should be reconciled to one canonical name per family before any PR to `schema/join-keys.yaml`; `INSDC_RUN` / `BIOPROJECT` / `BIOSAMPLE` are the centre-neutral forms and read more accurately than the SRA-prefixed names.

License recorded as `EMBL-EBI-Terms-of-Use` (no SPDX code). Data is open and free with no EMBL-EBI-imposed access restriction; attribution is expected per good scientific practice and third-party / data-owner rights must be respected. Human controlled-access submissions follow a Data Access Committee mechanism. Flagging the license short-name for review, it does not yet appear in SCHEMA.md's known-cases list.
