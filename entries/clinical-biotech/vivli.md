---
id: vivli
name: Vivli
domain: clinical-biotech
entry_kind: registry
description: Independent non-profit repository and secure research environment for de-identified individual participant-level data (IPD) from completed clinical trials, with a public metadata search index and controlled access to the underlying datasets.
homepage_url: https://vivli.org/
docs_url: https://vivli.org/resources/
type:
  - web-ui
  - database
auth_required: dars-or-equivalent
cost: free-with-registration
license: Vivli-Data-Use-Agreement
rate_limit: "not applicable; public surface is the metadata search UI, data delivered inside a gated secure research environment after approval"
bulk_available: false
frequency: "continuous; new studies listed as sponsors and contributors add them"
lag: "studies are completed trials, typically shared years after primary completion once results are published or a sharing commitment matures"
geography: [global]
join_keys:
  - NCT_ID
  - DOI
primary_keys:
  - VIVLI_STUDY_ID
  - SPONSOR_STUDY_ID
join_key_fields:
  - join_key: NCT_ID
    fields: ["nctId", "secondaryIds (ClinicalTrials.gov registration)"]
  - join_key: DOI
    fields: ["doi (DataCite study-package DOI)"]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - discover which completed trials have shareable IPD
  - resolve a trial to its IPD data package via NCT or DOI
  - locate sponsor datasets for a drug or condition
  - scope an IPD meta-analysis feasibility check
  - cross-reference registry trials against available raw participant data
last_verified: 2026-07-03
build_priority: medium
notes: "Metadata (study listings, DOIs, registration IDs) is free to search without an account. Obtaining participant-level data requires a Vivli account, a submitted research proposal, Independent Review Panel approval where the contributor requires it, and a signed Data Use Agreement; data are then analysed only inside Vivli's Azure-based secure research environment. Some data requests may incur platform or hosting fees depending on the contributor and funding; access itself is not a paid subscription. No confirmed public JSON API, so access_test is omitted."
---

# Vivli

## Why this source matters

Vivli is an independent, non-profit global data-sharing platform for individual participant-level data (IPD) from completed clinical trials, run from the organisation that grew out of the Multi-Regional Clinical Trials Center (MRCT Center) at Brigham and Women's Hospital and Harvard, and funded by a consortium (Arnold Ventures, Doris Duke, Helmsley Charitable Trust, PhRMA, and others). It combines three things: a public metadata search index over 8,000+ trials covering roughly 5.2 million participants, a controlled data-request workflow, and an Azure-based secure research environment (SOC 2 Type 2) where approved researchers analyse the raw data. Its 55+ members include major pharma (Pfizer, GSK, Roche, Novartis, AbbVie) and academic institutions, making it the largest cross-sponsor pooling point for de-identified trial IPD. For an agent, Vivli is the bridge between a trial registry entry and the actual patient-level dataset behind it: the metadata layer is queryable and joinable, the data layer is gated. Secondary relevance to `academic` (each data package carries a citable DataCite DOI and produces publications) and `public-health` (pooled IPD for meta-analysis).

## Agent use cases

- discover which completed trials have shareable IPD
- resolve a trial to its IPD data package via NCT or DOI
- locate sponsor datasets for a drug or condition
- scope an IPD meta-analysis feasibility check
- cross-reference registry trials against available raw participant data

## Join strategy

Two registry-backed keys are exposed in the public metadata layer. `NCT_ID` links each listed study back to its ClinicalTrials.gov registration, so Vivli pairs directly with `clinicaltrials-gov`, `aact`, `who-ictrp`, and any registry-anchored source to answer "does raw IPD exist for this trial?". `DOI` is minted per study data package by DataCite at the time metadata appears in Vivli search (with a parent-child DOI structure for the datasets and documents inside a package), so Vivli pairs with `openalex`, Crossref, and any DOI-anchored scholarly source to connect a dataset to its citations and derived publications.

