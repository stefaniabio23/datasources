---
id: arrayexpress
name: ArrayExpress
domain: bio-genomics
entry_kind: corpus
description: EMBL-EBI archive of high-throughput functional genomics experiments (microarray and sequencing), now a collection within BioStudies, with MAGE-TAB metadata and raw sequencing reads brokered to ENA.
homepage_url: https://www.ebi.ac.uk/biostudies/arrayexpress
docs_url: https://www.ebi.ac.uk/biostudies/help
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: EMBL-EBI-Terms-of-Use
rate_limit: "unpublished; polite use expected, bulk pulls via FTP/Aspera rather than the API"
bulk_available: true
frequency: "continuous as submitters release studies"
lag: "days from submitter release to public availability; embargo dates set by submitters until linked publication"
geography: [global]
join_keys:
  - NCBI_TAXON_ID
  - PMID
primary_keys:
  - ARRAYEXPRESS_ACCESSION
join_key_fields:
  - join_key: NCBI_TAXON_ID
    fields:
      - "section.subsections.attributes[name=Organism]"
      - "section.links.attributes[name=Organism]"
  - join_key: PMID
    fields:
      - "section.subsections.attributes[name=PubMed ID]"
      - "section.attributes[name=PubMed ID]"
mcp_status: mcp-needed-low-value
mcp_maturity: none
agent_use_cases:
  - find functional-genomics experiments by organism or disease
  - retrieve sample-to-run mapping from SDRF
  - link an expression study to its publication
  - locate raw sequencing reads in ENA via study links
  - dedup European mirrors of GEO submissions
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/biostudies/api/v1/studies/E-MTAB-2770'"
  expected_status: 200
  expected_fields: [accno, attributes, section]
last_verified: 2026-06-22
build_priority: low
---

# ArrayExpress

## Why this source matters

ArrayExpress is EMBL-EBI's archive of high-throughput functional genomics experiments, covering both microarray and sequencing assays (gene expression, ChIP-seq, methylation, single-cell, and more). Run by the EMBL-EBI Functional Genomics team, it is the European counterpart to NCBI GEO and one of the canonical first stops for finding or reusing published expression data. In 2021 ArrayExpress was migrated into BioStudies, where it now exists as a collection rather than a standalone database; the old standalone ArrayExpress REST API was retired and all programmatic access now goes through the BioStudies endpoints. Raw sequencing reads are not stored in ArrayExpress itself, they are brokered to the European Nucleotide Archive (ENA) at submission and each study links out to the ENA run records. Secondary relevance to `academic` (most studies cite a backing publication via PubMed ID and DOI) and to bio-genomics expression analysis downstream, since the EBI Expression Atlas reuses ArrayExpress experiments as one of its primary inputs.

## Agent use cases

- find functional-genomics experiments by organism or disease
- retrieve sample-to-run mapping from SDRF
- link an expression study to its publication
- locate raw sequencing reads in ENA via study links
- dedup European mirrors of GEO submissions

## Join strategy

Canonical join keys exposed by ArrayExpress (via the BioStudies study JSON):

- `NCBI_TAXON_ID` through the organism characteristics carried on samples and study sections, the key cross-source pivot for joining to Ensembl, UniProt, NCBI Taxonomy, and any organism-keyed resource.
- `PMID` through the publication links on each study, letting agents reach back to OpenAlex, Europe PMC, and PubMed for the originating paper (DOIs are also present in attributes and can be extracted as a secondary literature pivot).

The native ArrayExpress accession is `E-MTAB-nnnnn` for direct EBI-deposited experiments. A large legacy block uses the `E-GEOD-nnnnn` prefix: these are mirrors of NCBI GEO Series, where `E-GEOD-12345` corresponds to GEO `GSE12345`. Treat `E-GEOD-` records as duplicates of the GEO source rather than independent studies, dedup against NCBI GEO before counting or analysing. The accession is source-internal and kept in `primary_keys` rather than `join_keys`; it is flagged in `## Review notes` because the Expression Atlas reuses it as a foreign key and it may warrant promotion to the canonical registry.

