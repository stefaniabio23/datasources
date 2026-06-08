---
id: clinicaltrials-gov
name: ClinicalTrials.gov
domain: clinical-biotech
description: US federal registry and results database of publicly and privately supported clinical studies conducted globally, run by the National Library of Medicine.
homepage_url: https://clinicaltrials.gov/
docs_url: https://clinicaltrials.gov/data-api/api
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "no published hard cap; documentation requests reasonable use, batching, and caching"
bulk_available: true
frequency: daily
lag: "registration and results updates depend on sponsor submission cadence; index refresh within ~24h"
geography: [global]
join_keys:
  - NCT_ID
  - EUDRACT_NUMBER
  - EU_CT_NUMBER
  - PMID
  - MESH_TERM
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cyanheads/clinicaltrialsgov-mcp-server
  - github.com/navisbio/AACT_clinicaltrials_MCP
mcp_notes: >
  Multiple community MCPs wrap API v2 (cyanheads, JackKuo666, agents100x, aafjes, pipeworx-io,
  navisbio AACT variant). None are official. Most expose search_studies and get_study; few
  cover eligibility-criteria parsing or results-section traversal well.
agent_use_cases:
  - clinical trial discovery by condition or intervention
  - sponsor and investigator lookup
  - eligibility-criteria parsing for patient matching
  - results and adverse-event extraction
  - drug-pipeline and competitor scan
access_test:
  command: "curl -sf 'https://clinicaltrials.gov/api/v2/studies/NCT04280705?format=json'"
  expected_status: 200
  expected_fields: [protocolSection, resultsSection, derivedSection, hasResults]
last_verified: 2026-06-08
build_priority: medium
---

# ClinicalTrials.gov

## Why this source matters

The US National Library of Medicine's registry of clinical studies, mandated by FDAAA 801 and ICMJE policy. ~500K studies across ~220 countries, with structured protocol sections, results when reported, sponsor and investigator metadata, and condition/intervention coding. For any agent reasoning about drug pipelines, trial feasibility, patient matching, or competitive intelligence in biotech, this is the canonical starting point. Public domain, free, no auth. Secondary relevance to `public-health` for epidemiology of intervention coverage.

## Agent use cases

- clinical trial discovery by condition or intervention
- sponsor and investigator lookup
- eligibility-criteria parsing for patient matching
- results and adverse-event extraction
- drug-pipeline and competitor scan

## Join strategy

The canonical key is `NCT_ID` (`^NCT[0-9]{8}$`), which propagates into PubMed, FDA labels, OpenFDA adverse-event reports, and most downstream biomedical sources. `secondaryIdInfos` in the protocol section frequently exposes `EUDRACT_NUMBER` and the newer `EU_CT_NUMBER` (CTIS) for cross-registry deduplication, plus sponsor-internal study codes. `referencesModule` lists `PMID` values for related publications. `conditionsModule` and `derivedSection.conditionBrowseModule` emit `MESH_TERM` values for condition tagging.

Common pairings: OpenFDA (adverse events by NCT or drug name), PubMed/OpenAlex (publications via PMID), DrugBank or RxNorm (interventions to drug concepts), EU CTIS (deduplicate EU trials via `EU_CT_NUMBER`).

## Access notes

Hit `https://clinicaltrials.gov/api/v2/studies/{NCT_ID}?format=json` for a single trial, or `/api/v2/studies?query.cond=...&query.term=...&pageSize=...&pageToken=...` for search. No auth, JSON or CSV, server-side pagination via `nextPageToken`. The `fields=` parameter trims the verbose response; useful when grabbing only identifiers and status. For bulk pulls, prefer the `/api/v2/studies/download` endpoint (zipped JSON or CSV of the whole registry, ~hundreds of MB) over deep-paginating. The community-maintained AACT database (Aggregated Analysis of ClinicalTrials.gov, hosted by CTTI at Duke) is a Postgres mirror with relational tables, useful for analytical SQL workloads.

## MCP / connector notes

Multiple community MCPs exist; `cyanheads/clinicaltrialsgov-mcp-server` (TypeScript, ~80 stars) is the most-starred and covers search + study detail + patient matching. `navisbio/AACT_clinicaltrials_MCP` wraps the Duke AACT Postgres mirror for SQL-style analytics. None are official NLM-published. Gaps across the existing set: weak eligibility-criteria parsing (text blob, needs structured extraction), inconsistent results-section traversal, no shared response-trimming convention. An ideal MCP surface would expose `search_studies`, `get_study`, `parse_eligibility`, `list_results_by_outcome`, `cross_registry_lookup` (NCT to EudraCT/EU CT).

## Review notes

- `license`: ClinicalTrials.gov data is a US Government work and therefore public domain under 17 USC 105. There is no standard SPDX code for "US Government Public Domain"; used `US-Government-Public-Domain` as a canonical short name. Flag if the project prefers `Public-Domain` or `CC0-1.0` instead.
- `EU_CT_NUMBER` and `EUDRACT_NUMBER` are included in YAML `join_keys` because they appear in `secondaryIdInfos` for trials cross-registered in Europe. Confirm this matches the project's threshold for inclusion (key is present in the source but not universally populated).
- Potential new join key for review: `WHO_UTN` (Universal Trial Number, ICMJE-recommended). Entity type: clinical_trial. Pattern: `^U[0-9]{4}-[0-9]{4}-[0-9]{4}$`. Other datasets that would use it: WHO ICTRP, ISRCTN, JPRN, ANZCTR. ClinicalTrials.gov accepts and displays UTNs in `secondaryIdInfos`. Worth adding if global trial deduplication is a target use case.
