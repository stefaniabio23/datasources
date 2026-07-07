---
id: cris-korea
name: Clinical Research Information Service (CRIS)
domain: clinical-biotech
entry_kind: registry
description: WHO- and ICMJE-recognised primary clinical trial registry for the Republic of Korea, operated by the Korea Disease Control and Prevention Agency, exposing Korean and English trial records via a web UI and a public-data-portal REST API.
homepage_url: https://cris.nih.go.kr/
docs_url: https://www.data.go.kr/data/3033869/openapi.do
type:
  - rest-api
  - web-ui
auth_required: api-key-free
cost: free-non-commercial
license: KOGL-Type-2
rate_limit: "data.go.kr quota: ~10,000 calls/day for development keys; higher for approved operational accounts; numOfRows max 50 per page"
bulk_available: false
frequency: continuous
lag: "sponsor-driven; records appear after editorial review, then propagate to WHO ICTRP every 4 weeks"
geography: [KOR]
join_keys:
  - WHO_UTN
primary_keys:
  - KCT_ID
join_key_fields:
  - join_key: WHO_UTN
    fields: [secondary_id]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No official or community MCP. Standalone value is narrow (Korea-scoped, Korean-language
  fields, non-commercial licence), and global agents can already reach CRIS records through
  the WHO ICTRP aggregate. If built, a Korea-specific connector should wrap the data.go.kr
  crisinfodataview endpoints (list / detail / statistics), inject the service key, normalise
  the resultType XML/JSON toggle, and pair Korean and English title fields.
agent_use_cases:
  - Korean clinical trial discovery by condition or intervention
  - cross-registry deduplication against ClinicalTrials.gov and WHO ICTRP
  - sponsor and institution monitoring for Korea-based research
  - trial-registration statistics for the Korean research landscape
  - retrieval of Korean-language protocol and outcome metadata
access_test:
  command: "curl -sf 'http://apis.data.go.kr/1352159/crisinfodataview/list?serviceKey=${CRIS_DATA_GO_KR_KEY}&resultType=JSON&numOfRows=1&pageNo=1'"
  expected_status: 200
  expected_fields: [resultCode, totalCount, trial_id, scientific_title_en]
last_verified: 2026-07-03
build_priority: low
structure: registry-snapshot
revisions_possible: true
notes: "access_test not executed; requires ${CRIS_DATA_GO_KR_KEY} (free data.go.kr service key). Homepage https://cris.nih.go.kr/ returns 200; single trials resolve at https://cris.nih.go.kr/cris/search/detailSearchEn.do?seq={n}."
---

# Clinical Research Information Service (CRIS)

## Why this source matters

CRIS is the national clinical trial registry of the Republic of Korea, launched in 2010 by the Korea Centers for Disease Control and Prevention (now the Korea Disease Control and Prevention Agency, KDCA) with funding from the Ministry of Health and Welfare. It is the 11th WHO ICTRP Primary Registry and is ICMJE-recognised, so registering with CRIS satisfies journal trial-registration policy, and its records flow into the WHO global trial graph every four weeks. Every record carries a Korean and an English view, which makes CRIS the authoritative English-language window onto Korea-sponsored interventional and observational studies that never register in ClinicalTrials.gov. For an agent building a global pipeline picture, CRIS is the Korea-shaped gap that ClinicalTrials.gov (US) and EU CTIS (EEA) do not cover. Secondary domain: public-health, for the large volume of publicly funded Korean health-services and prevention studies.

## Agent use cases

- Korean clinical trial discovery by condition or intervention
- cross-registry deduplication against ClinicalTrials.gov and WHO ICTRP
- sponsor and institution monitoring for Korea-based research
- trial-registration statistics for the Korean research landscape
- retrieval of Korean-language protocol and outcome metadata

## Join strategy

The source-native primary key is the KCT number (`KCT` followed by digits, e.g. `KCT0008394`), minted by CRIS to identify each registered study and used as `trial_id` in the API. It is not yet in the canonical join-key registry; see Review notes, where it is proposed as a new key alongside the existing `NCT_ID`, `ISRCTN_ID`, `EU_CT_NUMBER`, `EUDRACT_NUMBER`, `WHO_UTN` clinical-registry keys.

The one canonical join key CRIS exposes is `WHO_UTN`: registrants are encouraged to enter the WHO Universal Trial Number as a secondary identifier for retrospective cross-registry linking, so population is sparse and absence does not prove single-registration. CRIS also lets registrants record other registries' identifiers (including ClinicalTrials.gov `NCT_ID`) in its free-form secondary-identifier block, but these are not surfaced as dedicated, reliably-populated API fields, so `NCT_ID` is intentionally left out of `join_keys` pending field-path confirmation (see Review notes).