The MAGE-TAB metadata (IDF + SDRF) is where the experiment structure lives: the SDRF (Sample and Data Relationship Format) carries the run-to-sample mapping, which is the load-bearing table for reconstructing which raw file belongs to which biological sample. Raw sequencing reads live in ENA, so pair ArrayExpress with ENA (FASTQ behind the study), NCBI GEO (the US mirror / dedup target), Ensembl and UniProt for annotation, and OpenAlex/PubMed for the backing literature.

## Access notes

**Low-volume queries:** BioStudies REST API at `https://www.ebi.ac.uk/biostudies/api/v1`, no auth. Fetch a single study with `GET /studies/{accession}` (e.g. `/studies/E-MTAB-2770`), which returns JSON with top-level `accno`, `attributes`, and a nested `section` tree carrying samples, protocols, organism characteristics, and publication links; the `AttachTo` attribute names the `ArrayExpress` collection. Search is via the BioStudies search endpoint scoped to the ArrayExpress collection. The old `www.ebi.ac.uk/arrayexpress/...` REST routes are retired, do not target them.

**Large analyses:** bulk MAGE-TAB and processed-data files download over FTP/Aspera from the EMBL-EBI BioStudies file servers; the per-study `RootPath` attribute in the JSON points at the file area. An R/Bioconductor package (`ArrayExpress`, and the Atlas-oriented `ExpressionAtlas`) wraps programmatic retrieval for analysis workflows. To verify freshness, fetch a recently released accession and check its `ReleaseDate` attribute.

License is the EMBL-EBI Terms of Use: open access with no additional EBI-imposed redistribution restrictions beyond those set by the original data owners, attribution per good scientific practice. Per-study terms can vary, human-subject data and pre-publication embargoes follow data-type-specific release mechanisms, so a study may be under embargo until its linked paper publishes.

## MCP / connector notes

No official or community MCP found for ArrayExpress or the BioStudies API. Low-value to build standalone: the audience overlaps heavily with NCBI GEO (a GEO MCP plus E-GEOD dedup covers most of the demand), and the BioStudies API is clean enough that a thin wrapper adds little for one-off lookups. If built, the connector belongs inside a broader functional-genomics server alongside GEO/SRA/ENA, with a surface of `search_studies` (scoped to the ArrayExpress collection), `get_study` (trimmed from the verbose nested `section` tree), `get_sdrf` (parse the SDRF into a clean run-to-sample table), and `resolve_to_ena` (follow study links to the ENA run accessions). The connector must abstract over the deep BioStudies `section.subsections` nesting and over the E-GEOD-vs-GEO duplication.

## Review notes

Potential new join key for review: ARRAYEXPRESS_ACCESSION
  Entity type: functional_genomics_experiment
  Pattern: ^E-[A-Z]{4}-[0-9]+$ (canonical E-MTAB-nnnnn; legacy E-GEOD-nnnnn for GEO mirrors)
  Other datasets that would use it: EBI Expression Atlas (reuses ArrayExpress accessions as a foreign key), BioStudies, and any resource citing a specific ArrayExpress experiment. Note: E-GEOD- accessions map deterministically to GEO Series (E-GEOD-12345 = GSE12345); if added, document the GEO equivalence so consumers dedup rather than double-count.

Dedup caution: the E-GEOD- prefix block consists of GEO mirrors, not independent EBI studies. Any count or corpus build over ArrayExpress should dedup E-GEOD- records against NCBI GEO. Raw sequencing reads are not held here; they live in ENA and are reached via per-study links.

`license` set to the canonical short name `EMBL-EBI-Terms-of-Use`, consistent with other EBI entries in the directory; this short name is not yet an SPDX code. Confirm it matches the convention used elsewhere or whether a different canonical string is preferred.

`access_test` executed 2026-06-22 against `/studies/E-MTAB-2770`: returned 200 with `accno`, `attributes`, and `section` present, organism `Homo sapiens`, and publication DOIs in attributes.
