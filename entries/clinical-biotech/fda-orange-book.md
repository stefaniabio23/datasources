---
id: fda-orange-book
name: FDA Orange Book
domain: clinical-biotech
entry_kind: registry
description: FDA's Approved Drug Products with Therapeutic Equivalence Evaluations, the canonical US source for approved drug products, therapeutic equivalence (TE) codes, listed patents, and marketing exclusivity periods.
homepage_url: https://www.accessdata.fda.gov/scripts/cder/ob/
docs_url: https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files
type:
  - bulk-download
  - web-ui
  - rest-api
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "bulk zip is a static file; openFDA drugsfda mirror: 240 req/min and 1,000 req/day per IP anonymous, 120K/day with free key"
bulk_available: true
frequency: monthly
lag: "current edition refreshed monthly; daily Cumulative Supplement published between editions"
geography: [USA]
join_keys:
  - NDC
primary_keys:
  - FDA_APPLICATION_NUMBER
  - FDA_PRODUCT_NUMBER
  - PATENT_NUMBER
  - TE_CODE
  - EXCLUSIVITY_CODE
join_key_fields:
  - join_key: NDC
    fields: [openfda.product_ndc, openfda.package_ndc, products.openfda.product_ndc, products.openfda.package_ndc]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No dedicated Orange Book MCP. Patent and exclusivity tables are the canonical source for
  generic launch timing and IP analysis; not exposed by existing openFDA MCPs. Suggested surface:
  search_products, get_patents_for_application, get_exclusivity_for_application,
  list_te_equivalents, lookup_rld.
agent_use_cases:
  - generic-launch timing analysis
  - therapeutic equivalence lookup
  - reference listed drug (RLD) identification
  - drug patent and exclusivity mapping
  - ANDA pipeline diligence
access_test:
  command: "curl -sf 'https://api.fda.gov/drug/drugsfda.json?search=application_number:NDA020571&limit=1'"
  expected_status: 200
  expected_fields: [meta, results, products, application_number, sponsor_name]
last_verified: 2026-06-08
build_priority: high
---

# FDA Orange Book

## Why this source matters

The Orange Book (formally *Approved Drug Products with Therapeutic Equivalence Evaluations*) is the FDA Center for Drug Evaluation and Research's authoritative list of approved prescription, OTC, and discontinued drug products, their therapeutic equivalence (TE) ratings, sponsor-listed patents covered by Hatch-Waxman, and marketing exclusivity periods. It is the canonical US reference for two questions no other source answers cleanly: which generic is AB-rated substitutable for a given brand, and when can a generic legally launch. Patent and exclusivity tables are not exposed via the openFDA drugsfda endpoint; the bulk ZIP is the only complete source. Secondary relevance to `finance-markets` for pharma equity research (patent cliffs, generic entry) and to `healthcare-claims` for substitution-eligible product selection.

## Agent use cases

- generic-launch timing analysis
- therapeutic equivalence lookup
- reference listed drug (RLD) identification
- drug patent and exclusivity mapping
- ANDA pipeline diligence

## Join strategy

The Orange Book's primary entities are keyed by FDA application number plus product number (e.g. NDA 020571 product 001), which is an FDA-internal compound key. The same application-and-product key links the three Orange Book files (Products.txt, Patent.txt, Exclusivity.txt) and is shared with the openFDA `drugsfda` endpoint. Source-internal keys (`FDA_APPLICATION_NUMBER`, `FDA_PRODUCT_NUMBER`, `PATENT_NUMBER`, `TE_CODE`, `EXCLUSIVITY_CODE`) are intentionally outside the canonical registry; use them for direct Orange Book joins, not cross-source joins.

Cross-source joining to drug-product registries flows through `NDC`: openFDA's drugsfda mirror exposes NDCs in the `openfda` enrichment block for each product, which lets you bridge from an Orange Book application/product key to RxNorm (`RXNORM_CUI`), DailyMed labels, and prescription-claims sources. There is no direct DOI, NCT, or ICD link from the Orange Book itself; pair with Drugs@FDA submissions and ClinicalTrials.gov to recover trial and approval-history context for a listed product.

Potential new join keys flagged in Review notes: `FDA_APPLICATION_NUMBER` (also flagged in the openFDA entry), `US_PATENT_NUMBER`, and `UNII`.

## Access notes

