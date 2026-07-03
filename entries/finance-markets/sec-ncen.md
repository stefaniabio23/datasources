---
id: sec-ncen
name: SEC Form N-CEN Fund Census
domain: finance-markets
entry_kind: registry
description: Quarterly flat-file extracts of Form N-CEN annual census filings by US registered investment companies, covering fund structure, service providers, and operational disclosures.
homepage_url: https://www.sec.gov/data-research/sec-markets-data/form-n-cen-data-sets
docs_url: https://www.sec.gov/files/ncen_readme.pdf
type:
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
bulk_available: true
frequency: quarterly
lag: "up to one quarter; filings after 5:30pm ET on the last business day of a quarter land in the next quarterly posting"
geography: [USA]
join_keys:
  - CIK
  - LEI
primary_keys:
  - ACCESSION_NUMBER
  - SERIES_ID
  - CLASS_ID
  - FILE_NUMBER
join_key_fields:
  - join_key: CIK
    fields: [SUBMISSION.CIK, REGISTRANT.CIK, SERIES_CIK.SERIES_CIK]
  - join_key: LEI
    fields: [REGISTRANT.LEI, FUND_REPORTED_INFO.FUND_LEI, ADVISER.ADVISER_LEI, CUSTODIAN.CUSTODIAN_LEI]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - fund service-provider mapping
  - adviser and custodian relationship lookup
  - ETF authorized-participant analysis
  - fund-complex structure reconstruction
  - securities-lending and derivatives disclosure screening
access_test:
  command: "curl -sfI -A 'datasources-registry you@example.com' 'https://www.sec.gov/files/dera/data/form-n-cen-data-sets/2026q1_ncen.zip'"
  expected_status: 200
  expected_fields: []
last_verified: 2026-07-02
build_priority: low
---

# SEC Form N-CEN Fund Census

## Why this source matters

Form N-CEN is the annual census filing that every US registered investment company (except face-amount certificate companies) submits to the SEC under the Investment Company Act of 1940. The SEC's DERA group extracts the N-CEN XML submissions into flat, tab-delimited tables (up to 53 files per quarter) so analysts can work with the data without parsing raw XML. Each filing carries the full operational profile of a fund complex: registrant identity, directors, chief compliance officer, the roster of service providers (advisers, sub-advisers, custodians, transfer agents, administrators, principal underwriters, auditors, pricing services, securities-lending agents), plus disclosures on securities lending, derivatives, borrowing and lines of credit, swing pricing, ETF creation/redemption mechanics and authorized participants, money-market data, and UIT-specific items. This is the authoritative machine-readable map of who runs and services US mutual funds, ETFs, and closed-end funds. Secondary domain is `corporate-registry`, since the extracts are a directory of fund entities and their affiliated service organisations keyed by CIK and LEI.

## Agent use cases

- fund service-provider mapping
- adviser and custodian relationship lookup
- ETF authorized-participant analysis
- fund-complex structure reconstruction
- securities-lending and derivatives disclosure screening

## Join strategy

The two canonical join keys are `CIK` (the SEC Central Index Key of the registrant and of each series, in `SUBMISSION`, `REGISTRANT`, and `SERIES_CIK`) and `LEI` (the ISO 17442 Legal Entity Identifier, exposed for the registrant, funds, and nearly every service-provider table via `*_LEI` columns). CIK links N-CEN to the rest of SEC EDGAR (N-PORT holdings, N-CEN's sibling census, 10-K/10-Q, Form ADV advisers). LEI bridges to GLEIF and to counterparty datasets outside the SEC.

Source-internal identifiers that are not (yet) canonical registry keys live in `primary_keys`: `ACCESSION_NUMBER` (the per-filing primary key that joins the 53 tables to each other), the EDGAR `SERIES_ID` (e.g. `S000012345`) and `CLASS_ID` (e.g. `C000034567`) that identify individual fund series and share classes, and the Investment Company Act `FILE_NUMBER` (e.g. `811-xxxxx`). The EDGAR series/class identifiers are high-value cross-source keys for anyone joining fund-level SEC datasets (N-PORT, N-CEN, mutual-fund prospectus filings, EDGAR series/class lookup); they are flagged for review below as new-key candidates rather than invented into `join_keys`.

## Access notes

Bulk-only, no API. Download the per-quarter ZIP at `https://www.sec.gov/files/dera/data/form-n-cen-data-sets/<YYYY>q<N>_ncen.zip` (e.g. `2026q1_ncen.zip`). Coverage runs September 2018 to the current quarter; the set is refreshed quarterly (last reviewed 2026-03-31). Each ZIP unpacks to tab-delimited UTF-8 `.tsv` files plus a W3C tabular-data-model metadata JSON describing the tables and their key relationships. Join the tables on `ACCESSION_NUMBER` (and `SERIES_ID` / `FUND_ID` for the fund-level tables). SEC requires a descriptive `User-Agent` header with a contact email on every request; requests without one are rejected, and the fair-access policy caps automated traffic at roughly 10 requests/second. To check freshness, read the "September 2018 - March 2026" range and the download table on the landing page, or probe for the newest `<YYYY>q<N>_ncen.zip`. Note (from the landing page): filings using N-CEN schema version 3.1 introduced in EDGAR 25.2 are not yet included and will be added in a later update.

## MCP / connector notes

No N-CEN-specific MCP exists. A general SEC EDGAR MCP (`github.com/stefanoamorelli/sec-edgar-mcp`) covers filings and financial statements but does not model the N-CEN flat-file extracts. Marked `mcp-needed-low-value`: the audience (fund-structure and service-provider analysts) is narrower than headline EDGAR financials, and the data is a quarterly bulk drop rather than a live query surface, so a thin loader plus a documented schema serves most needs. A useful connector would expose: download_quarter(year, q), load_table(name), join_filing(accession_number) to stitch the 53 tables, lookup_fund(cik | series_id), and providers_for_fund(cik) returning the adviser/custodian/transfer-agent roster. The tricky part an MCP must abstract over is the many-table relational shape (one filing fans out across up to 53 tab-delimited files keyed by ACCESSION_NUMBER, SERIES_ID, and FUND_ID) and the "as-filed" redundancy from amendments.

## Review notes

Potential new join keys for review:

Potential new join key for review: SEC_SERIES_ID
  Entity type: fund_series (EDGAR series identifier for a registered investment company series)
  Pattern: ^S[0-9]{9}$
  Other datasets that would use it: SEC N-PORT, EDGAR mutual-fund series/class lookup, prospectus (485BPOS) filings, Form N-CEN

Potential new join key for review: SEC_CLASS_ID
  Entity type: fund_share_class (EDGAR class/contract identifier for a share class of a fund series)
  Pattern: ^C[0-9]{9}$
  Other datasets that would use it: SEC N-PORT, EDGAR mutual-fund series/class lookup, prospectus filings, Form N-CEN

Potential new join key for review: SEC_FILE_NUMBER (Investment Company Act file number)
  Entity type: registered_investment_company
  Pattern: ^811-[0-9]+$ (also 811- for management companies; other prefixes exist for other registrant types)
  Other datasets that would use it: SEC EDGAR company filings, Form ADV, N-CEN

License: the SEC publishes these as works of the US federal government; mapped to `US-Government-Public-Domain` per SCHEMA.md conventions. The landing-page disclaimer stresses the data is derived from as-filed registrant submissions and is not guaranteed accurate; captured in Access notes, no license nuance beyond public-domain status.
