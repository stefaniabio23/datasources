---
id: drugs-at-fda
name: Drugs@FDA
domain: clinical-biotech
entry_kind: registry
description: FDA's authoritative record of approved drug and biologic products, with full application, product, and submission/supplement approval history plus links to approval letters, labels, and review documents.
homepage_url: https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files
docs_url: https://open.fda.gov/apis/drug/drugsfda/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free
license: CC0
rate_limit: "openFDA API: 240 req/min and 1,000 req/day per IP without a key; 240 req/min and 120,000 req/day with a free key. Raw FDA bulk files have no limit."
bulk_available: true
frequency: "daily (Monday-Friday) on the openFDA mirror; raw FDA data files refreshed regularly"
lag: "days from FDA action to publication"
geography: [USA]
join_keys:
  - FDA_APPLICATION_NUMBER
  - NDC
  - UNII
primary_keys:
  - FDA_APPLICATION_NUMBER
  - PRODUCT_NUMBER
  - SUBMISSION_TYPE
  - SUBMISSION_NUMBER
join_key_fields:
  - join_key: FDA_APPLICATION_NUMBER
    fields: [application_number, openfda.application_number]
  - join_key: NDC
    fields: [openfda.product_ndc, openfda.package_ndc]
  - join_key: UNII
    fields: [openfda.unii]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No dedicated Drugs@FDA MCP. Generic openFDA MCPs exist but rarely model the submission/supplement
  timeline cleanly. Suggested surface: search_applications, get_application, get_submission_history,
  list_products, resolve_ndc_to_application, get_approval_documents. Connector should expose the
  Submissions array as a chronological approval/supplement log and surface ApplicationDocs URLs.
agent_use_cases:
  - drug approval lookup
  - supplement and label-change history tracking
  - approval-letter and review-document retrieval
  - sponsor-to-product mapping
  - NDA/ANDA/BLA crosswalk to NDC and UNII
access_test:
  command: "curl -sf 'https://api.fda.gov/drug/drugsfda.json?search=application_number:NDA018037&limit=1'"
  expected_status: 200
  expected_fields: [application_number, sponsor_name, products, submissions]
last_verified: 2026-06-22
build_priority: high
---

# Drugs@FDA

## Why this source matters

Drugs@FDA is the FDA's official record of every drug and therapeutic biologic the agency has approved, run by the Center for Drug Evaluation and Research. It covers most drug products approved since 1939, with approval letters, labels, and review documents available since 1998. Where DailyMed holds the current label text, Drugs@FDA holds the regulatory timeline: who applied (the sponsor), what was approved (each product, strength, and dosage form), and the full chain of original approvals and subsequent supplements with their dates, types, and statuses. For any agent reconstructing when a drug was approved, tracking a labeling or manufacturing supplement, or pulling the actual approval letter and clinical review PDFs, this is the primary source. It is the approval-history backbone that pairs with DailyMed (label text), the Orange Book (therapeutic equivalence), and openFDA's adverse-event and NDC endpoints.

## Agent use cases

- drug approval lookup
- supplement and label-change history tracking
- approval-letter and review-document retrieval
- sponsor-to-product mapping
- NDA/ANDA/BLA crosswalk to NDC and UNII

## Join strategy

The native key is `FDA_APPLICATION_NUMBER` (the ApplNo, e.g. `NDA018037`, `ANDA076298`, `BLA*`), which uniquely identifies an application and its sponsor. To pin a single product record, combine ApplNo with the source-internal `ProductNo` (`products[].product_number`); to pin a single regulatory event, add `SubmissionType` + `SubmissionNo` (`submissions[].submission_type` + `submission_number`, e.g. `ORIG` 1, `SUPPL` 12). These three are source-internal and live in `primary_keys`, not the canonical registry.

`NDC` and `UNII` are exposed only on the openFDA mirror, inside the enriched `openfda` block (`openfda.product_ndc`, `openfda.package_ndc`, `openfda.unii`), and only when openFDA has cross-matched the application to its product and substance data. They are not present in the raw FDA tab-delimited tables, which carry drug names, ingredients, strengths, and forms as free text rather than coded identifiers. Treat NDC/UNII here as a convenience crosswalk, not native data; for authoritative NDC resolution, cross via the openFDA NDC directory.

Pair with DailyMed for label text: the openFDA block also carries `openfda.spl_set_id`, which is the DailyMed `SETID`, giving a direct ApplNo-to-label join (SETID is not yet a canonical join key, flagged below). Pair with the Orange Book for therapeutic-equivalence ratings on the same ApplNo, and with openFDA drug-event for adverse-event signal on the same NDC.

## Access notes

**Quick agent queries:** openFDA REST API at `https://api.fda.gov/drug/drugsfda.json`. No auth needed for light use; a free API key (set `api_key=`) lifts the daily cap from 1,000 to 120,000 requests. First endpoints: `?search=application_number:NDA018037` for a record, `?search=openfda.brand_name:"..."` for brand search, `?count=` for aggregations. The `submissions` array is the approval/supplement history; the `application_docs` array carries URLs to approval letters, labels, and reviews on accessdata.fda.gov.

**Bulk pulls:** Raw FDA tab-delimited tables at `drugsatfda.zip` (Applications, Products, Submissions, ApplicationDocs, plus lookup tables), linked from the homepage. The openFDA JSON mirror is downloadable as a single bulk file at `https://download.open.fda.gov/drug/drugsfda/drug-drugsfda-0001-of-0001.json.zip`. Use the raw tables when you need the unenriched relational structure; use the openFDA JSON when you want the NDC/UNII/SETID crosswalk pre-joined. To verify freshness, check `meta.last_updated` in any API response.

## MCP / connector notes

No dedicated Drugs@FDA MCP. Generic openFDA wrappers exist but typically treat the endpoint as a flat record fetch and do not model the submission/supplement timeline, which is the most valuable structure here. Suggested surface: `search_applications` (by sponsor, brand, ingredient), `get_application` (trimmed), `get_submission_history` (chronological ORIG + SUPPL log with dates and types), `list_products`, `resolve_ndc_to_application`, `get_approval_documents` (ApplicationDocs URLs by type: letter / label / review). The connector should reshape the nested `submissions` array into a sorted event log and abstract over the raw-table vs openFDA-JSON shape difference (coded NDC/UNII present only in the latter).

## Review notes

Non-registered identifiers flagged:

- `ProductNo`, `SubmissionType`, `SubmissionNo` are source-internal composite keys (placed in `primary_keys` as `PRODUCT_NUMBER`, `SUBMISSION_TYPE`, `SUBMISSION_NUMBER`). They have no cross-source utility on their own and are intentionally not in the canonical registry.

- NDC and UNII are listed in `join_keys` but, per the join strategy above, are present only on the openFDA mirror's enriched `openfda` block and not in the raw FDA tables. If the registry consumer assumes native carriage, this is the caveat: they arrive via openFDA cross-matching, not from Drugs@FDA itself.

Potential new join key for review:

```
Potential new join key for review: SETID
  Entity type: spl_document
  Pattern: UUID v4 (e.g. c553fed1-3de5-4826-8eff-633b5923bf0b)
  Other datasets that would use it: DailyMed (mints it), openFDA drug-label and drugsfda endpoints (openfda.spl_set_id)
```

SETID would unlock a direct ApplNo-to-label join between Drugs@FDA and DailyMed. It is already flagged for review in the DailyMed entry; noting here that this entry also exposes it (via `openfda.spl_set_id`) strengthens the case for PRing it into `schema/join-keys.yaml`.