Recommended pairings: WHO ICTRP as the umbrella graph that already ingests CRIS every four weeks (the least-friction path for global agents); ClinicalTrials.gov and EU CTIS for cross-registry dedup where a shared `WHO_UTN` or secondary `NCT_ID` exists; OpenAlex or Europe PMC to reach associated publications, since CRIS does not itself expose `PMID` or `DOI`.

## Access notes

Two access paths. The human path is the web UI at `https://cris.nih.go.kr/` (Korean) with an English mirror; a single trial resolves at `https://cris.nih.go.kr/cris/search/detailSearchEn.do?seq={n}`. There is no bulk-download of the full corpus.

The programmatic path is the KDCA "임상연구 DB" open API on the Korean public data portal (data.go.kr dataset 3033869):

- **Base:** `GET http://apis.data.go.kr/1352159/crisinfodataview/list`
- **Required params:** `serviceKey` (URL-encoded key issued free on data.go.kr registration), `resultType` (`XML` or `JSON`).
- **Optional params:** `srchWord` (URL-encoded search keyword), `numOfRows` (max 50), `pageNo`.
- Companion endpoints under the same service expose a 70-field detail view and an 18-field registration-statistics view; the list view returns ~16 fields per record including `trial_id`, `scientific_title_kr`/`scientific_title_en`, `date_registration`, `study_type_kr`, `phase_kr`, and `primary_sponsor_kr`.

Gotchas:

- A data.go.kr account and per-dataset application are required before the `serviceKey` works; the key is free but approval and the Korean-language portal are friction for non-Korean users.
- Many payload fields are Korean-only (`_kr` suffix); English fields (`_en`) are populated for records the registrant chose to fill in both languages, so English coverage is partial.
- Records are editorially revised after publication; treat values as revisable and re-pull.
- Development keys are rate-limited (~10,000 calls/day); page politely with `numOfRows=50`.

## MCP / connector notes

No official or community MCP, and standalone value is low: the audience is Korea-scoped, the field set is Korean-language, the licence forbids commercial reuse, and global agents can already reach CRIS records through the WHO ICTRP aggregate. If a connector is built, it should wrap the three `crisinfodataview` endpoints (list, detail, statistics), inject the `serviceKey` from env, normalise the `resultType` XML/JSON toggle, and expose a small surface: `search_trials(keyword, limit, page)`, `get_trial(kct_id)`, `get_registration_stats()`. The better near-term investment is a unified WHO-ICTRP-fronted multi-registry MCP that treats CRIS as one upstream primary registry rather than a bespoke Korea connector.

## Review notes

- Potential new join key for review: `KCT_ID`
  - Entity type: clinical_trial
  - Pattern: `^KCT[0-9]+$` (observed as `KCT` + 7 digits, e.g. `KCT0008394`; bioregistry prefix `kcris`)
  - Other datasets that would use it: WHO ICTRP (ingests CRIS records under their KCT id), ClinicalTrials.gov and EU CTIS (as secondary/related registry ids), Europe PMC and OpenAlex (trial ids cited in Korean-study publications). Recommend PR-ing into `schema/join-keys.yaml` alongside the other national-registry clinical-trial keys.
- New license short name flagged: `KOGL-Type-2` (Korea Open Government License Type 2: attribution required, commercial use prohibited). The data.go.kr listing also references a CC-BY-NC framing for third-party content. No SPDX code exists for KOGL. Recommend registering `KOGL-Type-2` as a canonical short name in SCHEMA.md § License conventions (peers: `OGL-3.0`, `Crown-Copyright`). The non-commercial restriction is the reason `cost: free-non-commercial` was chosen over `free`.
- `NCT_ID` was deliberately excluded from `join_keys`: CRIS accepts it as a free-form secondary identifier but does not expose a dedicated, reliably-populated API field for it. If field-path inspection of the 70-field detail endpoint confirms a stable NCT field, add `NCT_ID` to `join_keys` in a follow-up.
- `join_keys` was kept to the supplied hints (`WHO_UTN`, plus `KCT` flagged as a candidate). `join_key_fields` for `WHO_UTN` points at the secondary-identifier block (`secondary_id`); the exact API field path was not confirmed against a live keyed response (access_test not executed, no service key), so re-verify once a `serviceKey` is available.
- access_test was constructed but not executed: the data.go.kr API is key-gated. The public homepage returns HTTP 200 (verified 2026-07-03).
