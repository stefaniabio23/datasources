---
id: ctg-db
name: CTG-DB (ClinicalTrials.gov MedDRA-Normalised Safety Database)
domain: clinical-biotech
entry_kind: registry
description: Open-source pipeline that transforms the full ClinicalTrials.gov XML archive into a relational database with arm-level adverse-event counts normalised to MedDRA terminology.
homepage_url: https://github.com/jlpainter/ctgdb
docs_url: https://arxiv.org/abs/2603.15936
type:
  - database
auth_required: none
cost: free
license: Apache-2.0
bulk_available: false
frequency: one-off snapshot (input archive downloaded 2026-02-10); no automatic refresh
lag: "snapshot-based; re-ingest CT.gov XML to update"
geography: [global]
join_keys:
  - NCT_ID
  - MEDDRA_TERM
primary_keys:
  - CTGDB_ARM_ID
join_key_fields:
  - join_key: NCT_ID
    fields: [clinical_trial.nct_id, ct_arms.nct_id]
  - join_key: MEDDRA_TERM
    fields: [adverse_events.meddra_pt, adverse_events.meddra_llt]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - cross-trial adverse-event retrieval
  - arm-level safety-signal comparison
  - MedDRA-normalised AE aggregation
  - placebo-vs-comparator safety diffs
access_test:
  command: "curl -sf 'https://api.github.com/repos/jlpainter/ctgdb'"
  expected_status: 200
  expected_fields: [full_name, license, pushed_at]
last_verified: 2026-07-03
build_priority: low
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: false
---

# CTG-DB (ClinicalTrials.gov MedDRA-Normalised Safety Database)

## Why this source matters

CTG-DB is an open-source pipeline (Painter, Haguinet, Bate) that ingests the complete ClinicalTrials.gov XML archive and produces a relational database purpose-built for cross-trial drug-safety analysis. ClinicalTrials.gov records adverse events as investigator-reported free text against heterogeneous denominators, which blocks systematic pharmacovigilance. CTG-DB preserves arm-level denominators, distinguishes placebo and comparator arms, and normalises AE strings to MedDRA (Preferred Terms, Lower-Level Terms, System Organ Classes) via deterministic exact plus fuzzy matching. Reported coverage: 59.2% of unique AE strings map to MedDRA (18.4% exact, 40.8% fuzzy), rising to 95.0% when weighted by affected participants. It is a derived analytic layer over ClinicalTrials.gov, not a primary registry, and its value is turning registry safety text into a joinable, ontology-aware schema.

## Agent use cases

- cross-trial adverse-event retrieval
- arm-level safety-signal comparison
- MedDRA-normalised AE aggregation
- placebo-vs-comparator safety diffs

## Join strategy

Two canonical keys are exposed. `NCT_ID` keys every trial (`clinical_trial` table) and arm (`ct_arms`), so CTG-DB joins directly to any NCT-keyed source (ClinicalTrials.gov API, TrialBench, Open Targets trial evidence, EU CTIS via WHO UTN bridges). `MEDDRA_TERM` on `adverse_events` (PT/LLT columns, with SOC hierarchy retained) joins to any MedDRA-coded safety source, notably openFDA FAERS, letting an agent line up registry-reported AEs against spontaneous-report signals for the same term.

Source-internal identity: `CTGDB_ARM_ID` is the pipeline's surrogate key for a study arm (patient-level data is never present; everything is aggregate arm-level). Interventions/drugs are retained as free-text names in a dimension table with UMLS concept identifiers but are NOT resolved to a canonical drug key (RxNorm/UNII/ChEMBL), so there is no drug join key here. See Review notes for the arm and UMLS candidates.

## Access notes

There is no hosted API or downloadable database dump. The GitHub repo (`jlpainter/ctgdb`, Apache-2.0) distributes source code only (Java-dominant, with Python and shell). To get the data you clone the repo and run the pipeline against a local copy of the ClinicalTrials.gov XML archive (the documented run used the 2026-02-10 archive: 544,315 studies, ~17 GB compressed, 25,274 files excluded). The logical schema is database-agnostic; primary deployment is MySQL or PostgreSQL, with SQLite for prototyping and CSV as the intermediate bulk-load format. Freshness is entirely a function of when you last re-ingested the archive; there is no auto-update. Verify the tool is current by checking the repo's last push via the GitHub API (`pushed_at`, most recent commit 2026-02-04). The arXiv paper (arXiv:2603.15936) is CC-BY-4.0; the code and produced schema are Apache-2.0, which is the operative license for anyone building and redistributing the database.

## MCP / connector notes

No MCP exists, and value is narrow: consumers must self-host the database first, so a connector would wrap a user-built MySQL/Postgres instance rather than a public endpoint. If built, a low-value connector surface would be `find_trials_by_condition`, `get_arm_adverse_events(nct_id)`, `search_ae_by_meddra_term`, and `compare_arms(nct_id)`, abstracting over the deployment DSN and the PT/LLT/SOC hierarchy joins. Direct SQL against the built schema is sufficient for most users.

## Review notes

- License nuance flagged above (Apache-2.0 for code/schema vs CC-BY-4.0 for the paper); YAML `license` uses the operative Apache-2.0. No new short name needed.
- `CTGDB_ARM_ID` is a source-native surrogate for a study arm, placed in `primary_keys` only (not registry-canonical).
- Potential new join key for review: `UMLS_CUI`
  - Entity type: biomedical_concept (interventions/conditions carry UMLS concept identifiers in CTG-DB dimension tables)
  - Pattern: `^C[0-9]{7}$`
  - Other datasets that would use it: any UMLS-mapped source (MetaMap outputs, DisGeNET, SemMedDB); would let CTG-DB interventions join beyond free-text drug names.
- Drug/intervention is intentionally NOT a canonical join key here: CTG-DB keeps interventions as free text and does not resolve them to RXNORM_CUI/UNII/CHEMBL_ID. Do not invent a drug join key for this entry.
- `join_key_fields` column names (`clinical_trial.nct_id`, `adverse_events.meddra_pt/llt`) are inferred from the paper's described logical schema, not verified column-by-column against the source; confirm against `documentation/` in the repo before relying on exact paths.
