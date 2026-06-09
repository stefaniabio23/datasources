---
id: international-genome-sample-resource
name: IGSR (International Genome Sample Resource)
domain: bio-genomics
entry_kind: registry
description: EMBL-EBI hosted registry of open-consent human genome samples and population variant calls from the 1000 Genomes Project and successor collections (HGSVC, MAGE, ONT, Illumina Platinum).
homepage_url: https://www.internationalgenome.org/
docs_url: https://www.internationalgenome.org/faq/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: EMBL-EBI-Terms-of-Use
rate_limit: "FTP/HTTP downloads rate-limited; Globus and AWS recommended for large transfers. /api/beta JSON endpoints have no published limit."
bulk_available: true
frequency: continuous
lag: "weeks-to-months between data producer release and ingestion into a new IGSR data collection"
geography: [global]
join_keys:
  - DOI
  - PMID
primary_keys:
  - BIOSAMPLE_ID
  - IGSR_SAMPLE_NAME
  - IGSR_POPULATION_CODE
  - IGSR_SUPERPOPULATION_CODE
  - IGSR_DATA_COLLECTION_TITLE
join_key_fields: []
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/dnaerys/onekgpd-mcp
  - github.com/de-grave/onekgpd-mcp
mcp_notes: >
  Two community MCPs target the 1000 Genomes Project dataset (Java), neither
  branded as IGSR-wide. A production connector should expose sample lookup
  (Coriell NA/HG IDs), population lookup, data-collection enumeration, and FTP
  path resolution for VCF/BAM/CRAM files, plus a thin pass-through to the
  Ensembl variant browser for per-variant context.
agent_use_cases:
  - resolve a Coriell sample to its sequencing data files
  - enumerate samples in a population or superpopulation
  - locate phase 3 or 30x high-coverage VCFs for a region
  - cross-reference IGSR sample to BioSample and downstream archives
  - bulk-pull population allele frequencies for cohort comparison
access_test:
  command: "curl -sf 'https://www.internationalgenome.org/api/beta/sample/NA12878'"
  expected_status: 200
  expected_fields: [_source.name, _source.biosampleId, _source.populations, _source.dataCollections]
last_verified: 2026-06-09
build_priority: medium
notes: "Access test executed 2026-06-09, returned 200 with sample record for NA12878 including biosampleId SAME123392, CEU/EUR population, and 7+ data collections."
---

# IGSR (International Genome Sample Resource)

## Why this source matters

IGSR is the EMBL-EBI hosted registry that took over stewardship of the 1000 Genomes Project after its formal conclusion, and now bundles successor collections including the 1000 Genomes 30x high-coverage release, the Human Genome Structural Variation Consortium (HGSVC) phase 2, MAGE RNA-seq, Illumina Platinum pedigrees, and the 1KG Oxford Nanopore (Vienna) long-read set. All samples are open-consent: research participants explicitly agreed to fully public release of their sequencing data, which makes IGSR the default substrate for benchmarking variant callers, training population-genetics models, and any agent task that needs real human genomes without a data access committee. The Coriell sample IDs (NA12878 and friends) are the most-used reference samples in genomics tooling.

## Agent use cases

- resolve a Coriell sample to its sequencing data files
- enumerate samples in a population or superpopulation
- locate phase 3 or 30x high-coverage VCFs for a region
- cross-reference IGSR sample to BioSample and downstream archives
- bulk-pull population allele frequencies for cohort comparison

## Join strategy

IGSR mints its own sample names (Coriell-issued `NA*` and `HG*` identifiers, e.g. `NA12878`, `HG00096`), population codes (`CEU`, `YRI`, `CHB`, ...), and superpopulation codes (`AFR`, `EUR`, `EAS`, `SAS`, `AMR`). These are canonical inside the population-genetics ecosystem but are not in the join-key registry. The reliable canonical bridge is `BIOSAMPLE_ID`: every IGSR sample record carries an EBI BioSample accession at `_source.biosampleId` (e.g. `SAME123392` for NA12878), which joins cleanly into ENA, NCBI SRA, and DDBJ. `DOI` and `PMID` apply to the cohort-level papers (1000 Genomes phase 3, 30x release, HGSVC) rather than per-sample data.

