---
id: loinc
name: LOINC
domain: clinical-biotech
entry_kind: reference-table
description: International reference terminology that assigns unique codes to laboratory tests, clinical measurements, observations, and documents.
homepage_url: https://loinc.org/
docs_url: https://loinc.org/fhir/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: account-required
cost: free-with-registration
license: LOINC-License
rate_limit: "not published; FHIR server is BETA, availability not guaranteed"
bulk_available: true
frequency: "semiannual major releases (v2.82 released 2026-02-24)"
geography: [global]
join_keys:
  - LOINC_CODE
  - SNOMED_CT_ID
primary_keys:
  - LOINC_CODE
mcp_status: mcp-needed-high-value
agent_use_cases:
  - lab-test normalisation
  - map local lab codes to a standard code
  - value-set expansion for observations
  - resolve LOINC code to component and units
  - cross-code translation via ConceptMap
access_test:
  command: "curl -sf -u \"$LOINC_USER:$LOINC_PASS\" 'https://fhir.loinc.org/CodeSystem/$lookup?system=http://loinc.org&code=2951-2'"
  expected_status: 200
  expected_fields: [resourceType, parameter]
last_verified: 2026-07-02
build_priority: medium
notes: "access_test not yet executed; FHIR server requires a free LOINC username/password (HTTP Basic) via ${LOINC_USER}/${LOINC_PASS}."
---

# LOINC

## Why this source matters

LOINC (Logical Observation Identifiers Names and Codes) is the international standard for identifying health measurements, observations, and documents, run by the Regenstrief Institute since 1994. Version 2.82 carries ~109,000 terms. It is the vocabulary that makes lab results comparable across systems: each test (analyte, property, timing, system, scale, method) gets one stable code, so "serum glucose" from one lab and another resolve to the same identifier. For an agent, LOINC is the normalisation layer that lets lab-observation data from EHRs, claims, public-health lab reporting, and clinical-trial results be joined on a shared code rather than free-text test names. Secondary relevance to `healthcare-claims` (lab codes in administrative/EHR data) and `public-health` (electronic lab reporting).

## Agent use cases

- lab-test normalisation
- map local lab codes to a standard code
- value-set expansion for observations
- resolve LOINC code to component and units
- cross-code translation via ConceptMap

## Join strategy

LOINC mints the `LOINC_CODE` (source-native primary key, e.g. `2951-2` for serum sodium). That code is the join surface: it appears in FHIR Observation resources, HL7 messages, EHR lab feeds, and many public-health and claims-adjacent lab datasets, so LOINC is the hub for normalising lab observations across those sources.

`LOINC_CODE` is not yet in `schema/join-keys.yaml`, so `join_keys` is empty for now; the code is flagged under Review notes as a candidate canonical key given its broad cross-source utility. LOINC also ships mappings to SNOMED CT (LOINC/SNOMED CT Collaboration files, on request), IEEE 11073 medical-device codes, RSNA radiology playbook, and UCUM units, and LOINC codes are cross-walked in UMLS (a `UMLS_CUI` per concept). None of those target vocabularies are in the registry yet; `UMLS_CUI` is flagged for review. Pair with DailyMed/openFDA for drug context and with any lab-result dataset that carries LOINC-coded observations.

## Access notes

Everything requires a free LOINC account (register at loinc.org). Three access paths:

- **FHIR terminology server** (`https://fhir.loinc.org`), HL7 FHIR, HTTP Basic auth with your LOINC username/password. Supports `$lookup` (CodeSystem), `$expand` and `$validate-code` (ValueSet), and `$translate` (ConceptMap). Marked BETA: the implementation may change without notice and Regenstrief advises against production use. Start with `$lookup` on a known code to confirm auth works.
- **Complete LOINC file** (bulk): a single ZIP (CSV + XML + OWL) with the core table plus accessory files (linguistic variants in 13 languages, answer lists, component hierarchies, IEEE/RSNA mappings). Best for building a local normalisation table; ~semiannual major releases.
- **SearchLOINC / Hierarchy Browser** (web UI): interactive lookup, login required, not for programmatic use.

Rate limits are not published. Treat the FHIR server as best-effort; for bulk or high-volume normalisation, load the downloaded file locally rather than hammering the BETA server.

## MCP / connector notes

No dedicated LOINC MCP found (checked modelcontextprotocol/servers, GitHub, npm, PyPI). High value: lab-test normalisation is a cross-cutting need for healthcare, claims, public-health, and clinical-trial entries in this directory, so one connector would serve several audiences. Suggested surface: `lookup_code` (code to component/property/units), `search_terms` (free-text to candidate LOINC codes), `expand_valueset`, `translate_code` (LOINC to/from SNOMED/other), and a `normalise_lab_name` helper that wraps search + best-match ranking. The connector must abstract over the two backends (BETA FHIR server vs. a locally loaded release file) and handle HTTP Basic auth from env vars, since the FHIR server is not guaranteed available.

## Review notes

- **License short name.** LOINC is distributed under the LOINC License (free, permissive, requires the copyright/attribution notice; `LoincLicense_5.8.txt` ships in the download). No SPDX code exists. Used the canonical short name `LOINC-License` in the `license` field; confirm/adopt this short name in the license conventions list.
- Potential new join key for review: `LOINC_CODE`
  - Entity type: lab_test_or_clinical_observation
  - Pattern: `^[0-9]{1,5}-[0-9]$` (numeric body plus a Mod-10 check digit, e.g. `2951-2`, `718-7`)
  - Other datasets that would use it: any EHR/FHIR Observation feed, electronic lab reporting (public-health), claims-linked lab result data, clinical-trial lab datasets. Source-native here, but broad cross-source utility argues for promotion to the canonical registry.
- Potential new join key for review: `UMLS_CUI`
  - Entity type: biomedical_concept
  - Pattern: `^C[0-9]{7}$` (e.g. `C0202041`)
  - Other datasets that would use it: UMLS Metathesaurus cross-walks LOINC, SNOMED CT, ICD, MeSH, RxNorm; a shared `UMLS_CUI` would let those terminology sources join. Not exposed directly by LOINC's own files (LOINC codes are mapped in UMLS, not the reverse), so utility is registry-wide rather than LOINC-specific.
- **Domain call.** Placed in `clinical-biotech` alongside other clinical reference sources (DailyMed, openFDA, Orange Book). `healthcare-claims` and `public-health` are defensible alternatives given LOINC's role in claims/EHR and lab-reporting normalisation; move if the registry prefers a coding-vocabulary home there.
- `access_test` constructed but not executed: the FHIR server requires a free LOINC account (HTTP Basic), no public no-auth endpoint exists.
