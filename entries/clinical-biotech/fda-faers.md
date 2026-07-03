---
id: fda-faers
name: FDA Adverse Event Reporting System (FAERS)
domain: clinical-biotech
entry_kind: event-stream
description: US FDA post-market pharmacovigilance database of spontaneous adverse-event and medication-error reports for drugs and therapeutic biologics, published as quarterly case-level extract files.
homepage_url: https://www.fda.gov/drugs/fda-adverse-event-monitoring-system-aems/fda-adverse-event-monitoring-system-aems-latest-quarterly-data-files
docs_url: https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "none published; bulk ZIP download only"
bulk_available: true
frequency: quarterly
lag: "posted ~1-2 months after each quarter closes; cases can be amended or deleted in later quarters"
geography: [global]
structure: event-log
pit_reconstructable: true
revisions_possible: true
join_keys:
  - MEDDRA_TERM
  - FDA_APPLICATION_NUMBER
primary_keys:
  - PRIMARYID
  - CASEID
  - ISR
join_key_fields:
  - join_key: MEDDRA_TERM
    fields: [reac.pt, indi.indi_pt]
  - join_key: FDA_APPLICATION_NUMBER
    fields: [drug.nda_num]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - adverse-event case retrieval
  - drug safety signal detection
  - disproportionality analysis (PRR / ROR)
  - drug-reaction co-occurrence mining
  - case-level demographic and outcome analysis
access_test:
  command: "curl -sf -r 0-64 -o /dev/null -w '%{http_code}' 'https://fis.fda.gov/content/Exports/faers_ascii_2024q1.zip'"
  expected_status: 206
last_verified: 2026-07-02
build_priority: medium
---

# FDA Adverse Event Reporting System (FAERS)

## Why this source matters

FAERS is the US FDA's spontaneous-reporting database for post-market drug and therapeutic-biologic safety, the primary evidence base for regulatory pharmacovigilance and the reference dataset for disproportionality methods (PRR, ROR, EBGM). Anyone can submit; reports come from manufacturers (mandatory), healthcare professionals, and consumers (voluntary via MedWatch), including foreign-sourced cases. FDA publishes de-identified case-level extracts each quarter (2004 to present, plus legacy AERS/`ISR` data back to 1969) as ZIP archives of seven relational files in ASCII and XML. This entry is the raw quarterly database, distinct from the `openfda` card: openFDA serves a queryable, NDC/RxNorm-enriched Elasticsearch view of the same FAERS cases, while the quarterly extracts carry the full case detail openFDA flattens away, drug role codes (primary/secondary suspect, concomitant, interacting), dechallenge/rechallenge, therapy start/stop dates (THER), report sources (RPSR), and case-version history. Load the raw files into a relational DB when you need case-level pharmacoepidemiology; use openFDA when you need a hosted query API.

## Agent use cases

- adverse-event case retrieval
- drug safety signal detection
- disproportionality analysis (PRR / ROR)
- drug-reaction co-occurrence mining
- case-level demographic and outcome analysis

## Join strategy

