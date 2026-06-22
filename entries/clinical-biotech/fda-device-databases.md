---
id: fda-device-databases
name: FDA Medical Device Databases
domain: clinical-biotech
entry_kind: registry
description: US FDA medical-device authorizations and post-market safety data via openFDA device endpoints and the CDRH databases, covering 510(k) clearances, PMA approvals, De Novo, classification, recalls/enforcement, MAUDE adverse events, and UDI.
homepage_url: https://open.fda.gov/apis/device/
docs_url: https://open.fda.gov/apis/device/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free
license: CC0
rate_limit: "240 req/min and 1,000 req/day anonymous per IP; 240 req/min and 120,000 req/day with free API key"
bulk_available: true
frequency: "weekly for most device endpoints; CDRH web databases refreshed on similar cadence"
lag: "MAUDE adverse-event ingestion lags reports by weeks to months; clearances and recalls fresher (days to weeks)"
geography: [USA]
join_keys: []
primary_keys:
  - K_NUMBER
  - PMA_NUMBER
  - DENOVO_NUMBER
  - FDA_PRODUCT_CODE
  - REGULATION_NUMBER
  - RECALL_NUMBER
  - MDR_REPORT_KEY
  - UDI_DI
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cmanohar/mcp-openfda
  - github.com/pipeworx-io/mcp-openfda
mcp_notes: >
  Community openFDA MCPs exist but skew toward the drug endpoints; device coverage (510k, pma,
  classification, event, udi) is inconsistent and the predicate-device chain is out of scope for
  all of them. Ideal surface: search_510k, get_pma, lookup_product_code, list_device_recalls,
  search_maude_events, lookup_udi, with product-code as the cross-endpoint pivot.
agent_use_cases:
  - device clearance and approval lookup
  - product-code class and regulation resolution
  - device recall and enforcement monitoring
  - MAUDE adverse-event signal mining
  - UDI to device-identifier resolution
access_test:
  command: "curl -sf 'https://api.fda.gov/device/510k.json?limit=1'"
  expected_status: 200
  expected_fields: [meta, results]
last_verified: 2026-06-22
build_priority: medium
---

# FDA Medical Device Databases

## Why this source matters

The device side of the FDA's public data is the canonical record of how a medical device reaches and stays on the US market: which pathway cleared or approved it (510(k) substantial equivalence, PMA, or De Novo), what class and regulation govern it, and what went wrong after launch (recalls, enforcement actions, MAUDE adverse-event reports). It is reachable two ways: the openFDA device REST API and bulk JSON (base `https://api.fda.gov/device/<endpoint>.json`), and the older CDRH web databases at accessdata.fda.gov (the 510(k) database at `cfPMN/pmn.cfm`, plus PMA, classification, and registration/listing). This entry covers the device endpoints specifically (510k, pma, classification, recall, enforcement, event, registrationlisting, udi), distinct from the drug-focused `openfda` entry. Both share the same auth, rate limits, CC0 licence, and Elasticsearch query layer, but the device identifiers, join targets, and predicate-chain gotcha are different enough to warrant their own card. Secondary relevance to `public-health` for post-market device surveillance.

## Agent use cases

- device clearance and approval lookup
- product-code class and regulation resolution
- device recall and enforcement monitoring
- MAUDE adverse-event signal mining
- UDI to device-identifier resolution

## Join strategy

None of the device-side identifiers are in the canonical join-key registry, so `join_keys` is empty by design and the identifiers live in `primary_keys`. The device records mint: 510(k) numbers (`K######`), PMA numbers (`P######` plus `S###` supplement suffixes), De Novo numbers (`DEN######`), the 3-letter product code, the CFR regulation number, recall numbers, MAUDE `mdr_report_key`, and the UDI-DI. The 3-letter product code is the cross-database glue: it is the one field that travels across 510k, pma, classification, recall, event, and udi, so a product-code lookup against `classification` resolves device class and regulation, and the same code pivots into clearances, approvals, recalls, and adverse events. The regulation number (CFR Title 21 citation) is the secondary pivot to the classification regulation.

The predicate-device chain (which prior device a 510(k) claims substantial equivalence to) is NOT in the API or the structured CDRH database. It lives only inside the 510(k) Summary PDFs linked from each clearance record. Any agent reconstructing equivalence lineage has to fetch and parse those PDFs; the structured data gives you the clearance, not the predicate it stands on.

