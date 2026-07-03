---
id: cms-medicare-part-d
name: CMS Medicare Part D Prescribers
domain: healthcare-claims
entry_kind: panel
description: CMS annual summary of prescription drugs prescribed to Original Medicare Part D beneficiaries, aggregated at three grains (by provider NPI, by provider and drug, by geography and drug) with claim counts, day supply, drug cost, and beneficiary counts.
homepage_url: https://data.cms.gov/provider-summary-by-type-of-service/medicare-part-d-prescribers
docs_url: https://data.cms.gov/resources/medicare-part-d-prescribers-by-provider-and-drug-data-dictionary
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "not published; anonymous data-api, polite paging expected (size/offset)"
bulk_available: true
frequency: annual
lag: "~18-24 months (data year 2024 released mid-2026)"
geography: [USA]
structure: panel
pit_reconstructable: false
revisions_possible: true
join_keys:
  - NPI
  - FIPS
  - US_STATE_CODE
primary_keys:
  - NPI
join_key_fields:
  - join_key: NPI
    fields:
      - Prscrbr_NPI
      - PRSCRBR_NPI
  - join_key: FIPS
    fields:
      - Prscrbr_State_FIPS
      - Prscrbr_Geo_Cd
  - join_key: US_STATE_CODE
    fields:
      - Prscrbr_State_Abrvtn
mcp_status: mcp-exists
mcp_maturity: experimental
mcp_package:
  - "github.com/openpharma-org/medicare-mcp"
mcp_notes: >
  Community MCP (medicare-mcp) wraps CMS provider datasets including Part D
  prescribers via search_prescribers; Node/TypeScript, not published to npm/pypi,
  low adoption (~6 stars). A stronger connector would front the three grains and
  add a drug-name to RxNorm/NDC resolver, since the Part D files carry only
  free-text brand and generic names.
agent_use_cases:
  - prescriber-level drug utilization lookup
  - opioid and antibiotic prescribing benchmarking
  - drug-cost trend analysis by provider or state
  - specialty and geographic prescribing comparison
  - Medicare Part D spend attribution by NPI
access_test:
  command: "curl -sf 'https://data.cms.gov/data-api/v1/dataset/9552739e-3d05-4c1b-8eff-ecabf391e2e5/data?size=1'"
  expected_status: 200
  expected_fields: [Prscrbr_NPI, Brnd_Name, Gnrc_Name, Tot_Clms, Tot_Drug_Cst]
last_verified: 2026-07-02
build_priority: medium
---

# CMS Medicare Part D Prescribers

## Why this source matters

The Centers for Medicare & Medicaid Services publishes annual, de-identified summaries of every prescription drug paid for under the Medicare Part D program, derived from CMS administrative claims in the Chronic Condition Data Warehouse. The source is three linked public-use files: by Provider (one row per prescribing NPI with totals plus opioid, antibiotic, antipsychotic, and beneficiary-demographic breakouts), by Provider and Drug (one row per NPI plus brand and generic drug name), and by Geography and Drug (national and state rollups per drug). For an agent, this is the authoritative US answer to "who prescribed what, how much did it cost Medicare, and where", covering roughly the entire Medicare Part D fee-for-service population. Secondary domains: public-health (opioid and antibiotic prescribing surveillance) and government-open-data (CMS open data, public domain). The sibling source Medicare Physician & Other Practitioners covers the Part B / procedure side (HCPCS-coded services) and is a separate entry.

## Agent use cases

- prescriber-level drug utilization lookup
- opioid and antibiotic prescribing benchmarking
- drug-cost trend analysis by provider or state
- specialty and geographic prescribing comparison
- Medicare Part D spend attribution by NPI

## Join strategy

`NPI` is the load-bearing join key. Both the by-Provider and by-Provider-and-Drug files key every row on the prescriber's National Provider Identifier (`Prscrbr_NPI` / `PRSCRBR_NPI`), which joins directly to NPPES, Open Payments, the Part B practitioner files, and any other NPI-indexed source. Geography joins on `FIPS` (state FIPS in `Prscrbr_State_FIPS`, and `Prscrbr_Geo_Cd` in the geography file) and on `US_STATE_CODE` (`Prscrbr_State_Abrvtn`).

