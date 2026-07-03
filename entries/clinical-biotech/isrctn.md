---
id: isrctn
name: ISRCTN Registry
domain: clinical-biotech
entry_kind: registry
description: WHO- and ICMJE-recognised primary clinical study registry for interventional and non-interventional studies, focused on studies involving UK participants but open to global registration, run by BioMed Central (Springer Nature).
homepage_url: https://www.isrctn.com/
docs_url: https://www.isrctn.com/page/faqs
type:
  - rest-api
  - web-ui
  - bulk-download
auth_required: none
cost: free
license: CC0
rate_limit: "no published quota; documented as polite, low-volume public use"
bulk_available: true
frequency: continuous
lag: "sponsor-driven; records appear once registered and editorially curated, typically days after submission"
geography: [global]
join_keys:
  - NCT_ID
  - WHO_UTN
  - EUDRACT_NUMBER
  - DOI
primary_keys:
  - ISRCTN_ID
join_key_fields:
  - join_key: NCT_ID
    fields: [trial.externalRefs.clinicalTrialsGovNumber]
  - join_key: WHO_UTN
    fields: [utrn]
  - join_key: EUDRACT_NUMBER
    fields: [trial.externalRefs.eudraCTNumber]
  - join_key: DOI
    fields: [trial.externalRefs.doi]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No official or community MCP. Stable public XML API (query-all and single-trial retrieve),
  no auth. Suggested surface: search_trials, get_trial, cross_registry_lookup (ISRCTN to NCT,
  EudraCT, WHO UTN via externalRefs), get_results_summary. MCP should parse the 67bricks XML
  namespace and normalise the four output formats (default, who, ukctg, internal).
agent_use_cases:
  - UK clinical trial discovery by condition or intervention
  - cross-registry deduplication with ClinicalTrials.gov and EU CTIS
  - non-commercial and publicly funded study lookup
  - results and plain-English-summary retrieval
  - pipeline and sponsor monitoring for UK research
access_test:
  command: "curl -sf 'https://www.isrctn.com/api/query/format/default?q=condition:cancer&limit=1'"
  expected_status: 200
  expected_fields: [allTrials, fullTrial, isrctn, externalRefs]
last_verified: 2026-07-02
build_priority: medium
structure: registry-snapshot
revisions_possible: true
notes: "Public XML API base is https://www.isrctn.com/api/query/. Single trials also resolve as HTML/DOI at https://www.isrctn.com/ISRCTN{n} and https://doi.org/10.1186/ISRCTN{n}."
---

# ISRCTN Registry

## Why this source matters

ISRCTN (International Standard Randomised Controlled Trial Number) is a WHO ICTRP primary registry and an ICMJE-recognised trial registry, operated by BioMed Central (Springer Nature) with UK governance and funding from the NHS Health Research Authority, NIHR, the Department of Health and Social Care, and Wellcome. It registers interventional and non-interventional clinical studies, with an explicit remit for studies that prospectively involve UK participants, though it accepts global and non-clinical registrations too. Because it is a WHO primary registry, its records flow upstream into the WHO global trial graph, making it the UK-centric complement to ClinicalTrials.gov (US) and EU CTIS (EEA). Every record is minted a persistent ISRCTN number and a Crossref DOI, and records include plain-English summaries, protocol details, and (increasingly) posted results. Secondary domain: public-health, for the large volume of publicly funded UK health-services and prevention studies.

## Agent use cases

- UK clinical trial discovery by condition or intervention
- cross-registry deduplication with ClinicalTrials.gov and EU CTIS
- non-commercial and publicly funded study lookup
- results and plain-English-summary retrieval
- pipeline and sponsor monitoring for UK research

## Join strategy

The source-native primary key is the ISRCTN number (`ISRCTN` followed by 8 digits, e.g. `ISRCTN11867516`), carried in `trial.@publicIdentifierCanonical` and the `<isrctn>` element. It is not yet a canonical registry key; see Review notes.

Canonical join keys live in the `<externalRefs>` block of each record: `NCT_ID` in `clinicalTrialsGovNumber`, `EUDRACT_NUMBER` in `eudraCTNumber`, and `DOI` in `doi`. The DOI is ISRCTN's own record DOI in the `10.1186/ISRCTN{n}` subspace (Crossref, BMC), so it joins to OpenAlex, Crossref, and Europe PMC where the trial record itself is cited. `WHO_UTN` is exposed as `utrn` in the WHO output format (`/format/who`) when the sponsor supplied a Universal Trial Number; population is sparse.

