---
id: nhs-prescription-cost-analysis
name: NHS Prescription Cost Analysis (PCA)
domain: healthcare-claims
entry_kind: time-series
description: NHSBSA monthly count of items dispensed and net ingredient cost for every drug, dressing, appliance, and medical device reimbursed by the NHS in community pharmacies in England, broken down by BNF code and NHS region.
homepage_url: https://www.nhsbsa.nhs.uk/prescription-data/dispensing-data/prescription-cost-analysis-pca-data
docs_url: https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: OGL-3.0
rate_limit: "not published; CKAN API is anonymous, polite use expected"
bulk_available: true
frequency: monthly
lag: "~2 months (e.g. January data published in March)"
geography: [GBR]
join_keys:
  - BNF_CODE
  - DATE
primary_keys:
  - BNF_PRESENTATION_CODE
  - BNF_CHEMICAL_SUBSTANCE_CODE
  - BNF_PARAGRAPH_CODE
  - BNF_SECTION_CODE
  - BNF_CHAPTER_CODE
  - SNOMED_CODE
  - REGION_CODE
  - STP_CODE
  - YEAR_MONTH
join_key_fields:
  - join_key: BNF_CODE
    fields:
      - BNF_PRESENTATION_CODE
      - GENERIC_BNF_EQUIVALENT_CODE
      - BNF_CHEMICAL_SUBSTANCE_CODE
      - BNF_PARAGRAPH_CODE
      - BNF_SECTION_CODE
      - BNF_CHAPTER_CODE
  - join_key: DATE
    fields:
      - YEAR_MONTH
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No MCP. Audience is UK health-policy analysts, pharmacoeconomics researchers,
  and primary-care benchmarking. A connector would wrap the NHSBSA Open Data
  Portal CKAN API. Suggested surface: search_pca(bnf_code, year_month),
  get_monthly_spend(bnf_chapter, region), top_drugs(year_month, by=spend|items),
  list_months(). Must handle the resource-per-month layout (one CKAN resource
  per YYYYMM) and the 2008-2020 historical archive that lives on the legacy
  NHSBSA website rather than the portal.
agent_use_cases:
  - England community-pharmacy spend tracking
  - generic-vs-branded dispensing share
  - regional and STP-level prescribing benchmarking
  - drug-class cost trends over time
  - shortages and price-spike monitoring
access_test:
  command: "curl -sf 'https://opendata.nhsbsa.net/api/3/action/package_show?id=prescription-cost-analysis-pca-monthly-data'"
  expected_status: 200
  expected_fields: [success, result, resources]
last_verified: 2026-06-09
build_priority: medium
notes: "CKAN datastore_search and datastore_search_sql endpoints returned HTTP 500 during verification on 2026-06-09; package_show is the reliable metadata path. Bulk CSV download per month is the dependable data path. The 2008-02 to 2020-12 historical archive lives on the legacy NHSBSA site, not the open data portal."
---

# NHS Prescription Cost Analysis (PCA)

## Why this source matters

PCA is the NHS Business Services Authority's record of every drug, dressing, appliance, and medical device dispensed in the community in England and submitted for reimbursement. Each monthly file has one row per BNF presentation, NHS region, Sustainability and Transformation Partnership (STP), dispenser type, and prep class, with columns for items, total quantity, and Net Ingredient Cost. Coverage runs from January 2021 onward on the open data portal, with a separate 2008-02 to 2020-12 archive on the legacy NHSBSA site. For agents working on UK prescribing patterns, drug-cost trends, generic substitution, regional variation, or shortages, this is the only authoritative dispensed-in-community spend dataset for England. Pair with NHS England's English Prescribing Dataset (EPD, prescriber-level monthly) for the prescribing side of the same flow, and with OpenPrescribing for analyst-friendly chart and trend tooling on the same underlying numbers. Secondary domain: public-health (drug-class trends), government-open-data (OGL-3.0 release).

## Agent use cases

