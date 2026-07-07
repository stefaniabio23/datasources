---
id: ctri
name: Clinical Trials Registry - India (CTRI)
domain: clinical-biotech
entry_kind: registry
description: WHO- and ICMJE-recognised primary clinical trials registry for studies conducted in India, run by ICMR, with mandatory prospective registration since 2009.
homepage_url: https://ctri.nic.in/
docs_url: https://ctri.nic.in/Clinicaltrials/faq.php
type:
  - web-ui
  - scraper-required
auth_required: none
cost: free
license: unknown
rate_limit: "no published quota; polite low-volume public web use expected"
bulk_available: false
frequency: continuous
lag: "records appear after editorial review, typically days after submission; monthly export to WHO ICTRP"
geography: [IND]
join_keys:
  - WHO_UTN
primary_keys:
  - CTRI_ID
join_key_fields:
  - join_key: WHO_UTN
    fields: [who-universal-trial-number-utn]
mcp_status: requires-scraping
mcp_maturity: none
mcp_notes: >
  No official or community MCP and no public API. Records are only reachable through
  the JS-driven CTRI web UI (keyword/advanced search + per-trial detail page) or,
  downstream, via the monthly WHO ICTRP export. A connector would need browser
  automation over the CTRI search forms, or should route through the WHO ICTRP
  layer where CTRI records already arrive normalised to the WHO TRDS schema.
agent_use_cases:
  - India clinical trial discovery by condition, intervention, or sponsor
  - cross-registry deduplication of multinational trials via WHO UTN
  - non-US/EU trial coverage for global pipeline scans
  - regulatory and DCGI-approval status lookup for Indian studies
  - prospective-registration and transparency audits
last_verified: 2026-07-03
build_priority: medium
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: true
notes: "access_test omitted: no public no-auth structured-data endpoint. CTRI is web-UI only (advanced search at /Clinicaltrials/advancesearchmain.php). Single CTRI records also resolve via WHO ICTRP at https://trialsearch.who.int/Trial2.aspx?TrialID=CTRI/YYYY/MM/NNNNNN (verified 200, 2026-07-03). Verify freshness from the record count / last-update date shown on the CTRI home page and the monthly ICTRP transfer."
---

# Clinical Trials Registry - India (CTRI)

## Why this source matters

CTRI is India's national clinical trials registry, launched July 2007 and hosted by the ICMR-National Institute for Research in Digital Health (formerly the National Institute of Medical Statistics). It is a WHO ICTRP primary registry and an ICMJE-recognised registry, and registration has been mandatory (prospective, before first enrolment) since 15 June 2009 under the Drugs Controller General of India. That mandate makes CTRI the authoritative source for interventional and observational studies conducted in India, including drug, device, vaccine, biologic, and traditional-medicine (AYUSH) trials that frequently never appear in ClinicalTrials.gov or EU CTIS. Its records flow monthly into the WHO global trial graph, so CTRI is the India-specific complement to ClinicalTrials.gov (US), EU CTIS (EEA), and ISRCTN (UK). Secondary relevance to public-health for the large volume of publicly funded Indian health-services and prevention research.

## Agent use cases

- India clinical trial discovery by condition, intervention, or sponsor
- cross-registry deduplication of multinational trials via WHO UTN
- non-US/EU trial coverage for global pipeline scans
- regulatory and DCGI-approval status lookup for Indian studies
- prospective-registration and transparency audits

## Join strategy

The source-native primary key is the CTRI number, form `CTRI/YYYY/MM/NNNNNN` (regex `^CTRI/[0-9]{4}/[0-9]{2,3}/[0-9]+$`, e.g. `CTRI/2023/04/052053`). It is not yet a canonical registry key; see Review notes (`CTRI_ID`).

The one canonical join key CTRI captures as a structured field is `WHO_UTN`, the WHO Universal Trial Number (`^U[0-9]{4}-[0-9]{4}-[0-9]{4}$`), recorded per trial and intended as the cross-registry spine that stitches the same study across CTRI, WHO ICTRP, CTIS, and ClinicalTrials.gov. Population is sponsor-driven and sparse.

CTRI also has a free-text "Secondary IDs" area where sponsors sometimes record a ClinicalTrials.gov `NCT_ID` (or other registry numbers) for dual-registered multinational trials, but it is unstructured and inconsistently populated, so `NCT_ID` is deliberately left out of YAML `join_keys` (flagged below) rather than asserted as a reliable field. Recommended pairings: ClinicalTrials.gov and EU CTIS for cross-registry dedup via `WHO_UTN`; WHO ICTRP as the umbrella graph and the practical bulk-access path for CTRI data; OpenAlex or Europe PMC to reach associated publications (CTRI does not expose `PMID` directly).

