---
id: rebec
name: ReBEC (Brazilian Registry of Clinical Trials)
domain: clinical-biotech
entry_kind: registry
description: Brazil's national WHO- and ICMJE-recognised primary clinical trials registry for experimental and non-experimental studies conducted on humans in Brazilian territory, run by Fiocruz for the Ministry of Health.
homepage_url: https://ensaiosclinicos.gov.br/
type:
  - web-ui
  - scraper-required
auth_required: none
cost: free
license: unknown
bulk_available: false
frequency: continuous
lag: "sponsor-driven; records appear once submitted and editorially validated"
geography: [BRA]
join_keys:
  - WHO_UTN
primary_keys:
  - RBR_ID
join_key_fields:
  - join_key: WHO_UTN
    fields: [utrn]
mcp_status: requires-scraping
mcp_maturity: none
mcp_notes: >
  No official or community MCP. The new gov.br platform is a CodeIgniter web app; the historical
  ICTRP XML dump path no longer resolves, so a dedicated connector would need HTML scraping of
  single-trial pages or, more reliably, reading ReBEC records via the WHO ICTRP redistribution.
  A multi-registry clinical-trials MCP (ClinicalTrials.gov + ISRCTN + EU CTIS + WHO ICTRP + ReBEC)
  is the higher-leverage build; ReBEC alone is low priority.
agent_use_cases:
  - Brazilian clinical trial discovery by condition or intervention
  - cross-registry deduplication via WHO UTN
  - Latin American / Lusophone trial-landscape monitoring
  - trial registration and status lookup for Brazil-conducted studies
access_test:
  command: "curl -sf -A 'Mozilla/5.0 (compatible; datasources-verify/1.0)' 'https://ensaiosclinicos.gov.br/rg/RBR-6qvdftm'"
  expected_status: 200
  expected_fields: ["RBR-6qvdftm", "UTN code"]
last_verified: 2026-07-03
build_priority: low
structure: registry-snapshot
revisions_possible: true
notes: "Single-trial pages resolve at https://ensaiosclinicos.gov.br/rg/RBR-{id} and return HTML (not JSON/XML). Raw curl without a browser-like User-Agent is 403-blocked at the nginx layer; the access_test sets a UA. Public overview dashboard at /api2/bi is HTML, not a data API."
---

# ReBEC (Brazilian Registry of Clinical Trials)

## Why this source matters

ReBEC (Registro Brasileiro de Ensaios Clínicos) is Brazil's national clinical trials registry, a WHO ICTRP primary registry and ICMJE-recognised registry. It is operated by Fundação Oswaldo Cruz (Fiocruz) for the Ministry of Health (DECIT/SECTICS), as a joint initiative with the Pan American Health Organization (PAHO/OPAS) and ANVISA. It records experimental and non-experimental studies on humans conducted in Brazilian territory, in Portuguese and English, and collects and publicly displays all 20 items of the WHO Trial Registration Data Set. Because it is a WHO primary registry, its records flow upstream into the WHO global trial graph, making ReBEC the Brazil-centric complement to ClinicalTrials.gov (US), EU CTIS (EEA), and ISRCTN (UK). Secondary domain: public-health, given the large share of publicly funded Brazilian health-system and prevention studies.

## Agent use cases

- Brazilian clinical trial discovery by condition or intervention
- cross-registry deduplication via WHO UTN
- Latin American / Lusophone trial-landscape monitoring
- trial registration and status lookup for Brazil-conducted studies

## Join strategy

The source-native primary key is the RBR number (`RBR-` followed by an alphanumeric slug, e.g. `RBR-6qvdftm`), carried in the record URL and page header. It is not yet a canonical registry key; see Review notes.

The one canonical join key ReBEC exposes is `WHO_UTN`, the WHO Universal Trial Number (e.g. `U1111-1286-6418`), shown on each trial page as "UTN code" and carried as `utrn` in the WHO ICTRP flat schema. This is the reliable cross-registry hinge: pair on `WHO_UTN` with ClinicalTrials.gov, ISRCTN, EU CTIS, and WHO ICTRP to deduplicate co-registered trials.

