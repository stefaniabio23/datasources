---
id: ohdsi-athena
name: OMOP / OHDSI Athena
domain: clinical-biotech
entry_kind: knowledge-graph
description: OHDSI's distribution point for the OMOP Standardized Vocabularies, a centralized crosswalk of 100+ medical terminologies (SNOMED, ICD-10, RxNorm, LOINC, NDC) mapped to standard OMOP concept IDs.
homepage_url: https://athena.ohdsi.org/
docs_url: https://ohdsi.github.io/TheBookOfOhdsi/StandardizedVocabularies.html
type:
  - bulk-download
  - unofficial-api
  - web-ui
auth_required: account-required
cost: free-with-registration
license: mixed-vocabulary-licenses
bulk_available: true
frequency: quarterly
geography: [global]
join_keys:
  - RXNORM_CUI
  - ICD_10
  - NDC
  - ATC_CODE
  - HCPCS
  - CPT
  - MESH_TERM
  - MEDDRA_TERM
  - OMOP_CONCEPT_ID
  - SNOMED_CT_ID
  - LOINC_CODE
primary_keys:
  - OMOP_CONCEPT_ID
join_key_fields:
  - join_key: RXNORM_CUI
    fields: ["concept_code (vocabulary_id=RxNorm)"]
  - join_key: ICD_10
    fields: ["concept_code (vocabulary_id in ICD10CM/ICD10/ICD10PCS)"]
  - join_key: NDC
    fields: ["concept_code (vocabulary_id=NDC)"]
  - join_key: ATC_CODE
    fields: ["concept_code (vocabulary_id=ATC)"]
  - join_key: HCPCS
    fields: ["concept_code (vocabulary_id=HCPCS)"]
  - join_key: CPT
    fields: ["concept_code (vocabulary_id=CPT4)"]
  - join_key: MESH_TERM
    fields: ["concept_code (vocabulary_id=MeSH)"]
  - join_key: MEDDRA_TERM
    fields: ["concept_code (vocabulary_id=MedDRA)"]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/OHNLP/omop_mcp"
  - "github.com/fastomop/omcp"
mcp_notes: >
  Community MCPs target the OMOP CDM / vocabulary layer generally, not the Athena
  distribution API specifically. OHNLP/omop_mcp exposes find_omop_concept for
  mapping clinical terminology to OMOP concepts with vocabulary priority ordering;
  fastomop/omcp queries an OMOP CDM instance. No connector wraps Athena's own
  (undocumented, WAF-gated) search API.
agent_use_cases:
  - medical code crosswalk
  - terminology normalization to standard concepts
  - drug and condition code mapping
  - vocabulary hierarchy traversal
  - standard-concept lookup
structure: registry-snapshot
revisions_possible: true
last_verified: 2026-07-02
build_priority: high
notes: >
  The athena.ohdsi.org/api/v1 JSON backend is undocumented and WAF/bot-gated:
  plain curl returns 403 (browse UI and the community athena-client Python SDK
  reach it from a browser-like session). No executable access_test could be
  confirmed at 200. Primary programmatic path is the account-gated bulk
  vocabulary CSV bundle.
---

# OMOP / OHDSI Athena

## Why this source matters

Athena is the download and browse portal for the OMOP Standardized Vocabularies, maintained by OHDSI (Observational Health Data Sciences and Informatics). It packages 100+ source vocabularies (over 10 million concepts, quarterly refreshed) into a single normalized schema where every clinical code, drug, condition, procedure, lab, device, is assigned a meaningless integer `concept_id` and cross-linked via `CONCEPT_RELATIONSHIP` ("Maps to") and `CONCEPT_ANCESTOR` (hierarchy). This makes it the reference crosswalk that lets an agent translate between SNOMED, ICD-10-CM, RxNorm, LOINC, NDC, HCPCS, CPT-4, ATC, MeSH, and MedDRA without building the mapping tables itself. Secondary domains: `healthcare-claims` (ICD-10/HCPCS/CPT/NDC are the administrative-claims coding backbone) and `public-health` (the OMOP CDM underpins observational-health networks like All of Us, N3C, and DARWIN EU).

## Agent use cases

- medical code crosswalk
- terminology normalization to standard concepts
- drug and condition code mapping
- vocabulary hierarchy traversal
- standard-concept lookup

