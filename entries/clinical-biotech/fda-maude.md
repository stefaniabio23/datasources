---
id: fda-maude
name: FDA MAUDE (Device Adverse Events)
domain: clinical-biotech
entry_kind: event-stream
description: US FDA Manufacturer and User Facility Device Experience database of medical-device adverse-event reports (malfunctions, injuries, deaths), reachable via the CDRH MAUDE web search and the openFDA device/event REST API and bulk JSON.
homepage_url: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfmaude/search.cfm
docs_url: https://open.fda.gov/apis/device/event/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free
license: CC0
rate_limit: "240 req/min and 1,000 req/day anonymous per IP; 240 req/min and 120,000 req/day with a free API key"
bulk_available: true
frequency: weekly
lag: "reports lag the event by weeks to months; openFDA-annotated coverage runs 2009 onward, raw MAUDE from ~1992"
geography: [USA]
join_keys: []
primary_keys:
  - MDR_REPORT_KEY
  - MDR_REPORT_NUMBER
  - MDR_EVENT_KEY
  - FDA_PRODUCT_CODE
  - PMA_PMN_NUMBER
  - UDI_DI
structure: event-log
pit_reconstructable: false
revisions_possible: true
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cyanheads/openfda-mcp-server
  - github.com/Augmented-Nature/OpenFDA-MCP-Server
mcp_notes: >
  Community openFDA MCPs wrap the device/event namespace but treat it as one generic search tool;
  none model the device-array explosion, the product-code pivot, or MAUDE's passive-surveillance
  caveats. Ideal surface: search_maude_events, get_mdr_report, count_events_by_product_code,
  count_events_by_product_problem, with product-code as the cross-endpoint pivot into 510k/pma/classification.
agent_use_cases:
  - device adverse-event signal mining
  - malfunction and injury trend counts by product code
  - manufacturer post-market safety monitoring
  - narrative (mdr_text) retrieval for a device
  - death and serious-injury event surfacing
access_test:
  command: "curl -sf 'https://api.fda.gov/device/event.json?limit=1'"
  expected_status: 200
  expected_fields: [meta, results, mdr_report_key, device, event_type]
last_verified: 2026-07-02
build_priority: medium
---

# FDA MAUDE (Device Adverse Events)

## Why this source matters

MAUDE (Manufacturer and User Facility Device Experience) is the FDA's public record of what goes wrong with medical devices in the field: malfunctions, patient injuries, and deaths reported by mandatory reporters (manufacturers, importers, device user facilities) and voluntary ones (clinicians, patients). It is the post-market safety counterpart to the clearance and approval records; where the device authorization databases tell you a device reached the market, MAUDE tells you what happened after. Two access paths cover it: the CDRH MAUDE web search at `accessdata.fda.gov/scripts/cdrh/cfdocs/cfmaude/search.cfm` (the human front door, given as the homepage), and the openFDA `device/event` REST API plus bulk JSON (`https://api.fda.gov/device/event.json`), which is the programmatic surface an agent should use. This is a standalone card by design: it overlaps the broader `fda-device-databases` entry, which spans all eight device endpoints, but MAUDE is the highest-volume, highest-signal, and most caveat-laden of them, with its own event-stream shape (one record per MDR report, a nested `device` array, and free-text `mdr_text` narratives) that warrants dedicated join and access notes. Secondary relevance to `public-health` for post-market device surveillance.

## Agent use cases

- device adverse-event signal mining
- malfunction and injury trend counts by product code
- manufacturer post-market safety monitoring
- narrative (mdr_text) retrieval for a device
- death and serious-injury event surfacing

## Join strategy

None of MAUDE's device identifiers are in the canonical join-key registry, so `join_keys` is empty by design and the identifiers live in `primary_keys`. Each record is keyed by `mdr_report_key` (the stable report id), with `report_number` and `event_key` as secondary handles. The joinable device attributes sit inside the nested `device[]` array: the 3-letter FDA product code (`device.device_report_product_code`), the premarket number (`pma_pmn_number` at the top level, holding either a 510(k) `K######` or a PMA `P######`, with `device.baseline_510_k__number` as an alternate carrier), and the UDI-DI (`device.udi_di` / `device.udi_public`, populated only on reports filed after the 2022 field addition). The `device.openfda` enrichment block adds `regulation_number`, `device_class`, `fei_number`, and `registration_number` when the annotation succeeds.

The 3-letter product code is the cross-database pivot: it is the one field that also travels across the `510k`, `pma`, `classification`, `recall`, and `udi` endpoints, so a MAUDE product-code count histograms adverse events for a device class, and the same code resolves class and regulation against `classification` or clearances against `510k`. None of product code, 510(k)/PMA number, or UDI-DI is a canonical join key yet; all three are flagged below and mirror the candidates already raised in `fda-device-databases`.