The drug dimension is the gap. The Part D files identify drugs only by free-text `Brnd_Name` and `Gnrc_Name`; they carry no `NDC`, no `RXNORM_CUI`, and no `HCPCS`. To join the drug axis to a coded source (openFDA NDC directory, RxNorm, DrugBank), an agent must resolve the brand/generic name to a code externally. `RXNORM_CUI` and `NDC` both already exist in the registry, but neither is native here, so they are deliberately not listed in `join_keys`; see Review notes. `HCPCS` applies to the Part B practitioner file, not to Part D.

Common pairings: NPPES (provider identity and taxonomy for each `Prscrbr_NPI`), Open Payments (industry payments to the same NPIs), openFDA / RxNorm (drug-name resolution to codes), and Medicare Physician & Other Practitioners (the HCPCS-coded Part B counterpart at the same NPI grain).

## Access notes

Hit the JSON data-api first: `https://data.cms.gov/data-api/v1/dataset/{datasetUUID}/data?size=1`. It is anonymous, returns JSON, and supports `size` and `offset` paging plus column filters. Each data year is a distinct dataset UUID, discoverable from the catalog at `https://data.cms.gov/data.json` (filter `dataset[].title` for "Medicare Part D Prescribers"). The access test uses the by-Provider-and-Drug data year 2024 UUID `9552739e-3d05-4c1b-8eff-ecabf391e2e5`; the by-Provider DY2024 UUID is `14d8e8a9-7e9b-4370-a044-bf97c46b4b44` and by-Geography-and-Drug DY2024 is `c8ea3f8e-3a09-4fea-86f2-8902fb4b0920`. Values arrive as strings even for numeric columns; cast client-side.

For bulk work, each file also has a `text/csv` download under `data.cms.gov/sites/default/files/...`; the by-Provider-and-Drug file is the large one (tens of millions of rows per year). Prefer the CSV for full-year pulls and the data-api for targeted NPI or drug lookups.

Freshness: annual. Data year 2024 was published mid-2026, an ~18-24 month lag. CMS restates prior years across release years (the by-Provider 2022 file was republished in late 2025 as a new version), so `revisions_possible` is true and there is no point-in-time vintage service; pin the dataset UUID and record the release date for reproducibility.

License: CMS public-use files are US Government works, free to use and redistribute with no registration. The AMA CPT copyright caveat that attaches to the Part B / physician PUF does not apply here, because Part D files contain no CPT/HCPCS codes. Small cells are suppressed: counts of 10 or fewer beneficiaries are withheld and flagged by the `*_Sprsn_Flag` columns.

## MCP / connector notes

An experimental community MCP exists: `medicare-mcp` (openpharma-org) exposes a `search_prescribers` method over the Part D data alongside physician, hospital, spending, and formulary tools. It wraps the Socrata/data-api layer, is Node/TypeScript, is not published to npm or pypi, and has low adoption (~6 stars), so treat it as a reference implementation rather than a dependency.

A stronger connector should expose: `get_prescriber(npi, year)`, `search_prescriber_drug(npi|drug, year)`, `top_drugs_by_geography(state|national, year)`, and `prescribing_trend(npi|drug, years)`. The must-abstract parts are the per-year dataset-UUID lookup (resolve a data year to its UUID via `data.json`), the all-strings JSON typing, the suppression flags, and, highest value, a drug-name to `RXNORM_CUI` / `NDC` resolver so the drug axis becomes joinable.

## Review notes

- Drug identifiers: this source exposes drugs only as free-text `Brnd_Name` / `Gnrc_Name`. `RXNORM_CUI` and `NDC` (both already in `schema/join-keys.yaml`) are therefore NOT listed in `join_keys`, because they are not native fields; resolving them requires an external name-to-code crosswalk. Flagging per the join-key hints (NDC, RXNORM_CUI) so a reviewer knows the omission is intentional, not an oversight. No new canonical keys are proposed.
- `HCPCS` (in the hints as "Part D/B") belongs to the sibling source Medicare Physician & Other Practitioners (Part B, HCPCS-coded services), not to Part D Prescribers. Recommend a separate entry (`cms-medicare-physician-other-practitioners`) for that dataset rather than stretching this one.
- Entry scope: this card covers all three Part D sub-datasets (by Provider, by Provider and Drug, by Geography and Drug) as one source per the one-entry-per-provider rule. `entry_kind: panel` and `structure: panel` reflect the provider/drug-by-year shape; the by-Geography file is the aggregated cross-section of the same claims.
- License short name `US-Government-Public-Domain` follows SCHEMA.md; the AMA CPT restriction noted in CMS terms applies only to the CPT-coded Part B PUF, not here.
