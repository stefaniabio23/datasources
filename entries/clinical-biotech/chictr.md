---
id: chictr
name: Chinese Clinical Trial Registry (ChiCTR)
domain: clinical-biotech
entry_kind: registry
description: WHO ICTRP primary clinical trial registry for mainland China, recording interventional, prevention, diagnostic, prognostic, and epidemiological studies, run by the Chinese Clinical Trial Registry centre at West China Hospital, Sichuan University.
homepage_url: https://www.chictr.org.cn/
docs_url: https://www.chictr.org.cn/indexEN.html
type:
  - web-ui
  - scraper-required
auth_required: none
cost: free
license: unknown
rate_limit: "no published quota; site enforces anti-bot / verification challenges that gate automated access"
bulk_available: false
frequency: continuous
lag: "registration number issued about two weeks after submission, following completion of the registry audit"
geography: [CHN]
join_keys:
  - WHO_UTN
primary_keys:
  - CHICTR_ID
join_key_fields:
  - join_key: WHO_UTN
    fields: [who-universal-trial-number]
mcp_status: mcp-exists
mcp_maturity: experimental
mcp_package:
  - "chictr-mcp-server (npm)"
  - github.com/PancrePal-xiaoyibao/chictr-mcp-server
mcp_notes: >
  One early-stage community MCP (PancrePal-xiaoyibao/chictr-mcp-server, TypeScript, ~5 stars,
  built for cancer patients and families). It drives the public site with Playwright browser
  automation plus Cheerio parsing to defeat anti-bot protection, since ChiCTR exposes no
  official API. Exposes search_trials (keyword / registration number / year), get_trial_detail,
  cache and runtime tooling, and verification-session handling. Scrape-based, so fragile to
  site changes.
mcp_command:
  - "npx -y chictr-mcp-server@latest"
agent_use_cases:
  - China-only clinical trial discovery by condition or intervention
  - cross-registry deduplication via WHO UTN and secondary IDs
  - coverage of trials absent from ClinicalTrials.gov and EU CTIS
  - traditional-Chinese-medicine and China-sponsor pipeline scans
  - registration-completeness and prospective-registration audits for China
last_verified: 2026-07-03
build_priority: medium
notes: "access_test omitted: no public no-auth structured data endpoint. The site is a JS single-page app with anti-bot verification; programmatic access requires browser automation (see the community MCP) or the WHO ICTRP aggregate export. Verify freshness from the record's registration/last-refreshed date, or reach ChiCTR records upstream via WHO ICTRP."
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: true
---

# Chinese Clinical Trial Registry (ChiCTR)

## Why this source matters

ChiCTR is the WHO ICTRP primary registry for mainland China, operated by the Chinese Clinical Trial Registry centre at West China Hospital, Sichuan University (Chengdu), a non-profit that registers trials free of charge. It records interventional trials plus prevention, diagnostic-test, prognostic, and epidemiological studies, and displays each record in both Chinese and English. For any agent that needs a complete world view of clinical research, ChiCTR is a coverage layer: a large share of China-sponsored trials, including traditional-Chinese-medicine studies, register here and never appear in ClinicalTrials.gov or EU CTIS. Records include protocol, recruitment status, funding, ethics approval, and interventions, and the registry publishes an IPD (individual participant data) sharing policy. Secondary relevance to `public-health` for research-gap and registration-completeness analysis of Chinese research. Its records also flow upstream into the WHO global trial graph.

## Agent use cases

- China-only clinical trial discovery by condition or intervention
- cross-registry deduplication via WHO UTN and secondary IDs
- coverage of trials absent from ClinicalTrials.gov and EU CTIS
- traditional-Chinese-medicine and China-sponsor pipeline scans
- registration-completeness and prospective-registration audits for China

## Join strategy

The source-native primary key is the ChiCTR registration number: modern records take the form `ChiCTR` followed by digits (e.g. `ChiCTR2300070727`, a year prefix plus sequence), while legacy records use a lettered form `ChiCTR-<letters>-<digits>` (e.g. `ChiCTR-ABC-12345`). This identifier is not yet a canonical registry key; see Review notes.

The one canonical join key ChiCTR reliably exposes is the WHO Universal Trial Number (`WHO_UTN`, `^U[0-9]{4}-[0-9]{4}-[0-9]{4}$`), the intended cross-registry spine obtained once from the UTN service and carried across every registry a trial appears in. Population is uneven, so absence of a UTN does not prove single-registration. ChiCTR records also carry a free-text "secondary IDs" field that can hold an `NCT_ID` or `EUDRACT_NUMBER` for dual-registered trials, but coverage is sparse and the field is unstructured, so those keys are left out of YAML `join_keys` pending confirmation against real records.

