---
id: pactr
name: Pan African Clinical Trials Registry (PACTR)
domain: clinical-biotech
entry_kind: registry
description: WHO- and ICMJE-recognised primary clinical trials registry for trials conducted in Africa, the only African member of the WHO Network of Primary Registries, operated by the South African Medical Research Council (SAMRC).
homepage_url: https://pactr.samrc.ac.za/
type:
  - web-ui
  - scraper-required
auth_required: none
cost: free
license: unknown
bulk_available: false
frequency: continuous
lag: "sponsor-driven; records appear once registered and curated; propagates to WHO ICTRP on a monthly transfer cycle"
geography: [Africa]
join_keys:
  - WHO_UTN
primary_keys:
  - PACTR_ID
  - PACTR_TRIAL_DISPLAY_ID
join_key_fields:
  - join_key: WHO_UTN
    fields: [universal-trial-number]
mcp_status: requires-scraping
mcp_notes: >
  No public API and no MCP. Records are server-rendered ASP.NET pages
  (TrialDisplay.aspx?TrialID=). The reliable machine-readable path for PACTR data
  is the WHO ICTRP export, which pulls PACTR monthly. A PACTR-specific connector
  would require HTML scraping of search results and trial-display pages, or should
  be subsumed by a WHO-ICTRP MCP that already normalises this registry.
agent_use_cases:
  - discover clinical trials conducted in Africa by condition, intervention, or country
  - cross-registry deduplication against ClinicalTrials.gov, ISRCTN, and EU CTIS via WHO UTN
  - monitor African trial activity for sponsors, funders, and NGOs
  - locate the African arm of a globally registered multi-country trial
  - resolve a PACTR number cited in a publication to its trial record
access_test:
  command: "curl -sfL 'https://pactr.samrc.ac.za/TrialDisplay.aspx?TrialID=25488'"
  expected_status: 200
last_verified: 2026-07-03
build_priority: low
structure: registry-snapshot
revisions_possible: true
notes: "No documented public API or bulk download. Trial records resolve at https://pactr.samrc.ac.za/TrialDisplay.aspx?TrialID={n} where {n} is the source-internal numeric display id (distinct from the PACTR registration number). Data reaches WHO ICTRP via a monthly transfer, so ICTRP is the practical programmatic access path."
---

# Pan African Clinical Trials Registry (PACTR)

## Why this source matters

PACTR is the WHO ICTRP primary registry for clinical trials conducted in Africa, and the only African member of the WHO Network of Primary Registries (recognised September 2009). It is hosted and operated by the South African Medical Research Council (SAMRC), with historical support from EDCTP and Cochrane South Africa. Registration is free and searching requires no login. It is designed around the constraints of African trialists (intermittent internet, alternative submission by email, post, or fax), and it is the authoritative place to find the African arm of a trial that a US- or EU-centric registry may under-cover. Because it is a WHO primary registry, every PACTR record propagates upstream into the WHO ICTRP global graph, making PACTR the Africa-regional complement to ClinicalTrials.gov (US), ISRCTN (UK), and EU CTIS (EEA). Secondary domain: public-health, given the heavy weighting toward malaria, HIV/TB, maternal health, and other endemic-disease and public-health interventions.

## Agent use cases

- discover clinical trials conducted in Africa by condition, intervention, or country
- cross-registry deduplication against ClinicalTrials.gov, ISRCTN, and EU CTIS via WHO UTN
- monitor African trial activity for sponsors, funders, and NGOs
- locate the African arm of a globally registered multi-country trial
- resolve a PACTR number cited in a publication to its trial record

## Join strategy

The source-native registration number is the PACTR number, `PACTR` followed by a timestamp-derived digit string (e.g. `PACTR202304525632216`). It is not yet a canonical registry key; see Review notes. A second, source-internal numeric display id addresses each record via `TrialDisplay.aspx?TrialID={n}` (e.g. `25488`) and is distinct from the PACTR number.

