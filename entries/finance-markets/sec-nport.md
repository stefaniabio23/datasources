---
id: sec-nport
name: SEC Form N-PORT Fund Holdings
domain: finance-markets
entry_kind: panel
description: Quarterly bulk data sets of monthly portfolio holdings reported by US registered management funds and ETFs on Form N-PORT, as tab-delimited relational tables.
homepage_url: https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets
docs_url: https://www.sec.gov/files/nport_readme.pdf
type:
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "10 req/sec across all SEC hosts; descriptive User-Agent with contact email required or HTTP 403"
bulk_available: true
frequency: quarterly (data-set posting); underlying reports are monthly holdings as of each month-end
lag: "reports filed within 60 days of fiscal-quarter end; publicly disseminated set refreshed each quarter"
release_lag_days: 60
geography: [USA]
structure: panel
pit_reconstructable: true
revisions_possible: true
join_keys:
  - CIK
  - CUSIP
  - ISIN
  - LEI
  - TICKER
primary_keys:
  - ACCESSION_NUMBER
  - HOLDING_ID
  - SEC_SERIES_ID
  - SEC_CLASS_ID
join_key_fields:
  - join_key: CIK
    fields: [REGISTRANT.CIK]
  - join_key: CUSIP
    fields: [FUND_REPORTED_HOLDING.CUSIP]
  - join_key: ISIN
    fields: [IDENTIFIERS.IDENTIFIER_ISIN]
  - join_key: LEI
    fields: [FUND_REPORTED_INFO.SERIES_LEI, BORROWER.LEI]
  - join_key: TICKER
    fields: [IDENTIFIERS.IDENTIFIER_TICKER]
mcp_status: mcp-needed-high-value
agent_use_cases:
  - fund portfolio-holdings extraction
  - security-level ownership lookup across funds
  - ETF and mutual-fund constituent reconstruction
  - counterparty and derivative exposure analysis
  - cross-fund concentration and crowding screens
access_test:
  command: "curl -sfI -A 'DatasourcesBot contact@example.com' 'https://www.sec.gov/files/dera/data/form-n-port-data-sets/2026q1_nport.zip'"
  expected_status: 200
  expected_fields: [content-length, content-type]
last_verified: 2026-07-02
build_priority: medium
notes: "Bulk-only: quarterly ZIPs of tab-delimited tables, one file per table (SUBMISSION, REGISTRANT, FUND_REPORTED_INFO, FUND_REPORTED_HOLDING, IDENTIFIERS, BORROWER, and derivative/repo detail tables), keyed by ACCESSION_NUMBER. Requests without a descriptive User-Agent (contact email) are rejected with HTTP 403. Individual N-PORT filings are also retrievable as XML from EDGAR, but this entry covers the pre-parsed relational data sets."
---

# SEC Form N-PORT Fund Holdings

## Why this source matters

Form N-PORT is the SEC filing on which US registered management investment companies and exchange-traded funds (organised as unit investment trusts), other than money-market funds, report monthly portfolio holdings under rule 30b1-9 of the Investment Company Act. The SEC republishes the structured content of every publicly disseminated N-PORT filing as quarterly bulk data sets: ZIP archives of tab-delimited tables (roughly 300-500 MB per quarter, coverage from 2019 Q4 onward) that flatten each filing into a relational schema documented in the readme PDF. This is the cleanest free, machine-readable window into what US funds actually hold, position by position, including debt terms, derivatives, repo, and counterparties. Primary domain is `finance-markets` (security-level holdings and exposures); the secondary domain is `corporate-registry`, since each report is keyed to a filer `CIK` and an SEC series/class identity.

## Agent use cases

- fund portfolio-holdings extraction
- security-level ownership lookup across funds
- ETF and mutual-fund constituent reconstruction
- counterparty and derivative exposure analysis
- cross-fund concentration and crowding screens

## Join strategy