Source-internal identifiers stay out of the canonical set: Vivli mints its own study identifier for each package (`VIVLI_STUDY_ID`) and surfaces the contributor's own protocol/study code (`SPONSOR_STUDY_ID`); both are useful for resolving within Vivli but are not cross-source canonical keys. The requester's "study id" hint maps to these native fields rather than to a registry key. See Review notes for a possible generic sponsor-protocol-id candidate. Studies frequently also list secondary registrations (EudraCT / EU CT, ISRCTN); these were not confirmed as consistently structured fields, so only `NCT_ID` is claimed here to avoid overstating.

## Access notes

The public surface is the search app at `https://search.vivli.org/` (a JavaScript single-page app), offering keyword, PICO, and quick-study-lookup search over trial metadata; searching and browsing study cards, DOIs, and registration IDs needs no account. There is no confirmed public no-auth JSON API for the metadata (re3data references an API doc, but that is re3data's own harvesting API, not a documented Vivli endpoint), so an executable `curl` field-contract could not be constructed; `access_test` is omitted. Re-verify freshness and coverage by loading the search app and checking the current study count and newest listed studies.

To reach participant-level data: (a) register a Vivli account, (b) submit a research proposal, (c) pass Independent Review Panel review where the data contributor requires it, and (d) sign the Data Use Agreement (currently DUA v1.4, March 2025). Approved data are then accessible only inside the secure research environment; there is generally no bulk export of raw IPD out of the enclave. Metadata access is free; specific data requests may carry platform or hosting fees depending on the contributor and the researcher's funding, so `cost: free-with-registration` reflects the access model rather than a guarantee of zero cost for every request.

## MCP / connector notes

No MCP exists. Value is bounded by the controlled-access model: only the metadata layer is programmatically useful, and Vivli does not publish a documented public API, so a connector today would scrape the search SPA. A useful low-value connector surface would be `search_studies` (keyword / PICO), `get_study_metadata` (returning NCT, DOI, sponsor id, condition, intervention, data-availability status), and `resolve_by_nct` / `resolve_by_doi` to answer the one high-signal question an agent asks Vivli: does shareable IPD exist for this trial, and under what request path. The connector must not attempt to bypass the DUA or reach the secure research environment; it abstracts discovery only, not data extraction.

## Review notes

- License: governed by the Vivli Data Use Agreement (custom terms, currently v1.4, March 2025), which has no SPDX code. Used canonical short name `Vivli-Data-Use-Agreement`; this is not yet in the `SCHEMA.md § License conventions` known-cases list. Flag for review.
- `auth_required: dars-or-equivalent` covers the account + research-proposal + IRP + DUA + secure-enclave flow, matching the requester's "Controlled access (dars-or-equivalent)" note.
- `cost: free-with-registration`: metadata search is free and account-gated data request is free to initiate, but some requests incur platform/hosting fees. `paid` would overstate; nuance documented in Access notes and `notes`.
- Requester join-key hints reconciled:
  - `NCT_ID` — in registry, exposed in study metadata, included.
  - "study id" — maps to Vivli's own `VIVLI_STUDY_ID` and the contributor's `SPONSOR_STUDY_ID`; neither is a canonical registry key. Placed in `primary_keys`. Potential new join key for review:
    - Proposed key: `SPONSOR_PROTOCOL_ID`
    - Entity type: `clinical_trial` (sponsor-assigned protocol / study code)
    - Pattern: free-form sponsor-specific string (no stable regex; e.g. company protocol codes)
    - Other datasets that would use it: `clinicaltrials-gov` (org study id / secondary ids), `who-ictrp`, `eu-ctis`, sponsor pipeline disclosures. Cross-source utility is real but the value space is unnormalised, so flagged rather than added.
  - `DOI` — added (not in the original hint): Vivli assigns a DataCite DOI per study data package, a genuine cross-source join to scholarly sources.
- `type`: `web-ui` (search SPA) + `database` (secure research environment). No `rest-api` claimed because no public documented API was confirmed.
- `bulk_available: false`: raw IPD is analysed inside the enclave and not offered as a bulk download.
- `access_test` omitted per skill guidance: the metadata surface is a JS SPA with no confirmed field-stable JSON endpoint, and the data surface is gated.
