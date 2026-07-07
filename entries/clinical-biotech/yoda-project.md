---
id: yoda-project
name: YODA Project (Yale Open Data Access)
domain: clinical-biotech
entry_kind: registry
description: Yale-based data-sharing intermediary that brokers controlled access to individual participant data (IPD) and clinical study reports from 500+ industry-sponsored clinical trials via a formal data-request and DUA process.
homepage_url: https://yoda.yale.edu/
type:
  - web-ui
auth_required: dars-or-equivalent
cost: free-with-registration
license: YODA-Data-Use-Agreement
rate_limit: "not applicable; no public API. Trial catalogue is browsable on the web; participant-level data is delivered only after request approval into a secure analysis environment"
bulk_available: false
frequency: "irregular; new trials and data partners added over time (J&J, Medtronic, Kenvue, QMUL, SI-BONE)"
lag: "historical; de-identified trial datasets are released years after study completion, after sponsor onboarding and de-identification"
geography: [global]
join_keys:
  - NCT_ID
primary_keys:
  - YODA_TRIAL_ID
  - SPONSOR_PROTOCOL_NUMBER
join_key_fields:
  - join_key: NCT_ID
    fields: ["trial catalogue NCT number (per-trial listing on yoda.yale.edu)"]
mcp_status: requires-scraping
agent_use_cases:
  - discover which sponsor trials have shareable IPD
  - locate a specific trial's dataset by NCT number for a meta-analysis
  - scope a secondary-analysis or reproducibility proposal
  - identify clinical study reports available on request
  - build a request-application shortlist across therapeutic areas
last_verified: 2026-07-03
build_priority: low
notes: "Access is gated: submit an online research proposal, complete a conflict-of-interest disclosure, accept the Data Use Agreement (DUA training video), and pass YODA steering-committee / due-diligence review. Approved data is analysed inside a secure environment; there is no bulk export and no programmatic API. Registration and access are free of charge."
---

# YODA Project (Yale Open Data Access)

## Why this source matters

The Yale Open Data Access (YODA) Project, run by the Yale Center for Outcomes Research and Evaluation (CORE), is a trusted intermediary that brokers responsible sharing of participant-level clinical trial data from industry sponsors. Full jurisdictional control of the data is transferred from the sponsor to YODA, which then reviews and grants access to external researchers for meta-analysis, replication, and secondary analysis. As of 2026 it catalogues 500+ trials (the bulk from Johnson & Johnson, plus Medtronic, Kenvue, QMUL, and SI-BONE) spanning oncology, cardiovascular, diabetes, ADHD, and other therapeutic areas, and has supported 200+ downstream publications. For an agent, YODA is not a queryable dataset but a discovery-and-access registry: it answers "does de-identified individual participant data (IPD) exist for this trial, and how do I request it?" This is the primary open channel for J&J IPD. Secondary relevance to `public-health` (evidence synthesis) but the source is clinical trial data, so `clinical-biotech` is primary.

## Agent use cases

- discover which sponsor trials have shareable IPD
- locate a specific trial's dataset by NCT number for a meta-analysis
- scope a secondary-analysis or reproducibility proposal
- identify clinical study reports available on request
- build a request-application shortlist across therapeutic areas

## Join strategy

The one canonical join key YODA exposes is `NCT_ID`: each trial in the browsable catalogue is identified by its ClinicalTrials.gov registration number, which is the reliable bridge to trial-level metadata (AACT / ClinicalTrials.gov), results, and downstream sources. Pair on `NCT_ID` with `clinicaltrials-gov` and `aact` to enrich a YODA trial with design, arms, outcomes, and sponsor context before drafting a data request, and with `who-ictrp` for cross-registry coverage.

Source-internal identifiers stay out of the canonical set: YODA assigns its own internal trial/dataset identifier, and each trial also carries the sponsor's protocol number (e.g. a J&J study number). These are useful for locating a specific dataset within the portal but have weak cross-source utility, so they live in `primary_keys` (`YODA_TRIAL_ID`, `SPONSOR_PROTOCOL_NUMBER`), not `join_keys`. The requester hint "study id" maps to these source-native fields rather than to a canonical registry key (see Review notes).

## Access notes

There is no public API and no bulk download. The trial catalogue at `yoda.yale.edu` is browsable without login and is the only surface an agent can hit today to enumerate available trials and read their NCT numbers, therapeutic areas, and data-availability status. Everything below that is gated.

To obtain data: (a) submit an online data-request application with a research proposal, (b) complete a conflict-of-interest disclosure, (c) view the Data Use Agreement training and accept the DUA, then (d) pass review by the YODA steering committee and a due-diligence assessment. Approved requesters analyse the de-identified participant-level data inside a secure hosted analysis environment under the DUA (with data-expiration terms); the data is not exported to the requester. Registration and access are free.

Re-verify freshness by checking the current trial count and partner list on the catalogue page at `https://yoda.yale.edu/` (504+ trials as of the 2026-07-03 check).

## MCP / connector notes

No MCP exists and the data itself cannot be delivered by one: participant-level access is behind a manual application, committee review, and a secure analysis environment, so no connector can bypass the DUA. The only programmatically reachable surface is the public trial catalogue, which has no documented API and would require browser automation / scraping to enumerate. A low-value connector could front discovery only, `search_trials` (by NCT, sponsor, therapeutic area, data-availability status) and `get_trial_metadata` over the catalogue, plus a `describe_request_process` helper. It would stop at the request boundary; it cannot fetch IPD. Hence `mcp-needed-low-value` in spirit, recorded as `requires-scraping` because even the catalogue exposes no API.

## Review notes

- License: governed by the YODA Project Data Use Agreement (no SPDX code, no fixed public license string). Used canonical short name `YODA-Data-Use-Agreement`; this is not in the `SCHEMA.md § License conventions` known-cases list. Flag for review.
- `auth_required: dars-or-equivalent` per the requester note and the application + committee-review + DUA flow (matches the physionet controlled-access pattern).
- `cost: free-with-registration`: YODA charges no access fee; the barrier is the application and DUA, not payment.
- `entry_kind: registry`: the browsable, agent-facing artifact is a catalogue where each row is one trial (a canonical thing). The delivered data is patient-level, but that surface is gated and not modeled here. `mixed` was considered (catalogue + IPD datasets) but the discoverable layer is registry-shaped.
- Requester join-key hints reconciled:
  - `NCT_ID` — in registry, native to each catalogue entry, included.
  - "study id" — source-native, NOT a canonical registry key. Placed in `primary_keys` as `YODA_TRIAL_ID` and `SPONSOR_PROTOCOL_NUMBER`. A generic sponsor/protocol study identifier has low cross-source join value (no shared namespace across sponsors), so it is not proposed as a new canonical key; if a future entry needs it, a `SPONSOR_PROTOCOL_NUMBER` key could be considered but is likely too heterogeneous to standardise.
- `access_test` omitted: no public no-auth structured endpoint exists (catalogue is web-ui, data is gated). Freshness check documented in Access notes.
- `type` limited to `web-ui`: no `rest-api`, `bulk-download`, or `database` access is offered to requesters; the secure analysis environment is not a modeled access mode here.
