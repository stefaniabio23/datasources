---
id: eu-ted
name: TED (Tenders Electronic Daily)
domain: government-open-data
entry_kind: event-stream
description: EU public procurement notices from the Supplement to the Official Journal, published daily with a free anonymous search API, bulk XML, and a Linked Open Data / SPARQL backend.
homepage_url: https://ted.europa.eu/
docs_url: https://docs.ted.europa.eu/api/latest/index.html
type:
  - rest-api
  - bulk-download
  - database
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "anonymous search API; per-IP throttling, no published hard quota"
bulk_available: true
frequency: daily
lag: "notices appear on TED on or shortly after publication in the OJ Supplement"
geography: [global]
join_keys:
  - ISO_3
  - NUTS
primary_keys:
  - TED_PUBLICATION_NUMBER
join_key_fields:
  - join_key: ISO_3
    fields: [buyer-country]
  - join_key: NUTS
    fields: [place-of-performance]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/pipeworx-io/mcp-ted-eu"
  - "fbuchner-ted-mcp"
mcp_notes: >
  Community MCPs wrap the anonymous TED v3 search API (no key). Suggested surface:
  search_notices (expert query), get_notice (by publication-number), get_notice_xml.
  Must abstract the eForms expert-query syntax and the 24-language notice-title map.
agent_use_cases:
  - public procurement search
  - supplier and buyer diligence
  - contract-award monitoring
  - CPV-category market sizing
  - cross-border tender discovery
access_test:
  command: "curl -sf -X POST 'https://api.ted.europa.eu/v3/notices/search' -H 'Content-Type: application/json' -d '{\"query\":\"classification-cpv=33600000\",\"fields\":[\"publication-number\",\"buyer-country\",\"place-of-performance\"],\"limit\":1,\"page\":1}'"
  expected_status: 200
  expected_fields: [notices, publication-number, totalNoticeCount]
last_verified: 2026-07-07
build_priority: medium
---

# TED (Tenders Electronic Daily)

## Why this source matters

TED is the online version of the Supplement to the Official Journal of the EU, run by the Publications Office of the European Union. It publishes every public procurement notice above the EU thresholds: contract notices, contract-award notices, prior-information notices, and design contests across all EU/EEA member states plus some third-country and EU-institution tenders. Notices are published in 24 languages and the underlying data (buyer, value, CPV category, place of performance, winner) can be freely reused for commercial or non-commercial purposes. For an agent it is the canonical, structured record of who is buying what in the European public sector, with a secondary `corporate-registry` character because each notice names buyer and winning-supplier organisations.

## Agent use cases

- public procurement search
- supplier and buyer diligence
- contract-award monitoring
- CPV-category market sizing
- cross-border tender discovery

## Join strategy

TED exposes two canonical geographic join keys. `buyer-country` carries the buyer's ISO 3166-1 alpha-3 country code (`ISO_3`, e.g. `SVK`), and `place-of-performance` carries the `NUTS` region code of where the contract is performed (e.g. `SK031`). Both are directly filterable and returnable in the v3 search API.

The source-internal identifier is the TED publication number (`TED_PUBLICATION_NUMBER`, e.g. `229365-2016`, now `NNNNNN-YYYY`), which uniquely keys each published notice and drives the XML/PDF/HTML render URLs; it lives in `primary_keys`, not the canonical registry, since no other dataset references it.

The highest-value identifier TED carries that is NOT yet in the registry is the CPV code (Common Procurement Vocabulary), the field `classification-cpv`. CPV is a shared EU vocabulary used by many procurement and spend datasets (national procurement portals, OpenTender, spend-analytics providers), so it is a strong new-join-key candidate. Flagged under Review notes. Buyer and supplier organisations also carry national registration numbers and occasionally an `LEI` inside notice XML, but these are not reliably exposed as top-level search fields, so they are not mapped here.

## Access notes

Hit the search API first: `POST https://api.ted.europa.eu/v3/notices/search` with a JSON body of `query` (eForms expert-query syntax, e.g. `classification-cpv=33600000 AND place-of-performance IN (SVK)`), a `fields` array, and `limit`/`page`. No API key is needed for reading published notices; an EU-Login API key is only required to validate or submit unpublished notices. Full-detail notice content is retrieved as eForms XML at `https://ted.europa.eu/en/notice/{publication-number}/xml`.

For large analyses use bulk instead of paginating: daily and monthly notice packages (eForms XML, plus legacy TED-schema XML for older years) are published on the TED website and mirrored on data.europa.eu. The TED Open Data Service (`https://data.ted.europa.eu/`) additionally offers the whole collection as RDF under the eProcurement Ontology (ePO) with a public SPARQL endpoint for cross-notice queries. Gotcha: coverage and field completeness change at the 2023-2024 eForms cutover, older notices use the TED schema with different field names.

## MCP / connector notes

Community MCP servers exist and wrap the anonymous v3 search API, so no credential handling is required: `github.com/pipeworx-io/mcp-ted-eu` and the `fbuchner-ted-mcp` server (also listed on PulseMCP / LobeHub), plus hosted Apify actors. No official Publications Office MCP. Known gaps: none abstract the SPARQL/RDF backend, and the eForms expert-query grammar plus the 24-language `notice-title` object are the parts a good connector must hide. Suggested surface: `search_notices`, `get_notice`, `get_notice_xml`, `list_cpv_categories`.

## Review notes

Potential new join key for review: CPV
  Entity type: procurement_classification
  Pattern: `^[0-9]{8}-[0-9]$` (8-digit Common Procurement Vocabulary code plus check digit; often stored without the check digit as 8 digits)
  Source field: `classification-cpv`
  Other datasets that would use it: national procurement portals, data.europa.eu procurement datasets, OpenTender/OpenOpps, EU spend-analytics providers. Strong cross-source value.

License note: the CC-BY-4.0 licence covers editorial content of the SIMAP/TED sites; the notice data itself is declared freely reusable for commercial and non-commercial purposes (attribution to the OJEU Supplement expected). CC-BY-4.0 is the closest SPDX code; confirm before treating individual notice text as CC-BY.

`buyer-country` returns ISO 3166-1 alpha-3 (`SVK`), which maps cleanly to `ISO_3`; some TED fields elsewhere use alpha-2, so map to `ISO_2` if a downstream field turns out to be two-letter.