The one canonical join key PACTR exposes is `WHO_UTN` (WHO Universal Trial Number), carried on the record's "Universal Trial Number (UTN)" field when the sponsor supplied one. As with other primary registries, UTN population is sparse, so treat it as opportunistic rather than a guaranteed bridge. Records may also cite secondary identifiers from other registries (ClinicalTrials.gov `NCT_ID`, ISRCTN) in free-text "secondary id" fields, but these are inconsistently populated and not exposed as structured fields, so they are not mapped here; scrape them per-record if a join demands it.

Recommended pairings: WHO ICTRP as the umbrella graph that already ingests PACTR monthly (the cleanest way to query PACTR programmatically alongside every other primary registry); ClinicalTrials.gov, ISRCTN, and EU CTIS for cross-registry dedup where a shared `WHO_UTN` exists.

## Access notes

Web-only. The registry is a server-rendered ASP.NET application (`ATMWeb`). Search is free and unauthenticated via the homepage search form and a GIS map viewer; individual records resolve at `https://pactr.samrc.ac.za/TrialDisplay.aspx?TrialID={n}` using the source-internal numeric display id. There is no documented REST API, no query endpoint, and no bulk download. Some deep-link paths (e.g. `Documentation.aspx`, `TrialDisplay/Search.aspx`) intermittently return a server error page, so verify against the homepage and a known `TrialDisplay.aspx?TrialID=` record.

For any programmatic use, go through WHO ICTRP rather than scraping PACTR directly: PACTR transfers its full record set to ICTRP monthly, so ICTRP carries the same trials in a normalised schema. Scrape PACTR pages directly only when you need a field ICTRP drops or the latest edit before the next monthly sync. Be polite: set a `User-Agent`, throttle, and cache, as the platform is not built for high-volume automated access.

## MCP / connector notes

No official or community MCP. Given the absence of an API, a PACTR-specific connector would need HTML scraping of the search UI and `TrialDisplay.aspx` pages, which is brittle. The higher-leverage build is a WHO-ICTRP MCP (or a BioMCP-style multi-registry server) that already unifies ClinicalTrials.gov, ISRCTN, EU CTIS, and PACTR; PACTR coverage then comes largely for free through the ICTRP monthly ingest. If a PACTR-native surface is still wanted: `search_trials(condition, intervention, country, status)`, `get_trial(pactr_number_or_display_id)`, `cross_registry_lookup(utn)`. The connector must abstract over the ASP.NET postback search form, the split between the PACTR registration number and the internal `TrialID`, and the intermittent server-error pages.

## Review notes

- Potential new join key for review: `PACTR_ID`
  - Entity type: clinical_trial
  - Pattern: `^PACTR[0-9]+$` (timestamp-derived digit body, e.g. `PACTR202304525632216`; bioregistry uses the same regex, prefix `pactr:`)
  - Other datasets that would use it: WHO ICTRP (carries the PACTR number as the source registry id), ClinicalTrials.gov and ISRCTN (as secondary/related registry ids), Europe PMC and OpenAlex (trial ids cited in publication metadata). Recommend PR-ing into `schema/join-keys.yaml` alongside the existing `NCT_ID`, `EU_CT_NUMBER`, `EUDRACT_NUMBER`, `WHO_UTN` clinical-registry keys, and in the same batch as the `ISRCTN_ID` candidate flagged on the ISRCTN entry.
- `license: unknown`. The site references Terms and Conditions and FAQs and states that searching and registration are free, but no explicit reuse/redistribution licence (CC0, CC-BY, or a named registry-data term) was locatable from the public pages. Set to `unknown` rather than assumed-open. Re-verify against the Terms and Conditions page and confirm before treating PACTR metadata as freely redistributable; for reuse in practice, prefer the WHO ICTRP copy, whose terms are documented.
- `join_key_fields` for `WHO_UTN` uses a descriptive field label (`universal-trial-number`) rather than a JSON path, because the source is HTML with no API. Re-map to a real path if a structured PACTR feed or the ICTRP record is used as the ingest surface instead.
- `access_test` uses a specific `TrialID` deep link (`25488`) that returned a live 200 with a real record (`PACTR202304525632216`) on 2026-07-03; the homepage also returns 200. Several other deep-link paths returned server-error pages, so pin the test to a known-good record URL.