Bulk ZIP is the canonical source. Download from `https://www.fda.gov/media/76860/download?attachment` (current filename pattern: `EOBZIP_YYYY_MM.zip`, refreshed monthly with the new edition; the FDA also publishes a daily Cumulative Supplement during the month). The archive contains three ASCII text files, tilde (`~`) delimited:

- `products.txt`, fields: Ingredient, DF;Route, Trade_Name, Applicant, Strength, Appl_Type (N or A), Appl_No, Product_No, TE_Code, Approval_Date, RLD, RS, Type (RX, OTC, DISCN), Applicant_Full_Name.
- `patent.txt`, fields: Appl_Type, Appl_No, Product_No, Patent_No, Patent_Expire_Date, Drug_Substance_Flag, Drug_Product_Flag, Patent_Use_Code, Patent_Delist_Request_Flag, Patent_Submission_Date.
- `exclusivity.txt`, fields: Appl_Type, Appl_No, Product_No, Exclusivity_Code, Exclusivity_Date.

Web UI search at `https://www.accessdata.fda.gov/scripts/cder/ob/` supports lookup by active ingredient, proprietary name, applicant, or application number; useful for spot checks but not bulk extraction.

Partial API coverage via openFDA `drugsfda` (`https://api.fda.gov/drug/drugsfda.json`): each result includes a `products` array with `te_code`, `marketing_status`, `dosage_form`, `route`, `reference_drug`, `reference_standard`, and the `openfda` enrichment block (NDCs, RxCUIs, UNIIs). **Patent and exclusivity tables are not in this endpoint**, so for IP-driven workflows the ZIP is required.

License: federal work of the US government, public domain under 17 USC 105; no attribution requirement. Field definitions stable since 2017, file format unchanged since the EOB transition.

Gotchas:

- DISCN-status products remain in the file (discontinued, not delisted); filter on `Type` for active-market analysis.
- Patent records can list pediatric-exclusivity-extended expiry dates as the raw `Patent_Expire_Date`; cross-check against the Exclusivity table.
- TE codes are absent for innovator-only products with no approved generic; null TE is not a quality issue.
- File encoding is ASCII with occasional Windows-1252 stragglers; decode defensively.
- Application number is bare digits (6 chars) in the bulk file; some downstream sources prefix with `NDA`/`ANDA`/`BLA`.

## MCP / connector notes

No dedicated Orange Book MCP. The community openFDA MCPs (see the openFDA entry) cover the `drugsfda` mirror but not the patent or exclusivity tables, which are the highest-value-add of the Orange Book. A connector would need to ingest and refresh the monthly ZIP locally, then expose `search_products` (by ingredient, trade name, applicant, application number), `get_patents_for_application`, `get_exclusivity_for_application`, `list_te_equivalents` (find all AB-rated products for a given RLD), and `lookup_rld` (identify the reference listed drug for an ingredient or generic). Tricky bits: parsing tilde-delimited ASCII robustly, reconciling pediatric-exclusivity-extended patent dates, and crosswalking the bare 6-digit application number to the NDA/ANDA/BLA-prefixed form used by Drugs@FDA and SEC filings.

## Review notes

- Potential new join key for review: `FDA_APPLICATION_NUMBER`. Entity type: `drug_approval`. Pattern: bare 6-digit form `^[0-9]{6}$` or prefixed `^(NDA|ANDA|BLA)[0-9]{6}$`. Other datasets that would use it: Orange Book, Drugs@FDA, openFDA, Purple Book, CMS Medicare drug pricing, SEC filings. Already flagged on the openFDA entry; the Orange Book is the highest-leverage user of this key.
- Potential new join key for review: `US_PATENT_NUMBER`. Entity type: `patent`. Pattern: variable (e.g. `^[0-9]{1,11}$` for utility patents; design and plant patents differ). Other datasets that would use it: USPTO PatentsView, Google Patents, PatentScope. Critical for pharma IP analysis; the Orange Book is the canonical pharma-patent listing.
- Potential new join key for review: `UNII`. Entity type: `chemical_substance`. Pattern: `^[A-Z0-9]{10}$`. Also flagged on the openFDA entry. The Orange Book exposes ingredient strings rather than UNII directly, but the openFDA mirror adds UNII via the enrichment block.
- `auth_required: none` reflects the bulk ZIP and web UI; the optional openFDA mirror access uses the openFDA quota (anon 1K/day per IP, 120K/day with free key). Documented in body rather than YAML to avoid conflating distribution surfaces.
- `geography: [USA]` aligned to ISO-3; matches the openFDA entry's convention.
