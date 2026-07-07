---
id: jrct
name: Japan Registry of Clinical Trials (jRCT)
domain: clinical-biotech
entry_kind: registry
description: Japan's national clinical-trial registry run by the Ministry of Health, Labour and Welfare, disclosing specified clinical trials and regenerative-medicine studies under the Clinical Trials Act; a WHO ICTRP primary registry that, together with the legacy UMIN-CTR, forms the Japan Primary Registries Network (JPRN).
homepage_url: https://jrct.mhlw.go.jp/
docs_url: https://jrct.mhlw.go.jp/en-top
type:
  - web-ui
  - scraper-required
auth_required: none
cost: free
license: jRCT-Terms-of-Use
rate_limit: "no public API; terms prohibit automated/bulk download beyond personal use"
bulk_available: false
frequency: continuous
lag: "sponsor-driven; records appear after MHLW submission and are updated as trials progress"
geography: [JPN]
join_keys:
  - WHO_UTN
primary_keys:
  - JRCT_ID
  - UMIN_ID
join_key_fields:
  - join_key: WHO_UTN
    fields: [who-universal-trial-number]
mcp_status: requires-scraping
mcp_maturity: none
mcp_notes: >
  No official or community MCP. jRCT exposes only a JS-driven web UI with per-record HTML pages and
  no documented REST/bulk API; its terms forbid programmatic download beyond personal use, so a direct
  connector must scrape politely (or route through WHO ICTRP / the NIPH rctportal cross-search instead).
  Suggested surface: search_trials, get_trial (parse the jRCT record page and secondary-ID block),
  cross_registry_lookup (jRCT to WHO UTN, UMIN, NCT). An unofficial UMIN-CTR client (github.com/mokjpn/umin-ctr)
  is the closest existing tooling for the legacy sister registry.
agent_use_cases:
  - Japanese clinical trial discovery by disease or intervention
  - regenerative-medicine and specified-clinical-trial lookup under the Clinical Trials Act
  - cross-registry deduplication with ClinicalTrials.gov and EU CTIS via WHO UTN
  - sponsor and institution pipeline monitoring in Japan
  - legacy academic trial retrieval via UMIN-CTR
access_test:
  command: "curl -sf -A 'datasources-verify' -o /dev/null -w '%{http_code}' 'https://jrct.mhlw.go.jp/en-top'"
  expected_status: 200
last_verified: 2026-07-03
build_priority: medium
structure: registry-snapshot
revisions_possible: true
notes: "Homepage migrated from https://jrct.niph.go.jp/ (now unreachable) to https://jrct.mhlw.go.jp/. NIPH runs the cross-search portal https://rctportal.niph.go.jp/en over jRCT + UMIN-CTR + JMACCT + JAPIC. Legacy sister registry UMIN-CTR: https://center6.umin.ac.jp/cgi-open-bin/ctr_e/index.cgi (verified 200 on 2026-07-03)."
---

# Japan Registry of Clinical Trials (jRCT)

## Why this source matters

jRCT is Japan's national clinical-trial registry, operated by the Ministry of Health, Labour and Welfare (MHLW) and launched in 2018 to disclose trials submitted under the Clinical Trials Act (specified clinical trials) and the Act on the Safety of Regenerative Medicine. It became a WHO ICTRP primary registry in December 2018 and is the modern anchor of the Japan Primary Registries Network (JPRN), which also feeds WHO. jRCT is the Japanese counterpart to ClinicalTrials.gov (US), EU CTIS (EEA), and ISRCTN (UK): the authoritative source for interventional and regenerative-medicine trials conducted in Japan, including many industry and physician-initiated studies that never register elsewhere.

This entry also covers the legacy **UMIN-CTR** (UMIN Clinical Trials Registry), run by the University Hospital Medical Information Network Center at the University of Tokyo since 2005. UMIN-CTR is the older academic-facing WHO primary registry for Japan; it holds a large back-catalogue of investigator-initiated trials (IDs `UMIN000000000` and legacy `C000000000`). jRCT did not absorb UMIN-CTR, so both must be searched to cover Japanese trials across time. The NIPH "Clinical Trials Search" portal (rctportal) cross-searches jRCT, UMIN-CTR, JMACCT, and JAPIC in one query.

## Agent use cases

- Japanese clinical trial discovery by disease or intervention
- regenerative-medicine and specified-clinical-trial lookup under the Clinical Trials Act
- cross-registry deduplication with ClinicalTrials.gov and EU CTIS via WHO UTN
- sponsor and institution pipeline monitoring in Japan
- legacy academic trial retrieval via UMIN-CTR

## Join strategy

The source-native primary key is the **jRCT number**, form `jRCT` + a lowercase letter + digits, e.g. `jRCTs041220087` (pattern `^jRCT\w?\d+$`). The letter encodes the regulatory route (`s` denotes a specified clinical trial under the Clinical Trials Act; other letters cover regenerative-medicine and enterprise/physician-initiated categories). UMIN-CTR mints its own **UMIN ID** (`UMIN` + 9 digits, plus legacy `C` + 9-digit numbers). Neither is yet a canonical registry key; see Review notes.

