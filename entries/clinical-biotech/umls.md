---
id: umls
name: UMLS Metathesaurus
domain: clinical-biotech
entry_kind: knowledge-graph
description: NLM's Unified Medical Language System Metathesaurus, a concept graph that crosswalks 200+ biomedical vocabularies (SNOMED CT, RxNorm, LOINC, ICD-10, MeSH, CPT) under shared Concept Unique Identifiers.
homepage_url: https://www.nlm.nih.gov/research/umls/index.html
docs_url: https://documentation.uts.nlm.nih.gov/rest/home.html
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: account-required
cost: free-with-registration
license: UMLS-License
bulk_available: true
frequency: "biannual (AA release ~May, AB release ~November)"
geography: [global]
join_keys:
  - MESH_TERM
  - ICD_10
  - RXNORM_CUI
  - CPT
  - HCPCS
  - MEDDRA_TERM
  - ATC_CODE
  - UMLS_CUI
  - SNOMED_CT_ID
  - LOINC_CODE
primary_keys:
  - UMLS_CUI
  - UMLS_AUI
  - UMLS_LUI
  - UMLS_SUI
  - UMLS_TUI
join_key_fields:
  - join_key: MESH_TERM
    fields:
      - "atoms.code (rootSource=MSH)"
      - "search/current?sabs=MSH&returnIdType=code -> result.ui"
  - join_key: ICD_10
    fields:
      - "atoms.code (rootSource=ICD10CM or ICD10)"
      - "search/current?sabs=ICD10CM&returnIdType=code -> result.ui"
  - join_key: RXNORM_CUI
    fields:
      - "atoms.code (rootSource=RXNORM)"
      - "search/current?sabs=RXNORM&returnIdType=code -> result.ui"
  - join_key: CPT
    fields:
      - "atoms.code (rootSource=CPT)"
  - join_key: HCPCS
    fields:
      - "atoms.code (rootSource=HCPCS)"
  - join_key: MEDDRA_TERM
    fields:
      - "atoms.code (rootSource=MDR)"
  - join_key: ATC_CODE
    fields:
      - "atoms.code (rootSource=ATC)"
mcp_status: mcp-exists
mcp_maturity: experimental
mcp_package:
  - "github.com/geneialco/umls-server"
mcp_notes: >
  Community two-tier server (FastAPI wrapper + stdio MCP for Claude Desktop). Exposes
  term search, CUI lookup, CUI detail, and ancestor traversal. Requires the operator's
  own UMLS API key; not an official NLM connector.
agent_use_cases:
  - normalise a diagnosis or drug string to a CUI
  - crosswalk ICD-10 to SNOMED CT or MeSH
  - map RxNorm to ATC drug class
  - expand a concept via synonyms and hierarchy
  - resolve source-asserted codes across vocabularies
access_test:
  command: "curl -sf 'https://uts-ws.nlm.nih.gov/rest/content/current/CUI/C0009044?apiKey=${UMLS_API_KEY}'"
  expected_status: 200
  expected_fields: [pageCount, result]
last_verified: 2026-07-02
build_priority: high
notes: "access_test not yet executed; requires ${UMLS_API_KEY} from a UTS profile."
---

# UMLS Metathesaurus

## Why this source matters

The Unified Medical Language System (UMLS) Metathesaurus is the National Library of Medicine's master crosswalk for biomedical terminology. It ingests 200+ source vocabularies, SNOMED CT, RxNorm, LOINC, ICD-10-CM, MeSH, CPT, HCPCS, MedDRA, ATC, Gene Ontology, and assigns every synonymous term across them a shared Concept Unique Identifier (CUI). That makes it the canonical hub for normalising free-text clinical language and for translating a code in one vocabulary into the equivalent code in another. Any agent working across clinical, drug, or disease datasets that use different coding systems needs this as the join layer. Secondary relevance to `healthcare-claims` (it carries the ICD-10-CM / CPT / HCPCS billing vocabularies) and `public-health` (disease and adverse-event terminologies).

## Agent use cases

