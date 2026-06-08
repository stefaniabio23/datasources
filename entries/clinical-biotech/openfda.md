---
id: openfda
name: openFDA
domain: clinical-biotech
description: US FDA Elasticsearch-backed public API and bulk downloads covering drug adverse events, product labeling, NDC directory, recalls, device safety reports, and food enforcement.
homepage_url: https://open.fda.gov/
docs_url: https://open.fda.gov/apis/
type:
  - rest-api
  - bulk-download
auth_required: api-key-free
cost: free
license: CC0
rate_limit: "240 req/min and 1,000 req/day anonymous per IP; 240 req/min and 120,000 req/day with free API key"
bulk_available: true
frequency: "varies by endpoint; many refreshed weekly, some daily"
lag: "weeks to months for adverse-event reports (FAERS quarterly ingestion); days for recalls and labels"
geography: [USA]
join_keys:
  - NDC
  - RXNORM_CUI
  - MEDDRA_TERM
  - NCT_ID
primary_keys:
  - SAFETYREPORTID
  - FDA_APPLICATION_NUMBER
  - SPL_SET_ID
  - SPL_ID
  - PRODUCT_NDC
  - PRODUCT_ID
  - RECALL_NUMBER
  - K_NUMBER
  - PMA_NUMBER
  - MDR_REPORT_KEY
  - UNII
join_key_fields:
  - join_key: NDC
    fields: [product_ndc, package_ndc, openfda.product_ndc, openfda.package_ndc, patient.drug.openfda.product_ndc, patient.drug.openfda.package_ndc, packaging.package_ndc]
  - join_key: RXNORM_CUI
    fields: [openfda.rxcui, patient.drug.openfda.rxcui]
  - join_key: MEDDRA_TERM
    fields: [patient.reaction.reactionmeddrapt, patient.drug.drugindication]
  - join_key: NCT_ID
    fields: [clinical_studies]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cmanohar/mcp-openfda
  - github.com/pipeworx-io/mcp-openfda
  - npmjs.com/package/@cyanheads/openfda-mcp-server
  - pypi.org/project/openfda-mcp-server
mcp_notes: >
  At least four community MCPs (cmanohar, pipeworx-io, cyanheads, BACH-AI-Tools). None official.
  Most expose drug adverse events, labels, and recalls; device and food endpoints less consistently
  covered. Ideal surface: search_adverse_events, get_label, list_recalls, lookup_ndc, device_events.
agent_use_cases:
  - drug adverse-event signal mining
  - product label and indication lookup
  - drug and device recall monitoring
  - NDC to drug-concept resolution
  - post-market device safety surveillance
access_test:
  command: "curl -sf 'https://api.fda.gov/drug/label.json?limit=1'"
  expected_status: 200
  expected_fields: [meta, results]
last_verified: 2026-06-08
build_priority: medium
---

# openFDA

## Why this source matters

openFDA is the FDA's public Elasticsearch-backed API and bulk-download surface for federal health and safety datasets: drug adverse events (FAERS), product labeling (SPL), NDC directory, drugs@FDA approvals, recall enforcement reports, drug shortages, device adverse events (MAUDE), device classifications, 510(k) and PMA clearances, UDI, food enforcement, and animal/veterinary adverse events. Free, CC0, no auth required for low-volume use. The canonical machine-readable entry point to FDA regulatory data, and the primary source for post-market drug and device safety signals. Secondary relevance to `public-health` for surveillance and to `healthcare-claims` for drug-product code resolution.

## Agent use cases

- drug adverse-event signal mining
- product label and indication lookup
- drug and device recall monitoring
- NDC to drug-concept resolution
- post-market device safety surveillance

## Join strategy

