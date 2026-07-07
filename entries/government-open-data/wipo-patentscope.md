---
id: wipo-patentscope
name: WIPO PATENTSCOPE
domain: government-open-data
entry_kind: registry
description: WIPO's free search service over 128M patent documents, including 5.4M published PCT international applications plus national and regional collections.
homepage_url: https://patentscope.wipo.int/
docs_url: https://www.wipo.int/en/web/patentscope/data/index
type:
  - web-ui
  - bulk-download
  - unofficial-api
auth_required: none
cost: freemium
license: WIPO-Terms-of-Use
bulk_available: true
frequency: "PCT weekly (Thursdays), daily bibliographic updates; national collections ad hoc per office"
lag: "PCT data available on day of publication; national collection lag varies by office"
geography: [global]
join_keys:
  - PATENT_PUBLICATION_NUMBER
primary_keys:
  - WO_PUBLICATION_NUMBER
  - PCT_APPLICATION_NUMBER
  - PATENT_PUBLICATION_NUMBER
mcp_status: mcp-needed-high-value
agent_use_cases:
  - prior-art search
  - PCT application lookup
  - patent family retrieval
  - cross-lingual patent search
  - technology landscaping
last_verified: 2026-07-02
build_priority: medium
---

# WIPO PATENTSCOPE

## Why this source matters

PATENTSCOPE is the World Intellectual Property Organization's public search service over roughly 128 million patent documents, including about 5.4 million published international applications filed under the Patent Cooperation Treaty (PCT). It is the definitive free source for PCT applications and aggregates national and regional collections contributed by IP offices across Europe, Asia, the Americas, and Africa. It is the only free tool offering cross-lingual information retrieval (CLIR) and Markush chemical-structure search. Run by WIPO, a UN specialized agency, it functions as an intellectual-property registry: each row is one patent document keyed by a canonical publication number. Of secondary relevance to `clinical-biotech` and `bio-genomics` for chemistry and life-science prior art, and to `corporate-registry`/`finance-markets` for mapping assignees to inventing organisations.

## Agent use cases

- prior-art search
- PCT application lookup
- patent family retrieval
- cross-lingual patent search
- technology landscaping

## Join strategy

PATENTSCOPE exposes no identifier that currently maps to a canonical key in `schema/join-keys.yaml`, so `join_keys` is empty. Its native identifiers are patent-domain-specific: the WO publication number for PCT applications (e.g. `WO2020123456`), the PCT application number (e.g. `PCT/US2019/012345`), and the national/regional publication number for documents from contributed collections (e.g. `US20200123456A1`, `EP3000000A1`). These live in `primary_keys`. Two of them are strong candidates for the canonical registry (flagged below) because patents are a natural join target across EPO, USPTO, Google Patents, Lens.org, and OpenAlex (which links works to patents). Country/office prefixes on publication numbers are WIPO ST.3 codes, which overlap with but are not identical to ISO 3166-1 alpha-2, so they are not claimed as `ISO_2` here.

## Access notes

Free interactive search is web-UI only at `https://patentscope.wipo.int/` and is JavaScript-heavy; there is no free public REST endpoint, so `access_test` is omitted. Verify freshness by confirming the current week's PCT publications appear (new WO numbers publish every Thursday). Programmatic access is paid: the PCT Web Service (SOAP/Java) runs 600 CHF/year limited or 2,000 CHF/year full-access. Bulk data products are separately licensed subscriptions (PCT-Bibliographic 400 CHF/year; PCT-Text 3,900 CHF non-derivative / 19,500 CHF derivative; PCT-Images 3,900 CHF/year; ISA documents 2,000 CHF/year; backfile hard-drive sets from 1,600 CHF), with a 50% discount for non-profits and conditional-use clauses in WIPO's general sale conditions. Third-party scraper wrappers (e.g. Apify, community Ruby gems) exist but are unofficial and rate-fragile.

## MCP / connector notes

No official WIPO MCP. Community multi-database patent MCP servers (e.g. `myownipgit/mcp-server-patent`, `patent-mcp-server` on PyPI) advertise WIPO coverage alongside EPO and USPTO, but WIPO integration typically leans on the paid SOAP service or scraping rather than a clean free API, so coverage and stability are unverified. Marked `mcp-needed-high-value`: three-plus entries would want a shared patent connector. A useful MCP surface would expose `search_patents` (with CLIR and field-scoped queries), `get_document` by publication number, `get_patent_family`, and `get_pct_status`, abstracting over the SOAP contract or the web-UI, handling the WO-number vs national-number distinction, and normalising multilingual bibliographic fields.

## Review notes

Two candidate join keys surfaced from this source (both flagged, not invented into `join_keys`):

Potential new join key for review: PATENT_PUBLICATION_NUMBER
  Entity type: patent_document
  Pattern: office-prefixed publication number, e.g. `US20200123456A1`, `EP3000000A1`, `JP2020123456A` (WIPO ST.3 country code + serial + kind code)
  Other datasets that would use it: EPO OPS, USPTO PatentsView, Google Patents, Lens.org, Espacenet

Potential new join key for review: PCT_NUMBER
  Entity type: pct_application
  Pattern: WO publication number `^WO[0-9]{4}[0-9]{6}$` (e.g. `WO2020123456`) and/or PCT application number `^PCT/[A-Z]{2}[0-9]{4}/[0-9]{6}$`
  Other datasets that would use it: EPO OPS, Espacenet, Lens.org, national office registers

License short name `WIPO-Terms-of-Use` is not in SCHEMA.md's known-cases list; it is a placeholder canonical short name for WIPO's mixed free-search-plus-paid-subscription terms. Confirm the preferred canonical string before merge. Free search of the site is permitted; bulk/derivative reuse is governed by paid non-derivative vs derivative licenses.

Domain choice: filed under `government-open-data` (WIPO is a UN intergovernmental agency and PATENTSCOPE is an official public registry). No dedicated intellectual-property domain exists in the 11-value enum; consider whether patents warrant one if more patent sources are added.