Recommended pairings: ClinicalTrials.gov and EU CTIS for cross-registry dedup (`NCT_ID`, `EUDRACT_NUMBER`, `WHO_UTN`); WHO ICTRP as the umbrella graph; OpenAlex or Europe PMC to reach the trial's associated publications (ISRCTN does not itself expose `PMID`). Note the `externalRefs` fields are frequently empty, since many UK studies register only in ISRCTN, so cross-registry coverage is partial.

## Access notes

Public XML API, no auth, no API key. Two calls:

- **Query many:** `GET https://www.isrctn.com/api/query/format/{fmt}?q={query}&limit={n}&offset={m}`. Free-text `q=diabetes` and field-scoped `q=condition:cancer` both work; `limit`/`offset` paginate. The response root is `<allTrials totalCount="...">` with repeated `<fullTrial>` children in the `http://www.67bricks.com/isrctn` namespace.
- **Single trial:** query with the ISRCTN number as free text, or resolve the human page `https://www.isrctn.com/ISRCTN{n}` (also mirrored at `https://doi.org/10.1186/ISRCTN{n}`).

Four output formats select the field set: `default` (full ISRCTN schema), `who` (WHO ICTRP flat schema, includes `utrn` and `secondary_ids`), `ukctg` (UK Clinical Trials Gateway), and `internal`. Search-result CSV export is available via the web UI for lightweight bulk pulls; for the full corpus, paginate the query API and persist locally. No published rate limit, so batch politely and set a `User-Agent`.

Known gotchas:

- The API documentation is a draft (linked from the FAQs page, `bit.ly/ISRCTN_APIdoc_v0_6`); field paths verified empirically against live responses, not a formal contract.
- Field-scoped query field names are non-obvious (`condition:` works, `trial_id:` returns 0); use free-text for ID lookups.
- `externalRefs` cross-registry fields are often empty; absence does not prove single-registration.
- Records are versioned (`@version`, `@lastUpdated`) and edited after publication, so treat values as revisable.

## MCP / connector notes

No official or community MCP. High-value gap: a general clinical-trials MCP (or an extension of a BioMCP-style multi-registry server) that unifies ClinicalTrials.gov, EU CTIS, and ISRCTN under one cross-registry interface would serve three or more entries in this directory. Suggested surface:

- `search_trials(condition, intervention, sponsor, status, limit, offset)` - wraps the query API, normalises pagination and the 67bricks namespace.
- `get_trial(isrctn)` - fetches and flattens one record across formats.
- `cross_registry_lookup(isrctn)` - reads `externalRefs` (NCT, EudraCT) and `utrn`, optionally resolving to ClinicalTrials.gov and CTIS.
- `get_results_summary(isrctn)` - surfaces posted results and the plain-English summary for downstream LLM use.

The MCP must abstract over the four output formats, the XML namespace, and the empty-field-vs-absent ambiguity.

## Review notes

- Potential new join key for review: `ISRCTN_ID`
  - Entity type: clinical_trial
  - Pattern: `^ISRCTN[0-9]{8}$` (canonical form; the `<isrctn>` element holds the bare 8-digit body)
  - Other datasets that would use it: WHO ICTRP, ClinicalTrials.gov (as a secondary/related registry id), Europe PMC and OpenAlex (trial IDs in publication metadata), EU CTIS (secondary identifiers). Recommend PR-ing into `schema/join-keys.yaml` alongside the existing `NCT_ID`, `EU_CT_NUMBER`, `EUDRACT_NUMBER`, `WHO_UTN` clinical-registry keys.
- `EUDRACT_NUMBER` was added to `join_keys` beyond the supplied hints because the source exposes a dedicated `<eudraCTNumber>` element in `externalRefs` and the key already exists in the registry. Flag if the project wants the entry restricted strictly to the hinted keys (NCT_ID, WHO_UTN, DOI).
- `license: CC0` reflects the dominant case: metadata for contributions submitted on or after 1 Jan 2019 is reusable without restriction on a CC0 basis. Narrative elements (plain-English summary, study objectives, interventions, outcome measures, results) are CC-BY, and pre-2019 records may carry legacy terms. Nuance kept in Access notes per SCHEMA conventions; flag if a compound `CC0-with-CC-BY-narrative` short name is preferred.
- The XML API endpoints and `externalRefs` field paths are verified empirically against live 200 responses, not from a stable published API contract (docs are marked draft). Re-verify after any registry platform update.
