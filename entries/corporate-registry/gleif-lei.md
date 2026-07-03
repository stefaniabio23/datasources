---
id: gleif-lei
name: GLEIF LEI
domain: corporate-registry
entry_kind: registry
description: Global register of Legal Entity Identifiers (ISO 17442) for legal entities, with reference data, corporate-ownership relationships, and BIC/ISIN/MIC cross-mappings.
homepage_url: https://www.gleif.org/en/lei-data/gleif-api
docs_url: https://api.gleif.org/docs
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC0
rate_limit: "60 req/min per user"
bulk_available: true
frequency: Golden Copy three times daily; ISIN-to-LEI mapping daily; BIC-to-LEI mapping monthly
lag: "same-day; entity reference data as self-reported and validated by the managing LOU"
geography: [global]
join_keys:
  - LEI
  - ISIN
  - ISO_2
  - DATE
primary_keys:
  - LEI
join_key_fields:
  - join_key: LEI
    fields: [data.id, data.attributes.lei]
  - join_key: ISIN
    fields: [data.attributes.isin]
  - join_key: ISO_2
    fields: [data.attributes.entity.legalAddress.country, data.attributes.entity.headquartersAddress.country, data.attributes.entity.jurisdiction]
  - join_key: DATE
    fields: [data.attributes.entity.creationDate, data.attributes.registration.initialRegistrationDate, data.attributes.registration.lastUpdateDate]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/olgasafonova/gleif-mcp-server"
  - "gleif-mcp-server (pypi)"
mcp_notes: >
  Community MCP with LEI lookup, fuzzy entity search, BIC/ISIN cross-reference,
  parent/child ownership traversal, and batch validation over the public GLEIF API.
  No auth; connector should throttle to the 60 req/min budget client-side.
agent_use_cases:
  - counterparty KYC
  - LEI-to-ISIN security resolution
  - beneficial-ownership tracing
  - cross-registry entity resolution
  - BIC/SWIFT to legal-entity lookup
structure: registry-snapshot
access_test:
  command: "curl -sf 'https://api.gleif.org/api/v1/lei-records/529900T8BM49AURSDO55'"
  expected_status: 200
  expected_fields: [data.id, data.attributes.lei, data.attributes.entity, data.attributes.registration]
last_verified: 2026-07-02
build_priority: high
---

# GLEIF LEI

## Why this source matters

The Global Legal Entity Identifier Foundation runs the authoritative register behind the ISO 17442 LEI, a 20-character code identifying legal entities that participate in financial transactions. Coverage is ~2.8M active LEIs across 200+ jurisdictions, published as CC0 with no registration required. The GLEIF API sits on top of the "Golden Copy" and exposes Level 1 reference data (legal name, address, jurisdiction, legal form, status), Level 2 corporate-ownership relationships (direct and ultimate parent), and cross-mappings to BIC, ISIN, and MIC. This is the canonical bridge between a company's legal identity and its securities and messaging identifiers, so it is also a `finance-markets` source: the LEI-to-ISIN map (maintained with ANNA) resolves which securities an issuer has on the market.

## Agent use cases

- counterparty KYC
- LEI-to-ISIN security resolution
- beneficial-ownership tracing
- cross-registry entity resolution
- BIC/SWIFT to legal-entity lookup

## Join strategy

`LEI` is both the source-native primary key and a canonical join key: fetch a record directly at `/lei-records/{LEI}`. GLEIF is the hub that maps `LEI` to `ISIN` (via the `/lei-records/{LEI}/isins` relationship endpoint, refreshed daily) and to country via `ISO_2` (legal address, HQ address, and jurisdiction fields return alpha-2 codes). `DATE` covers entity creation and registration timestamps.

Pair with GLEIF's ISIN mapping to reach securities-market sources (OpenFIGI, exchange feeds) keyed on `ISIN`; pair with Companies House or other national registries on entity identity, using `registeredAs` (the local registration number) as a soft bridge. Ownership relationships (`direct-parent`, `ultimate-parent`) let an agent walk a corporate tree by chaining LEI lookups; these are GLEIF-internal graph edges, not registry join keys.

BIC and MIC cross-mappings are exposed (`data.attributes.bic`, `data.attributes.mic`) but neither is a canonical join key yet, see Review notes.

## Access notes

**Most queries:** REST API at `https://api.gleif.org/api/v1/`, no auth, JSON:API format. Start with `GET /lei-records/{LEI}` for a single entity or `GET /lei-records?filter[lei]=<comma-separated>` to enrich a batch. Fuzzy name/BIC/ISIN search via `/fuzzycompletions` and `filter[bic]` / `filter[isin]` query params. Rate limit is 60 req/min per user; there is no key, so throttle client-side rather than relying on quota headers.

**Wide-net analyses:** the Golden Copy and delta concatenated files (full LEI population, three times daily) are the bulk path, faster than paginating the API for full-population joins. ISIN-to-LEI and BIC-to-LEI mapping files are separate downloads on the same terms.

Known gotchas:

- The base LEI record does not embed ISINs; they live behind the `/isins` relationship endpoint and in the separate daily mapping file.
- `bic` and `mic` are arrays and are frequently null; BIC-to-LEI mapping is only monthly, so it lags entity changes.
- Records for lapsed/retired entities remain; filter on `entity.status` and `registration.status` for active-only.
- Reference data is self-reported and validated by the managing LOU, quality varies by issuer.

## MCP / connector notes

Community MCP exists: `github.com/olgasafonova/gleif-mcp-server` (also on PyPI as `gleif-mcp-server`), ~29 tools covering LEI lookup, fuzzy entity search, BIC/SWIFT and ISIN cross-reference, country browse, ownership relationship traversal, LEI validation, and batch validation, over the public API with no external data files. Gaps to check before relying on it: bulk Golden Copy ingestion (it is API-only, so full-population joins still need the download service) and client-side handling of the 60 req/min budget.

## Review notes

Two useful identifiers GLEIF exposes are not in `schema/join-keys.yaml`:

Potential new join key for review: BIC
  Entity type: financial_institution / business_party (ISO 9362 Business Identifier Code, aka SWIFT code)
  Pattern: ^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$
  Other datasets that would use it: SWIFT/ISO 20022 messaging references, bank reference data, any payments source keyed on SWIFT/BIC

Potential new join key for review: MIC
  Entity type: market_or_trading_venue (ISO 10383 Market Identifier Code)
  Pattern: ^[A-Z0-9]{4}$
  Other datasets that would use it: exchange/venue reference data, market-data feeds, securities-listing sources

Company legal name (`entity.legalName`) is exposed and searchable (fuzzy) but is not a stable identifier, so it is intentionally left out of `join_keys`; use it as a match feature, not a join key.

License: LEI data is published by GLEIF under CC0 1.0 (public-domain dedication) with attribution requested but not required. The "LEI Data Terms of Use" page frames it as free, unrestricted, no-registration use; `CC0` captures the operative grant.
