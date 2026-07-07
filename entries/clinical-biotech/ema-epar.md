---
id: ema-epar
name: EMA EPAR / Medicines
domain: clinical-biotech
entry_kind: registry
description: The European Medicines Agency's public register of centrally authorised human and veterinary medicines, with regulatory status, active substance, ATC code, therapeutic area, marketing-authorisation timeline, and links to European Public Assessment Reports (EPARs).
homepage_url: https://www.ema.europa.eu/en/medicines
docs_url: https://www.ema.europa.eu/en/medicines/download-medicine-data
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: EC-Reuse-Notice-2011-833
rate_limit: "No documented limit. A WAF returns 429 to bare/non-browser requests; send a normal User-Agent header."
bulk_available: true
frequency: "daily (tables refreshed overnight; JSON report regenerated up to twice daily)"
lag: "days from EMA/EC regulatory action to publication"
geography: [EU, EEA]
join_keys:
  - ATC_CODE
  - MESH_TERM
primary_keys:
  - EMA_PRODUCT_NUMBER
join_key_fields:
  - join_key: ATC_CODE
    fields: [atc_code_human, atcvet_code_veterinary]
  - join_key: MESH_TERM
    fields: [therapeutic_area_mesh]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/openpharma-org/ema-mcp"
  - "apify.com/ryanclinton/ema-medicines-search"
mcp_command:
  - "node build/index.js (clone github.com/openpharma-org/ema-mcp, then npm install && npm run build)"
mcp_notes: >
  Community MCP (openpharma-org/ema-mcp) wraps the EMA JSON report files behind a single
  ema_info tool with 14 methods (search_medicines, get_medicine_by_name, search_epar_documents,
  get_orphan_designations, get_supply_shortages, get_referrals, get_post_auth_procedures, etc.).
  JavaScript, not npm-published (build and run locally). Apify actor also exposes an MCP endpoint.
agent_use_cases:
  - EU centrally authorised medicine lookup
  - ATC-class to authorised-product mapping
  - orphan / biosimilar / generic status filtering
  - marketing-authorisation timeline retrieval
  - EPAR document discovery
access_test:
  command: "curl -sf -A 'Mozilla/5.0' 'https://www.ema.europa.eu/en/documents/report/medicines-output-medicines_json-report_en.json' | head -c 400"
  expected_status: 200
  expected_fields: [meta, data, ema_product_number, atc_code_human, international_non_proprietary_name_common_name]
last_verified: 2026-07-02
build_priority: high
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: true
---

# EMA EPAR / Medicines

## Why this source matters

The European Medicines Agency maintains the authoritative public register of medicines evaluated through the EU centralised procedure, run by the agency on behalf of the European Commission. Each row is one medicine (human or veterinary) with its regulatory status (`Authorised`, `Withdrawn`, `Refused`, opinion status), active substance and INN, ATC code, MeSH therapeutic area, marketing-authorisation holder, the full date timeline (start of evaluation, opinion adopted, EC decision, marketing authorisation, suspension/withdrawal), regulatory flags (orphan, biosimilar, generic, conditional approval, exceptional circumstances, PRIME, additional monitoring, advanced therapy), and a link to the medicine's EPAR page. It is the EU counterpart to Drugs@FDA: where Drugs@FDA holds US approval history, EMA EPAR holds the centralised EU approval record, and the two together cover most of the global pharma regulatory picture. For any agent reconstructing when a drug was authorised in the EU, filtering by orphan/biosimilar status, mapping an ATC class to authorised products, or pulling the EPAR assessment documents, this is the primary source. Secondary domain overlap: `bio-genomics` and `public-health` via ATC/MeSH-tagged retrieval.

## Agent use cases

- EU centrally authorised medicine lookup
- ATC-class to authorised-product mapping
- orphan / biosimilar / generic status filtering
- marketing-authorisation timeline retrieval
- EPAR document discovery

## Join strategy

The exposed canonical keys are `ATC_CODE` (`atc_code_human` for human medicines, `atcvet_code_veterinary` for veterinary) and `MESH_TERM` (`therapeutic_area_mesh`, a coarse therapeutic-area MeSH heading such as "Migraine Disorders", one per medicine rather than a full indication coding). ATC is the reliable coded join; MeSH here is therapeutic-area granularity, useful for bucketing but not indication-level precision.