## Join strategy

Athena's value is that it holds many external code systems in one table keyed by `concept_id`. External codes live in the `concept_code` column, disambiguated by `vocabulary_id`. Canonical registry keys it exposes via `concept_code`: `RXNORM_CUI` (vocabulary_id=RxNorm), `ICD_10` (ICD10CM / ICD10 / ICD10PCS), `NDC`, `ATC_CODE`, `HCPCS`, `CPT` (CPT4; descriptions require a separate UMLS key, codes ship), `MESH_TERM` (MeSH), `MEDDRA_TERM` (MedDRA). Use Athena as the hub to resolve any of these into a standard concept, then join outward to sources keyed on the same identifier (RxNorm to DailyMed/openFDA, ICD-10 to claims, ATC to drug-class analytics).

Athena's native `concept_id` (`OMOP_CONCEPT_ID`) is the primary key inside every OMOP CDM instance; it is source-internal here but has strong cross-source utility because every OHDSI dataset references it. It is flagged as a new-join-key candidate below, along with `SNOMED` and `LOINC`, which Athena carries but the registry does not yet define.

## Access notes

Browsing and searching is public at `athena.ohdsi.org`. Downloading vocabulary bundles requires a free account (email-validated); a work email is needed to request license-restricted vocabularies (SNOMED, CPT-4, MedDRA, etc.), which OHDSI does not redistribute freely and which are usable only inside an OMOP CDM. CPT-4 descriptions must be merged post-download via the provided utility using your own UMLS API key.

The `athena.ohdsi.org/api/v1` JSON backend (e.g. `/concepts?query=`, `/concepts/{id}`) is undocumented and sits behind bot protection: plain `curl` returns `403 Forbidden` regardless of headers. The AthenaUI front end and the community `athena-client` Python SDK reach it from browser-like sessions. To verify freshness without the API, check the latest vocabulary release on the OHDSI/Athena GitHub releases page or the version banner on the Athena download screen (releases are roughly quarterly).

## MCP / connector notes

Community MCPs exist for the OMOP layer but none wraps Athena's distribution API directly. `OHNLP/omop_mcp` exposes `find_omop_concept` to map free-text or coded clinical terminology to OMOP concepts with vocabulary-priority ordering (e.g. "SNOMED > LOINC > RxNorm"), backed by an LLM; `fastomop/omcp` (OMCP) queries a live OMOP CDM database instance. A purpose-built Athena connector would abstract over the WAF-gated search API and the account-gated bulk download, exposing: `search_concepts` (name/code, filter by vocabulary/domain/standard-flag), `get_concept`, `map_code` (source code + vocabulary to standard concept via "Maps to"), `get_descendants`/`get_ancestors` (CONCEPT_ANCESTOR), and `list_vocabularies`.

## Review notes

License field uses a non-SPDX short name `mixed-vocabulary-licenses` (new candidate, not in SCHEMA.md's known list): the OMOP vocabulary bundle is not one license. Structure and tooling are open, but each source vocabulary carries its own terms (SNOMED via UMLS/national licenses, CPT-4 via AMA, MedDRA via license), several restricted to use inside an OMOP CDM and not for individual patient care. Stephanie to decide whether to canonicalize this short name or split license nuance elsewhere.

Potential new join keys for review:

- Proposed key: `OMOP_CONCEPT_ID`
  - Entity type: standardized_clinical_concept
  - Pattern: integer (`^[0-9]+$`)
  - Other datasets that would use it: every OMOP CDM instance and OHDSI network study (All of Us, N3C, DARWIN EU); the canonical primary key across the OMOP ecosystem.

- Proposed key: `SNOMED` (SNOMED CT concept id)
  - Entity type: clinical_concept
  - Pattern: integer SCTID (`^[0-9]{6,18}$`)
  - Other datasets that would use it: EHR-derived sources, ICD-to-SNOMED crosswalks, clinical registries. Carried in Athena as `concept_code` where vocabulary_id=SNOMED.

- Proposed key: `LOINC`
  - Entity type: lab_or_measurement_code
  - Pattern: `^[0-9]{1,5}-[0-9]$`
  - Other datasets that would use it: lab/measurement data, EHR observation tables. Carried in Athena as `concept_code` where vocabulary_id=LOINC.
