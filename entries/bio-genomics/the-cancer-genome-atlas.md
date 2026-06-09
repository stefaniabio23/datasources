---
id: the-cancer-genome-atlas
name: The Cancer Genome Atlas (TCGA, via Broad GDAC Firehose)
domain: bio-genomics
entry_kind: mixed
description: Pan-cancer multi-omic atlas of ~11,000 tumour samples across 33 cancer types, processed and distributed by the Broad Institute GDAC Firehose pipeline as standardised level-3 datasets and analysis runs.
homepage_url: https://gdac.broadinstitute.org/
docs_url: https://gdac.broadinstitute.org/runs/info/data_run_versioning.html
type:
  - bulk-download
  - rest-api
  - web-ui
  - dataset-dump
auth_required: none
cost: free
license: TCGA-Data-Use
rate_limit: "no published per-IP limit; bulk archives served over HTTPS, FireBrowse REST has no documented quota"
bulk_available: true
frequency: "frozen; final stddata run 2016-01-28, final analyses run 2016-01-28 (released 2017), CPTAC AWG runs through 2020"
lag: "static archive; TCGA data collection completed 2013, GDAC processing wound down 2017"
geography: [global]
join_keys:
  - GENE_SYMBOL
  - ENSEMBL_ID
  - ENTREZ_GENE_ID
  - DOI
  - PMID
primary_keys:
  - TCGA_BARCODE
  - TCGA_PATIENT_BARCODE
  - TCGA_SAMPLE_BARCODE
  - TCGA_ALIQUOT_BARCODE
  - TCGA_PROJECT_ID
  - TCGA_COHORT_CODE
join_key_fields:
  - join_key: GENE_SYMBOL
    fields: [Hugo_Symbol, gene, gene_symbol]
  - join_key: ENSEMBL_ID
    fields: [Ensembl_gene_id, gene_id]
  - join_key: ENTREZ_GENE_ID
    fields: [Entrez_Gene_Id, entrez_id]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No MCP exists for GDAC Firehose or the NCI GDC TCGA endpoints. Suggested surface:
  list_cohorts, get_clinical(cohort, barcode), get_mutations(gene, cohort),
  get_expression(gene, cohort), get_copy_number(gene, cohort), get_survival(cohort).
  Connector must abstract over (a) frozen Firehose archive paths vs live GDC API,
  (b) TCGA barcode hierarchy (project, patient, sample, portion, aliquot), and
  (c) the split between open (clinical, level-3 summaries) and controlled (raw BAMs,
  germline variants under dbGaP phs000178) access tiers.
agent_use_cases:
  - pan-cancer mutation prevalence lookup
  - cohort-level expression and survival analysis
  - tumour-vs-normal differential expression
  - copy-number and methylation profiling by gene
  - target-disease prioritisation for oncology
access_test:
  command: "curl -sfI 'https://gdac.broadinstitute.org/runs/stddata__2016_01_28/'"
  expected_status: 200
last_verified: 2026-06-09
build_priority: medium
notes: "GDAC Firehose is the Broad's frozen processing mirror of TCGA. For current TCGA queries, agents should also know about the NCI Genomic Data Commons REST API at api.gdc.cancer.gov, which is the canonical live endpoint; this entry covers the Broad GDAC URL the user supplied. FireBrowse REST (firebrowse.org) currently returns certificate errors via WebFetch and was not test-hit."
---

# The Cancer Genome Atlas (TCGA, via Broad GDAC Firehose)

## Why this source matters

TCGA is the foundational pan-cancer molecular atlas: ~11,000 patients across 33 cancer types, profiled for somatic mutations (WES, later WGS), copy number (SNP arrays), DNA methylation (450K arrays), mRNA expression (RNA-seq and Agilent arrays), miRNA expression, and reverse-phase protein arrays (RPPA), with linked clinical, demographic, and outcome data. Run jointly by the NCI and NHGRI from 2006 to 2013, it is the reference cohort any oncology agent should hit for cohort-level prevalence, expression, or survival questions, and the substrate for the PanCanAtlas analyses. The Broad Institute Genome Data Analysis Center (GDAC) Firehose at this URL is the Broad's pipeline output: standardised level-3 datasets ("stddata" runs) and downstream analysis runs (MutSig, GISTIC, clustering, correlations), organised as static, versioned archives. The processing pipeline is wound down (final stddata run 2016-01-28, final analyses run 2016-01-28 published 2017), so Firehose is a frozen mirror; live TCGA queries now go through the NCI Genomic Data Commons (GDC) at api.gdc.cancer.gov. Secondary domain: `clinical-biotech` for target validation, biomarker discovery, and drug-repurposing diligence keyed on tumour molecular profiles.