The data set exposes several canonical join keys. `CIK` identifies the filing registrant (`REGISTRANT` table). Each holding row carries a `CUSIP` (`FUND_REPORTED_HOLDING`), and the `IDENTIFIERS` table (Item C.1.e) supplies `ISIN` and `TICKER` for holdings lacking or supplementing a CUSIP. `LEI` appears in multiple places: the reporting fund's series LEI (`FUND_REPORTED_INFO.SERIES_LEI`) and the LEIs of securities-lending borrowers, repo counterparties, and derivative counterparties. Use `CUSIP`/`ISIN` to join holdings to security-master and issuer sources (OpenFIGI, Nasdaq listings), `CIK` to join to SEC EDGAR filer metadata and XBRL fundamentals, and `LEI` to join to GLEIF for counterparty entity resolution.

Source-native identifiers not in the canonical registry: `ACCESSION_NUMBER` (the filing key that stitches all tables together), `HOLDING_ID` (row key for each position), and the SEC fund `SERIES_ID` (`S`-prefixed) and `CLASS_ID` (`C`-prefixed) that identify the fund series and share class within a registrant. Series and class ids are the natural cross-source key for fund-level joins (N-PORT, N-CEN, prospectus filings, EDGAR mutual-fund search) and are flagged below as new-key candidates.

## Access notes

No API. Download the per-quarter ZIP from the pattern `https://www.sec.gov/files/dera/data/form-n-port-data-sets/<YYYY>q<N>_nport.zip` (e.g. `2026q1_nport.zip`); the landing page lists every available quarter. Each ZIP unpacks to one `.tsv` per table plus the readme mapping columns to Form N-PORT items. A descriptive `User-Agent` header including a contact email is mandatory across all SEC hosts, and the 10 req/sec ceiling applies; anonymous or default-curl requests return HTTP 403. To check freshness without pulling the full file, issue a `HEAD` against the latest quarter's ZIP or read the "Last Reviewed or Updated" date on the landing page. Note the disclosure lag: N-PORT reports are filed up to 60 days after fiscal-quarter end and only the publicly disseminated (final month of quarter) data appears in these sets, so the newest holdings visible trail real time by a quarter or more. Amended filings (N-PORT/A) restate positions, so join on `ACCESSION_NUMBER` and keep the latest amendment per report.

## MCP / connector notes

No MCP targets the N-PORT structured data sets specifically. Existing community SEC MCPs (`stefanoamorelli/sec-edgar-mcp`, `luisrincon23/sec-mcp`, EdgarTools MCP) wrap EDGAR filing retrieval and XBRL fundamentals, not the pre-parsed bulk holdings tables. High value because holdings-level data feeds ownership, crowding, and exposure questions that recur across finance-markets and corporate-registry consumers. A useful connector would download and cache the quarterly ZIPs, load the TSVs into a queryable store, and expose `get_fund_holdings(cik_or_series, period)`, `find_holders_of(cusip_or_isin)`, `get_counterparty_exposure(lei)`, and `holding_detail(accession, holding_id)`. It must abstract the multi-table join on `ACCESSION_NUMBER`, resolve series/class ids to fund names, inject a compliant `User-Agent`, and de-duplicate amended filings.

## Review notes

Secondary domain `corporate-registry` (filer `CIK` and SEC series/class identity); primary placement in `finance-markets` because security-level holdings are the main draw.

Potential new join key for review: `SEC_SERIES_ID`
  Entity type: investment_fund_series
  Pattern: `^S[0-9]{9}$`
  Other datasets that would use it: SEC Form N-CEN data sets, EDGAR mutual-fund / series-class search, prospectus (485BPOS) filings. Canonical fund-series key across the SEC investment-company corpus.

Potential new join key for review: `SEC_CLASS_ID`
  Entity type: investment_fund_share_class
  Pattern: `^C[0-9]{9}$`
  Other datasets that would use it: SEC Form N-CEN, EDGAR class/contract search, fund fee and returns filings. Share-class-level key beneath `SEC_SERIES_ID`.

Potential new join key for review: `ACCESSION_NUMBER`
  Entity type: sec_filing
  Pattern: `^[0-9]{10}-[0-9]{2}-[0-9]{6}$`
  Other datasets that would use it: every SEC-filing-derived source. Already flagged as a shared candidate by the `finance-markets/sec-companyfacts` and `corporate-registry/sec-edgar` cards; not invented here, just seconded.
