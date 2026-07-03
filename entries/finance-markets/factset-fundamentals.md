---
id: factset-fundamentals
name: FactSet Fundamentals API
domain: finance-markets
entry_kind: panel
description: Standardised company financials, derived ratios, and business/geographic segment data for global public companies, addressed by market identifier.
homepage_url: https://www.factset.com/marketplace/catalog/product/factset-fundamentals-api
docs_url: https://developer.factset.com/api-catalog/factset-fundamentals-api
type:
  - rest-api
auth_required: api-key-paid
cost: paid
license: proprietary
rate_limit: "not publicly documented for Fundamentals; async batching supports bulk pulls (requests may run up to ~20 min)"
bulk_available: true
frequency: "daily updates as filings are processed"
geography: [global]
join_keys:
  - TICKER
  - ISIN
  - CUSIP
  - FIGI
  - SEDOL
primary_keys:
  - FACTSET_PERMANENT_ID
  - FACTSET_ENTITY_ID
join_key_fields:
  - join_key: TICKER
    fields: [ids, requestId]
  - join_key: ISIN
    fields: [ids, requestId]
  - join_key: CUSIP
    fields: [ids, requestId]
  - join_key: FIGI
    fields: [ids, requestId]
  - join_key: SEDOL
    fields: [ids, requestId]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - company financial-statement retrieval
  - cross-company ratio comparison
  - business and geographic segment analysis
  - fundamentals-driven screening
access_test:
  command: "curl -sf -u \"${FACTSET_USERNAME_SERIAL}:${FACTSET_API_KEY}\" 'https://api.factset.com/content/factset-fundamentals/v3/metrics'"
  expected_status: 200
  expected_fields: [data]
revisions_possible: true
pit_reconstructable: false
last_verified: 2026-07-02
notes: "access_test not executed; requires paid FactSet credentials (${FACTSET_USERNAME_SERIAL} + ${FACTSET_API_KEY})."
---

# FactSet Fundamentals API

## Why this source matters

FactSet Fundamentals is a commercial, standardised financials feed covering global public companies: over 750 fundamental items and ratios spanning income statement, balance sheet, cash flow, per-share metrics, and business/geographic segments, all normalised to a common template so figures are comparable across companies, sectors, and countries. It is one of the two or three institutional-grade fundamentals sources (alongside S&P Capital IQ and Refinitiv) that sell-side and buy-side analysts treat as authoritative. For an agent, the value is standardisation plus deep history: as-reported line items are mapped into a consistent schema, which removes the filing-parsing burden that free sources (SEC EDGAR, company IR pages) impose. Paid and enterprise-gated; there is no free tier.

## Agent use cases

- company financial-statement retrieval
- cross-company ratio comparison
- business and geographic segment analysis
- fundamentals-driven screening

## Join strategy

The API is addressed by security-level market identifiers. It accepts `TICKER` (exchange-qualified), `ISIN`, `CUSIP`, `FIGI` (Bloomberg/OpenFIGI), and `SEDOL` as inputs, all canonical keys in the registry, and echoes the supplied identifier back in each data point's `requestId` alongside FactSet's own `fsymId`. That makes it a strong hub for stitching fundamentals onto market data, holdings, or corporate-registry sources keyed on any of those five identifiers. FactSet mints its own symbology: the FactSet Permanent Identifier (`fsymId`, with `-R` regional / `-S` security / `-L` listing variants) and the FactSet Entity ID. These are source-internal (`primary_keys`) and require the separate FactSet Symbology / Concordance API to resolve to third-party IDs, so use the standard identifiers above for cross-source joins, not the FactSet permanent IDs. LEI and CIK are resolvable through Symbology but were not confirmed as direct Fundamentals inputs.

## Access notes

Auth is either OAuth 2.0 client-credentials or an API key over HTTP Basic, where the username is the FactSet `username-serial` and the password is the generated API key (create at https://developer.factset.com/authentication). Base host is `api.factset.com`; the Fundamentals v3 surface exposes `/metrics` (catalogue of available items and definitions), `/fundamentals` (financial data for a list of ids + metrics), and `/segments` (business/geographic segments). Hit `/metrics` first to enumerate the item universe. Both GET and POST support async batching for bulk workflows (long-running requests up to ~20 min), which is the intended path for wide id x metric pulls. An official Enterprise SDK (`fds.sdk.FactSetFundamentals`, Python/NuGet) wraps auth and pagination. Standard fundamentals are as-reported and can be restated; FactSet sells a separate point-in-time fundamentals product for backtests that need vintage-safe values.

## MCP / connector notes

No MCP exists. Audience is narrow (FactSet subscribers only), so this is low-value to build speculatively. If built, a connector should expose `list_metrics`, `get_fundamentals(ids, metrics, periodicity, fiscalPeriod)`, and `get_segments`, abstracting over the OAuth-vs-Basic auth split, the sync/async batching switch, and identifier normalisation (map an arbitrary user-supplied ticker/ISIN/CUSIP/FIGI to the form the API expects). The official Enterprise SDK is the practical substrate; an MCP would mostly wrap it and add response trimming.

## Review notes

- License short name `proprietary` is used because FactSet content is commercial and paywalled with no SPDX identifier and no public licence document; redistribution is governed by the subscriber's FactSet contract. Confirm whether the registry wants a more specific canonical short name (e.g. `FactSet-Commercial`) for enterprise paid feeds; several other paid vendors (S&P Capital IQ, Refinitiv, Bloomberg) will hit the same gap.
- No new join keys proposed. All five mapped keys (`TICKER`, `ISIN`, `CUSIP`, `FIGI`, `SEDOL`) already exist in `schema/join-keys.yaml`. FactSet Permanent Identifier and FactSet Entity ID are source-internal and left in `primary_keys` rather than invented into the canonical registry.
