---
id: eu-ctis
name: EU CTIS (Clinical Trials Information System)
domain: clinical-biotech
entry_kind: registry
description: EU and EEA single-entry-point registry for clinical trials of human medicines under Regulation 536/2014, run by the European Medicines Agency in cooperation with member states and the European Commission.
homepage_url: https://euclinicaltrials.eu/
docs_url: https://euclinicaltrials.eu/about-this-website/
type:
  - rest-api
  - web-ui
auth_required: none
cost: free
license: EU-Commission-Reuse-Decision-2011-833
rate_limit: "no published quota; documented as polite, low-volume public use"
bulk_available: false
frequency: continuous
lag: "sponsor-driven; new trial records and decisions appear once the relevant member state publishes them, typically within days of authorisation"
geography: [global]
join_keys:
  - EU_CT_NUMBER
  - EUDRACT_NUMBER
  - WHO_UTN
primary_keys:
  - EU_CT_NUMBER
  - CTIS_PART_ONE_ID
  - CTIS_PRODUCT_PK
  - EU_MP_NUMBER
join_key_fields:
  - join_key: EU_CT_NUMBER
    fields: [ctNumber, authorizedApplication.applicationInfo.ctNumber]
  - join_key: EUDRACT_NUMBER
    fields: [authorizedApplication.eudraCt.eudraCtCode, authorizedApplication.authorizedPartI.trialDetails.clinicalTrialIdentifiers.secondaryIdentifyingNumbers.additionalRegistries.number]
  - join_key: WHO_UTN
    fields: [authorizedApplication.authorizedPartI.trialDetails.clinicalTrialIdentifiers.secondaryIdentifyingNumbers.additionalRegistries.number]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No official or community MCP. API is undocumented but stable JSON over HTTPS (POST search,
  GET retrieve). Suggested surface: search_trials, get_trial, list_decisions_by_country,
  cross_registry_lookup (EU CT to EudraCT and NCT via secondary identifiers), get_protocol_part_one.
agent_use_cases:
  - EU clinical trial discovery by condition or product
  - sponsor and CRO lookup across EEA
  - regulatory decision timeline tracking
  - cross-registry deduplication with ClinicalTrials.gov and ISRCTN
  - pipeline monitoring for European biotech and pharma
access_test:
  command: "curl -sf -X POST -H 'Content-Type: application/json' -d '{\"pagination\":{\"page\":1,\"size\":1},\"searchCriteria\":{\"containAll\":\"\",\"containAny\":\"\",\"containNot\":\"\"}}' 'https://euclinicaltrials.eu/ctis-public-api/search'"
  expected_status: 200
  expected_fields: [pagination, data]
last_verified: 2026-06-08
build_priority: high
notes: "Public API endpoints (/ctis-public-api/search, /ctis-public-api/retrieve/{ctNumber}) are not formally documented by EMA; verified empirically and used by the official ctis-public web UI."
---

# EU CTIS (Clinical Trials Information System)

## Why this source matters

EMA's single portal for clinical trial applications, authorisations, and supervision across the EU and EEA, mandated by Regulation (EU) No 536/2014 and live since 31 January 2022. Sponsors submit one application covering up to 30 countries; member-state competent authorities and ethics committees coordinate through the system; the public layer publishes protocol Part I, sponsor metadata, recruitment status, decision dates per country, and (once the transition from EudraCT completes) trial results. For any agent reasoning about European drug development, regulatory timelines, or cross-jurisdiction trial design, CTIS is the canonical European counterpart to ClinicalTrials.gov. CTIS is also a WHO ICTRP primary registry, so its records flow upstream into the WHO global trial graph.

## Agent use cases

- EU clinical trial discovery by condition or product
- sponsor and CRO lookup across EEA
- regulatory decision timeline tracking
- cross-registry deduplication with ClinicalTrials.gov and ISRCTN
- pipeline monitoring for European biotech and pharma

## Join strategy

The canonical key is `EU_CT_NUMBER` (`^[0-9]{4}-[0-9]{6}-[0-9]{2}-[0-9]{2}$`), exposed as `ctNumber` in every record. Trials that originated under the prior Directive 2001/20/EC carry a legacy `EUDRACT_NUMBER` (`^[0-9]{4}-[0-9]{6}-[0-9]{2}$`) in the secondary-identifier fields, useful for cross-walking to the EU Clinical Trials Register (EUDRACT) and to records in ClinicalTrials.gov where US and EU sponsors dual-registered. `WHO_UTN` appears for trials that obtained a Universal Trial Number, supporting joins to ISRCTN, JPRN, ANZCTR, and other ICTRP primary registries.