The raw quarterly files are drug-name-based, not code-based, and this is the load-bearing difference from the `openfda` entry. Drugs are free text in the DRUG file (`drugname` as reported, `prod_ai` active ingredient); there is no native `NDC` and no native `RXNORM_CUI`. To join FAERS drugs to coded drug identifiers you must resolve names yourself (RxNorm approximate-match / RxNav, or borrow openFDA's `openfda` enrichment block keyed on the same `primaryid`).

Canonical keys that ARE natively present:

- `MEDDRA_TERM` — reactions are coded as MedDRA Preferred Terms in the REAC file (`pt`); indications are MedDRA terms in the INDI file (`indi_pt`). This is the reliable join axis, pair with any MedDRA-coded source (openFDA, EudraVigilance summaries, SIDER, label ADR sections).
- `FDA_APPLICATION_NUMBER` — the DRUG file carries `nda_num` (NDA/ANDA/BLA number) when the reporter supplied it, giving a crosswalk to Drugs@FDA, Orange Book, and Purple Book. Coverage is partial (frequently blank for OTC, foreign, or older cases).

Source-internal identifiers stay out of the canonical registry: `PRIMARYID` (unique case-version row), `CASEID` (stable across versions of the same case; keep only the latest version per case to avoid double counting), `ISR` (legacy pre-2012Q3 individual-safety-report id used by the old AERS files), and `drug_seq` / `indi_drug_seq` for within-case linkage across the seven files. Use these to stitch DEMO, DRUG, REAC, OUTC, RPSR, THER, and INDI within a quarter, not for cross-source joins.

## Access notes

No API and no auth for the raw data: download quarterly ZIPs directly. ASCII archives follow `https://fis.fda.gov/content/Exports/faers_ascii_<yyyy>q<q>.zip` (XML variant `faers_xml_<yyyy>q<q>.zip`); the QDE portal (`docs_url`) lists every quarter and the ASCII/DELETED-case documentation. Each ASCII archive unzips to seven pipe-delimited files named `<FILE><yy>Q<q>.txt` (e.g. `DEMO24Q1.txt`). Join within a quarter on `primaryid`; deduplicate cases on `caseid` keeping the highest `caseversion`, and apply the quarter's deleted-case list before analysis. Note the FDA server returns `Content-Length: 0` on HEAD (Qlik quirk); verify freshness with a ranged GET or a normal GET, not HEAD. The original FDA landing URL (`/drugs/drug-approvals-and-databases/fda-adverse-event-reporting-system-faers-database`) now 404s after FDA's AEMS rebrand; the AEMS latest-quarterly-data-files page is the current landing. For interactive exploration without downloading, the FAERS Public Dashboard (`https://fis.fda.gov/sense/app/...`) offers filtered counts but is not bulk-exportable.

## MCP / connector notes

No MCP targets the raw quarterly extracts, and the value of building one is low: the query use case is already served by openFDA's FAERS endpoint, which has several community MCPs (see the `openfda` entry). The raw files are bulk-load-into-a-database territory, not a request/response surface, and their genuine advantage (full case-version and role-code detail) is consumed by pharmacoepidemiology pipelines, not chat agents. If built anyway, the useful surface is not an API wrapper but an ETL helper: `download_quarter`, `load_ascii_to_db`, `dedupe_cases` (latest `caseversion`, apply deleted list), `compute_disproportionality` (2x2 by drug x PT). It must abstract over schema drift (fields added from 2012Q3 and 2014Q3), the `ISR`-to-`PRIMARYID` legacy break, and case deduplication, the three things that silently corrupt naive counts.

## Review notes

- Join-key hints reconciled against the actual source. `NDC` and `RXNORM_CUI` were supplied as hints but are NOT natively present in the raw FAERS quarterly files, which identify drugs by free-text name (`drugname` / `prod_ai`). Listing them in `join_keys` would misrepresent the payload and break the generated join-field index, so they are excluded here and documented under Join strategy as resolution-dependent. Both keys ARE valid for the `openfda` card, which serves the enriched FAERS view, that is the intended split between the two entries. `MEDDRA_TERM` (native, REAC.pt / INDI.indi_pt) is mapped.
- Added `FDA_APPLICATION_NUMBER` (native via DRUG.`nda_num`) which was not in the hint list but is genuinely exposed and already in the registry. Coverage is partial.
- No new canonical join keys proposed; all mapped and discussed keys already exist in `schema/join-keys.yaml`.
- License: the QDE page publishes no explicit licence statement. Treated as `US-Government-Public-Domain` (US federal work, 17 USC 105); files are de-identified per FDA before release.
- `homepage_url` uses the current AEMS quarterly-data-files page because the original target URL 404s post-rebrand. `access_test` uses a ranged GET (returns 206) because the server reports `Content-Length: 0` on HEAD; a normal GET returns 200.
- Overlaps deliberately with `openfda` (same underlying cases, distinct access surface and pharmacovigilance use). Not a duplicate; see Why this source matters for the split.
