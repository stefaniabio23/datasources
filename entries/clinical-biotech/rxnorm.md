---
id: rxnorm
name: RxNorm
domain: clinical-biotech
entry_kind: knowledge-graph
description: NLM normalized drug terminology that assigns each clinical drug a concept id (RxCUI) and cross-maps it to NDC, ATC, DrugBank, UNII, SPL, and other pharmacy vocabularies.
homepage_url: https://www.nlm.nih.gov/research/umls/rxnorm/index.html
docs_url: https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: UMLS-Metathesaurus-License
rate_limit: "20 req/sec per IP (RxNav shared limit across RxNorm/RxClass/RxTerms/Interaction APIs)"
bulk_available: true
frequency: "monthly full release (first Monday); weekly updates for Current Prescribable Content"
lag: "new FDA-approved drugs appear within weeks via weekly prescribable-content updates"
geography: [USA]
structure: registry-snapshot
pit_reconstructable: true
revisions_possible: true
join_keys:
  - RXNORM_CUI
  - NDC
  - ATC_CODE
  - DRUGBANK_ID
  - UNII
  - SETID
  - HCPCS
  - FDA_APPLICATION_NUMBER
primary_keys:
  - RXNORM_CUI
join_key_fields:
  - join_key: RXNORM_CUI
    fields: [properties.rxcui, idGroup.rxnormId, propConceptGroup.propConcept.propValue]
  - join_key: NDC
    fields: [ndcGroup.ndcList.ndc]
  - join_key: ATC_CODE
    fields: [propConceptGroup.propConcept.propValue, rxclassDrugInfoList.rxclassDrugInfo.rxclassMinConceptItem.classId]
  - join_key: DRUGBANK_ID
    fields: [propConceptGroup.propConcept.propValue]
  - join_key: UNII
    fields: [propConceptGroup.propConcept.propValue]
  - join_key: SETID
    fields: [propConceptGroup.propConcept.propValue]
  - join_key: HCPCS
    fields: [propConceptGroup.propConcept.propValue]
  - join_key: FDA_APPLICATION_NUMBER
    fields: [propConceptGroup.propConcept.propValue]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/JamesANZ/medical-mcp (npm: medical-mcp)"
mcp_command:
  - "npm install -g medical-mcp"
mcp_notes: >
  medical-mcp is a multi-API medical connector (FDA, WHO, PubMed, RxNorm), not RxNorm-dedicated;
  RxNorm coverage is a subset of its tools. A focused RxNorm connector (normalize_drug_name,
  get_rxcui_properties, get_ndcs, map_to_atc, get_related_by_tty, remap_retired_rxcui) would
  serve the many drug-linking entries in this registry better.
agent_use_cases:
  - drug name normalization
  - NDC-to-ingredient resolution
  - cross-vocabulary drug code mapping
  - brand-to-ingredient rollup
  - retired-RxCUI remapping
access_test:
  command: "curl -sf 'https://rxnav.nlm.nih.gov/REST/rxcui/198440/properties.json'"
  expected_status: 200
  expected_fields: [properties.rxcui, properties.name, properties.tty]
last_verified: 2026-07-02
build_priority: high
---

# RxNorm

## Why this source matters

RxNorm is the US National Library of Medicine's normalized terminology for clinical drugs. It mints a Concept Unique Identifier (RxCUI) for every ingredient, strength, dose form, and branded/generic drug, links those concepts through typed relationships (TTYs: IN, SCD, SBD, BN), and cross-maps each concept to the proprietary and public vocabularies used across US pharmacy and formulary systems (NDC, ATC, DrugBank, UNII, SPL, HCPCS, SNOMED CT, FDA application numbers). For an agent, RxNorm is the canonical hub for turning a messy free-text drug string or a bare NDC into a stable concept and then fanning out to every other drug source. It sits alongside the existing `umls`, `dailymed`, `drugbank`, and `chembl` entries; RxNorm is the normalization layer those sources join through. Secondary relevance: `healthcare-claims` (NDC/HCPCS resolution for claims data).

## Agent use cases

- drug name normalization
- NDC-to-ingredient resolution
- cross-vocabulary drug code mapping
- brand-to-ingredient rollup
- retired-RxCUI remapping

## Join strategy