## Agent use cases

- pan-cancer mutation prevalence lookup
- cohort-level expression and survival analysis
- tumour-vs-normal differential expression
- copy-number and methylation profiling by gene
- target-disease prioritisation for oncology

## Join strategy

TCGA keys every biospecimen on the hierarchical **TCGA barcode**: `TCGA-XX-XXXX-NNL-NNL-XXXX-NN` decomposes into project, tissue source site, patient, sample type, portion, plate, and analyte. Agents typically join at the patient barcode (`TCGA-XX-XXXX`) for clinical-to-molecular pivots, or the aliquot barcode for assay-level traceability. Cohorts are referenced by short codes (`BRCA`, `LUAD`, `GBM`, `SKCM`); Firehose archive paths embed these directly. Gene-level rows expose `GENE_SYMBOL` (HGNC, e.g. `TP53`), `ENTREZ_GENE_ID`, and in later releases `ENSEMBL_ID` for RNA-seq quantifications. MAF files carry HGVS strings, hg19 coordinates (Firehose era; GDC has rebuilt to hg38), dbSNP rsIDs where available, and COSMIC IDs in annotated variants. Publication metadata for the marker papers carries `DOI` and `PMID`.

Pair TCGA with cBioPortal (curated cohort views, same barcodes), the NCI GDC (live API, hg38, harmonised mutations), Open Targets (target-disease scores by `ENSEMBL_ID`), GTEx and Human Protein Atlas (normal-tissue baselines), CCLE/DepMap (matched cancer cell lines by lineage), and OncoKB or CIViC (clinical annotation of variants). For survival analyses, the patient barcode plus the clinical TSV from each cohort's stddata archive is the minimum.

See Review notes for `TCGA_BARCODE`, `TCGA_PATIENT_BARCODE`, and `TCGA_COHORT_CODE` as candidate canonical join keys; barcodes are widely cross-referenced (cBioPortal, GDC, PanCanAtlas freezes, downstream re-analyses).

## Access notes

Three practical paths from this homepage:

1. **Static archive downloads.** Browse `https://gdac.broadinstitute.org/runs/` to the desired run (latest stddata is `stddata__2016_01_28/`, latest analyses is `analyses__2016_01_28/` published 2017). Each run contains per-cohort directories with tarred level-3 deliverables: clinical TSV, mutation MAFs, expression matrices, methylation beta values, copy-number GISTIC outputs, etc. Stable HTTPS paths, no auth, no rate limit.
2. **`firehose_get` CLI.** Broad-published bash wrapper for bulk pulls. Pattern: `firehose_get -tasks <task-regex> stddata <date> <cohort>`, e.g. `firehose_get -tasks rnaseqv2 stddata 2016_01_28 BRCA`. Useful when scripting cohort sweeps; just resolves to the same archive URLs.
3. **FireBrowse REST.** Companion REST API at `firebrowse.org/api/v1/` with Python (`firebrowse-py`), R (`FirebrowseR`), and Unix bindings. Surfaces clinical, mutation MAF rows, mRNAseq, CNV, and analysis-run outputs as JSON or TSV. As of verification, the FireBrowse cert chain returns errors from generic clients (verify before relying on it in production agents).

License is the **TCGA Data Use Policy**: open level-3 summary data (clinical, mutations, expression, methylation level 3) is freely redistributable with citation; level-1/2 raw data (BAMs, genotypes, germline variants) is dbGaP-controlled under accession `phs000178` and requires a Data Access Request (IRB-style, weeks to months). The homepage states "Downloading data from this site constitutes agreement to TCGA data usage policy". Practically: cite the TCGA Research Network and the relevant marker paper for each cohort, do not attempt to re-identify donors, and propagate the same terms downstream.

Freshness: this archive is frozen. For current TCGA queries (harmonised to hg38, ongoing legacy data migration, controlled-tier requests), use the NCI GDC at `https://api.gdc.cancer.gov/` instead. An agent treating "TCGA" as live should default to GDC and use GDAC Firehose only for reproducing 2016-era analyses or pulling pre-computed MutSig/GISTIC outputs that GDC does not re-host.

## MCP / connector notes

