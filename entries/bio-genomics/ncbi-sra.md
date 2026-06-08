---
id: ncbi-sra
name: NCBI SRA (Sequence Read Archive)
domain: bio-genomics
description: Largest public repository of high-throughput raw sequencing reads and alignment metadata, run by NCBI/NLM/NIH.
homepage_url: https://www.ncbi.nlm.nih.gov/sra
docs_url: https://www.ncbi.nlm.nih.gov/sra/docs/
type:
  - rest-api
  - bulk-download
  - database
auth_required: api-key-free
cost: free
license: US-Government-Public-Domain
rate_limit: "3 req/sec anon; 10 req/sec with NCBI API key (api_key param); higher on request"
bulk_available: true
frequency: continuous
lag: "hours-to-days after submitter release; embargoed studies appear on disclosed release date"
geography: [global]
join_keys:
  - PMID
  - PMCID
  - DOI
  - MESH_TERM
primary_keys:
  - SRA_RUN_ID
  - SRA_EXPERIMENT_ID
  - SRA_SAMPLE_ID
  - SRA_STUDY_ID
  - BIOPROJECT_ID
  - BIOSAMPLE_ID
join_key_fields:
  - join_key: PMID
    fields: [linksets.linksetdbs.links]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/CSI-Genomics-and-Data-Analytics-Core/ncbi-sra-mcp-server
  - github.com/musharna/data-aggregator-mcp
mcp_notes: >
  Two community MCPs exist; both early-stage and SRA-specific surfaces are thin. A
  production connector should wrap E-utilities (esearch/esummary/efetch against
  db=sra) plus the SRA Run Selector / cloud BigQuery + Athena tables, and abstract
  the SRA Toolkit (prefetch + fasterq-dump) for actual read retrieval.
agent_use_cases:
  - find sequencing runs for a study or organism
  - resolve publication to underlying raw reads
  - bulk metadata pulls for cohort assembly
  - cross-reference BioProject and BioSample
  - locate cloud-resident FASTQ/BAM for compute-near-data workflows
access_test:
  command: "curl -sf 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=SRR000001&retmode=json'"
  expected_status: 200
  expected_fields: [header, esearchresult]
last_verified: 2026-06-08
build_priority: medium
notes: "Access test executed 2026-06-08, returned 200 with expected fields. Anonymous query worked; api_key param recommended for sustained use."
---

# NCBI SRA (Sequence Read Archive)

## Why this source matters

SRA is the primary global archive for raw next-generation sequencing reads, run by the National Center for Biotechnology Information at NLM/NIH. Submissions cover every domain of life including human clinical cohorts (controlled-access via dbGaP), microbiome and environmental metagenomics, single-cell, and long-read platforms. It is mirrored on AWS and Google Cloud with BigQuery and Athena query layers over the metadata, which makes it the default substrate for any agent that needs to go from a publication or organism to the underlying reads. Secondary relevance to `public-health` for pathogen surveillance datasets (SARS-CoV-2, foodborne outbreaks, AMR).

## Agent use cases

- find sequencing runs for a study or organism
- resolve publication to underlying raw reads
- bulk metadata pulls for cohort assembly
- cross-reference BioProject and BioSample
- locate cloud-resident FASTQ/BAM for compute-near-data workflows

## Join strategy

SRA exposes few external canonical join keys in its own records. The reliable bridges are `PMID`, `PMCID`, and `DOI` via linked PubMed citations (use ELink across `db=sra` and `db=pubmed`), plus `MESH_TERM` indexing on associated publications.

The load-bearing identifiers are SRA-internal and intentionally outside the canonical registry: `SRR` (run), `SRX` (experiment), `SRS` (sample), `SRP` (study), plus the parent `PRJNA`/`PRJEB`/`PRJDB` BioProject accessions and `SAMN`/`SAMEA`/`SAMD` BioSample accessions. Use these for direct SRA, BioProject, and BioSample lookups; map to ENA's matching ERR/ERX/ERS/ERP space (INSDC mirror) when joining with European nucleotide resources. Pair with Ensembl or RefSeq for downstream genome context, and with GEO for processed expression matrices that often share the same BioProject.

## Access notes

**Programmatic metadata:** NCBI E-utilities at `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`. Hit `esearch.fcgi?db=sra` for queries, `esummary.fcgi?db=sra` for record summaries, `efetch.fcgi?db=sra&rettype=runinfo&retmode=csv` for the canonical run-info CSV. Add `&api_key=${NCBI_API_KEY}` to lift from 3 req/sec to 10 req/sec; request higher rates from NCBI for bulk pulls. Include `&tool=` and `&email=` for traceability and to recover from rate-limit blocks. Run heavy jobs nights and weekends per NCBI's stated policy.

**Bulk metadata:** Use the SRA Run Selector or query the public BigQuery dataset (`nih-sra-datasets.sra`) or AWS Athena tables for second-level filtering across the full metadata corpus, far faster than paginating E-utilities.

**Reads:** Actual FASTQ/BAM retrieval is via the SRA Toolkit (`prefetch` + `fasterq-dump`) or directly from the AWS/GCP buckets. Anonymous for public data; dbGaP controlled-access requires JWT or NGC file plus a current Toolkit build.

## MCP / connector notes

Two community MCPs are listed on GitHub (`ncbi-sra-mcp-server`, `data-aggregator-mcp`), both early-stage and neither comprehensively covers the SRA surface. A production connector should expose: `search_runs(query, organism, platform, layout)`, `get_run_metadata(SRR)`, `resolve_publication_to_runs(PMID|DOI)`, `list_bioproject_runs(PRJNA)`, and `get_cloud_uri(SRR, provider)`. It must abstract over E-utilities pagination, BigQuery/Athena for any query that touches the full metadata table, and the Toolkit for read access. Streaming large result sets and translating SRA-internal accessions to ENA mirror accessions are common ergonomic wins.

## Review notes

Potential new join keys for review (all SRA/INSDC-internal but reusable across SRA, ENA, DDBJ, BioProject, BioSample, GEO):

```
Potential new join key for review: SRA_RUN_ID
  Entity type: sequencing_run
  Pattern: ^(SRR|ERR|DRR)[0-9]+$
  Other datasets that would use it: ENA, DDBJ, GEO (via SRA-linked runs)

Potential new join key for review: BIOPROJECT_ID
  Entity type: study
  Pattern: ^(PRJNA|PRJEB|PRJDB)[0-9]+$
  Other datasets that would use it: ENA, DDBJ, GEO, NCBI BioProject

Potential new join key for review: BIOSAMPLE_ID
  Entity type: biological_sample
  Pattern: ^SAM(N|EA|D)[0-9]+$
  Other datasets that would use it: ENA, DDBJ, GEO, NCBI BioSample
```

License is "US Government Public Domain" by default for NCBI-generated metadata and the archive structure itself; individual submissions may carry submitter-specific terms or, for human data, dbGaP controlled-access restrictions. Recorded as `US-Government-Public-Domain` per the canonical short-name convention.
