---
id: who-ictrp
name: WHO ICTRP (International Clinical Trials Registry Platform)
domain: clinical-biotech
entry_kind: registry
description: WHO meta-registry that aggregates clinical trial records from primary and partner registries worldwide into a single searchable data set keyed on a common trial-registration schema.
homepage_url: https://www.who.int/tools/clinical-trials-registry-platform
docs_url: https://www.who.int/tools/clinical-trials-registry-platform/the-ictrp-search-portal
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free-non-commercial
license: WHO-ICTRP-Terms-of-Use
rate_limit: "no published quota for the Search Portal; the real-time XML web service is request-gated and may carry a cost-recovery fee"
bulk_available: true
frequency: weekly
lag: "sponsor- and registry-driven; ICTRP re-imports from primary registries on a weekly cycle, so records trail the source registry by up to a week"
geography: [global]
join_keys:
  - NCT_ID
  - EUDRACT_NUMBER
  - WHO_UTN
primary_keys:
  - ICTRP_TRIAL_ID
join_key_fields:
  - join_key: NCT_ID
    fields: [TrialID, Secondary_ID]
  - join_key: EUDRACT_NUMBER
    fields: [TrialID, Secondary_ID]
  - join_key: WHO_UTN
    fields: [utn]
mcp_status: mcp-exists
mcp_maturity: experimental
mcp_package:
  - github.com/mattjohnpowell/clinical-trials-mcp
mcp_notes: >
  One early-stage community MCP (mattjohnpowell/clinical-trials-mcp, TypeScript, ~0 stars,
  2 commits) wraps both the ICTRP Search Portal web service and ClinicalTrials.gov, exposing
  search_trials and get_trial_details. Immature and unproven; a robust cross-registry
  connector is still effectively needed.
agent_use_cases:
  - global clinical trial discovery across national registries
  - cross-registry deduplication via UTN and secondary IDs
  - non-US/EU trial coverage (JPRN, ANZCTR, ChiCTR, CTRI, ISRCTN)
  - trial-registration completeness and prospective-registration audits
  - pipeline and epidemiology scans beyond ClinicalTrials.gov
last_verified: 2026-07-02
build_priority: medium
notes: "access_test omitted: no public no-auth structured data endpoint. The real-time ICTRP XML web service is request/fee-gated (email ictrpinfo@who.int); bulk records come via the Search Portal CSV/XML export (web UI) or a SharePoint request form. Verify freshness from the weekly refresh date on the Search Portal."
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: true
---

# WHO ICTRP (International Clinical Trials Registry Platform)

## Why this source matters

The ICTRP is WHO's global meta-registry: it does not register trials itself but aggregates records from a network of primary registries (ClinicalTrials.gov, EU CTIS / EudraCT, ISRCTN, JPRN, ANZCTR, ChiCTR, CTRI, and more) into one searchable data set built on the WHO Trial Registration Data Set (TRDS), a minimum standard of ~24 fields. For any agent that needs a complete world view of clinical research rather than a single jurisdiction, ICTRP is the deduplication and coverage layer above ClinicalTrials.gov and CTIS, capturing trials from national registries that never appear in the US or EU systems. Run by the WHO ICTRP Secretariat in Geneva. Secondary relevance to `public-health` for global research-gap and registration-completeness analysis.

## Agent use cases

- global clinical trial discovery across national registries
- cross-registry deduplication via UTN and secondary IDs
- non-US/EU trial coverage (JPRN, ANZCTR, ChiCTR, CTRI, ISRCTN)
- trial-registration completeness and prospective-registration audits
- pipeline and epidemiology scans beyond ClinicalTrials.gov

## Join strategy

ICTRP's value is that it carries the source registry's own identifier in the `TrialID` field, so a single record exposes `NCT_ID` (when `Source_Register` is ClinicalTrials.gov), `EUDRACT_NUMBER` (EU Clinical Trials Register / EudraCT), and registry-native IDs like ISRCTN, EUCTR, JPRN, ACTRN, ChiCTR, CTRI. The `Secondary_ID` field holds cross-registrations, which is where dual-registered US/EU trials expose a second canonical key. The WHO Universal Trial Number (`WHO_UTN`, `^U[0-9]{4}-[0-9]{4}-[0-9]{4}$`) is the intended cross-registry spine: obtained once from the UTN service and carried across every registry a trial appears in, it is the cleanest key for stitching the same trial across ICTRP, CTIS, and ClinicalTrials.gov.

