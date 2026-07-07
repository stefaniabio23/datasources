---
id: euctr-eudract
name: EU Clinical Trials Register (EUCTR / EudraCT)
domain: clinical-biotech
entry_kind: registry
description: Legacy public register of interventional clinical trials of medicines conducted in the EU and EEA between May 2004 and January 2025 under Directive 2001/20/EC, backed by the EudraCT database and run by the European Medicines Agency.
homepage_url: https://www.clinicaltrialsregister.eu/
docs_url: https://www.clinicaltrialsregister.eu/about.html
type:
  - web-ui
  - bulk-download
  - scraper-required
auth_required: none
cost: free
license: EU-Commission-Reuse-Decision-2011-833
rate_limit: "no published quota; polite low-volume public use expected; text download capped at 20 records per request"
bulk_available: false
frequency: legacy
lag: "static legacy register; closed to new EudraCT protocols after 30 January 2025, only residual results-section updates for existing trials"
geography: [EU, EEA]
join_keys:
  - EUDRACT_NUMBER
  - NCT_ID
  - WHO_UTN
primary_keys:
  - EUDRACT_NUMBER
join_key_fields:
  - join_key: EUDRACT_NUMBER
    fields: ["A.2 EudraCT number"]
  - join_key: NCT_ID
    fields: ["A.5.2 US NCT (ClinicalTrials.gov registry) number"]
  - join_key: WHO_UTN
    fields: ["A.5.3 WHO universal trial number (UTN)"]
mcp_status: requires-scraping
mcp_maturity: none
mcp_notes: >
  No official API and no MCP. The register serves server-rendered HTML from a URL-parameterised
  search; a connector must scrape trial-protocol pages or drive the 20-record text export. Suggested
  surface: search_trials, get_trial_protocol, get_trial_results, cross_registry_lookup
  (EudraCT to NCT and WHO UTN via the A.5 secondary-identifier fields). The mature open-source
  reference is the R package ctrdata, which already parses EUCTR into structured records.
agent_use_cases:
  - historical EU/EEA trial discovery by condition, product, or sponsor
  - cross-registry deduplication with ClinicalTrials.gov and ISRCTN
  - EudraCT-to-NCT identifier cross-walking for legacy trials
  - retrospective sponsor and pipeline analysis pre-2025
  - results-reporting compliance auditing for older EU trials
access_test:
  command: "curl -sf -A 'datasources-registry/1.0' 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=cancer&page=1' -o /dev/null -w '%{http_code}'"
  expected_status: 200
  expected_fields: ["EudraCT"]
last_verified: 2026-07-03
build_priority: low
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: false
notes: "Legacy layer. New EU/EEA medicine trials now register in CTIS (see eu-ctis entry); EUCTR is the frozen prior register. No documented API; access is HTML scraping plus a per-request 20-record .txt export."
---

# EU Clinical Trials Register (EUCTR / EudraCT)

## Why this source matters

The EU Clinical Trials Register is the public window onto EudraCT, the European Medicines Agency's database of every interventional clinical trial of a medicinal product run in the EU and EEA from 1 May 2004 under Directive 2001/20/EC. It holds protocol summaries, per-country authorisation status, and (for many trials) a results section. As of 30 January 2025 EudraCT stopped accepting new protocols: all new EU/EEA medicine trials now go through CTIS under Regulation 536/2014, so EUCTR is the frozen legacy layer covering roughly two decades of European trial history. It stays load-bearing for any retrospective work: reference-class forecasting, results-reporting compliance audits, and de-duplicating older trials that were dual-registered on ClinicalTrials.gov. Governance is EMA plus the European Commission and Heads of Medicines Agencies; the newer CTIS layer already lives in the registry as `eu-ctis`.

## Agent use cases

- historical EU/EEA trial discovery by condition, product, or sponsor
- cross-registry deduplication with ClinicalTrials.gov and ISRCTN
- EudraCT-to-NCT identifier cross-walking for legacy trials
- retrospective sponsor and pipeline analysis pre-2025
- results-reporting compliance auditing for older EU trials

## Join strategy

The native and canonical key is `EUDRACT_NUMBER` (`^[0-9]{4}-[0-9]{6}-[0-9]{2}$`), shown as protocol field `A.2` and embedded in every trial URL (`/ctr-search/trial/{eudract}/{country}`). The register's `A.5` secondary-identifier block carries the cross-registry keys: `NCT_ID` (field `A.5.2`, "US NCT number") for trials dual-registered on ClinicalTrials.gov, and `WHO_UTN` (field `A.5.3`) for trials assigned a WHO Universal Trial Number, which bridges to ISRCTN, JPRN, ANZCTR, and other ICTRP primary registries.

