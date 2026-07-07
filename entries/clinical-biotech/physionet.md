---
id: physionet
name: PhysioNet (MIMIC-IV / eICU)
domain: clinical-biotech
entry_kind: mixed
description: NIH-funded MIT repository of de-identified biomedical data whose flagship credentialed resources are the MIMIC-IV and eICU-CRD intensive-care EHR databases (diagnoses, labs, prescriptions, vitals, notes, waveforms).
homepage_url: https://physionet.org/
docs_url: https://mimic.mit.edu/
type:
  - bulk-download
  - database
  - web-ui
auth_required: dars-or-equivalent
cost: free-with-registration
license: PhysioNet-Credentialed-Health-Data-License-1.5.0
rate_limit: "not applicable; credentialed data is delivered as bulk file download or queried on Google Cloud BigQuery / GCS after approval"
bulk_available: true
frequency: "irregular; versioned releases (MIMIC-IV v3.1 released 2024-10-11)"
lag: "historical and de-identified with per-patient date-shifting; MIMIC-IV covers ICU/ED admissions across roughly 2008-2022, released years after collection"
geography: [USA]
join_keys:
  - ICD_10
  - NDC
  - LOINC_CODE
primary_keys:
  - MIMIC_SUBJECT_ID
  - MIMIC_HADM_ID
  - MIMIC_STAY_ID
  - EICU_PATIENTUNITSTAYID
  - EICU_UNIQUEPID
join_key_fields:
  - join_key: ICD_10
    fields: ["diagnoses_icd.icd_code (rows where icd_version=10)", "procedures_icd.icd_code (ICD-10-PCS, rows where icd_version=10)"]
  - join_key: NDC
    fields: ["prescriptions.ndc (11-digit form)"]
mcp_status: mcp-exists
mcp_maturity: experimental
mcp_package:
  - "m4-mcp (PyPI)"
mcp_notes: >
  M3 / m4-mcp is a research-grade community connector: one command pulls MIMIC-IV from
  PhysioNet, launches a local DuckDB+Parquet (or SQLite) instance or connects to hosted
  BigQuery, and exposes natural-language-to-SQL over read-only, injection-checked queries.
  Requires the user's own PhysioNet credentialing; the MCP does not bypass the DUA.
agent_use_cases:
  - ICU cohort definition by ICD-10 diagnosis
  - lab and vitals time-series extraction
  - medication-exposure lookup by NDC
  - clinical-note and waveform retrieval for a stay
  - outcome / mortality modelling on real EHR data
last_verified: 2026-07-02
build_priority: high
notes: "Access to MIMIC-IV, MIMIC-IV-Note, MIMIC-CXR, and eICU-CRD requires PhysioNet credentialing: a completed CITI 'Data or Specimens Only Research' training certificate plus a signed project-specific Data Use Agreement. Registration and data are free; there is no fee. Some other PhysioNet resources are fully open, but the flagship clinical databases are credentialed."
---

# PhysioNet (MIMIC-IV / eICU)

## Why this source matters

PhysioNet is an NIH-funded biomedical data publishing platform run by the MIT Laboratory for Computational Physiology (with Beth Israel Deaconess Medical Center), hosting several hundred de-identified resources across physiological waveforms, structured EHR, clinical text, imaging, and machine-learning models for ~190,000 registered users. Its flagship resources are the intensive-care EHR databases: MIMIC-IV (~65,000 ICU and ~200,000 ED patients from Beth Israel Deaconess, 364,627 unique individuals as of v3.0) and eICU-CRD (~200,000 multi-center US ICU stays contributed via the Philips eICU telehealth programme). Each carries patient-level diagnoses, laboratory results, medications, vitals, procedures, and (for MIMIC) free-text notes, radiology, and bedside waveforms. For any agent reasoning about real-world critical-care trajectories, benchmark clinical-ML tasks (mortality, length-of-stay, sepsis onset, phenotyping), or lab/medication patterns at admission scale, MIMIC-IV and eICU are the canonical open EHR references. Secondary domains: `public-health` (population-scale de-identified EHR for epidemiology) and `healthcare-claims` (admission and coding structure overlapping US administrative data, though this is clinical care data, not payer claims).

## Agent use cases

- ICU cohort definition by ICD-10 diagnosis
- lab and vitals time-series extraction
- medication-exposure lookup by NDC
- clinical-note and waveform retrieval for a stay
- outcome / mortality modelling on real EHR data

## Join strategy

Registry-backed keys the clinical databases expose natively are `ICD_10` (MIMIC-IV `diagnoses_icd.icd_code` where `icd_version=10`, with ICD-9 also present under `icd_version=9`; procedures carry ICD-10-PCS in `procedures_icd.icd_code`) and `NDC` (MIMIC-IV `prescriptions.ndc`, converted to 11-digit form). Pair on `ICD_10` with any diagnosis-coded source (openFDA, CMS, ICD reference tables) and on `NDC` with DailyMed, openFDA drug labels, RxNorm, or the FDA NDC directory.

Source-internal identifiers stay out of the canonical set: MIMIC-IV keys every table on `subject_id` (patient), `hadm_id` (hospital admission), and `stay_id` (ICU stay); eICU-CRD keys on `patientunitstayid`, `patienthealthsystemstayid`, and `uniquepid`. These are unique within their database but resalted and date-shifted, so they never join across to other sources or to real-world identifiers.