`RXNORM_CUI` is the native primary key and the central hub. RxNorm exposes forward mappings (RxCUI to external code) via `/REST/rxcui/{rxcui}/allProperties.json?prop=codes`, where each code appears as `propConceptGroup.propConcept` with `propName` naming the vocabulary and `propValue` holding the code. Confirmed live: `ATC_CODE`, `DRUGBANK_ID`, `UNII` (propName `UNII_CODE`), `SETID` (propName `SPL_SET_ID`), `HCPCS`, and `FDA_APPLICATION_NUMBER` (propNames `NDA`/`ANDA`/`BLA`). `NDC` comes from the dedicated `/rxcui/{rxcui}/ndcs.json` endpoint (`ndcGroup.ndcList.ndc`). ATC is also retrievable at class granularity via the RxClass API (`rxclassDrugInfoList...classId`, ATC1-4 level). Reverse lookups (external code to RxCUI) use `findRxcuiById?idtype=<TYPE>&id=<code>`, returning `idGroup.rxnormId`; the full idtype list is available at `/REST/idtypes.json`.

Recommended hub role: normalize inbound drug strings or NDCs to an RxCUI, then join to `dailymed` (SETID/SPL), `drugbank` (DrugBank id), `openfda`/`drugs-at-fda` (NDC, FDA application number), and `chembl` via a UNII or name bridge. RxNorm does NOT natively expose `CHEMBL_ID` (see Review notes).

## Access notes

Hit the RxNav REST API first: base `https://rxnav.nlm.nih.gov/REST/`, JSON or XML by extension, no key and no account required. Rate limit is 20 requests/sec per IP shared across all RxNav APIs (RxNorm, RxClass, RxTerms, Interaction); the terms of service cap sustained programmatic use, so batch and cache. Start with `getRxProperty`/`allProperties` for code mapping, `findRxcuiByString` (approximate match) for free-text normalization, and `getRxcuiHistoryStatus` to remap retired/remapped RxCUIs (concepts do get retired and remapped, so backtests need vintage handling). Bulk: the full monthly RRF release (pipe-delimited UTF-8, first Monday of each month) requires a free UMLS Terminology Services / Metathesaurus License account because it embeds restricted source vocabularies (First Databank, Micromedex, Multum, Gold Standard). The Current Prescribable Content subset (weekly) is downloadable with no license. Historical monthly archives are retained, which is what makes point-in-time reconstruction possible.

## MCP / connector notes

An `mcp-exists` match is only partial: `medical-mcp` (github.com/JamesANZ/medical-mcp) is a community, multi-API server (FDA, WHO, PubMed, RxNorm) that runs locally with no keys, but RxNorm is a slice of its surface rather than the focus. Gaps: no dedicated approximate-match normalization tool, no retired-RxCUI remapping, no bulk RRF loader. A focused RxNorm connector should abstract over the forward-vs-reverse lookup split (`allProperties` vs `findRxcuiById`), auto-select TTY when rolling brands up to ingredients, and expose `normalize_drug_name`, `get_rxcui_properties`, `get_ndcs`, `map_to_atc`, `get_related_by_tty`, and `remap_retired_rxcui`.

## Review notes

- **License short name not yet canonical.** Used `UMLS-Metathesaurus-License` for the full RRF release (embeds restricted third-party source vocabularies, requires a free UMLS/UTS license account). The RxNav API and the Current Prescribable Content subset are open with no license, so the field slightly over-restricts the agent-facing API path; nuance is in Access notes. Flagging `UMLS-Metathesaurus-License` as a new canonical kebab-case license short name for `SCHEMA.md`. The existing `umls.md` entry likely faces the same choice; align them.
- **CHEMBL_ID dropped despite the hint.** RxNorm's `idtypes.json` and `allProperties` do not expose ChEMBL ids (confirmed live against `/REST/idtypes.json`), so `CHEMBL_ID` was intentionally omitted from `join_keys`. Bridge to ChEMBL via UNII or drug name, not directly.
- **Added join keys beyond the hint list.** RxNorm genuinely exposes `UNII`, `SETID`, `HCPCS`, and `FDA_APPLICATION_NUMBER` (all already in `schema/join-keys.yaml`), so they were included. All verified against a live `allProperties?prop=codes` response for RxCUI 11289 (warfarin).
- **Potential new join key for review: `SNOMEDCT`** (or `SNOMED_CT`).
    - Entity type: clinical_concept (drug/substance)
    - Pattern: `^[0-9]{6,18}$` (SNOMED CT concept id, e.g. 372756006)
    - Other datasets that would use it: UMLS, DailyMed, LOINC, any EHR-derived source. RxNorm exposes it via `allProperties` (propName `SNOMEDCT`) but there is no canonical SNOMED key in the registry yet, so it was not added to `join_keys`.
- **`auth_required: none` reflects the API path.** The primary agent surface (RxNav REST) needs no auth; only the full bulk release needs a free account. Kept `none` since that is what the `access_test` and most agent use hit.