## Access notes

Hit `https://api.fda.gov/device/event.json?search=...&limit=...`. HTTPS only. Anonymous access is 1,000 req/day per IP (too low for iterative work); a free API key (`?api_key=...`) lifts that to 120,000 req/day, both under the 240 req/min ceiling. The query grammar is the same Lucene-style syntax as the other openFDA endpoints: `search=device.device_report_product_code:"DXN"+AND+event_type:"Death"`, `count=device.openfda.device_class` for histograms, `skip=`/`limit=` to paginate (max `limit=1000`, max `skip=25000`). Useful pivots: `event_type` (Death / Injury / Malfunction), `product_problems`, `date_of_event`, `date_received`.

Bulk: zipped JSON mirroring the API shape at `https://download.open.fda.gov/`, index at `https://api.fda.gov/download.json`. The `device/event` corpus is large and sharded across many yearly files; each refresh is a full re-download, no incremental diffs. Use bulk for anything past the 25K skip ceiling. The CDRH MAUDE web search (the homepage URL) is the human mirror and the only place to browse individual reports interactively.

Gotchas:

- MAUDE is passive surveillance: reports are unverified, often incomplete, and duplicated; the FDA states a causal relationship between device and event cannot be inferred from a report. Counts are signals, not incidence rates or denominators.
- The `device` array can hold multiple devices per report; product code and UDI live inside it, not at the top level. Flatten before counting.
- The `openfda` enrichment (class, regulation, FEI) is best-effort and absent on many records, especially older ones.
- Supplemental and follow-up reports restate earlier ones; `mdr_report_key` is stable but a single incident can span multiple report versions, so treat the corpus as revisable (`revisions_possible: true`), not point-in-time frozen.

## MCP / connector notes

Community openFDA MCPs (`cyanheads/openfda-mcp-server`, `Augmented-Nature/OpenFDA-MCP-Server`, both GitHub) expose the `device/event` namespace through a generic search tool but do not model MAUDE's specifics: the nested `device[]` explosion, the product-code pivot, the death/injury/malfunction split, or the passive-surveillance caveats agents must surface alongside any count. A MAUDE-specific surface would expose `search_maude_events`, `get_mdr_report` (by `mdr_report_key`), `count_events_by_product_code`, and `count_events_by_product_problem`, with device-array flattening, Lucene helpers, API-key injection, bulk-vs-API routing past the 25K skip ceiling, and a built-in caveat banner so downstream agents never treat report counts as failure rates.

## Review notes

- Potential new join key for review: `FDA_PRODUCT_CODE`. Entity type: `device_product_class`. Pattern: 3-letter alpha (e.g. `DXN`, `KPR`). The cross-database glue: the single identifier that travels across every FDA device endpoint (510k, pma, classification, recall, event, udi). Highest-value candidate; already flagged in `fda-device-databases`.
- Potential new join key for review: `UDI_DI`. Entity type: `device_identifier`. Pattern: GS1/HIBCC/ICCBBA device identifier string (no single canonical regex; GS1 GTIN-14 is `^[0-9]{14}$`). Other datasets that would use it: GUDID/openFDA `udi` endpoint, hospital supply and recall trackers. Populated only on post-2022 MAUDE reports.
- Potential new join key for review: `FDA_510K_NUMBER`. Entity type: `device_clearance`. Pattern: `^K[0-9]{6}$`. Carried here in `pma_pmn_number` / `device.baseline_510_k__number`. Other datasets: CDRH 510(k) database, UDI, recalls.
- Potential new join key for review: `FDA_PMA_NUMBER`. Entity type: `device_approval`. Pattern: `^P[0-9]{6}(/S[0-9]{3})?$`. Carried here in `pma_pmn_number`. Other datasets: CDRH PMA database, UDI, recalls.
- Note: the openFDA `device/event` endpoint packs both 510(k) and PMA numbers into the single `pma_pmn_number` field, so `PMA_PMN_NUMBER` is listed as a primary key; disambiguation to a specific 510(k) vs PMA canonical key would happen at promotion time.
- License is CC0 / US public domain for the FDA data itself. GMDN nomenclature terms that appear in linked UDI/GUDID data are licensed separately by the GMDN Agency and are not covered by CC0.
- Intentional overlap with `fda-device-databases`: this MAUDE card is deliberately standalone per the task brief. Confirm the project wants both the broad device-databases card and this MAUDE-specific one rather than folding MAUDE detail into the sibling.