The one canonical join key jRCT reliably exposes is `WHO_UTN` (WHO Universal Trial Number), part of the WHO-required Trial Registration Data Set surfaced on each record. Records may also list secondary IDs from other registries (UMIN, JapicCTI, and occasionally a ClinicalTrials.gov `NCT_ID`), but these are free-text and inconsistently populated, so they are not asserted as structured `join_keys` here.

Recommended pairings: ClinicalTrials.gov and EU CTIS for cross-registry dedup via `WHO_UTN`; WHO ICTRP as the umbrella graph that already ingests jRCT and UMIN-CTR; the NIPH rctportal for a single Japan-wide cross-search. To reach a trial's publications, resolve through WHO ICTRP or match sponsor/condition into OpenAlex or Europe PMC (jRCT does not itself expose `PMID`, `DOI`, or `NCT_ID` as structured fields).

## Access notes

jRCT is a JavaScript-driven web UI at `https://jrct.mhlw.go.jp/` (English at `/en-top`). Search supports free text, disease/target name, recruitment status (Pending / Recruiting / All), and prefecture of the implementing institution. Each result resolves to an HTML detail page. There is **no documented REST or bulk API**, and the terms explicitly prohibit downloading data by automated programming beyond the scope of personal use, so treat programmatic access as scraping and throttle accordingly. For freshness, re-run a search in the UI and check record update dates; the registry updates continuously as sponsors submit and revise plans.

UMIN-CTR is a separate CGI web UI (`https://center6.umin.ac.jp/cgi-open-bin/ctr_e/index.cgi`), fully bilingual because UMIN requires English for all text fields, with per-record `ctr_view.cgi?recptno=...` pages. An unofficial client exists (`github.com/mokjpn/umin-ctr`).

For a compliant programmatic path, prefer the **WHO ICTRP** export (which already aggregates JPRN records) or the **NIPH rctportal** cross-search, rather than scraping jRCT directly. The `jrct.niph.go.jp` host in older references now refuses connections; the live registry is `jrct.mhlw.go.jp`.

## MCP / connector notes

No official or community MCP. Building one directly on jRCT is awkward: JS-rendered pages, no API contract, and terms that bar automated bulk download. The higher-value move is a general Japan-trials (or multi-registry) connector that reads through WHO ICTRP / rctportal for coverage and only scrapes jRCT/UMIN record pages for fields the aggregators drop. Suggested surface:

- `search_trials(condition, intervention, status, prefecture, source)` - unify jRCT + UMIN-CTR (via rctportal) with normalised status vocabularies.
- `get_trial(id)` - accept a jRCT number or UMIN ID; parse the record page and its secondary-ID block.
- `cross_registry_lookup(id)` - surface `WHO_UTN` and any listed UMIN / JapicCTI / NCT secondary IDs for dedup.

The MCP must abstract over two different site technologies (jRCT SPA vs UMIN CGI), the personal-use download restriction, and the free-text, inconsistently populated secondary-ID fields.

## Review notes

- Potential new join key for review: `JRCT_ID`
  - Entity type: clinical_trial
  - Pattern: `^jRCT\w?\d+$` (e.g. `jRCTs041220087`; the lowercase letter encodes the regulatory route)
  - Other datasets that would use it: WHO ICTRP, NIPH rctportal, ClinicalTrials.gov and EU CTIS (as secondary/related registry IDs), OpenAlex and Europe PMC (trial IDs cited in publications). Recommend PR-ing alongside the existing clinical-registry keys (`NCT_ID`, `EU_CT_NUMBER`, `EUDRACT_NUMBER`, `WHO_UTN`).
- Potential new join key for review: `UMIN_ID`
  - Entity type: clinical_trial
  - Pattern: `^(UMIN[0-9]{9}|C[0-9]{9})$` (current `UMIN000001159`; legacy `C000000000`)
  - Other datasets that would use it: WHO ICTRP, NIPH rctportal, and jRCT/other-registry records that cite UMIN as a secondary ID. Same JPRN cluster as `JRCT_ID`.
- `license: jRCT-Terms-of-Use` is a placeholder canonical short name, not an SPDX code. jRCT publishes no open-data licence; its terms permit appropriate public use but prohibit automated download beyond personal use. UMIN-CTR has its own separate terms. Flag whether a registered short name (or per-registry split) is wanted before merge.
- Only `WHO_UTN` is asserted as a structured `join_key`; jRCT/UMIN native IDs and free-text secondary IDs (NCT, JapicCTI) are intentionally left out of `join_keys` pending the two new-key decisions above. Flag if the project wants `NCT_ID` added on the strength of the (inconsistent) secondary-ID field.
- `access_test` was executed on 2026-07-03: `curl` to `https://jrct.mhlw.go.jp/en-top` returned 200 (and `center6.umin.ac.jp` UMIN-CTR search returned 200). The task-supplied homepage `https://jrct.niph.go.jp/` returned no connection (000); homepage_url set to the live `jrct.mhlw.go.jp` per the fallback rule.