- normalise a diagnosis or drug string to a CUI
- crosswalk ICD-10 to SNOMED CT or MeSH
- map RxNorm to ATC drug class
- expand a concept via synonyms and hierarchy
- resolve source-asserted codes across vocabularies

## Join strategy

UMLS is a crosswalk source: its value is that one CUI aggregates the codes from every source vocabulary. Canonical registry keys it exposes include `MESH_TERM`, `ICD_10`, `RXNORM_CUI`, `CPT`, `HCPCS`, `MEDDRA_TERM`, and `ATC_CODE`, each carried as an atom `code` namespaced by its `rootSource` (SAB) value (MSH, ICD10CM, RXNORM, CPT, HCPCS, MDR, ATC). Use the `/search` endpoint with `returnIdType=code&sabs=<SAB>` to pull the source-asserted code for a concept, or `/crosswalk` to jump directly from a code in one vocabulary to codes in another.

The CUI itself (`UMLS_CUI`, pattern `^C[0-9]{7}$`) is the source-internal primary key and the single most useful cross-source identifier UMLS mints, but it is not yet in the canonical registry, so it lives in `primary_keys` and is flagged below. Atom (`UMLS_AUI`), lexical (`UMLS_LUI`), string (`UMLS_SUI`), and semantic-type (`UMLS_TUI`) IDs are also source-internal. SNOMED CT and LOINC codes are exposed by UMLS but have no canonical key yet; both are flagged below.

## Access notes

Hit `GET https://uts-ws.nlm.nih.gov/rest/content/current/CUI/{cui}?apiKey=...` first for a single-concept fetch. Auth is a personal API key found in the UTS "My Profile" area after your UMLS license is approved (free in the US, issued to individuals, not organisations). Pass it as the `apiKey` query parameter on every call; older ticket-granting-ticket auth is deprecated. Key endpoints: `/search/current` (string or code lookup, filter with `sabs` and `returnIdType`), `/content/current/CUI/{cui}` and its `/atoms`, `/relations`, `/definitions` sub-resources, `/crosswalk/current/source/{sab}/{code}`, and the semantic-network `/semantic-network`. For large-scale work, download the full release files (RRF) and load them locally with MetamorphoSys into MySQL or Oracle rather than paginating the API; releases ship twice a year (AA ~May, AB ~November).

## MCP / connector notes

A community MCP exists (`github.com/geneialco/umls-server`): a FastAPI wrapper plus a stdio MCP server for Claude Desktop, offering term search, CUI-by-term search, CUI detail, and ancestor retrieval. It is experimental and requires the operator to supply their own UMLS API key. A stronger connector would abstract over the SAB soup: expose `normalise_term -> CUI`, `crosswalk(code, from_sab, to_sab)`, `get_atoms(cui, sabs)`, `get_relations(cui)`, and `get_semantic_types(cui)`, handling the license-gated key transparently and trimming the verbose atom payloads.

## Review notes

License short name `UMLS-License` is not an SPDX code and is not in SCHEMA.md's known-short-name list. It refers to the UMLS Metathesaurus License Agreement (free, individual, US-no-charge, redistribution and vendor-agreement restrictions on some source vocabularies such as SNOMED CT and CPT). Flagging for a canonical short-name decision.

Potential new join keys for review:

- UMLS_CUI
  - Entity type: biomedical_concept
  - Pattern: ^C[0-9]{7}$
  - Other datasets that would use it: DisGeNET, MedGen, Open Targets, MetaMap/cTAKES NLP output, many biomedical KGs reference CUIs directly.

- SNOMED_CT_ID
  - Entity type: clinical_concept
  - Pattern: ^[0-9]{6,18}$ (SNOMED CT SCTID)
  - Other datasets that would use it: SNOMED CT International/US editions, NHS clinical data, ICD-10-to-SNOMED maps, many EHR-derived sources.

- LOINC_CODE
  - Entity type: lab_or_clinical_observation
  - Pattern: ^[0-9]{1,5}-[0-9]$
  - Other datasets that would use it: LOINC, lab result feeds, FHIR observation coding, HL7 messages.