- England community-pharmacy spend tracking
- generic-vs-branded dispensing share
- regional and STP-level prescribing benchmarking
- drug-class cost trends over time
- shortages and price-spike monitoring

## Join strategy

`BNF_CODE` is the load-bearing canonical join key. PCA exposes the full British National Formulary hierarchy in every row: 2-digit chapter, 4-digit section, 6-digit paragraph, 9-character chemical substance code, and 15-character presentation code, plus a separate `GENERIC_BNF_EQUIVALENT_CODE` that maps branded products to their generic equivalent. Any one of these is a valid join target, depending on whether the joining source carries product-level or chapter-level codes. The SNOMED CT dm+d code is also present per row but is not yet in the canonical registry.

`DATE` joins on `YEAR_MONTH` (integer `YYYYMM`); convert to ISO `YYYY-MM` when joining onto sources that store monthly periods as ISO dates.

Source-internal IDs (`REGION_CODE`, `STP_CODE`) name NHS England administrative geographies. They are not in the canonical registry. They do not align to LSOA, MSOA, LAD, or ICB codes without an explicit lookup; STPs were succeeded by Integrated Care Boards in 2022, so multi-year analyses need both vocabularies.

Common pairings: OpenPrescribing (chart and trend layer over PCA + EPD), NHS England EPD (prescriber-side counterpart at GP-practice grain), dm+d (SNOMED drug dictionary for richer product metadata), BNF/NICE (drug class metadata).

Potential new join keys flagged in Review notes.

## Access notes

The current canonical landing page is the NHSBSA marketing page at `nhsbsa.nhs.uk/prescription-data/dispensing-data/prescription-cost-analysis-pca-data`. The actual data lives on the NHSBSA Open Data Portal (`opendata.nhsbsa.net`), which is CKAN-backed. The PCA package ID is `358e443c-b299-4370-aed4-eca63ce3ba68` and the URL slug is `prescription-cost-analysis-pca-monthly-data`. Each month is a separate CKAN resource; `PCA_202101` was the first, and the resource list grows by one per month. The package metadata endpoint is the single most useful agent surface because it returns the full resource list with per-month download URLs:

```
https://opendata.nhsbsa.net/api/3/action/package_show?id=prescription-cost-analysis-pca-monthly-data
```

For bulk reads, download the per-month CSV directly. The January 2021 file is around 230 MB unzipped; later months are similar. The download URL pattern is `https://opendata.nhsbsa.net/dataset/358e443c-b299-4370-aed4-eca63ce3ba68/resource/<resource_id>/download/pca_<YYYYMM>.csv`. Resources advertise `datastore_active: true`, so in principle row-level queries via CKAN `datastore_search` and `datastore_search_sql` should work. On 2026-06-09 both returned HTTP 500 against `opendata.nhsbsa.net/api/3/action/datastore_search?resource_id=<uuid>&limit=1`; treat the row-level API as unreliable and prefer bulk CSV until upstream confirms. The portal publishes the NHSBSA `open-data-portal-api` GitHub repo (R and Python notebooks) as the canonical client example.

License is OGL-3.0 (Open Government Licence v3.0); attribute "Contains public sector information licensed under the Open Government Licence v3.0" plus the NHSBSA. No registration, no key.

Column schema (per row, January 2021 release):

```
YEAR_MONTH, REGION_NAME, REGION_CODE, STP_NAME, STP_CODE,
DISPENSER_ACCOUNT_TYPE, BNF_PRESENTATION_CODE, BNF_PRESENTATION_NAME,
SNOMED_CODE, SUPPLIER_NAME, UNIT_OF_MEASURE,
GENERIC_BNF_EQUIVALENT_CODE, GENERIC_BNF_EQUIVALENT_NAME,
BNF_CHEMICAL_SUBSTANCE_CODE, BNF_CHEMICAL_SUBSTANCE,
BNF_PARAGRAPH_CODE, BNF_PARAGRAPH,
BNF_SECTION_CODE, BNF_SECTION,
BNF_CHAPTER_CODE, BNF_CHAPTER,
PREP_CLASS, PRESCRIBED_PREP_CLASS,
ITEMS, TOTAL_QUANTITY, NIC
```

