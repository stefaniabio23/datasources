---
id: sec-edgar
name: SEC EDGAR
domain: corporate-registry
description: US SEC system of all corporate filings (10-K, 10-Q, 8-K, S-1, 13F, etc.) with company metadata and structured XBRL financial facts.
homepage_url: https://www.sec.gov/edgar
docs_url: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "10 req/sec across all data.sec.gov and www.sec.gov endpoints. User-Agent header with contact email required."
bulk_available: true
frequency: real-time for filings dissemination; nightly bulk ZIP refresh (~3am ET)
lag: "sub-second for submissions API, under a minute for XBRL APIs"
geography: [USA]
join_keys:
  - CIK
  - TICKER
  - DATE
  - URL
primary_keys:
  - CIK
  - ACCESSION_NUMBER
  - SIC
  - EIN
join_key_fields:
  - join_key: CIK
    fields: [cik, cik_str]
  - join_key: TICKER
    fields: [tickers, ticker]
  - join_key: DATE
    fields: [filings.recent.filingDate, filings.recent.reportDate, filings.recent.acceptanceDateTime, facts.us-gaap.*.units.*.end, facts.us-gaap.*.units.*.filed]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/stefanoamorelli/sec-edgar-mcp
  - github.com/cyanheads/secedgar-mcp-server
  - github.com/LuisRincon23/SEC-MCP
mcp_notes: >
  Multiple community MCPs; none official. Most-starred is stefanoamorelli/sec-edgar-mcp (Python).
  A canonical MCP should expose search_filings, get_company_submissions, get_company_facts,
  get_company_concept, get_frame, and full-text search; abstract over CIK zero-padding,
  enforce the 10 req/sec ceiling client-side, and inject a compliant User-Agent.
agent_use_cases:
  - US public-company diligence
  - financial-statement extraction
  - insider-trading and 13F tracking
  - filing event monitoring
  - cross-company XBRL benchmarking
access_test:
  command: "curl -sf -A 'ResearchBot contact@example.com' 'https://data.sec.gov/submissions/CIK0000320193.json'"
  expected_status: 200
  expected_fields: [cik, name, tickers, exchanges, sic, filings]
last_verified: 2026-06-08
build_priority: high
notes: Secondary domain is finance-markets. Requests without a descriptive User-Agent (including a contact email) are rejected with HTTP 403.
---

# SEC EDGAR

## Why this source matters

EDGAR (Electronic Data Gathering, Analysis, and Retrieval) is the SEC's mandatory filing system for US public companies and other registered entities: ~17M filings since 1994, ~3,000 new filings per business day. Operated by the US Securities and Exchange Commission, fully public-domain (17 USC 105), no auth, no key. The `data.sec.gov` JSON APIs deliver per-company submission history and structured XBRL financial facts; the bulk archive holds nightly ZIPs of every filing index plus per-filing primary documents. Secondary domain is `finance-markets`: XBRL company facts and frames are the cleanest free source of structured fundamentals for US issuers.

## Agent use cases

- US public-company diligence
- financial-statement extraction
- insider-trading and 13F tracking
- filing event monitoring
- cross-company XBRL benchmarking

## Join strategy

`CIK` is the SEC's Central Index Key, the canonical US-filer identifier (numeric, zero-padded to 10 digits in URLs). `TICKER` is exposed on the submissions object for publicly-traded issuers and via the `company_tickers.json` lookup file. `DATE` keys filing acceptance and period-of-report fields. `URL` deep-links into the primary document archive at `https://www.sec.gov/Archives/edgar/data/<cik>/<accession>/`.

EDGAR-internal IDs that are useful for intra-EDGAR joins but not canonical:

- `ACCESSION_NUMBER` (e.g. `0000320193-24-000123`): unique per filing.
- `SIC` (Standard Industrial Classification, 4-digit): coarse sector code, EDGAR-specific.
- `EIN`, `LEI`: exposed on the submissions JSON; LEI bridges to GLEIF.

Pair with OpenFIGI for `CUSIP`/`ISIN`/`FIGI` mappings on US securities, GLEIF for `LEI`, OpenAlex or Crossref for cited research in disclosures, and Companies House for cross-jurisdiction corporate-group reconstruction.

## Access notes

**Per-company lookups:** `https://data.sec.gov/submissions/CIK##########.json` returns filing history, tickers, exchanges, SIC, EIN, LEI, former names, addresses.

**Structured financials:** `data.sec.gov/api/xbrl/companyfacts/CIK##########.json` (all XBRL facts for one issuer), `companyconcept/CIK##########/us-gaap/<Concept>.json` (one concept across time), `frames/us-gaap/<Concept>/<Unit>/CY####Q#I.json` (one concept across all issuers for one period).

**Bulk:** `https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip` (all submissions) and `https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip` (all XBRL facts), refreshed nightly ~3am ET.

**Full-text search:** `https://efts.sec.gov/LATEST/search-index?q=<query>` (used by the EDGAR full-text UI; unofficial but stable).

Hard rules:

- 10 requests/second across all SEC hosts; persistent abuse triggers IP-level throttling.
- `User-Agent` header MUST identify the requester and a contact email (e.g. `Sample Company AdminContact@sample.com`). Anonymous browsers and default curl get HTTP 403.
- CORS not supported on `data.sec.gov`; server-side fetch only.
- XBRL APIs only aggregate facts using standard taxonomies (`us-gaap`, `ifrs-full`, `dei`, `srt`); custom-extension concepts are not in `frames` or `companyfacts`.
- Pre-1994 filings are paper-only; request via FOIA.

## MCP / connector notes

Multiple community MCPs exist; none official. Most-starred is `stefanoamorelli/sec-edgar-mcp` (Python, ~313 stars). Others: `cyanheads/secedgar-mcp-server` (TypeScript), `LuisRincon23/SEC-MCP`, `cotrane/mcp-edgar-sec`, `flothjl/edgar-sec-mcp`, `openpharma-org/sec-mcp`, `bxxd/mcp-edgar-ux`, `leopoldodonnell/edgar-mcp`.

Coverage and quality vary widely. A canonical MCP should expose `search_filings` (full-text + form-type filter), `get_company_submissions`, `get_company_facts`, `get_company_concept`, `get_frame`, `get_filing_document`, and a `lookup_cik_by_ticker` helper. It must abstract over CIK zero-padding, inject a compliant `User-Agent`, enforce the 10 req/sec ceiling client-side with queueing rather than 429-and-retry, and trim the very verbose XBRL facts payload before returning.

## Review notes

Potential new join key for review: `ACCESSION_NUMBER`
  Entity type: sec_filing
  Pattern: `^[0-9]{10}-[0-9]{2}-[0-9]{6}$`
  Other datasets that would use it: any source citing SEC filings (FactSet, S&P Capital IQ exports, EDGAR-derived datasets).

Potential new join key for review: `LEI`
  Entity type: legal_entity
  Pattern: `^[A-Z0-9]{18}[0-9]{2}$`
  Other datasets that would use it: GLEIF, ESMA, Companies House (where reported), most regulatory filings globally. Strong cross-jurisdiction join candidate.

Potential new join key for review: `SIC`
  Entity type: industry_classification
  Pattern: `^[0-9]{4}$`
  Other datasets that would use it: BLS, Census Business Patterns, FFIEC, most US regulatory datasets pre-NAICS adoption.

Secondary domain `finance-markets` is real, not academic: the XBRL APIs are arguably the primary draw for fundamentals workflows. If domain dual-tagging is added post-MVP, this entry should carry both.
