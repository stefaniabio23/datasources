---
id: form-adv-iapd
name: SEC Form ADV / IAPD
domain: corporate-registry
entry_kind: registry
description: US regulatory registry of investment adviser firms and their representatives, sourced from Form ADV filings and published via Investment Adviser Public Disclosure.
homepage_url: https://adviserinfo.sec.gov/
docs_url: https://www.sec.gov/data-research/sec-markets-data/information-about-registered-investment-advisers-exempt-reporting-advisers
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "unofficial JSON API; keep to a few req/sec (community consensus ~7 req/sec)"
bulk_available: true
frequency: "web/JSON search updated daily; bulk CSV complete files monthly, historical files quarterly"
lag: "filings appear on IAPD within ~1 business day; bulk CSV lags by weeks"
geography: [USA]
join_keys:
  - LEI
primary_keys:
  - CRD_NUMBER
  - SEC_FILE_NUMBER
join_key_fields:
  - join_key: LEI
    fields:
      - "1P"
mcp_status: mcp-needed-low-value
agent_use_cases:
  - investment adviser due diligence
  - RIA firm lookup by name or CRD
  - regulatory-AUM and custody screening
  - adviser-representative disclosure checks
  - entity resolution via LEI
access_test:
  command: "curl -sf 'https://api.adviserinfo.sec.gov/search/firm?query=blackrock&hits=1&type=Firm&investmentAdvisors=true&start=0'"
  expected_status: 200
  expected_fields: [hits.total, firm_source_id, firm_ia_full_sec_number, firm_name]
last_verified: 2026-07-02
build_priority: medium
notes: "search.adviserinfo.sec.gov JSON API is unofficial/undocumented (powers the public IAPD UI). LEI is only in the bulk Form ADV Part 1A CSV (Item 1.P / column 1P), not in the JSON search records."
---

# SEC Form ADV / IAPD

## Why this source matters

Investment Adviser Public Disclosure (IAPD) is the public face of Form ADV, the uniform registration form every SEC- and state-registered investment adviser must file. The data is collected through the Investment Adviser Registration Depository (IARD), operated by FINRA on behalf of the SEC and state regulators, and is one canonical row per firm and per adviser representative: legal and other names, CRD number, SEC file number, regulatory assets under management, employee and advisory-client counts, custody flags, disciplinary disclosures, and links to the firm's Form ADV Part 2 brochure and Form CRS. It is the authoritative US registry for the asset-management industry and doubles as a `finance-markets` source: the AUM, custody, and adviser-count fields drive competitive and risk analysis, not just entity lookup.

## Agent use cases

- investment adviser due diligence
- RIA firm lookup by name or CRD
- regulatory-AUM and custody screening
- adviser-representative disclosure checks
- entity resolution via LEI

## Join strategy

The one canonical join key IAPD exposes is `LEI` (Form ADV Part 1A Item 1.P), which links a registered adviser to GLEIF (`gleif-lei`) and to any other source keyed on the Legal Entity Identifier. LEI is reported only by firms that hold one and appears in the bulk Form ADV Part 1A CSV (column `1P`), not in the JSON search records.

The two identifiers that uniquely key IAPD's own entities are the CRD number (`firm_source_id` / `basicInformation.firmId` for firms, `ind_source_id` for individuals) and the SEC file number (`firm_ia_full_sec_number`, e.g. `801-XXXXX` for registered advisers or `802-XXXXX` for exempt/foreign advisers; the JSON detail splits it into `iaSECNumber` + `iaSECNumberType`). Neither is in the canonical registry yet; both are strong cross-source join-key candidates (see Review notes) because FINRA CRD numbers recur across BrokerCheck and other regulatory datasets, and SEC file numbers appear in SEC filings. Note the CIK in the registry is an EDGAR key and is distinct from the CRD number, do not conflate them.

## Access notes

Fastest programmatic path is the undocumented JSON API behind the IAPD site: `https://api.adviserinfo.sec.gov/search/firm?query=<name>&hits=10&type=Firm&investmentAdvisors=true&start=0` for firm search, `https://api.adviserinfo.sec.gov/search/firm/<CRD>` for the full firm record, and `https://api.adviserinfo.sec.gov/search/individual?query=<name>` for representatives. No auth, returns JSON. It is unofficial and undocumented, so treat the shape as unstable and rate-limit yourself (community practice is a few req/sec). For complete, stable, documented data use the bulk Form ADV CSVs from the SEC: complete Part 1A/Schedules/DRP files refreshed monthly, plus historical quarterly files back to January 2001 (SEC-registered advisers) and December 2011 (exempt reporting advisers). The bulk CSVs carry every Form ADV item, including LEI, that the JSON search endpoint omits.

## MCP / connector notes

No MCP exists. Third-party wrappers are paid (sec-api.io) or scraper-based (Apify actors). A useful connector would expose: `search_firm(query)`, `get_firm(crd)`, `search_individual(query)`, `get_brochure(crd)`, and `bulk_adv(period)`. The main things it must abstract over are the split between the fast-but-undocumented JSON API and the slow-but-complete bulk CSVs (LEI and most Item-level fields only exist in the latter), and normalising the SEC file number into its `801-`/`802-` prefixed form. Marked low-value because the audience is narrower than a general company registry, but the LEI bridge to GLEIF gives it cross-source reach.

## Review notes

Potential new join key for review: `CRD_NUMBER`
  Entity type: financial_professional_or_firm (FINRA Central Registration Depository number)
  Pattern: `^[0-9]+$`
  Other datasets that would use it: FINRA BrokerCheck, SEC Form BD / broker-dealer data, state securities regulators. High cross-source utility within US financial-industry registries.

Potential new join key for review: `SEC_FILE_NUMBER`
  Entity type: sec_registrant (SEC-assigned file number; adviser form uses 801-/802- prefixes, broker-dealers 8-, funds 811-/814-)
  Pattern: `^[0-9]{3}-[0-9]+$`
  Other datasets that would use it: SEC EDGAR, Form BD, investment-company registrations. Distinct from CIK (already in the registry).

License: SEC/federal works are US-Government-Public-Domain (17 USC 105); the IAPD terms add a no-warranty/attribution-style disclaimer but place no redistribution restriction on the data itself. Confirm the short name is acceptable.
