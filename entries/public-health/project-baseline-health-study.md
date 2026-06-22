---
id: project-baseline-health-study
name: Project Baseline Health Study
domain: public-health
entry_kind: panel
description: Deep-phenotyped longitudinal cohort of ~2,500 US adults followed 2017-2023 with annual clinical assessments, multi-organ imaging, continuous Verily Study Watch wearable data, labs, functional tests, and participant-reported outcomes. Access is request-gated through Verily's platform.
homepage_url: https://verily.com/solutions/pre-platform/data-partners/project-baseline
type:
  - database
  - web-ui
auth_required: account-required
cost: free-with-registration
license: unknown
notes: "cost enum set to free-with-registration to satisfy the schema; the actual fee model for researcher data access is not published and may involve a partnership or data-access agreement. license not stated on public pages (recorded as unknown)."
bulk_available: false
frequency: "closed cohort; enrolment and active follow-up ran 2017-2023, no new participant data added"
lag: "not applicable; the study has completed its active follow-up window"
geography: [USA]
join_keys:
  - NCT_ID
primary_keys:
  - PROJECT_BASELINE_PARTICIPANT_ID
join_key_fields:
  - join_key: NCT_ID
    fields: ["study-level registration identifier NCT03154346"]
mcp_status: requires-scraping
agent_use_cases:
  - deep-phenotyping cohort reference
  - wearable-derived activity / sleep / heart-rate phenotypes
  - multi-modal imaging context for a disease
  - functional-test and patient-reported-outcome lookup
last_verified: 2026-06-22
build_priority: low
notes: "Substantive participant-level data is request-gated through Verily's workbench platform and is not openly downloadable. auth_required, cost, and license could not be confirmed from public pages; cost and license recorded as unknown rather than guessed. access_test omitted: no public programmatic endpoint."
---

# Project Baseline Health Study

## Why this source matters

A deeply phenotyped US longitudinal cohort run by Verily (Alphabet's life-sciences arm) in collaboration with Duke University and Stanford Medicine, with the study sponsored through Baseline Study LLC. Roughly 2,500 diverse participants were enrolled across sites in California and North Carolina and followed from 2017 to 2023. The study's distinguishing feature is the density of per-participant data rather than cohort size: annual clinical assessments and vitals, a full laboratory panel (chemistry, lipids, HbA1c, hematology), multi-organ imaging with core-lab reads (cardiac ECG / echocardiogram / coronary calcium score, chest X-ray, ophthalmology), functional tests (6-minute walk, grip strength, chair stand, pulmonary function), continuous wearable monitoring via the Verily Study Watch (activity, sleep, heart rate), and participant-reported outcomes (PHQ-9, EQ-5D-5L, lifestyle surveys). For an agent reasoning about deep phenotyping, wearable-derived physiology, or multi-modal disease signatures, Project Baseline is the closest US analogue in kind to UK Biobank: a controlled-access, deeply characterised cohort rather than an open dataset. It is much smaller than UK Biobank and richer per participant in continuous sensor data. Secondary relevance: `clinical-biotech` (registered on ClinicalTrials.gov as NCT03154346) and `bio-genomics` where omic assays are included.

## Agent use cases

- deep-phenotyping cohort reference
- wearable-derived activity / sleep / heart-rate phenotypes
- multi-modal imaging context for a disease
- functional-test and patient-reported-outcome lookup

## Join strategy

The only registry-backed cross-source key is `NCT_ID` (`NCT03154346`), which links the study record to ClinicalTrials.gov and any source that references the trial by its registration identifier. This is a study-level join, not a participant-level one.

Participant-level data uses internal study identifiers minted by Verily that have no cross-source utility; these are captured in `primary_keys` as `PROJECT_BASELINE_PARTICIPANT_ID` (placeholder name, the public-facing schema is not published). As a closed cohort with resalted internal IDs, there is no participant-level join to any external dataset by design, the same pattern as UK Biobank's per-application `eid`. No `join_keys` beyond `NCT_ID`. Imaging, labs, and survey instruments use standard coding systems (PHQ-9, EQ-5D-5L, ICD-coded conditions) inside the controlled environment, but these are not exposed as queryable cross-source fields, so none are flagged here.

## Access notes

**Controlled access, no open download.** This is the load-bearing fact for any agent. There is no public bulk download and no open programmatic API for participant-level records. Researchers request access through Verily's workbench platform (the "request access" link on the homepage), which is a partnership-gated, account-required model: a researcher applies and analyses approved data inside Verily's hosted environment rather than receiving a downloadable extract. The exact application process, eligibility criteria, fee structure, and data-use license were not stated on the public pages reviewed, so `cost` and `license` are recorded as `unknown` rather than guessed. The honest summary an agent should act on: this cohort can inform what data exists and how it was collected, but participant-level analysis requires a successful access request and runs in-platform.

To verify freshness: re-check the homepage `https://verily.com/solutions/pre-platform/data-partners/project-baseline` and the ClinicalTrials.gov record at `https://clinicaltrials.gov/study/NCT03154346` for the current access pathway and any published data-use terms.

## MCP / connector notes

No MCP, and one is not feasible against the substantive surface: participant data sits behind a request-access workbench with no public API. The only programmatically reachable surface is the ClinicalTrials.gov record (NCT03154346), already covered by a ClinicalTrials.gov entry. A connector specific to Project Baseline would add little until Verily publishes a queryable metadata or data-dictionary endpoint. If that appears, a useful MCP surface would mirror the UK Biobank Showcase pattern: `list_data_modalities`, `get_instrument_metadata`, `search_variables`, returning what the cohort holds without returning participant rows. Marked `requires-scraping` because the only structured public information today is the homepage and the trial registry HTML.

## Review notes

- `cost: unknown` and `license: unknown`: the public homepage does not state the research-access fee model or a data-use license. Recorded as `unknown` per the prefer-honest-gaps rule rather than assuming free or paid. Flag for human confirmation if the access terms are located (e.g. via a Verily data-access agreement or a partner-institution data-use page).
- `auth_required: account-required` was chosen over `dars-or-equivalent` because the public framing is a "request access via the platform" / account-gated workbench model rather than a formal Data Access Request Service with a published committee process. If the actual process turns out to be a formal data-access-committee review with an MTA, `dars-or-equivalent` would be the better value, flag for review.
- `primary_keys: PROJECT_BASELINE_PARTICIPANT_ID` is a placeholder identifier name. The study's internal participant-ID scheme is not published; the value documents that participant-level IDs exist and are study-internal, not a confirmed field name.
- `entry_kind: panel` fits the longitudinal-cohort shape (one row per participant, repeated annual visits plus continuous wearable streams, multiple modalities). `mixed` was considered but `panel` is the more specific honest description, consistent with the UK Biobank entry.
- No new join keys proposed: as a closed cohort, the source exposes no cross-source participant identifiers beyond the study-level `NCT_ID`, which is already in the registry.