EUCTR does not mint or expose `EU_CT_NUMBER`; that identifier belongs to the newer CTIS regime (see `eu-ctis`). A legacy trial is linked to its CTIS successor, when one exists, only through the shared `EUDRACT_NUMBER`, so `EUDRACT_NUMBER` is the join backbone between the two EU layers. The `A.5.1` ISRCTN number is also printed on protocol pages but has no canonical key in the registry yet (flagged below).

Common pairings: `eu-ctis` and ClinicalTrials.gov (dedup via `EUDRACT_NUMBER` / `NCT_ID`), WHO ICTRP (via `WHO_UTN`), EMA EPAR and openFDA (post-marketing safety for products that reached approval), OpenAlex or Europe PMC (publications by sponsor or product name; EUCTR does not expose `PMID`).

## Access notes

There is no documented API. Two access paths:

- **URL search (HTML):** `GET https://www.clinicaltrialsregister.eu/ctr-search/search?query={terms}&page={n}` returns server-rendered result pages. Individual protocols are at `https://www.clinicaltrialsregister.eu/ctr-search/trial/{eudractNumber}/{country}` (per-country protocol) and `.../trial/{eudractNumber}/results` for the results section. Everything is scraped from HTML; there is no JSON contract.
- **Text export:** the search UI offers a plain-text (`.txt`) download capped at 20 records per request. Usable for tiny pulls, impractical as a bulk channel.

No auth, no API key, no published rate limit. Treat as low-volume public infrastructure: set a descriptive `User-Agent`, throttle, and cache locally. For any analytical corpus, the practical route is the R package `ctrdata`, which paginates the search, fetches each protocol, and normalises EUCTR (plus CTIS, CTGOV, ISRCTN) into a local document store.

Known gotchas:

- The same trial appears once per participating country (`.../2010-018661-40/GB`, `.../2010-018661-40/FR`); collapse on `EUDRACT_NUMBER` to get one logical trial.
- Legacy markup: old jQuery/HTML tables, `IE=8` compatibility headers, no stable element IDs. Scrapers break on layout changes; pin selectors and re-verify.
- Results-section coverage is uneven; many older trials carry a protocol but no posted results.
- The register is now largely static. Freshness is verified by watching for updated results postings, not new protocol registrations, which have ceased.
- EMA and national competent authorities disclaim liability for reuse; some Part I detail may be commercially deferred.

## MCP / connector notes

No official or community MCP. Because the source is HTML-only with no API, an MCP has to embed a scraper rather than wrap an endpoint, which is why the honest status is `requires-scraping`. Suggested surface:

- `search_trials(condition, product, sponsor, country, page)` — wraps the URL search and parses result rows.
- `get_trial_protocol(eudractNumber, country)` — fetches and flattens one country's protocol page (A/B/C/D/E/F/G sections).
- `get_trial_results(eudractNumber)` — parses the results section when present.
- `cross_registry_lookup(eudractNumber)` — extracts the `A.5` block (`NCT_ID`, `WHO_UTN`, ISRCTN, sponsor protocol code) and optionally resolves to ClinicalTrials.gov.

The connector should collapse per-country duplicates on `EUDRACT_NUMBER`, tolerate the legacy markup, and ideally delegate parsing to `ctrdata` rather than reimplementing it.

## Review notes

- `license`: EUCTR publishes only a liability disclaimer, no SPDX-style statement. EMA content generally falls under Commission Decision 2011/833/EU on reuse of Commission documents. Reused the canonical short name `EU-Commission-Reuse-Decision-2011-833` already established by the `eu-ctis` entry for cross-entry consistency; flag if the project prefers a different canonical string for EUCTR specifically.
- `type` includes `bulk-download` only for the 20-record `.txt` export, which is a small paged export rather than a true bulk dump; `bulk_available` is set to `false` accordingly. Flag if the project wants `bulk-download` reserved for genuine full-corpus dumps.
- Potential new join key for review: `ISRCTN`
    Entity type: clinical_trial
    Pattern: `^ISRCTN[0-9]{8}$`
    Other datasets that would use it: ISRCTN registry (`isrctn` entry), WHO ICTRP (`who-ictrp`), CTIS (`eu-ctis`), ClinicalTrials.gov secondary IDs. EUCTR prints it in protocol field `A.5.1` but it is not yet in `schema/join-keys.yaml`, so it is not added to `join_keys`.
- `EU_CT_NUMBER` was intentionally excluded from `join_keys`: it is a CTIS-era identifier (Regulation 536/2014) that legacy EUCTR trials do not carry. Cross-linking to `eu-ctis` runs through the shared `EUDRACT_NUMBER` instead.
- `access_test` was executed: the search URL returned HTTP 200 (server-rendered HTML). `expected_fields` names an HTML text marker ("EudraCT") rather than a JSON field because the source has no JSON contract.
- `join_key_fields` paths are EudraCT protocol form field codes (`A.2`, `A.5.2`, `A.5.3`), not JSON paths, since the source is scraped HTML.