Recommended pairings: WHO ICTRP as the umbrella graph that already ingests ChiCTR (join on `WHO_UTN` and secondary IDs); ClinicalTrials.gov and EU CTIS for the minority of dual-registered trials; OpenAlex or Europe PMC to reach associated publications. Because ChiCTR is the primary source for many China-only trials, treat it as authoritative for those records rather than a mirror.

## Access notes

No official API. The public site (`https://www.chictr.org.cn/`, English mirror `indexEN.html`, search at `searchprojEN.html`) is a JS single-page app that enforces anti-bot verification challenges, so plain HTTP fetching of structured data does not work. The realistic access paths are:

- **Browser automation:** drive the search UI with a headless browser and parse the rendered record pages (the community MCP below does exactly this with Playwright + Cheerio). Search filters include country/region, disease code, sponsoring unit, funding source, recruitment status, and study type.
- **WHO ICTRP aggregate:** ChiCTR records are re-imported into the WHO ICTRP Search Portal on its weekly cycle, so bulk/structured access to ChiCTR trials is often cleaner via the `who-ictrp` entry than by scraping ChiCTR directly.
- **ResMan:** the linked ResMan data-management platform (`www.medresman.org`) provides additional trial data-management functionality for registrants.

Freshness check: a registration number is assigned about two weeks after submission once the audit completes; read the registration and last-refreshed dates on the record. No bulk export is published by ChiCTR itself.

## MCP / connector notes

One community MCP exists: `github.com/PancrePal-xiaoyibao/chictr-mcp-server` (`chictr-mcp-server` on npm, TypeScript, ~5 stars, v2.x as of 2026), built to help cancer patients and families. It uses Playwright browser automation and Cheerio parsing to defeat the site's anti-bot protection rather than any API, and exposes `search_trials` (keyword / registration number / year, including recent-months search), `get_trial_detail`, cache tooling (`get_cache_stats_v2`, `clear_cache`), runtime metrics, and verification-session handling. Treat it as experimental and fragile: because it scrapes a protected JS site, it breaks when ChiCTR changes markup or tightens verification. Run with `npx -y chictr-mcp-server@latest`.

A production-grade connector would need to abstract over the verification challenge, normalise the bilingual (Chinese/English) record schema, and resolve trials across `CHICTR_ID` + `WHO_UTN` + secondary IDs. Suggested surface: `search_trials(condition, intervention, sponsor, status, study_type, region)`, `get_trial(chictr_id)`, `resolve_by_utn(utn)`, `cross_registry_lookup(chictr_id)`. For anything bulk or dedup-oriented, prefer routing through WHO ICTRP.

## Review notes

- Potential new join key for review: `CHICTR_ID`
  - Entity type: clinical_trial
  - Pattern: `^ChiCTR(-[A-Z]+)*-?[0-9]+$` (covers modern `ChiCTR2300070727` and legacy `ChiCTR-ABC-12345`; per Bioregistry the pattern is `^ChiCTR(-[A-Z]+-)?\d+$`)
  - Other datasets that would use it: WHO ICTRP (carried in `TrialID` / `Secondary_ID`), ClinicalTrials.gov and EU CTIS secondary IDs, Europe PMC and OpenAlex (trial IDs in publication metadata). Recommend PR-ing into `schema/join-keys.yaml` alongside `NCT_ID`, `EU_CT_NUMBER`, `EUDRACT_NUMBER`, `WHO_UTN`, and the flagged `ISRCTN_ID`.
- `license: unknown`: the ChiCTR site asserts blanket copyright ("All rights reserved") and publishes no explicit reuse/redistribution licence for its metadata. Set to `unknown` rather than inventing an SPDX code or short name. If the project wants a placeholder short name for asserted-copyright registries, `All-Rights-Reserved` or a `ChiCTR-Terms-of-Use` string could be introduced, but neither is a defined open licence. The IPD sharing policy governs registrant-supplied raw trial data, not the registry metadata licence.
- `type: [web-ui, scraper-required]` and omitted `access_test` reflect that ChiCTR exposes no official API and gates automated access behind anti-bot verification. If the project would rather represent ChiCTR access through the WHO ICTRP aggregate, consider `discovered_via: who-ictrp`; left unset because ChiCTR is a primary source in its own right, not discovered via ICTRP.
- `join_key_fields` for `WHO_UTN` uses a descriptive slug (`who-universal-trial-number`) rather than a verified JSON path, since access is via scraped HTML with no documented field schema. Re-verify against a live record or the WHO ICTRP export (`utn`) before relying on the path.
- Secondary IDs (`NCT_ID`, `EUDRACT_NUMBER`) appear in an unstructured field with sparse coverage and were deliberately excluded from `join_keys`. Confirm whether the project's inclusion threshold (present but sparse and unstructured) warrants adding them.