RxNorm and LOINC were hinted for this source but are not treated as native join keys here. See Review notes: MIMIC-IV normalises medications through NDC (and internal GSN / formulary codes), not RxNorm CUIs, so RxNorm is reachable only via an NDC-to-RxNorm crosswalk rather than a source field; and LOINC (historically `d_labitems.loinc_code`) is not a canonical registry key and its mapping now lives in the MIMIC Code Repository rather than the shipped tables.

## Access notes

No open data API. The public `physionet.org` project pages, schema documentation (`mimic.mit.edu`), and the MIMIC Code Repository are browsable without login and are the surface an agent can hit today to confirm table structure, version, and coding conventions. Participant-level rows are gated.

To obtain the data: (a) register a PhysioNet account, (b) complete the CITI "Data or Specimens Only Research" training and upload the certificate to get credentialed, and (c) sign the project-specific Data Use Agreement (MIMIC-IV is under the PhysioNet Credentialed Health Data License / DUA 1.5.0). Registration and data are free of charge. Two delivery paths after approval:

- **Bulk download.** Comma-delimited (`.csv.gz`) files per table from the project's Files page. Load into Postgres/DuckDB with the DDL published in the MIMIC Code Repository.
- **Google Cloud.** MIMIC-IV v3.1 is hosted on BigQuery (`physionet-data.mimiciv_3_1_hosp`, `mimiciv_3_1_icu`) and GCS; access is granted to the credentialed user's Google account. Querying incurs the user's own GCP costs.

No per-IP rate limit applies because the substantive surface is not an open HTTP API. Re-verify freshness by checking the latest version and release date at `https://physionet.org/content/mimiciv/`.

## MCP / connector notes

An experimental community MCP exists: M3 (`m4-mcp` on PyPI), which retrieves MIMIC-IV from PhysioNet, stands up a local DuckDB+Parquet or SQLite instance (or connects to hosted BigQuery), and exposes natural-language querying over read-only, SQL-injection-checked queries with schema introspection. It does not bypass credentialing; the user supplies their own PhysioNet access. Gaps: research-grade maturity, MIMIC-IV-centric (eICU and waveform resources not covered), and no abstraction over the many other PhysioNet datasets. A fuller connector would front the PhysioNet catalogue (`search_projects`, `get_project_metadata`, `get_table_schema`) plus a credential-aware query surface (`run_sql`, `describe_table`, `get_code_dictionary`) that respects the DUA boundary.

## Review notes

- License: MIMIC-IV / eICU-CRD are governed by the "PhysioNet Credentialed Health Data License 1.5.0" and its matching Data Use Agreement, which has no SPDX code. Used canonical short name `PhysioNet-Credentialed-Health-Data-License-1.5.0`; this is not yet in the `SCHEMA.md § License conventions` known-cases list. Flag for review. Note that other PhysioNet resources carry different licences (some Open Data Commons / fully open); this entry's field reflects the flagship credentialed databases.
- `cost: free-with-registration` is correct rather than `paid`: PhysioNet charges no access fee (unlike UK Biobank). The only cost barrier is CITI training + DUA signature, plus any self-incurred GCP compute if using BigQuery.
- `auth_required: dars-or-equivalent` covers the credentialing + DUA flow.
- `domain`: chose `clinical-biotech` (patient-level clinical EHR alongside the clinical-vocabulary cluster). `public-health` and `healthcare-claims` were considered and are noted as secondary in the opening section. UK Biobank sits in `public-health` because it is a prospective cohort; MIMIC/eICU are routine-care EHR, hence clinical.
- `entry_kind: mixed`: PhysioNet spans time-series (waveforms), panel/registry (EHR), corpus (clinical notes), and imaging across hundreds of datasets. Considered `is_directory: true` since PhysioNet is a publishing platform, but this entry targets MIMIC-IV/eICU as primary data sources, not purely a discovery directory.
- Requester join-key hints reconciled:
  - `ICD_10` — in registry, native (`diagnoses_icd`), included.
  - `NDC` — in registry, native (`prescriptions.ndc`), added (not in the original hint but it is the accurate medication join key).
  - `RXNORM_CUI` — in registry but NOT natively exposed; MIMIC-IV uses NDC/GSN, so RxNorm is only reachable via an NDC-to-RxNorm crosswalk. Excluded from `join_keys` to avoid overstating; documented in Join strategy.
  - `LOINC` — NOT in the canonical registry. Potential new join key for review:
    - Entity type: `laboratory_observation_code`
    - Pattern: `^[0-9]{1,5}-[0-9]$` (e.g. `2160-0`)
    - Other datasets that would use it: openFDA, OHDSI Athena, UMLS, most lab-carrying EHR sources; MIMIC-IV historically exposed it in `d_labitems.loinc_code` and the mapping is now maintained in the MIMIC Code Repository.
- `access_test` omitted: all participant-level surfaces (bulk files and BigQuery) require credentialing and non-HTTP or authenticated access, so a `curl -sf` cannot satisfy an expected-fields contract. Freshness check documented in Access notes.