## Access notes

Public, no auth, but web-UI only, there is no documented REST API and no bulk-download file. Two practical paths:

- **CTRI web UI (primary):** keyword search from the home page (`https://ctri.nic.in/`) or the advanced search form (`/Clinicaltrials/advancesearchmain.php`), which filters by registration status, trial type, study category (drug/device/vaccine/etc.), design, phase, sponsor type, recruitment status, and Indian state/district. Individual records render as a server-side detail page. The site is JS- and form-driven, so programmatic use means driving the forms with browser automation rather than hitting a JSON endpoint. The published per-trial data set and field definitions are documented in `CTRI_Dataset_and_Description.pdf` on the site.
- **WHO ICTRP (downstream bulk):** CTRI exports to WHO ICTRP monthly, so the cleanest way to pull CTRI records in bulk (normalised to the WHO TRDS schema) is the ICTRP Search Portal CSV/XML export. Single CTRI records also resolve at `https://trialsearch.who.int/Trial2.aspx?TrialID=CTRI/YYYY/MM/NNNNNN` (verified 200, 2026-07-03).

No published rate limit, so scrape politely and set a `User-Agent`. Freshness check: the CTRI home page shows a running registered-trial count and last-update date; ICTRP trails CTRI by up to a month.

## MCP / connector notes

No official or community MCP. Because CTRI has no API, a direct connector requires browser automation over the search forms (`mcp_status: requires-scraping`), or should route through a WHO ICTRP-based cross-registry server where CTRI data already arrives in the WHO TRDS schema, which is the lower-effort, more robust path. A useful surface: `search_trials(condition, intervention, sponsor, state, status)`, `get_trial(ctri_number)`, `resolve_by_utn(utn)`, `cross_registry_lookup(ctri_number)`. The connector must abstract over the form-driven pagination, the unstructured "Secondary IDs" free text, and the CTRI-vs-ICTRP freshness gap. A general multi-registry MCP (ClinicalTrials.gov + CTIS + ISRCTN + WHO ICTRP + CTRI) would serve three or more entries in this directory, so this is a high-value target even though the CTRI-specific surface is scraping-bound.

## Review notes

- Potential new join key for review: `CTRI_ID`
  - Entity type: clinical_trial
  - Pattern: `^CTRI/[0-9]{4}/[0-9]{2,3}/[0-9]+$` (e.g. `CTRI/2023/04/052053`)
  - Other datasets that would use it: WHO ICTRP (carries CTRI numbers in its `TrialID`/`Secondary_ID` fields), ClinicalTrials.gov and EU CTIS as secondary/related registry IDs, Europe PMC and OpenAlex (trial IDs in publication metadata). Strong candidate to PR into `schema/join-keys.yaml` alongside `NCT_ID`, `EU_CT_NUMBER`, `EUDRACT_NUMBER`, `WHO_UTN`, mirroring the pending `ISRCTN_ID` request.
- `NCT_ID` is intentionally excluded from `join_keys`: CTRI can carry an NCT number in an unstructured "Secondary IDs" free-text area for dual-registered multinational trials, but there is no dedicated structured field and population is inconsistent. Flag if the project wants it added on a present-but-sparse basis (as ICTRP handles secondary IDs).
- `license: unknown`. CTRI is described as a "free and online public record system" run by ICMR, but no formal open-data license or SPDX-mappable terms were found on the site. Data redistributed downstream via WHO ICTRP falls under WHO ICTRP terms of use (attribution, keep current, no commercial/marketing use). Recommend a human confirm whether an Indian government / ICMR public-record term applies before assigning a canonical short name; `cost: free` and `auth_required: none` reflect free public read access regardless.
- `join_key_fields` for `WHO_UTN` uses the CTRI data-set label (`who-universal-trial-number-utn`) rather than an API field path, since CTRI exposes no JSON API; re-verify against `CTRI_Dataset_and_Description.pdf` or a live record before relying on the path.
- `access_test` omitted: no public no-auth structured-data endpoint (web-UI/scraper only). The WHO ICTRP resolver returning 200 for a CTRI TrialID is documented in `notes` as the freshness/reachability check.