If product code and the FDA device-pathway numbers are promoted to canonical join keys (flagged below), this entry would expose them for cross-source joining against any future device-registry, recall-tracker, or UDI-resolution source.

## Access notes

Hit `https://api.fda.gov/device/<endpoint>.json?search=...&limit=...` where endpoint is one of `510k`, `pma`, `classification`, `recall`, `enforcement`, `event`, `registrationlisting`, `udi`. 510(k) clearances run from 1976; MAUDE `event` records carry openFDA annotations from 2009 onward. HTTPS only. Anonymous access is 1,000 req/day per IP, too low for iterative work; a free API key (`?api_key=...`) lifts that to 120,000 req/day. Both share the 240 req/min ceiling. Query syntax is the same Lucene-style grammar as the drug endpoints (`search=product_code:"DXN"+AND+decision_date:[20200101+TO+20231231]`); `count=` histograms a field, `skip=`/`limit=` paginate (max `limit=1000`, max `skip=25000`).

Bulk: zipped JSON mirroring the API shape at `https://download.open.fda.gov/`, index at `https://api.fda.gov/download.json`. MAUDE `event` is large and sharded across many files; full re-download per refresh, no incremental diffs. The CDRH web databases (510(k) search at `https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm`) are the human-facing mirror and the place to reach the 510(k) Summary PDFs that the API does not expose.

Gotchas:

- MAUDE reports are voluntary and unverified; counts are signals, not device-failure incidence.
- The `openfda` enrichment block (device class, regulation number, registration/FEI numbers) is best-effort and not present on every record.
- The record for one device is split across endpoints (clearance in `510k`, class in `classification`, failures in `event`/`recall`) plus the Summary PDFs; there is no single joined device object.
- Predicate-device lineage is only in the 510(k) Summary PDFs, never in the structured data.

## MCP / connector notes

The community openFDA MCPs (`cmanohar/mcp-openfda`, `pipeworx-io/mcp-openfda`, both GitHub) nominally cover the device namespace but in practice expose drug endpoints best; device 510k/pma/classification/udi coverage is inconsistent and none handle the predicate-PDF problem. A device-specific connector surface would expose `search_510k`, `get_pma`, `lookup_product_code` (the cross-endpoint pivot returning class + regulation), `list_device_recalls`, `search_maude_events`, and `lookup_udi`, with built-in Lucene helpers, API-key injection, bulk-vs-API routing past the 25K skip ceiling, and ideally a `fetch_510k_summary_pdf` helper that retrieves and parses the predicate chain the structured API omits.

## Review notes

- Potential new join key for review: `FDA_PRODUCT_CODE`. Entity type: `device_product_class`. Pattern: 3-letter alpha (e.g. `DXN`, `KPR`). The cross-database glue: it is the single identifier that travels across every device endpoint (510k, pma, classification, recall, event, udi). Highest-value candidate of the four; promoting it would unlock product-code joins across any future device source.
- Potential new join key for review: `FDA_510K_NUMBER`. Entity type: `device_clearance`. Pattern: `^K[0-9]{6}$`. Other datasets that would use it: CDRH 510(k) database, UDI database, recall/enforcement reports.
- Potential new join key for review: `FDA_PMA_NUMBER`. Entity type: `device_approval`. Pattern: `^P[0-9]{6}(/S[0-9]{3})?$` (base PMA plus optional supplement suffix). Other datasets that would use it: CDRH PMA database, UDI, recalls.
- Potential new join key for review: `FDA_DENOVO_NUMBER`. Entity type: `device_authorization`. Pattern: `^DEN[0-9]{6}$`. Other datasets that would use it: CDRH De Novo classification orders, classification database.
- License is CC0 / US public domain for the FDA data itself. The GMDN (Global Medical Device Nomenclature) terms surfaced in the UDI/GUDID data are licensed separately by the GMDN Agency and are not covered by CC0; downstream redistribution of GMDN terms needs a separate licence.
- `geography: [USA]` follows the ISO-3 convention used in the sibling `openfda` entry.
- This entry deliberately overlaps the existing `openfda` entry (which lists `K_NUMBER`, `PMA_NUMBER`, `MDR_REPORT_KEY` in its `primary_keys` and mentions device endpoints). The split is intentional: `openfda` is the drug-side card, this is the device-side card. Confirm the project wants both rather than folding device detail into the single `openfda` entry.