ReBEC also records free-text secondary identifiers (WHO data-set item 2), which can include a ClinicalTrials.gov `NCT_ID` for co-registered studies, but this field is inconsistently populated and was not verified as a stable path in the sampled record, so `NCT_ID` is intentionally left out of `join_keys`. Reach ReBEC's associated publications via the WHO ICTRP umbrella graph or by matching `WHO_UTN` into OpenAlex / Europe PMC where the trial ID is cited; ReBEC does not itself expose `PMID` or `DOI`.

## Access notes

No documented public REST API or working bulk endpoint on the current platform. The site was migrated to the gov.br domain on a CodeIgniter stack, and the historical ICTRP bulk XML dump (`/rg/all/xml/ictrp`) and per-trial XML/JSON format suffixes now return 404. Practical access paths:

- **Single trial (HTML):** `GET https://ensaiosclinicos.gov.br/rg/RBR-{id}` returns the full record as HTML (status, sponsor, condition, interventions, WHO data set, UTN code). Scrape for structured fields.
- **Search:** the public web UI at the homepage (Algolia-backed) lists and filters trials; no documented JSON search endpoint.
- **Bulk / programmatic:** for a machine-readable ReBEC corpus, read ReBEC records through the WHO ICTRP redistribution (see the `who-ictrp` entry) rather than scraping page-by-page.

Gotchas:

- Raw `curl` is blocked with `403 Forbidden` at nginx unless a browser-like `User-Agent` is set; the `access_test` sets one.
- Records are versioned; WHO's profile notes every modification creates a new register with an audit link, so treat values as revisable (`revisions_possible: true`).
- No license is published for reuse of the trial data; the WHO data set is displayed at no charge but redistribution terms are unstated (see Review notes).

## MCP / connector notes

No official or community MCP. Because the current platform offers no clean API, a dedicated ReBEC connector would need HTML scraping of `/rg/RBR-{id}` pages plus Algolia-search wrapping, which is fragile. The higher-leverage build is a multi-registry clinical-trials MCP that unifies ClinicalTrials.gov, ISRCTN, EU CTIS, WHO ICTRP, and ReBEC under one cross-registry interface keyed on `WHO_UTN`; ReBEC would ride along as one backend rather than justifying a standalone server. Suggested surface if built: `search_trials(condition, intervention, status)`, `get_trial(rbr_id)`, `cross_registry_lookup(rbr_id)` reading the UTN and secondary IDs.

## Review notes

- Potential new join key for review: `RBR_ID`
  - Entity type: clinical_trial
  - Pattern: `^RBR-[a-z0-9]+$` (bioregistry canonical form; example `RBR-6qvdftm`)
  - Other datasets that would use it: WHO ICTRP (as the source registry id), ClinicalTrials.gov and EU CTIS (as secondary/related registry ids), OpenAlex and Europe PMC (trial IDs cited in publication metadata), Bioregistry (`rebec:` prefix). Recommend PR-ing into `schema/join-keys.yaml` alongside the existing `NCT_ID`, `EU_CT_NUMBER`, `EUDRACT_NUMBER`, `WHO_UTN`, and the proposed `ISRCTN_ID` clinical-registry keys. Placed in `primary_keys` only for now, per the no-invention rule.
- `license: unknown` — ReBEC publishes the full WHO Trial Registration Data Set at no charge but states no reuse/redistribution license on the site or the WHO profile. Left as `unknown` rather than guessing a CC or public-domain term. Flag if the project prefers a placeholder short name for WHO-primary-registry public data.
- `type` excludes `bulk-download`: the previously documented ICTRP XML dump path 404s on the migrated platform and no replacement bulk export was found. `bulk_available: false` reflects this; re-verify if ReBEC restores a dump endpoint.
- Access is HTML-only (`scraper-required`); the `access_test` validates liveness via a single-trial page (HTTP 200, contains `RBR-6qvdftm` and `UTN code`), not a JSON contract.
