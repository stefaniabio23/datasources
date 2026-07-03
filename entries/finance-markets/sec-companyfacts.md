---
id: sec-companyfacts
name: SEC EDGAR Company Facts (XBRL)
domain: finance-markets
entry_kind: panel
description: Structured XBRL financial facts for US SEC filers, queryable per-company (company facts / concept) or per-period across all issuers (frames).
homepage_url: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
docs_url: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "10 req/sec across all data.sec.gov endpoints; descriptive User-Agent with contact email required or HTTP 403"
bulk_available: true
frequency: within minutes of filing acceptance; nightly bulk companyfacts.zip refresh (~3am ET)
lag: "minutes from filing acceptance to XBRL API availability"
geography: [USA]
structure: panel
pit_reconstructable: true
revisions_possible: true
join_keys:
  - CIK
  - TICKER
  - DATE
primary_keys:
  - CIK
  - ACCESSION_NUMBER
  - US_GAAP_TAG
join_key_fields:
  - join_key: CIK
    fields: [cik, data.cik]
  - join_key: TICKER
    fields: ["company_tickers.json:ticker"]
  - join_key: DATE
    fields: ["units.*.start", "units.*.end", "units.*.filed", "facts.us-gaap.*.units.*.end", "data.end"]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/stefanoamorelli/sec-edgar-mcp
  - github.com/cyanheads/secedgar-mcp-server
mcp_notes: >
  Community SEC MCPs expose get_company_facts, get_company_concept, and get_frame over these
  same endpoints. A dedicated fundamentals connector should abstract CIK zero-padding, resolve
  ticker to CIK via company_tickers.json, inject a compliant User-Agent, enforce 10 req/sec, and
  flatten the deeply nested units payload into tidy (tag, unit, period, value, filed) rows.
agent_use_cases:
  - structured financial-statement extraction
  - cross-company fundamentals benchmarking
  - point-in-time fundamentals reconstruction
  - concept-level time series (revenue, EPS, debt)
  - XBRL-tagged screening across all US filers
access_test:
  command: "curl -sf -A 'DatasourcesBot contact@example.com' 'https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json'"
  expected_status: 200
  expected_fields: [cik, entityName, facts]
last_verified: 2026-07-02
build_priority: high
notes: "Requests without a descriptive User-Agent (including a contact email) are rejected with HTTP 403. Own card despite corporate-registry/sec-edgar: this entry is the fundamentals-focused XBRL surface (companyfacts / companyconcept / frames), where the broader sec-edgar card covers submissions, full-text search, and the raw filing archive."
---

# SEC EDGAR Company Facts (XBRL)

## Why this source matters

The `data.sec.gov/api/xbrl/*` endpoints are the cleanest free source of structured fundamentals for US SEC filers. Every value a company tags in XBRL when it files a 10-K, 10-Q, or 8-K is exposed three ways: `companyfacts` (all standardised facts for one issuer), `companyconcept` (one concept across time for one issuer), and `frames` (one concept across every issuer for a single reporting period). Operated by the US Securities and Exchange Commission, fully public-domain (17 USC 105), no auth, no key. Each datapoint carries its own `filed` date and reporting `frame`, so the panel supports genuine point-in-time reconstruction rather than only the latest restated view. Secondary domain is `corporate-registry`: `CIK` is the SEC's canonical filer identifier. This is a dedicated card for the XBRL fundamentals surface; the broader `corporate-registry/sec-edgar` entry covers submissions history, the bulk filing archive, and full-text search.

## Agent use cases

- structured financial-statement extraction
- cross-company fundamentals benchmarking
- point-in-time fundamentals reconstruction
- concept-level time series (revenue, EPS, debt)
- XBRL-tagged screening across all US filers

## Join strategy

`CIK` is the primary key and the only identifier the XBRL endpoints accept directly (zero-padded to 10 digits in the URL, e.g. `CIK0000320193`). It appears as `cik` on `companyfacts`/`companyconcept` and as `data.cik` on `frames` rows. `TICKER` is not in the XBRL payloads; resolve ticker to CIK first via the sibling lookup file `https://www.sec.gov/files/company_tickers.json`, then query. `DATE` keys every fact through `start`/`end` (period) and `filed` (disclosure date) fields, which is what enables point-in-time slicing.

