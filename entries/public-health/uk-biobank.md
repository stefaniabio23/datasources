---
id: uk-biobank
name: UK Biobank
domain: public-health
entry_kind: panel
description: Deep-phenotyped longitudinal cohort of ~500,000 UK adults with whole-genome sequencing, imaging, biomarkers, lifestyle questionnaires, and linked NHS hospital, cancer, death, and primary-care records. Access is by approved application only.
homepage_url: https://www.ukbiobank.ac.uk/
docs_url: https://biobank.ndph.ox.ac.uk/showcase/
type:
  - bulk-download
  - database
  - web-ui
auth_required: dars-or-equivalent
cost: paid
license: UKB-Material-Transfer-Agreement
rate_limit: "not applicable; data is delivered as bulk dispatches or accessed inside the DNAnexus Research Analysis Platform after application approval"
bulk_available: true
frequency: "rolling additions; major data refreshes (imaging, sequencing, linked EHR) on a multi-month cycle"
lag: "EHR linkage typically several months behind event date; imaging and -omics releases lag enrolment by years"
geography: [GBR]
join_keys:
  - ICD_10
  - OPCS_4
  - BNF_CODE
  - GENE_SYMBOL
  - ENSEMBL_ID
  - RSID
primary_keys:
  - UKB_PARTICIPANT_EID
  - UKB_FIELD_ID
  - UKB_INSTANCE
  - UKB_ARRAY_INDEX
join_key_fields:
  - join_key: ICD_10
    fields: ["field-41270 (HES diagnoses, main + secondary)", "field-40001 (primary cause of death)", "field-40002 (contributory causes of death)", "field-40006 (cancer-registry ICD-10)"]
  - join_key: OPCS_4
    fields: ["field-41272 (HES operative procedures)"]
  - join_key: BNF_CODE
    fields: ["primary-care prescription tables (GP prescriptions, dispensing-system-specific BNF / Read v2 / dm+d mappings)"]
  - join_key: GENE_SYMBOL
    fields: ["WES/WGS pVCF annotations", "exome and imputed-variant per-gene burden tables"]
  - join_key: ENSEMBL_ID
    fields: ["WES/WGS VEP annotations on the RAP"]
  - join_key: RSID
    fields: ["imputed-genotype bim/pgen files (rsid column)", "GWAS summary-stats releases"]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No MCP. The substantive data is controlled-access and sits behind an Access Application
  Management System approval plus a fee, so a connector cannot front the bulk records.
  Useful MCP surface would target the public Data Showcase: search_fields,
  get_field_metadata, get_coding, list_categories, get_data_dictionary. The Showcase
  itself returns HTML; an MCP would scrape or wrap the published TSV exports of the
  data dictionary and codings catalogues.
agent_use_cases:
  - genotype-phenotype association lookup
  - cohort definition by ICD-10 / OPCS-4 / BNF code
  - field-metadata and coding lookup via Data Showcase
  - PheWAS and ExWAS variant-to-phenotype mapping
  - imaging-derived-phenotype context for a disease
last_verified: 2026-06-09
build_priority: medium
notes: "Substantive data access requires an approved application via the Access Management System (AMS), an institutional Material Transfer Agreement, and an access fee. The public Data Showcase exposes field, category, and coding metadata without login; that surface is what an MCP would realistically wrap."
---

# UK Biobank

## Why this source matters

The deepest open-to-researchers prospective cohort in the world. Roughly 500,000 UK adults aged 40-69 at enrolment (2006-2010), now followed for two decades with whole-genome sequencing on the full cohort, exome sequencing, SNP array genotypes, multi-organ MRI imaging (~100k participants), retinal OCT, DXA, blood and urine biomarker panels, Olink proteomics on ~53k, NMR metabolomics on ~120k, repeated lifestyle questionnaires, wrist-accelerometer activity, cognitive tests, and longitudinal linkage to NHS hospital episodes (HES), cancer registries, death registers, and (in England) primary-care GP records. Funded by the Medical Research Council, Wellcome, the UK Department of Health, NHS, Diabetes UK, and the Scottish Government. Used by ~30,000 researchers across 90+ countries with over 9,000 peer-reviewed publications by late 2023. For any agent reasoning about genotype-phenotype links, imaging-derived phenotypes, polygenic risk, lifestyle exposures, or drug-prescription patterns at population scale, UK Biobank is the canonical reference cohort. Secondary domains: `bio-genomics` (WGS / WES / array data and per-gene burden summaries) and `healthcare-claims` (HES, cancer registry, GP prescribing records as the UK-side counterpart to US claims sources).

## Agent use cases

- genotype-phenotype association lookup
- cohort definition by ICD-10 / OPCS-4 / BNF code
- field-metadata and coding lookup via Data Showcase
- PheWAS and ExWAS variant-to-phenotype mapping
- imaging-derived-phenotype context for a disease

## Join strategy

Registry-backed keys are `ICD_10` (HES diagnoses field 41270, death registry fields 40001/40002, cancer registry field 40006), `OPCS_4` (HES procedures field 41272), `BNF_CODE` (primary-care prescription tables for England GP records, alongside dispensing-system-specific Read v2 and dm+d mappings), `GENE_SYMBOL` and `ENSEMBL_ID` (WES/WGS VEP-annotated pVCFs and per-gene burden tables on the Research Analysis Platform), and `RSID` (imputed-genotype pgen/bim and GWAS summary releases). Pair with Open Targets and Open Targets Genetics for variant-to-disease prior, with GWAS Catalog for replication, with FinnGen for cross-cohort meta-analysis, and with Ensembl / UniProt for functional annotation.

