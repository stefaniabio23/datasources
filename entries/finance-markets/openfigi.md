---
id: openfigi
name: OpenFIGI
domain: finance-markets
description: Bloomberg-operated open mapping service that resolves third-party security identifiers (ISIN, CUSIP, SEDOL, ticker) to the Financial Instrument Global Identifier (FIGI) and back.
homepage_url: https://www.openfigi.com/
docs_url: https://www.openfigi.com/api/documentation
type:
  - rest-api
auth_required: api-key-free
cost: free
license: Public-Domain-Dedication
rate_limit: "anon: 25 mapping req/min, 10 jobs/req, 5 search-or-filter req/min. With API key: 25 mapping req/6s, 100 jobs/req, 20 search-or-filter req/min."
bulk_available: false
frequency: continuous
geography: [global]
join_keys:
  - FIGI
  - ISIN
  - CUSIP
  - SEDOL
  - TICKER
primary_keys:
  - FIGI
  - COMPOSITE_FIGI
  - SHARE_CLASS_FIGI
join_key_fields:
  - join_key: FIGI
    fields: [data.figi, data.compositeFIGI, data.shareClassFIGI]
  - join_key: TICKER
    fields: [data.ticker]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/urbancanary/openfigi-mcp
mcp_notes: >
  Single community MCP exists. Suggested canonical surface: map_identifiers (batched
  POST /v3/mapping), search_instruments (POST /v3/search), filter_instruments
  (POST /v3/filter), get_enum_values (GET /v3/mapping/values/:key). Connector must
  handle the 25-per-batch request shape, surface rate-limit headers, and chunk
  large id lists to respect the with-key 100-jobs-per-request cap.
agent_use_cases:
  - resolve ISIN/CUSIP/SEDOL to FIGI
  - cross-exchange security normalisation
  - ticker disambiguation across venues
  - portfolio identifier reconciliation
  - enrich security metadata (exchange, security type, market sector)
access_test:
  command: "curl -sf -X POST 'https://api.openfigi.com/v3/mapping' -H 'Content-Type: application/json' --data '[{\"idType\":\"ID_ISIN\",\"idValue\":\"US4592001014\"}]'"
  expected_status: 200
  expected_fields: [figi, name, ticker, exchCode, securityType]
last_verified: 2026-06-08
build_priority: medium
---

# OpenFIGI

## Why this source matters

OpenFIGI is Bloomberg's free identifier-mapping service for the Financial Instrument Global Identifier (FIGI), an open ISO 10962-style code that uniquely names a security at the global, country-composite, and exchange-listing levels. It is the canonical bridge between the licensed identifier zoo (ISIN, CUSIP, SEDOL, ticker, Wertpapier, OCC, OPRA) and a permissively-licensed key any agent can store and redistribute. FIGI itself is dedicated to the public domain by Bloomberg, which makes OpenFIGI the only free service that resolves the proprietary-but-ubiquitous identifiers downstream finance data is keyed on. Secondary domain: any `corporate-registry` entry that needs to attach listed securities back to a company.

## Agent use cases

- resolve ISIN/CUSIP/SEDOL to FIGI
- cross-exchange security normalisation
- ticker disambiguation across venues
- portfolio identifier reconciliation
- enrich security metadata (exchange, security type, market sector)

## Join strategy

OpenFIGI is built as a join service. It accepts and emits every canonical security key in the registry: `FIGI`, `ISIN`, `CUSIP`, `SEDOL`, `TICKER`. Source-side `idType` strings map onto the registry as follows: `ID_BB_GLOBAL` and `COMPOSITE_ID_BB_GLOBAL` to `FIGI`; `ID_ISIN` to `ISIN`; `ID_CUSIP` to `CUSIP`; `ID_SEDOL` to `SEDOL`; `TICKER` and `BASE_TICKER` to `TICKER`. Source-internal-only identifiers (`ID_WERTPAPIER`, `ID_COMMON`, `OCC_SYMBOL`, `OPRA_SYMBOL`, `SHARE_CLASS_FIGI`) are not in the canonical registry, use them for direct OpenFIGI lookups, not cross-source joins.

Recommended pairing: use OpenFIGI as the normalisation hop between sources keyed on different security IDs. Resolve any incoming ID to FIGI first, then key downstream joins on FIGI to avoid the ISIN-vs-CUSIP-vs-ticker collision space (same ticker on multiple exchanges, same ISIN across share classes, etc.). The `compositeFIGI` and `shareClassFIGI` fields in the response let you collapse exchange-level listings to country or share-class roll-ups.

## Access notes

Hit `POST https://api.openfigi.com/v3/mapping` first with a JSON array of `{idType, idValue}` objects. Anonymous use works but is heavily throttled (25 mapping requests/min, 10 jobs per request). Register at `/user/signup` for a free API key, send it in the `X-OPENFIGI-APIKEY` header, and the limits jump to 25 requests per 6 seconds with 100 jobs per request, which is what "map hundreds of thousands of instruments in minutes" means in the marketing copy. Search and filter endpoints stay tightly capped (5/min anon, 20/min with key) because they are full-text scans rather than direct lookups.

Bloomberg dedicates FIGI identifiers themselves to the public domain (unrestricted redistribution, commercial or non-commercial, no attribution required for the codes). Trademark restrictions apply to the names "FIGI" and "OPENFIGI", do not imply endorsement. Liability is capped at fifty US dollars; the service ships "as is". No bulk download is offered, the API is the only access mode.

Watch the response headers `ratelimit-limit`, `ratelimit-remaining`, `ratelimit-reset` to back off cleanly; OpenFIGI returns HTTP 429 fast under load.

## MCP / connector notes

A community MCP exists at `github.com/urbancanary/openfigi-mcp` (single-author repo, not widely adopted, treat as experimental despite the maturity tier). Suggested canonical surface for any replacement: `map_identifiers` (batched POST /v3/mapping), `search_instruments` (POST /v3/search), `filter_instruments` (POST /v3/filter), `get_enum_values` (GET /v3/mapping/values/:key for exchCode, securityType, currency lookups). The connector must chunk large input lists to respect the 100-jobs-per-request cap, surface rate-limit headers, and ideally cache FIGI lookups locally since the mapping is stable.

## Review notes

None.
