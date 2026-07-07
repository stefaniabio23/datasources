---
id: anzctr
name: ANZCTR (Australian New Zealand Clinical Trials Registry)
domain: clinical-biotech
entry_kind: registry
description: WHO- and ICMJE-recognised primary clinical trials registry for Australia, New Zealand, and international studies, run by the NHMRC Clinical Trials Centre at the University of Sydney.
homepage_url: https://www.anzctr.org.au/
docs_url: https://www.anzctr.org.au/Faq.aspx
type:
  - web-ui
  - bulk-download
  - scraper-required
auth_required: none
cost: free
license: ANZCTR-Terms-of-Use
rate_limit: "no published quota; public site behind a bot-filtering WAF that rejects non-browser HTTP clients"
bulk_available: true
frequency: continuous
lag: "sponsor-driven; records appear after registration and editorial curation, and propagate to WHO ICTRP on its weekly re-import cycle"
geography: [AUS, NZL, global]
join_keys:
  - NCT_ID
  - WHO_UTN
primary_keys:
  - ACTRN_ID
join_key_fields:
  - join_key: WHO_UTN
    fields: [utrn, secondary_ids]
  - join_key: NCT_ID
    fields: [secondary_ids]
mcp_status: requires-scraping
mcp_notes: >
  No official or community MCP, and no public no-auth API: the site is behind a WAF that
  returns 403 to direct HTTP clients, so programmatic access needs browser automation or
  the WHO ICTRP aggregation layer. Practical connector path is to reach ANZCTR trials via
  WHO ICTRP (which re-imports ANZCTR weekly) rather than scraping the ASP.NET UI directly.
  If scraping ANZCTR itself, drive the search page and the per-trial XML/Excel export.
agent_use_cases:
  - Australia and New Zealand clinical trial discovery by condition or intervention
  - cross-registry deduplication with ClinicalTrials.gov via secondary IDs and UTN
  - non-US/EU trial coverage for pipeline and epidemiology scans
  - WHO Trial Registration Data Set retrieval for AU/NZ studies
  - prospective-registration and registration-completeness audits
last_verified: 2026-07-03
build_priority: low
structure: registry-snapshot
revisions_possible: true
notes: "access_test omitted: no public no-auth structured endpoint. Direct curl to https://www.anzctr.org.au/ and to TrialReview.aspx returns HTTP 403 (WAF); the only public paths are the JS search UI (Excel export of search results) and the per-trial WHO-format XML download button. Reach ANZCTR data programmatically via WHO ICTRP. Verify freshness from the WHO ICTRP weekly refresh date or the trial record's last-updated field."
---

# ANZCTR (Australian New Zealand Clinical Trials Registry)

## Why this source matters

ANZCTR is the online public registry of clinical trials for Australia and New Zealand, operated as a not-for-profit by the NHMRC Clinical Trials Centre at the University of Sydney and housed there since 2005. In 2007 it was one of the first three registries recognised by the WHO ICTRP as a Primary Registry, and it is ICMJE-compliant, so its records carry the full WHO Trial Registration Data Set (the ~24-field minimum standard) and flow upstream into the WHO global trial graph. Although its remit is Australian and New Zealand research, it accepts registrations from all countries, so it is the Oceania-centric complement to ClinicalTrials.gov (US), EU CTIS (EEA), and ISRCTN (UK). Each trial is minted a persistent ACTRN (Australian Clinical Trial Registration Number). Secondary domain: public-health, given the large volume of publicly funded health-services and prevention studies it holds.

## Agent use cases

- Australia and New Zealand clinical trial discovery by condition or intervention
- cross-registry deduplication with ClinicalTrials.gov via secondary IDs and UTN
- non-US/EU trial coverage for pipeline and epidemiology scans
- WHO Trial Registration Data Set retrieval for AU/NZ studies
- prospective-registration and registration-completeness audits

## Join strategy

The source-native primary key is the ACTRN (`ACTRN` followed by 14 digits, e.g. `ACTRN12623000498695`), which resolves at `https://www.anzctr.org.au/Trial/Registration/TrialReview.aspx?ACTRN={actrn}`. ACTRN is not yet a canonical registry key; see Review notes.

