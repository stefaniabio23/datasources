---
id: opencorporates
name: OpenCorporates
domain: corporate-registry
description: Cross-jurisdiction database of legal entities sourced from 140+ official company registries worldwide.
homepage_url: https://opencorporates.com/
docs_url: https://api.opencorporates.com/documentation/API-Reference
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: freemium
license: ODbL-1.0
rate_limit: "Free tier: 50 req/day, 200 req/month. Paid tiers from £2,250/yr (500/mo, 200/day) up to enterprise bulk."
bulk_available: true
frequency: varies by jurisdiction (real-time to monthly, mirrors source registry cadence)
lag: "hours-to-weeks; depends on the upstream government registry"
geography: [global]
join_keys:
  - COMPANIES_HOUSE_NUMBER
  - CIK
  - ISO_2
  - ISO_3
  - DATE
  - URL
  - WIKIDATA_QID
primary_keys:
  - OPENCORPORATES_COMPANY_URI
  - OPENCORPORATES_OFFICER_ID
  - OPENCORPORATES_STATEMENT_ID
join_key_fields:
  - join_key: COMPANIES_HOUSE_NUMBER
    fields: [results.company.company_number]
  - join_key: CIK
    fields: [results.company.identifiers.uid]
  - join_key: ISO_2
    fields: [results.company.jurisdiction_code]
  - join_key: DATE
    fields: [results.company.incorporation_date, results.company.dissolution_date, results.company.retrieved_at]
  - join_key: URL
    fields: [results.company.opencorporates_url, results.company.registry_url, results.company.source.url]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  Suggested surface: search_companies, get_company, get_officers, get_filings,
  search_officers, get_statements. MCP must handle the (jurisdiction_code, company_number)
  composite key, track the strict daily/monthly quota client-side, and abstract over
  the v0.4 path prefix.
agent_use_cases:
  - cross-border company diligence
  - beneficial-ownership tracking
  - sanctions and KYC screening
  - investigative journalism
  - supply-chain entity resolution
access_test:
  command: 'curl -sf "https://api.opencorporates.com/v0.4/companies/gb/00102498?api_token=${OPENCORPORATES_TOKEN}"'
  expected_status: 200
  expected_fields: [results, api_version]
last_verified: 2026-06-08
build_priority: high
notes: access_test not yet executed; requires OPENCORPORATES_TOKEN env var. Free tier quota (50/day, 200/mo) is very tight; agents doing systematic enrichment need a paid plan or the free pro-bono allowance available to journalists, NGOs, and academics.
---

# OpenCorporates

## Why this source matters

The largest open cross-jurisdiction company database, ~200M legal entities sourced directly from 140+ official government registries (all US states, all Canadian provinces, every EU member, plus most of Asia, Africa, and the Caribbean). Run by OpenCorporates Limited (UK, founded 2010). The natural complement to single-country registers like Companies House and SEC EDGAR: one schema, one API, one set of identifiers spanning jurisdictions whose own registries are heterogeneous, paywalled, or web-only. Used heavily by investigative journalism (ICIJ, OCCRP), compliance/KYC pipelines, and academic corporate-network research.

## Agent use cases

- cross-border company diligence
- beneficial-ownership tracking
- sanctions and KYC screening
- investigative journalism
- supply-chain entity resolution

## Join strategy

OpenCorporates' primary key is a `(jurisdiction_code, company_number)` composite (e.g. `gb/00102498`, `us_de/4574889`). The `jurisdiction_code` maps to `ISO_2` for sovereign jurisdictions and to ISO 3166-2 subdivision codes for US states and Canadian provinces. The `company_number` is whatever the upstream registry assigns: for `gb` it maps cleanly onto `COMPANIES_HOUSE_NUMBER`; for `us_*` SEC-registered filers it ties to `CIK` via the filings cross-reference.

OpenCorporates-internal IDs (`OPENCORPORATES_COMPANY_URI`, `OPENCORPORATES_OFFICER_ID`, `OPENCORPORATES_STATEMENT_ID`) are intentionally outside the canonical registry; use them for intra-OC joins only.

Pair with GLEIF for LEI cross-walks, Open Ownership for beneficial-ownership statements, OpenSanctions for sanctions/PEP overlays, and Wikidata (`WIKIDATA_QID`) for entity disambiguation against public figures.

Potential new join key flagged in Review notes.

## Access notes

**Start here:** REST API at `https://api.opencorporates.com/v0.4/`. Token via `?api_token=${OPENCORPORATES_TOKEN}` query parameter (not header). Free token from `https://opencorporates.com/api_accounts/new`.

**Free-tier ceiling is the binding constraint:** 50 req/day and 200 req/month. That's enough for ad-hoc lookups, nowhere near enough for enrichment pipelines. Paid plans start at £2,250/year for 500 req/month. Journalists, NGOs, academics, and anti-corruption researchers can apply for free at-scale access via OpenCorporates' pro-bono programme.

**Bulk-data delivery** is Enterprise-only via SFTP, with jurisdiction selection and configurable cadence. No free bulk snapshot. For one-off large pulls outside the enterprise tier, the practical fallback is to hit upstream registries directly (Companies House for GB, SEC EDGAR for US filers) and use OpenCorporates only for the jurisdictions where no good free alternative exists.

Known gotchas:

- Pagination caps at `page=100`. For large result sets, filter harder rather than paginate deeper.
- `per_page` maximum is 100; default is 30.
- Data freshness varies per jurisdiction; check `previous_names`, `retrieved_at`, and `last_processed_at` per record rather than assuming.
- Officer records are deduplicated heuristically across companies; matches are not authoritative.
- Share-alike (ODbL) licensing means redistributed derivative datasets must also be ODbL; commercial reuse without share-alike obligations requires a paid licence.

## MCP / connector notes

No official MCP. Strong fit for one: a single connector unlocks 140+ jurisdictions whose native registries are heterogeneous (HTML scrape, paid SOAP, PDF-only) or behind language barriers. Suggested surface: `search_companies(q, jurisdiction_code?)`, `get_company(jurisdiction_code, company_number)`, `get_officers(company)`, `search_officers(q)`, `get_filings(company)`, `get_statements(id)`.

Connector must: (a) abstract the v0.4 path prefix, (b) track the strict daily/monthly quota client-side and degrade gracefully rather than burning the day's calls, (c) handle the composite `(jurisdiction_code, company_number)` key as a single argument, (d) flatten `results.company` / `results.officer` wrappers, (e) surface OC's `inactive`/`dissolved` status so agents don't act on stale entities.

## Review notes

Potential new join key for review: `OPENCORPORATES_COMPANY_URI`
  Entity type: cross-jurisdiction legal entity
  Pattern: `^https://opencorporates\.com/companies/[a-z_]{2,5}/[A-Za-z0-9-]+$` (or the shorter `<jurisdiction_code>/<company_number>` form)
  Other datasets that would use it: ICIJ Offshore Leaks, Open Ownership Register, OpenSanctions, Aleph (OCCRP). All four cross-reference OC URIs as the de facto stable identifier for non-GB, non-US legal entities.

License is `ODbL-1.0` (Open Database Licence v1.0) for the free open-data tier; commercial/enterprise tiers ship under a separate commercial licence. SCHEMA.md's license-conventions table does not list ODbL among its named-canonical short names; SPDX recognises `ODbL-1.0` so this entry uses the SPDX form. Confirm acceptable.