`EU_CT_NUMBER` (CTIS) also flows in as CTIS is an ICTRP data provider, but population in current exports is uneven, so it is left out of YAML `join_keys` pending confirmation. `ISRCTN` is heavily represented but is not yet a canonical key in the registry (flagged below).

ICTRP-internal handling: the aggregated `TrialID` doubles as the record key, so there is no separate WHO-minted primary key; treat `TrialID` as source-registry-scoped, not globally unique on its own. Common pairings: ClinicalTrials.gov and EU CTIS (resolve the same trial via `WHO_UTN` / `Secondary_ID`), ISRCTN (UK/international trials), PubMed/OpenAlex (publications by registered ID).

## Access notes

Three access paths, in increasing friction:

- **Search Portal (free, no auth):** the web UI at `https://trialsearch.who.int/` lets you query and export selected records or the full result set as CSV or XML at no charge. This is the primary public path but it is a JS single-page app, so programmatic use means driving the export rather than a documented JSON API.
- **Bulk full-database export (request-gated):** to pull all new/updated records on the weekly cycle, submit the WHO SharePoint access request form (linked from the ICTRP downloads page). Free, but requires a request.
- **Real-time XML web service / crawling (request-gated, possible fee):** the ICTRP Search Portal Web Service interrogates the database live via XML web services; access requires emailing `ictrpinfo@who.int`, is documented as "for research purposes only", and the Secretariat states it recovers costs, so a fee may apply. The crawling service has been intermittently unavailable.

Freshness check: the database is refreshed weekly; read the processing/refresh date shown on the Search Portal and, per the terms, display it alongside any redistributed data. Terms of use require attributing the source as WHO ICTRP, keeping data current, showing the processing date, claiming no proprietary rights, and not using extracted data for marketing, promotional, or commercial purposes.

## MCP / connector notes

One community MCP exists (`github.com/mattjohnpowell/clinical-trials-mcp`, TypeScript) covering both ICTRP and ClinicalTrials.gov via the ICTRP web service, exposing `search_trials` and `get_trial_details`. It is early-stage (0 stars, 2 commits) and unproven against the fee-gated web service, so treat it as experimental. A production-grade connector would need to abstract over the three access paths (Search Portal export, SharePoint bulk, XML web service), normalise the WHO TRDS schema across heterogeneous source registries, and resolve the same trial across `TrialID` + `WHO_UTN` + `Secondary_ID`. Suggested surface: `search_trials(condition, intervention, country, source_register, status)`, `get_trial(trial_id)`, `resolve_by_utn(utn)`, `cross_registry_lookup(trial_id)`, `export_updates(since_date)`.

## Review notes

- `license`: WHO ICTRP publishes bespoke terms of use (attribution as WHO ICTRP, keep current, display processing date, no proprietary claims, no marketing/promotional/commercial use) with no SPDX code. Used `WHO-ICTRP-Terms-of-Use` as a canonical kebab-case short name; flag if the project prefers a different string. The non-commercial restriction is why `cost` is set to `free-non-commercial` rather than `free`.
- `auth_required: none` reflects the free public Search Portal path. The bulk full-record export (SharePoint form) and the real-time XML web service both require an email request and the web service may carry a cost-recovery fee; consider whether the project wants `account-required` or `api-key-paid` to capture those secondary paths.
- Potential new join key for review: `ISRCTN`. Entity type: clinical_trial. Pattern: `^ISRCTN[0-9]{8}$`. Other datasets that would use it: WHO ICTRP, ISRCTN registry (BMC/Springer Nature), EU CTIS and ClinicalTrials.gov secondary IDs. Heavily populated in ICTRP; a strong candidate for the canonical registry if global trial deduplication is in scope.
- `EU_CT_NUMBER` is deliberately excluded from `join_keys` despite CTIS being an ICTRP data provider, because its population in current ICTRP exports is uneven. Confirm whether the project's inclusion threshold (present but sparse) warrants adding it.
- `join_key_fields` uses the documented ICTRP export column names (`TrialID`, `Secondary_ID`) and a lowercase `utn` for the Universal Trial Number; exact XML/CSV field casing was not verified against a live export (no clean public API), so re-check field names against an actual Search Portal export before relying on the paths.
- `primary_keys: [ICTRP_TRIAL_ID]` is a label for the `TrialID` column; WHO mints no separate globally-unique record ID, so this key is source-registry-scoped.