Pair with NCBI SRA / ENA to retrieve raw reads, Ensembl for variant annotation on the same GRCh38 coordinates, GTEx for tissue expression context, and gnomAD for broader population frequencies. Coriell NA/HG IDs flagged for the registry below.

## Access notes

**Sample / population lookup:** Undocumented but stable JSON endpoints exist at `https://www.internationalgenome.org/api/beta/sample/{SAMPLE_NAME}` and `https://www.internationalgenome.org/api/beta/population/{POPULATION_CODE}`. Responses return an Elasticsearch `_source` envelope with `name`, `biosampleId`, `populations`, `sex`, `dataCollections`, `relatedSample`, and `synonyms`. No collection or list endpoint is exposed; agents must already know the sample or population code, or scrape the data portal UI to enumerate.

**Bulk data:** Primary FTP at `https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/`. Heavy users should switch to Globus (recommended by IGSR), Aspera, or the AWS Open Data mirror at `s3://1000genomes/` (registered at `registry.opendata.aws/1000-genomes`). NCBI and DDBJ also mirror. File formats are VCF (variants), BAM and CRAM (alignments), and FASTQ (raw reads). Variant calls are released against GRCh38 for all current collections; the legacy phase 3 release also has GRCh37 coordinates.

**License nuance:** IGSR operates under EMBL-EBI Terms of Use rather than a standard open-data license, recorded here as `EMBL-EBI-Terms-of-Use`. Individual data collections add their own data-reuse statements (e.g. HGSVC follows Fort Lauderdale principles, granting data producers first publication rights; 1000 Genomes phase 3 is unrestricted with citation). The collection's `dataReusePolicy` URL appears inline in each sample record. Cite the 2020 NAR paper (Fairley et al., 2020, DOI `10.1093/nar/gkz836`) when republishing.

## MCP / connector notes

Two community MCPs (`dnaerys/onekgpd-mcp`, `de-grave/onekgpd-mcp`) wrap the 1000 Genomes Project dataset in Java; neither covers the full IGSR surface (HGSVC, MAGE, Platinum, ONT collections) or the `/api/beta` JSON endpoints. A production connector should expose: `get_sample(sample_name)`, `get_population(code)`, `list_samples_in_population(code)`, `list_data_collections()`, `resolve_ftp_paths(sample_name, collection, data_type)`, and `get_variants(region, collection)`. It needs to abstract over the undocumented portal API plus FTP / S3 path conventions per collection (paths embed the collection slug, e.g. `data_collections/1000G_2504_high_coverage/`), and route bulk pulls to S3 rather than FTP.

## Review notes

Potential new canonical short-name for review:

```
Proposed license short name: EMBL-EBI-Terms-of-Use
  Used by: IGSR, and likely many other EBI-hosted resources (Ensembl variation,
  Europe PMC partner data, BioModels) that operate under EBI's institutional
  terms rather than a standard SPDX license. Worth standardising before more
  EBI entries land.
```

Potential new join keys for review:

```
Potential new join key for review: BIOSAMPLE_ID
  Entity type: biological_sample (EBI BioSample accession)
  Pattern: ^SAM[NED][AG]?[0-9]+$
  Other datasets that would use it: ENA, NCBI SRA, DDBJ, BioStudies, ArrayExpress,
  PRIDE. Every IGSR sample record exposes one at _source.biosampleId (e.g.
  SAME123392 for NA12878). Currently in primary_keys only because it is not yet
  in the canonical registry; promote and move to join_keys on acceptance.

Potential new join key for review: IGSR_SAMPLE_NAME
  Entity type: human_genome_sample
  Pattern: ^(NA|HG)[0-9]{4,6}$
  Other datasets that would use it: NCBI SRA, ENA, GIAB, gnomAD, dbGaP, Coriell
  catalog. Coriell-issued IDs that have become the de facto reference-sample
  vocabulary in human genomics tooling.

Potential new join key for review: IGSR_POPULATION_CODE
  Entity type: human_population
  Pattern: ^[A-Z]{3}$
  Other datasets that would use it: gnomAD (partial overlap), HGDP, SGDP,
  Ensembl variation. Three-letter codes from the 1000 Genomes population
  taxonomy (CEU, YRI, CHB, JPT, ...).
```

No `/api/beta` documentation is published by IGSR; the endpoints used here were discovered through portal traffic and may move without notice. Re-verify on each refresh.