Drug records expose `NDC` (National Drug Code) as the primary US drug-product identifier, plus `RXNORM_CUI` in the `openfda` enrichment block (`rxcui`) for joining to RxNorm-based clinical terminologies. Adverse-event reports tag reactions with `MEDDRA_TERM` (`reactionmeddrapt`) and, less consistently, indications with MedDRA Lowest-Level Terms. Drug label records frequently carry `NCT_ID` references in trial-history fields, useful for crosswalks back to ClinicalTrials.gov. Substance-level joins use `UNII` (FDA's Unique Ingredient Identifier) which appears across drug, food, and tobacco endpoints.

openFDA-internal identifiers (`application_number` for Drugs@FDA, `report_number` for FAERS, `k_number` and `pma_number` for device clearances, `recall_number` for enforcement reports) are intentionally outside the canonical registry; use them for direct openFDA lookups, not cross-source joins.

Common pairings: RxNorm and DrugBank (NDC and RxCUI to drug concept), ClinicalTrials.gov (NCT to trial protocol), DailyMed (SPL set ID for full label text), CMS NPPES (provider context for prescriber-side analysis).

## Access notes

Hit `https://api.fda.gov/<noun>/<endpoint>.json?search=...&limit=...` where noun is `drug`, `device`, `food`, `animalandveterinary`, or `tobacco`. HTTPS only. No auth works for casual use (1,000 req/day per IP), but anything iterative needs a free API key (`?api_key=...`, 120K req/day). Higher quotas via `open@fda.hhs.gov`.

Search syntax is Lucene-style (`search=patient.reaction.reactionmeddrapt:"headache"+AND+receivedate:[20200101+TO+20231231]`). Use `count=` to histogram a field instead of returning records. Pagination via `skip=` and `limit=` (max `limit=1000`, max `skip=25000`); for deeper scans, narrow by date range or use the bulk downloads.

Bulk: zipped JSON files mirroring API response shape at `https://download.open.fda.gov/`, index at `https://api.fda.gov/download.json`. No incremental diffs, refresh requires full re-download per endpoint. Large endpoints (FAERS adverse events, MAUDE device events) are sharded into many small files.

Gotchas:

- FAERS data is voluntary and unverified; counts are signals, not incidence.
- The `openfda` enrichment block (containing `rxcui`, `unii`, `pharm_class_*`) is best-effort and not present on every record.
- MedDRA Preferred Terms only; no LLT-to-PT rollup in the API.
- Adverse-event ingestion lags actual reports by months; recalls and labels are fresher.

## MCP / connector notes

Several community MCPs exist; none official. `cmanohar/mcp-openfda` and `pipeworx-io/mcp-openfda` (both GitHub) and `@cyanheads/openfda-mcp-server` (npm) are the most discoverable. Coverage skews toward drug adverse events, labels, and recalls; device and food endpoints are less consistently exposed. None standardise response trimming or query-budget tracking for FAERS pagination. An ideal connector surface would expose `search_adverse_events`, `get_label`, `list_recalls`, `lookup_ndc`, `device_events`, with built-in Lucene query helpers, automatic API-key injection, and bulk-vs-API routing for analyses over the 25K-record skip ceiling.

## Review notes

- Potential new join key for review: `UNII`. Entity type: `chemical_substance`. Pattern: `^[A-Z0-9]{10}$` (10-char alphanumeric). Other datasets that would use it: DailyMed, GSRS (Global Substance Registration System), RxNorm, USDA FoodData Central. FDA's canonical substance identifier; worth adding if substance-level joins across FDA and food sources are in scope. Listed in YAML `join_keys` on the assumption it will be promoted; remove if the project prefers strict pre-registration.
- Potential new join key for review: `FDA_APPLICATION_NUMBER` (NDA/ANDA/BLA). Entity type: `drug_approval`. Pattern: `^(NDA|ANDA|BLA)[0-9]{6}$` or 6-digit bare form. Other datasets that would use it: Drugs@FDA, Orange Book, Purple Book, Medicare drug pricing. Not flagged in YAML; mentioned here as a candidate.
- `geography: [USA]` used as a short region label; ISO_3 would be `USA`. Confirm preferred convention (other entries use `[global]` or ISO-3 strings); aligned to ISO-3 here.
- `auth_required: api-key-free` reflects practical reality (anonymous quota of 1K/day is too low for agent workloads). If the project prefers strict reading where anon access exists, switch to `none` and note the quota in body.