CTIS-internal identifiers (`authorizedPartI.id`, product `productPk`, `euMpNumber` such as `PRD10997227`) are not in the canonical registry; use them for direct CTIS traversal, not cross-source joins.

Common pairings: ClinicalTrials.gov (deduplicate via `EU_CT_NUMBER` in `secondaryIdInfos`), WHO ICTRP (via `WHO_UTN`), EMA EPAR / OpenFDA (post-marketing safety for authorised products), OpenAlex or PubMed (publications by sponsor or product name; CTIS does not currently expose `PMID`).

## Access notes

The public web UI lives at `https://euclinicaltrials.eu/ctis-public/`. Its backing API is undocumented but stable and JSON-only over HTTPS:

- **Search:** `POST https://euclinicaltrials.eu/ctis-public-api/search` with a JSON body containing `pagination` (`page`, `size`) and `searchCriteria` (`containAll`, `containAny`, `containNot`). Empty criteria returns the full corpus (~11,700 records and growing). Sort via `sort.property` + `sort.direction`.
- **Single record:** `GET https://euclinicaltrials.eu/ctis-public-api/retrieve/{ctNumber}` returns the full authorised application (Part I, products, sponsors, decision metadata).
- No auth, no API key, no published rate limit. Treat as low-volume public infrastructure: batch politely, cache, identify the client via `User-Agent`.
- No bulk download. For analytical workloads, paginate the search endpoint (size capped around 100 per page in practice) and persist locally.

Known gotchas:

- The API surface is not contractually stable; EMA can change response shapes without notice. Pin against `last_verified` and re-check after major CTIS portal releases.
- Some commercially sensitive Part I content is deferred under Article 81(4) of the Regulation; absence of a field does not mean the trial lacks that attribute.
- Decision dates are reported per country (`decisionDate: "ES: 07/05/2024"`) and as an overall date; parse both.
- Date format in list responses is `DD/MM/YYYY`; the retrieve endpoint uses ISO 8601. Normalise client-side.
- Results-section coverage is still ramping; the EUDRACT-to-CTIS transition for legacy trials completed in 2025, so older trials may live only in the legacy EU Clinical Trials Register at `clinicaltrialsregister.eu`.

## MCP / connector notes

No official or community MCP. High-value gap: every agent doing European clinical or regulatory work hits this source, and the undocumented API plus inconsistent date and decision-per-country shapes are exactly the friction an MCP should absorb. Suggested surface:

- `search_trials(condition, product, sponsor, status, country, page)` — wraps the POST search, normalises pagination.
- `get_trial(ctNumber)` — wraps retrieve, flattens Part I and product subdocuments.
- `list_decisions_by_country(ctNumber)` — parses the per-country decision strings into structured rows.
- `cross_registry_lookup(ctNumber)` — pulls secondary identifiers (`EUDRACT_NUMBER`, `WHO_UTN`, sponsor codes) and optionally resolves to ClinicalTrials.gov by NCT lookup.
- `get_protocol_part_one(ctNumber)` — surfaces the public protocol summary cleanly for downstream LLM consumption.

The MCP should pin a `User-Agent`, implement response-shape version detection, and degrade gracefully when EMA changes field names.

## Review notes

- `license`: CTIS does not publish a standalone SPDX-style licence statement. EMA content generally falls under Commission Decision 2011/833/EU on reuse of Commission documents (attribution, no endorsement implied), which has no SPDX code. Used `EU-Commission-Reuse-Decision-2011-833` as a canonical short name consistent with SCHEMA.md conventions. Flag if the project prefers a different canonical string (e.g. `EMA-Reuse-Policy` or `CC-BY-4.0` if EMA confirms a Creative Commons mapping for CTIS specifically).
- The CTIS public API endpoints (`/ctis-public-api/search`, `/ctis-public-api/retrieve/{ctNumber}`) are not formally documented by EMA. They are inferred from the official ctis-public web UI's network calls and verified empirically (search returns ~11,700 records, retrieve returns full Part I JSON). If EMA publishes formal API docs later, update `docs_url` and re-verify field stability.
- `bulk_available: false` reflects the absence of a published bulk dump. Paginated extraction of the full corpus is feasible but not officially sanctioned; flag if the project wants a stricter interpretation that excludes scrape-style bulk reconstruction.
- `WHO_UTN` is included in `join_keys` because CTIS captures it when sponsors supply it, though population is not universal. Confirm this matches the project's inclusion threshold (key present in the source but sparsely populated).
