---
id: cms-open-payments
name: CMS Open Payments
domain: healthcare-claims
entry_kind: mixed
description: US federal registry of payments and transfers of value from drug and medical device manufacturers and GPOs to physicians, non-physician practitioners, and teaching hospitals.
homepage_url: https://openpaymentsdata.cms.gov/
docs_url: https://openpaymentsdata.cms.gov/about/api
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
bulk_available: true
frequency: annual
lag: "program-year data published the following June (~6 months after year end); refreshed periodically within each cycle"
geography: [USA]
structure: event-log
pit_reconstructable: false
revisions_possible: true
release_lag_days: 180
join_keys:
  - NPI
  - NDC
  - US_STATE_CODE
primary_keys:
  - OPEN_PAYMENTS_RECORD_ID
  - COVERED_RECIPIENT_PROFILE_ID
  - TEACHING_HOSPITAL_ID
  - TEACHING_HOSPITAL_CCN
  - MANUFACTURER_GPO_MAKING_PAYMENT_ID
join_key_fields:
  - join_key: NPI
    fields: [covered_recipient_npi]
  - join_key: NDC
    fields:
      - associated_drug_or_biological_ndc_1
      - associated_drug_or_biological_ndc_2
      - associated_drug_or_biological_ndc_3
      - associated_drug_or_biological_ndc_4
      - associated_drug_or_biological_ndc_5
  - join_key: US_STATE_CODE
    fields: [recipient_state]
mcp_status: mcp-needed-high-value
agent_use_cases:
  - physician conflict-of-interest lookup
  - manufacturer payment footprint by drug or device
  - KOL and prescriber influence mapping
  - payment-to-prescribing signal joins
  - teaching-hospital funding analysis
access_test:
  command: "curl -sf 'https://openpaymentsdata.cms.gov/api/1/datastore/query/93b512a7-7f65-539b-9e20-bbcc535750bd?limit=1'"
  expected_status: 200
  expected_fields: [count, results]
last_verified: 2026-07-02
build_priority: high
---

# CMS Open Payments

## Why this source matters

Open Payments is the US federal transparency database mandated by the Physician Payments Sunshine Act (Affordable Care Act Section 6002) and run by the Centers for Medicare & Medicaid Services (CMS). Drug and medical-device manufacturers and group purchasing organisations (GPOs) must report every payment or transfer of value (meals, travel, consulting fees, research funding, royalties, ownership stakes) made to physicians, non-physician practitioners, and teaching hospitals. Each program year holds tens of millions of records (2024 General Payments alone has ~15.5M rows). Because every recipient carries an NPI and every drug/device can carry an NDC, this is the canonical bridge between industry-payment behaviour and downstream prescribing or claims data, high-value for pharma commercial diligence, conflict-of-interest research, and KOL mapping.

## Agent use cases

- physician conflict-of-interest lookup
- manufacturer payment footprint by drug or device
- KOL and prescriber influence mapping
- payment-to-prescribing signal joins
- teaching-hospital funding analysis

## Join strategy

The load-bearing canonical key is `NPI` (`covered_recipient_npi`), which joins Open Payments to NPPES, Medicare Part D prescriber data, and any NPI-keyed claims source. Drug/device payments expose up to five `NDC` values (`associated_drug_or_biological_ndc_1..5`), joining to openFDA, DailyMed, and RxNorm-derived vocabularies. `recipient_state` maps to `US_STATE_CODE` for state-level rollups.

Source-internal identifiers stay in `primary_keys`: `record_id` (one per payment line), `covered_recipient_profile_id` (CMS-minted physician/NPP profile ID, stable across program years and the natural key for the physician-profile supplement files), `teaching_hospital_id` and `teaching_hospital_ccn`, and `applicable_manufacturer_or_applicable_gpo_making_payment_id` (the manufacturer/GPO payer ID). The manufacturer/GPO payer ID and the teaching-hospital CCN are cross-source candidates flagged in Review notes, they are not yet in the registry.

## Access notes

Modern API is DKAN, not the legacy Socrata endpoint (`89ej-cy77` still exists but is deprecated). Base: `https://openpaymentsdata.cms.gov/api/1/`. List datasets at `/metastore/schemas/dataset/items`; each program year is a separate dataset with its own distribution UUID (e.g. 2024 General Payments distribution is `93b512a7-7f65-539b-9e20-bbcc535750bd`). Query a distribution with `/datastore/query/{distributionId}?limit=&offset=&conditions[0][property]=&conditions[0][value]=&conditions[0][operator]==`; add `download?...&format=csv` for CSV streaming. No auth, no documented rate limit, but each program year must be queried separately (there is no single cross-year table via the API). For full-corpus work, pull the annual ZIP bulk files from `download.cms.gov/openpayments/` (one ZIP per program year with General, Research, Ownership, and profile-supplement CSVs plus a README). Publication cadence is annual (typically June) with within-cycle refreshes, so treat values as revisable and vintage as of the publication cycle date embedded in the filename.

## MCP / connector notes

No dedicated Open Payments MCP found. An adjacent community server (`github.com/openpharma-org/medicare-mcp`) wraps CMS Medicare provider/claims data via Socrata but does not target the DKAN Open Payments API. High value: three-plus healthcare entries (NPPES, Medicare prescriber, openFDA) would want the same NPI/NDC-joined payment surface. Suggested MCP surface: `search_payments(npi | manufacturer | drug | year)`, `get_recipient_profile(profile_id)`, `payments_by_manufacturer(id, year)`, `summarize_recipient(npi)`, `list_program_years`. The connector must abstract over the per-program-year distribution UUIDs (resolve year -> distribution from the metastore), page the DKAN datastore, and normalise the wide 90-plus-column schema down to the load-bearing fields.

## Review notes

Potential new join key for review: MANUFACTURER_GPO_ID
  Entity type: reporting_entity (drug/device manufacturer or GPO)
  Pattern: CMS-minted numeric-ish ID in `applicable_manufacturer_or_applicable_gpo_making_payment_id`; stable across Open Payments program years
  Other datasets that would use it: internal to Open Payments (general, research, ownership files); limited external reuse, so likely low cross-source value

Potential new join key for review: CCN (CMS Certification Number)
  Entity type: cms_certified_provider (hospital / teaching hospital / facility)
  Pattern: 6-character CMS provider number in `teaching_hospital_ccn`
  Other datasets that would use it: broad CMS provider ecosystem (Provider of Services file, Hospital Compare, Medicare cost reports, Care Compare). Genuine cross-source utility; stronger new-key candidate than the manufacturer ID.

Domain call: filed under `healthcare-claims` alongside `nppes-npi` (the NPI minting registry) since NPI is the primary bridge; it is a payment-transparency registry rather than claims per se. `entry_kind: mixed` because the source spans dated payment event-logs (General/Research payments) and registry-style profile supplements (physician and teaching-hospital profiles). License is US-Government-Public-Domain (federal work, 17 USC 105); CMS publishes with no redistribution restriction.
