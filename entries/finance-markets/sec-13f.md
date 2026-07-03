---
id: sec-13f
name: SEC Form 13F Holdings
domain: finance-markets
entry_kind: panel
description: Quarterly institutional investment-manager portfolio holdings extracted from Form 13F EDGAR filings, released as flattened bulk data sets.
homepage_url: https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
docs_url: https://www.sec.gov/files/form_13f_readme.pdf
type:
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "no key; SEC requires a descriptive User-Agent header, fair-access 10 req/sec ceiling"
bulk_available: true
frequency: quarterly
lag: "managers must file within 45 days of quarter-end; data sets refreshed quarterly"
release_lag_days: 45
geography: [US]
structure: panel
pit_reconstructable: true
revisions_possible: true
join_keys:
  - CIK
  - CUSIP
primary_keys:
  - ACCESSION_NUMBER
  - CIK
  - INFOTABLE_SK
join_key_fields:
  - join_key: CIK
    fields: [SUBMISSION.CIK, COVERPAGE.CIK]
  - join_key: CUSIP
    fields: [INFOTABLE.CUSIP]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/stefanoamorelli/sec-edgar-mcp"
  - "github.com/cyanheads/secedgar-mcp-server"
  - "github.com/leopoldodonnell/edgar-mcp"
mcp_notes: >
  Community EDGAR MCPs surface 13F-HR holdings by parsing the live information table from
  EDGAR rather than the flattened quarterly data sets; none is official and none targets the
  bulk TSV product specifically. A dedicated connector should expose the manager-by-security-by-quarter
  panel with CUSIP and CIK resolution.
agent_use_cases:
  - institutional-ownership lookup
  - manager portfolio reconstruction
  - 13F consensus / crowding analysis
  - quarter-over-quarter position change tracking
  - CUSIP-to-holder reverse lookup
access_test:
  command: "curl -sI -A 'datasources-registry contact@example.com' 'https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01sep2025-30nov2025_form13f.zip' | grep -i '^HTTP'"
  expected_status: 200
last_verified: 2026-07-02
build_priority: medium
---

# SEC Form 13F Holdings

## Why this source matters

Form 13F is the mandatory quarterly disclosure of US equity holdings by institutional investment managers exercising discretion over 100M USD or more in Section 13(f) securities. The SEC publishes the XML-derived portion of every filing as flattened, tab-delimited quarterly data sets covering roughly three months of acceptances per file, going back to 2013. Operated by the US Securities and Exchange Commission, fully public-domain (17 USC 105), no auth, no key. The data set is a set of related tables (SUBMISSION, COVERPAGE, INFOTABLE, OTHERMANAGER, SIGNATURE, SUMMARYPAGE) keyed on ACCESSION_NUMBER; INFOTABLE is the payload, one row per security position with issuer name, CUSIP, market value, share/principal count, and put/call flag. Secondary domain is `corporate-registry`: the filing manager is identified by `CIK`, the SEC's canonical filer key. This card covers the bulk quarterly data-set product; the live filings and submission metadata are covered by `corporate-registry/sec-edgar`.

## Agent use cases

- institutional-ownership lookup
- manager portfolio reconstruction
- 13F consensus / crowding analysis
- quarter-over-quarter position change tracking
- CUSIP-to-holder reverse lookup

## Join strategy

Two canonical join keys are native. `CIK` identifies the filing manager (`SUBMISSION.CIK`, `COVERPAGE.CIK`), joining to `corporate-registry/sec-edgar` and `finance-markets/sec-companyfacts` for the manager's own filing history. `CUSIP` (`INFOTABLE.CUSIP`) identifies each held security; it is the bridge to the rest of the securities universe, so pair with OpenFIGI to resolve CUSIP to `FIGI`/`ISIN`/`TICKER`, then to price and fundamentals sources. `TICKER` was requested as a hint but is NOT natively present in the 13F data sets; the filing carries only issuer name and CUSIP, so a ticker join requires an external CUSIP-to-ticker crosswalk (OpenFIGI or `company_tickers.json`) and is not asserted in `join_keys`. Source-internal keys stay out of the registry: `ACCESSION_NUMBER` uniquely identifies each filing and `INFOTABLE_SK` each holding row; both live in `primary_keys`. `ACCESSION_NUMBER` is flagged below as a cross-source-key candidate, consistent with the sibling SEC entries.

## Access notes

Bulk only, no query API. Download the quarterly zip from `https://www.sec.gov/files/structureddata/data/form-13f-data-sets/<01mmmYYYY-ddmmmYYYY>_form13f.zip` (e.g. `01sep2025-30nov2025_form13f.zip`); each contains tab-delimited `.tsv` tables plus a readme. SEC requires a descriptive `User-Agent` (name plus contact email) on every request or it returns 403, and enforces a fair-access ceiling near 10 req/sec. Join INFOTABLE to SUBMISSION/COVERPAGE on `ACCESSION_NUMBER` to attribute holdings to a manager. Freshness check: list the data-set page and compare the newest file's date range and `last-modified` header; new quarters land a few weeks after the 45-day filing deadline. Note that amendments (13F-HR/A) restate prior holdings, so a manager's final position for a quarter may span multiple accessions, use the latest amendment.

## MCP / connector notes

Community SEC EDGAR MCPs exist (`stefanoamorelli/sec-edgar-mcp`, `cyanheads/secedgar-mcp-server`, `leopoldodonnell/edgar-mcp`), and EdgarTools ships an MCP with a 13F tool. All parse the live information table from EDGAR filings rather than the flattened quarterly bulk product, and none is official. A connector purpose-built for this data set should expose `get_manager_holdings(cik, quarter)`, `get_holders_of(cusip, quarter)`, and `get_position_changes(cik, from_quarter, to_quarter)`, download and cache the quarterly zips, resolve the ACCESSION_NUMBER joins into a tidy `(cik, manager, cusip, issuer, value, shares, put_call, quarter)` panel, dedupe amendments to the latest, and inject a compliant User-Agent.

## Review notes

Potential new join key for review: `ACCESSION_NUMBER`
  Entity type: sec_filing
  Pattern: `^[0-9]{10}-[0-9]{2}-[0-9]{6}$` (e.g. `0000320193-24-000123`)
  Other datasets that would use it: `corporate-registry/sec-edgar`, `finance-markets/sec-companyfacts` (both already flag it); it is the universal EDGAR filing key across all SEC form-type data sets.

`TICKER` was supplied as a join-key hint but the 13F data sets do not expose it; holdings are keyed on CUSIP and issuer name only. Left out of `join_keys` deliberately; resolve via OpenFIGI or `company_tickers.json`. No new domains, enum values, or license ambiguity.