`NIC` is Net Ingredient Cost in GBP, the pre-discount list cost of the medicine. It is not the amount actually reimbursed and not the patient-paid charge.

Gotchas:

- Coverage is dispensing in England only, regardless of where the prescription originated. Wales, Scotland, and Northern Ireland publish separately.
- PCA is classified as Management Information, not an Official Statistic. NHSBSA notes the figures are not statistically validated.
- Hospital-dispensed, prison-dispensed, private prescriptions, and unsubmitted reimbursement claims are excluded.
- STP codes were superseded by ICB codes in July 2022; the column header remained `STP_CODE` in some publications, so verify the vocabulary per month.
- The 2008-02 to 2020-12 archive sits on the legacy `nhsbsa.nhs.uk` site, not the open data portal, and uses a different file layout.

## MCP / connector notes

No MCP. Audience is moderately narrow (UK health-policy analysts, pharmacoeconomics, primary-care benchmarking) but the directory already includes adjacent UK and US drug-spend sources, so an NHS-prescribing MCP that fronts PCA plus EPD plus OpenPrescribing would be high-leverage for that cohort.

Suggested MCP surface:

- `list_months()` returning the full set of `(YEAR_MONTH, resource_id, download_url)` rows from `package_show`
- `search_pca(bnf_code, year_month, region_code?)` returning rows for a given BNF code at any hierarchy level
- `get_monthly_spend(bnf_chapter, region_code?, range=...)` aggregating ITEMS and NIC
- `top_drugs(year_month, by=spend|items, n=50)`
- `compare_branded_vs_generic(bnf_chemical_substance_code, range=...)` using `GENERIC_BNF_EQUIVALENT_CODE`

The MCP must abstract over the resource-per-month layout, the 500-erroring datastore endpoints, the 2008-2020 legacy archive that lives off-portal, and the STP-to-ICB geography transition.

## Review notes

- The existing `BNF_CODE` registry key covers chapter, section, paragraph, chemical-substance, and presentation in one hierarchical namespace. PCA exposes all five levels in distinct columns. If the registry later needs separate keys per hierarchy level (e.g. `BNF_CHEMICAL_SUBSTANCE_CODE` vs `BNF_PRESENTATION_CODE`), revisit `join_key_fields` here; for now they are mapped to the single `BNF_CODE` key.
- Potential new join keys for review:
  - `SNOMED_DMD`. Entity type: `uk_drug_product`. Pattern: numeric SNOMED CT concept ID from the dm+d (Dictionary of Medicines and Devices) subset. PCA carries this in `SNOMED_CODE`. Other datasets that would use it: NHS Digital secondary care medicines, NHS England EPD, dm+d browser, NHS terminology server. Worth registering once a second source lands.
  - `NHS_REGION_CODE`, `NHS_STP_CODE`. Entity type: `uk_geography`. The registry already has `ICB_CODE`. NHS England region and STP are distinct administrative tiers carried by PCA in `REGION_CODE` and `STP_CODE`. May warrant their own keys if more NHS sources land.
- The CKAN `datastore_search` and `datastore_search_sql` endpoints both returned HTTP 500 during verification on 2026-06-09 despite `datastore_active: true` on every resource. Worth confirming with NHSBSA Data Services or retrying before promising row-level API access to downstream consumers. Access test uses `package_show`, which does succeed.
- License short-name in YAML uses `OGL-3.0`, matching the form referenced in `SCHEMA.md` and `CLAUDE.md`. The CKAN package metadata reports it as `OGL-UK-3.0`; standardised here.
- Domain placement: `healthcare-claims` is the closest fit (reimbursement submissions to a national payer), so a new `entries/healthcare-claims/` folder is introduced. PCA is administrative reimbursement data, not a clinical claim per se; if Stephanie prefers `public-health` or `government-open-data` for the UK reimbursement stack, this entry can be relocated without other changes.