Source-native identifiers useful for intra-EDGAR joins but not in the canonical registry:

- `ACCESSION_NUMBER` (`accn`, e.g. `0000320193-24-000123`): the filing each fact came from; joins back to the raw document archive.
- `US_GAAP_TAG` (the XBRL concept name, e.g. `Revenues`, `AccountsPayableCurrent`): the taxonomy element that names the financial line item.

Pair with `corporate-registry/sec-edgar` for submission metadata and primary documents, OpenFIGI for `CUSIP`/`ISIN`/`FIGI` on the underlying securities, and FRED or Polygon for market-side series to align against the fundamentals.

## Access notes

Three endpoints, all under `https://data.sec.gov/api/xbrl/`:

- `companyfacts/CIK##########.json` - every standardised fact for one issuer, nested `facts.<taxonomy>.<tag>.units.<unit>[]`.
- `companyconcept/CIK##########/us-gaap/<Concept>.json` - one concept across time for one issuer.
- `frames/us-gaap/<Concept>/<Unit>/CY####Q#I.json` - one concept across all issuers for one period (the trailing `I` marks instantaneous/point-in-time concepts; flow concepts drop it).

Bulk alternative: `https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip`, refreshed nightly ~3am ET, is faster than paginating per-company for full-universe pulls.

Hard rules:

- 10 requests/second across all SEC hosts; persistent abuse triggers IP-level throttling.
- `User-Agent` header MUST identify the requester and a contact email; default curl and anonymous browsers get HTTP 403.
- CORS is not supported on `data.sec.gov`; server-side fetch only.
- Only standard taxonomies (`us-gaap`, `ifrs-full`, `dei`, `srt`) are aggregated. Company-specific extension concepts never appear in `frames` or `companyfacts`.
- Amended filings restate values, so the same (tag, period) can have multiple datapoints with different `accn`/`filed`; dedupe on the latest `filed` for a current view, or filter by `filed <= as_of` for point-in-time.

## MCP / connector notes

Covered by the same community SEC MCPs as the broader EDGAR card (`stefanoamorelli/sec-edgar-mcp`, `cyanheads/secedgar-mcp-server`); none official, and their XBRL handling varies. A fundamentals-focused connector should expose `get_company_facts`, `get_company_concept`, `get_frame`, and a `lookup_cik_by_ticker` helper backed by `company_tickers.json`. It must abstract CIK zero-padding, inject a compliant `User-Agent`, enforce the 10 req/sec ceiling with client-side queueing, and flatten the deeply nested `units` structure into tidy `(cik, tag, unit, start, end, val, accn, filed, frame)` rows so agents get a rectangular panel instead of raw JSON.

## Review notes

Own card despite the existing `corporate-registry/sec-edgar` entry: this one is scoped to the XBRL fundamentals surface (companyfacts / companyconcept / frames) and lives in `finance-markets` because structured fundamentals are its primary draw. The two are complementary, not duplicative; if domain dual-tagging is added post-MVP, both should carry `finance-markets` + `corporate-registry`.

Potential new join key for review: `ACCESSION_NUMBER`
  Entity type: sec_filing
  Pattern: `^[0-9]{10}-[0-9]{2}-[0-9]{6}$`
  Other datasets that would use it: any source citing SEC filings (the corporate-registry/sec-edgar card already flags this; shared candidate).

Potential new join key for review: `US_GAAP_TAG`
  Entity type: xbrl_concept
  Pattern: `^[A-Za-z][A-Za-z0-9]*$` (us-gaap/ifrs-full/dei/srt taxonomy element name)
  Other datasets that would use it: any XBRL-derived fundamentals source (Financial Statement Data Sets, financial-data vendors normalising to us-gaap tags). Cross-source join on the financial-line-item concept itself, distinct from the company key.