Canonical join keys come from the record's secondary-identifier and UTN fields. ANZCTR encourages Responsible Registrants to enter the WHO Universal Trial Number (`WHO_UTN`, `^U[0-9]{4}-[0-9]{4}-[0-9]{4}$`) and other registries' numbers as secondary IDs, so a dual-registered trial can expose `NCT_ID` (ClinicalTrials.gov) alongside the UTN. Both are the cleanest spine for stitching the same trial across ANZCTR, ClinicalTrials.gov, EU CTIS, and WHO ICTRP. Population of secondary IDs is sponsor-driven and therefore uneven; absence does not prove single-registration.

Recommended pairings: WHO ICTRP as the umbrella graph (ANZCTR is one of its providers, so the same trial resolves there via `TrialID`/`Secondary_ID`/`WHO_UTN`); ClinicalTrials.gov for cross-registry dedup; OpenAlex or Europe PMC to reach associated publications (ANZCTR does not itself expose `PMID` or `DOI` for linked papers).

## Access notes

No public REST API. Direct HTTP requests to the homepage and to `TrialReview.aspx` return HTTP 403 from a bot-filtering WAF, confirmed on 2026-07-03 with a browser User-Agent, so an access-test curl is intentionally omitted. Three practical paths:

- **Web search UI (free, no auth):** `https://www.anzctr.org.au/TrialSearch.aspx` is a JavaScript ASP.NET app; query by condition, intervention, sponsor, or ID, then export the result set to Excel, or download selected trials as a WHO-format XML summary (Request number, Scientific title, ACTRN, Anticipated start date, plus the full WHO fields per record). Programmatic use means driving the UI, not calling a documented endpoint.
- **Per-trial record:** resolve by ACTRN at `TrialReview.aspx?ACTRN={actrn}` (browser) and use the record's XML export button.
- **WHO ICTRP (recommended for agents):** because ANZCTR is a WHO Primary Registry that re-imports weekly into ICTRP, the cleanest machine path to ANZCTR records is through the ICTRP Search Portal / bulk export rather than scraping ANZCTR directly.

Freshness: read the trial record's last-updated field, or the WHO ICTRP weekly processing date when reaching the data through ICTRP.

## MCP / connector notes

No official or community MCP targets ANZCTR specifically. Given the WAF and the absence of a public API, a dedicated connector would need browser automation, so the higher-leverage route is a cross-registry MCP (BioMCP-style) that reaches ANZCTR through WHO ICTRP, which already has an early-stage community server. Suggested surface if built against ANZCTR directly: `search_trials(condition, intervention, sponsor, status, country)`, `get_trial(actrn)`, `cross_registry_lookup(actrn)` (reads secondary IDs and UTN to resolve NCT / CTIS), `export_whoxml(actrn)`. The connector must abstract over the ASP.NET postback search flow, the WAF, and the sponsor-entered-vs-empty ambiguity of secondary identifier fields.

## Review notes

- Potential new join key for review: `ACTRN_ID`
  - Entity type: clinical_trial
  - Pattern: `^ACTRN[0-9]{14}$` (e.g. `ACTRN12623000498695`; bioregistry records the looser `^ACTRN\d+$`)
  - Other datasets that would use it: WHO ICTRP (carries ACTRN in `TrialID`), ClinicalTrials.gov and EU CTIS (as secondary/related registry IDs), Europe PMC and OpenAlex (trial IDs in publication metadata). Recommend PR-ing into `schema/join-keys.yaml` alongside the existing `NCT_ID`, `EU_CT_NUMBER`, `EUDRACT_NUMBER`, `WHO_UTN`, and the pending `ISRCTN` clinical-registry keys.
- `license: ANZCTR-Terms-of-Use` is a proposed canonical kebab-case short name; ANZCTR data is free and publicly accessible (WHO TRDS, 24/7) but published under registry copyright and citation terms with no SPDX code, and no explicit open reuse licence was located. Flag if the project prefers a different string, or wants `cost: free-non-commercial` if the terms are read as non-commercial.
- `access_test` omitted because the site returns 403 to non-browser HTTP clients (verified 2026-07-03). If the project wants a live check, it must run through WHO ICTRP or headless-browser automation.
- `join_key_fields` uses inferred WHO-format field names (`utrn`, `secondary_ids`); exact XML/CSV casing was not verified against a live ANZCTR export because the export is gated behind the JS UI and WAF. Re-check field paths against an actual WHO-format XML download before relying on them.
- `primary_keys: [ACTRN_ID]` is a label for the ACTRN; the source mints no other record ID.
