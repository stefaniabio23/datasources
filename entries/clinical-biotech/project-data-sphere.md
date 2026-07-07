---
id: project-data-sphere
name: Project Data Sphere
domain: clinical-biotech
entry_kind: corpus
description: Free digital library of de-identified, patient-level data from academic and industry Phase II-III oncology clinical trials.
homepage_url: https://data.projectdatasphere.org/
docs_url: https://data.projectdatasphere.org/projectdatasphere/html/resources/PDF/HOW_TO_ACCESS_AND_DOWNLOAD_DATA
type:
  - bulk-download
  - web-ui
  - database
auth_required: account-required
cost: free-with-registration
license: PDS-Data-Sharing-Agreement
bulk_available: true
frequency: irregular
lag: "historical; datasets contributed after trial completion"
geography: [global]
join_keys:
  - NCT_ID
primary_keys:
  - PDS_UNIQUE_DATASET_ID
  - PDS_TRIAL_ID
join_key_fields:
  - join_key: NCT_ID
    fields: [trial-summary.nct-number]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - external control arm construction
  - historical comparator retrieval
  - patient-level survival analysis
  - trial result reanalysis
  - oncology outcomes benchmarking
last_verified: 2026-07-03
build_priority: low
notes: "Data access gated behind an application and a signed Data Sharing Agreement; no public no-auth data endpoint, so access_test omitted."
---

# Project Data Sphere

## Why this source matters

Project Data Sphere (PDS) is a free web platform run by Project Data Sphere, LLC, an initiative of the CEO Roundtable on Cancer (launched 2014). It hosts de-identified, patient-level data (individual patient data, IPD) from historical academic and industry Phase II-III cancer clinical trials, mostly control/comparator arms. Researchers at life-science companies, hospitals, and independent investigators can access every dataset at no cost after an approved application, with no per-study research proposal required. For agents building external control arms or reanalysing oncology outcomes, PDS is one of the few sources of genuine patient-level trial records rather than aggregate summaries.

## Agent use cases

- external control arm construction
- historical comparator retrieval
- patient-level survival analysis
- trial result reanalysis
- oncology outcomes benchmarking

## Join strategy

PDS exposes `NCT_ID` as the single canonical bridge: each trial summary carries its ClinicalTrials.gov registration number, which links a PDS dataset out to `clinicaltrials-gov`, `aact`, `open-targets`, and any other source keyed on `NCT_ID`. That join is the primary way to enrich a downloaded PDS dataset with protocol, sponsor, arm, and endpoint metadata.

Source-internal identifiers are not cross-source keys: each dataset has a PDS Unique Dataset ID (needed for the SAS/CAS API path) and a PDS trial identifier. These live in `primary_keys`, used for direct PDS lookups, not joins. There is no canonical PDS study-id key in the registry and none is proposed, `NCT_ID` already covers the cross-source link (see Review notes for the "study id" hint).

## Access notes

Access requires an account: submit a short application describing your background and agree to the Terms of Use / Online Service User Agreement, then sign the Data Sharing Agreement. Once approved, all datasets are available. Trial summaries link to SAS-encoded datasets you can either download for use in your own statistical software or analyse in-platform via the bundled SAS tools (VDMML, LSAF). Datasets are also reachable through the platform's SAS CAS layer (including a Python connection) once you have the Unique Dataset ID from the dataset's Access Data page.

No public, unauthenticated data API exists, so no `access_test` is included. To check freshness, browse the Access Data catalogue at `https://data.projectdatasphere.org/projectdatasphere/html/content/102` and note newly listed trials; the platform grows irregularly as sponsors contribute completed trials.

## MCP / connector notes

No MCP exists. Value is capped by the access model: an application plus a signed Data Sharing Agreement gates all data, and the analytics API is SAS/CAS behind that auth wall. A useful connector would (1) list/search the trial catalogue and surface each dataset's `NCT_ID` and Unique Dataset ID, and (2) wrap authenticated SAS CAS/Python pulls of a named dataset. Both steps require a human-completed DSA first, so autonomous end-to-end use is limited; classified low-value until an agent-friendly access path exists.

## Review notes

- New license short name candidate: `PDS-Data-Sharing-Agreement`. PDS data is governed by a custom Online Service User Agreement plus a signed Data Sharing Agreement (`https://data.projectdatasphere.org/documents/resources_data_sharing_agreement.pdf`); no SPDX code applies. Confirm the canonical short name before merge.
- Join-key hint "study id" maps to PDS-internal identifiers (Unique Dataset ID / trial id), which are source-native and placed in `primary_keys`. Not proposed as a new canonical join key: it has no demonstrated cross-source utility and `NCT_ID` already provides the external bridge.
- `join_key_fields` path for `NCT_ID` (`trial-summary.nct-number`) is descriptive: NCT numbers appear in each trial's summary metadata on the platform, not in a documented JSON payload (no public API). Verify the exact field name if an authenticated schema becomes available.