The source-native key is the EMA product number (`ema_product_number`, e.g. `EMEA/H/C/005871`), which uniquely identifies the centralised procedure/product. It lives in `primary_keys` and is flagged below as a canonical-key candidate. The active substance and INN are carried as free text in `active_substance` and `international_non_proprietary_name_common_name`; INN is the practical bridge to substance-coded sources but is a name, not a coded identifier (flagged below).

EMA EPAR exposes no `UNII`, `DRUGBANK_ID`, `RXNORM_CUI`, `EU_CT_NUMBER`, or `FDA_APPLICATION_NUMBER`. To cross into those, resolve via ATC + INN: pair with ChEMBL and Open Targets (ATC/INN to molecule), Drugs@FDA and DailyMed for the US counterpart of the same substance, and EU-CTIS / ClinicalTrials.gov via active substance for the trial evidence behind an authorisation.

## Access notes

Primary programmatic path is the JSON report dump: a single GET to `https://www.ema.europa.eu/en/documents/report/medicines-output-medicines_json-report_en.json` returns the full table (~6.7 MB, ~2,712 records) as `{meta: {total_records, timestamp}, data: [...]}`. It is a static regenerated file, not a parameterised query API, so pull once and filter client-side. A WAF fronts the site and returns `429` to bare `curl`; send any normal `User-Agent` header and it returns `200`. Sibling report files follow the same pattern for orphan designations, shortages, referrals, post-authorisation procedures, and EPAR documents (the openpharma MCP enumerates 14 of them).

Human-facing bulk tables are on the download-medicine-data page in Excel (auto-updated overnight); the download page is the freshness reference. Note the field set changed in October 2025 (EMA product number added), and date fields use `DD/MM/YYYY`. An older static `Medicines_output_european_public_assessment_reports.xlsx` URL now 404s; use the download page or the JSON report instead.

**Regulatory-failure analysis.** The sibling report files include refused marketing authorisations and withdrawn applications, and CHMP negative opinions surface in the EPAR/procedure records. Pull the refusals/withdrawn report alongside the main medicines table to capture EU approval *failures*, not just successes, the European complement to FDA Complete Response Letters.

## MCP / connector notes

MCP exists (community): `openpharma-org/ema-mcp`, a JavaScript server that fetches the EMA JSON report files and exposes a single `ema_info` tool with 14 methods (`search_medicines`, `get_medicine_by_name`, `search_epar_documents`, `get_orphan_designations`, `get_supply_shortages`, `get_referrals`, `get_post_auth_procedures`, `get_dhpcs`, `get_psusas`, `get_pips`, and more). It is not npm-published, so clone, `npm install && npm run build`, and run `node build/index.js`. An Apify actor (`ryanclinton/ema-medicines-search`) additionally offers a hosted MCP endpoint. Gaps: static-file backed (no server-side per-record query, so the connector loads and filters the whole dump), no EPAR PDF text extraction beyond document URLs, and no cross-map to UNII/RxNorm/DrugBank (the connector would add value by resolving INN/ATC to those coded identifiers).

## Review notes

License: EMA content is reusable for commercial and non-commercial purposes under the European Commission reuse notice (Commission Decision 2011/833/EU) provided EMA is acknowledged as the source; third-party content and clinical reports are excluded. No SPDX code exists, so `license` uses the short name `EC-Reuse-Notice-2011-833`. New short name flagged for review; if adopted it would also apply to other EU institution open-data entries.

Potential new join keys for review:

```
Potential new join key for review: EMA_PRODUCT_NUMBER
  Entity type: drug_authorisation (EU centralised procedure/product)
  Pattern: ^EMEA/[HVA]/C/[0-9]{6}$ (e.g. EMEA/H/C/005871)
  Other datasets that would use it: EMA EPAR documents/orphan/post-auth report files, EU-CTIS and national registers linking to the EPAR
```

```
Potential new join key for review: INN
  Entity type: drug_substance (International Nonproprietary Name)
  Pattern: free-text lowercase substance name (e.g. atogepant); not a fixed regex
  Other datasets that would use it: ChEMBL, DrugBank, Drugs@FDA, DailyMed, EU-CTIS, WHO ATC/DDD index (name-based crosswalk to coded substance IDs)
```

INN is a name, not a coded ID, so any adoption should treat it as a fuzzy/normalising join key rather than an exact one. Both are currently held in `primary_keys` / free-text fields, not invented into `join_keys`.