No MCP exists for GDAC Firehose, FireBrowse, or the NCI GDC. Build value is high: TCGA underlies most oncology benchmarking, target validation, and biomarker work, and would be hit by any agent in this directory doing cancer-genomics, clinical-biotech, or drug-discovery tasks. Suggested surface for a canonical TCGA MCP (Firehose + GDC combined):

- `list_cohorts()`: 33 TCGA project codes with sample counts
- `get_clinical(cohort, barcode=None)`: demographics, stage, outcomes
- `get_mutations(gene, cohort=None)`: per-gene MAF rows pan-cancer or per-cohort
- `get_expression(gene, cohort, assay='rnaseqv2')`: RSEM-normalised counts by sample
- `get_copy_number(gene, cohort)`: GISTIC discrete or continuous CN
- `get_methylation(gene_or_probe, cohort)`: 450K beta values
- `get_survival(cohort, stratify_by=None)`: Kaplan-Meier-ready outcome tables
- `get_pancanatlas_freeze(table)`: PanCanAtlas harmonised mutation, CN, mRNA freezes

Connector must abstract over (a) Firehose frozen archive vs live GDC API selection per query, (b) TCGA barcode hierarchy (project, patient, sample, portion, aliquot) and the sample-type-code lookup (`01` primary tumour, `06` metastatic, `11` normal), (c) hg19 (Firehose) vs hg38 (GDC) coordinate systems, and (d) the open vs dbGaP-controlled tier boundary, surfacing a clear "requires dbGaP DAR" error rather than empty results when callers reach for raw sequence data.

## Review notes

- License: TCGA data use is governed by the TCGA Data Use Policy plus the NIH Genomic Data Sharing Policy; open-tier level-3 data has no SPDX identifier and "TCGA-Data-Use" is the canonical short name proposed here. Flag for review: not yet in `SCHEMA.md § License conventions`; if accepted, add there. The dbGaP-controlled tier (raw BAMs, germline calls) sits behind `phs000178` and is distinct from the open level-3 mirror this entry's URL points at.
- Domain choice: `bio-genomics` primary (the molecular atlas is the core asset); `clinical-biotech` secondary for target validation and clinical-outcome linkage. `mixed` entry_kind because TCGA spans genomics, transcriptomics, methylation, proteomics, and clinical outcomes across cohorts.
- Provenance ambiguity: this entry's homepage is the Broad GDAC Firehose, but the live canonical TCGA endpoint is the NCI GDC at `api.gdc.cancer.gov`. The two are complementary (Firehose hosts frozen pre-computed analyses; GDC hosts live harmonised data). If the registry later wants separate entries for GDC and Firehose, consider splitting; for now this entry treats Firehose as the access surface and points agents at GDC for live queries in the body.
- Potential new canonical join keys for review:
  - `TCGA_BARCODE`
    - Entity type: `cancer_biospecimen`
    - Pattern: `^TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}(-[0-9]{2}[A-Z])?(-[0-9]{2}[A-Z])?(-[A-Z0-9]{4})?(-[0-9]{2})?$`
    - Other datasets that would use it: NCI GDC, cBioPortal, PanCanAtlas freezes, ISB-CGC BigQuery tables, Xena Browser, Firehose, every downstream TCGA re-analysis.
  - `TCGA_PATIENT_BARCODE`
    - Entity type: `cancer_patient`
    - Pattern: `^TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}$`
    - Other datasets that would use it: same set as above; this is the join level for clinical-to-molecular pivots.
  - `TCGA_COHORT_CODE`
    - Entity type: `tcga_cohort`
    - Pattern: `^[A-Z]{2,4}$` (e.g. `BRCA`, `LUAD`, `STAD`)
    - Other datasets that would use it: GDC, cBioPortal, Firehose archives, PanCanAtlas, GDSC/CCLE cancer-type mappings.
  - `ENTREZ_GENE_ID`
    - Entity type: `gene`
    - Pattern: `^[0-9]+$`
    - Other datasets that would use it: NCBI Gene, GTEx, CCLE/DepMap, HPA, most biomedical cross-references. Already flagged in `human-protein-atlas.md` and `cancer-cell-line-encyclopedia.md`; consolidating here.
- COSMIC ID (`COSV*`, `COSM*`) appears in annotated MAFs and is a cross-source variant identifier worth a separate proposal alongside any other variant-keyed cancer dataset.
- `access_test` is a HEAD against the latest stddata run index; no JSON API is hit because Firehose is a static archive. FireBrowse REST was not test-hit due to TLS cert verification errors from generic clients; flag for human verification.