UK Biobank also exposes participant-internal identifiers that stay out of the canonical join-key set: `eid` (the participant ID, stable within an approved application but resalted per project so the same person has a different `eid` in two unrelated applications), `field_id` (Data Showcase variable ID, e.g. 41270 for HES diagnoses), `instance` (visit / repeat number), and `array_index` (within-field multi-value index). These are the four axes of every Showcase variable and the schema all bulk exports follow.

Several useful join keys that UK Biobank exposes are not yet in the registry: Read v2 / Read CTV3 primary-care diagnosis codes, SNOMED CT, dm+d drug identifiers, and ATC drug classification (UK Biobank publishes its own BNF-to-ATC and Read-to-ICD mappings). See Review notes.

## Access notes

Two surfaces, very different shape.

**Public Data Showcase** (`https://biobank.ndph.ox.ac.uk/showcase/`). No login required. Browse categories, search fields, inspect coding systems (ICD-10 = coding 19, OPCS-4 = coding 240, etc.), download the data dictionary and coding TSVs. This is what an agent can hit today without an application; it answers "is variable X in UK Biobank, and how is it coded" but never returns participant-level rows. Endpoints are HTML; scraping or wrapping the published TSV exports of `Data_Dictionary_Showcase.tsv` and `Codings.tsv` is the realistic path.

**Substantive data access** requires (a) registration as a UK Biobank researcher, (b) a project application through the Access Management System (AMS) describing the scientific rationale and analyses, (c) an institutional Material Transfer Agreement, and (d) payment of an access fee that scales by data type (baseline phenotypes are the cheapest tier; WGS, RAP compute, and proteomics are progressively more). Typical end-to-end time from application to data access is multiple months. Two delivery models:

- **Bulk dispatch.** Tabular phenotype data and many bulk genetic files are dispatched as encrypted archives the approved institution downloads and analyses on its own infrastructure. The `ukbconv`, `ukbfetch`, and `gfetch` utilities (downloadable from the Showcase under Downloads) decrypt and convert dispatch files.
- **Research Analysis Platform (RAP)**, hosted on DNAnexus on AWS. Imaging, WGS, WES, proteomics, and other large-volume data sit on RAP and are analysed in-platform via Jupyter, RStudio, Swiss Army Knife, dxFUSE, and the Apollo SQL interface. Compute and storage are billed per use against the researcher's account; the platform itself is not directly REST-callable for bulk export of participant records.

No published per-IP rate limit because the substantive surface is not an open HTTP API.

Re-derivation: identifiers (`eid`) are resalted per application, so cross-application linkage of individuals is not possible by design. Withdrawn-participant lists are issued periodically and approved researchers must remove those rows from local copies.

## MCP / connector notes

No MCP exists. Building one against the controlled-access surface is not feasible (data sits behind AMS approval, MTA, fee, and a per-project encryption key). A useful MCP would instead front the public Data Showcase metadata: `search_fields(query)`, `get_field_metadata(field_id)`, `get_coding(coding_id)`, `list_categories(parent_id)`, `get_data_dictionary()`, `download_coding_tsv(coding_id)`. That makes UK Biobank queryable as a *what variables and codings does this cohort hold* reference, which is what most agent tasks need before a human runs the actual analysis on RAP. Audience is narrow (population-genetics and epidemiology researchers), so build priority is medium rather than high.

## Review notes

- License: UK Biobank data is governed by the project-specific Material Transfer Agreement, not an SPDX licence. Used canonical short name `UKB-Material-Transfer-Agreement`; this is not yet in the `SCHEMA.md § License conventions` known-cases list. Flag for review.
- `auth_required: dars-or-equivalent` covers the AMS + MTA flow; if a more UKB-specific enum value is wanted later, flag here.
- `cost: paid` reflects that a per-project access fee is required even though headline framing is sometimes "open to bona fide researchers". The free Showcase metadata is not the substantive data.
- `entry_kind: panel` fits the longitudinal-cohort shape (one row per participant, repeated visits, multiple data modalities); `mixed` was considered but `panel` is the more specific honest description.
- Potential new join keys for review:
  - `READ_V2_CODE`
    - Entity type: primary_care_diagnosis_code
    - Pattern: 5-character alphanumeric (e.g. `G30..`)
    - Other datasets that would use it: CPRD, OpenSAFELY, NHS Digital primary-care extracts, Genes & Health
  - `READ_CTV3_CODE`
    - Entity type: primary_care_diagnosis_code
    - Pattern: 5-character alphanumeric
    - Other datasets that would use it: CPRD, NHS Digital, OpenSAFELY
  - `SNOMED_CT`
    - Entity type: clinical_concept
    - Pattern: integer concept ID
    - Other datasets that would use it: NHS Digital, OpenSAFELY, openFDA (partial), most modern EHR sources globally
  - `DMD_ID`
    - Entity type: uk_drug_product
    - Pattern: integer dm+d concept ID
    - Other datasets that would use it: NHS BSA prescribing data, OpenPrescribing, NHS Digital
  - `ATC_CODE` is already in the registry but UK Biobank exposes it via published BNF-to-ATC mappings; current entry's join-key list keeps `BNF_CODE` as the source-native code and treats ATC as a derived mapping rather than a source field.
- `access_test` omitted: substantive endpoints require approval and credentials; the Showcase is HTML, not a JSON API, so a `curl -sf` against it would not satisfy the expected-fields contract. Re-verify freshness by hitting `https://biobank.ndph.ox.ac.uk/showcase/` and confirming the Data Dictionary download date.
- Considered domain `bio-genomics` (heavy on WGS and array data) and `healthcare-claims` (HES + GP records); chose `public-health` because the cohort is the unit and population-health follow-up is the structural shape. Secondary domains noted in the opening section.
