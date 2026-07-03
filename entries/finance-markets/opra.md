---
id: opra
name: OPRA Options Feed
domain: finance-markets
entry_kind: event-stream
description: Consolidated real-time feed of quotes and last-sale reports for every US listed equity and index option, run by the Options Price Reporting Authority.
homepage_url: https://www.opraplan.com/
docs_url: https://www.opraplan.com/faqs
type:
  - rest-api
auth_required: api-key-paid
cost: paid
license: OPRA-Subscriber-Agreement
frequency: real-time
lag: "sub-second on the licensed real-time feed; a 15-minute-delayed tier is offered by most vendors"
geography: [USA]
join_keys:
  - TICKER
primary_keys:
  - OCC_OPTION_SYMBOL
join_key_fields:
  - join_key: TICKER
    fields: [underlying_symbol, root]
structure: event-log
pit_reconstructable: false
revisions_possible: false
mcp_status: mcp-needed-low-value
agent_use_cases:
  - live options quote lookup
  - options last-sale monitoring
  - implied-volatility surface construction
  - options order-flow analysis
notes: "Licensed real-time feed. No public no-auth endpoint; access is gated behind an OPRA Vendor or Subscriber agreement and a paid vendor (Databento, dxFeed, LSEG, ICE, Bloomberg). access_test omitted because there is no callable OPRA-native endpoint without a licence."
last_verified: 2026-07-02
build_priority: low
---

# OPRA Options Feed

## Why this source matters

OPRA (Options Price Reporting Authority, LLC) is the SEC-registered securities information processor that consolidates quotes and last-sale reports from all US options exchanges into a single feed. It is owned by the exchanges that generate the data (Cboe, Nasdaq, NYSE, MIAX, BOX, MEMX) and is the authoritative tape for US listed equity and index options, the options-market analogue of the CTA/UTP tapes for equities. The feed carries bid/ask quotations, trade prints with volume, open interest, and end-of-day summaries. It is a licensed real-time feed: there is no free public endpoint, and both raw redistribution (Vendor) and internal consumption (Subscriber) require an agreement with OPRA plus per-user or per-device display fees. Because every option row encodes its underlying equity symbol, OPRA is the join bridge between options activity and equities/corporate data, giving it secondary relevance to any equity-markets workflow.

## Agent use cases

- live options quote lookup
- options last-sale monitoring
- implied-volatility surface construction
- options order-flow analysis

## Join strategy

OPRA's canonical registry join key is `TICKER`: the OCC/OSI option symbol embeds the underlying root symbol (e.g. `AAPL` in `AAPL  240119C00150000`), so options rows join to any equities or corporate-registry source keyed on ticker. The source-native identifier is the full 21-character OCC/OSI option symbol (root + expiration + call/put + strike), tracked here as the primary key `OCC_OPTION_SYMBOL`; it uniquely identifies a contract but is not in the canonical registry. Two identifiers that would materially improve options joins are not yet in the registry and are flagged in Review notes: the OCC option symbol itself (contract-level join across options sources) and a millisecond/nanosecond event timestamp (`DATE` only covers ISO-8601 calendar dates, not intraday tick time). Pair OPRA with an equities quote source on `TICKER` for underlying context, and with a corporate registry for issuer resolution.

## Access notes

There is no OPRA-native REST endpoint to hit directly. Access requires either a Subscriber or Vendor agreement with OPRA and, in practice, a commercial data vendor that is an approved OPRA redistributor. Vendors that expose OPRA via an API/datafeed include Databento, dxFeed, LSEG, ICE, and Bloomberg; each mediates the OPRA licence and layers its own auth (typically a paid API key). The baseline OPRA redistributor fee is roughly USD 1,500/month, plus per-user display fees (nonprofessional from about USD 1.25/user/month, professional about USD 31.50/user or device/month); exact numbers live in the OPRA Fee Schedule and shift, so treat them as indicative. To verify freshness or entitlement, hit the chosen vendor's OPRA endpoint with the vendor's key; there is nothing to curl against opraplan.com itself. The raw OPRA form is a high-throughput binary multicast datafeed (its peak message-rate capacity is published for capacity planning), not an HTTP API, so most agents consume it through a vendor's normalized REST/streaming layer.

## MCP / connector notes

No MCP exists. An MCP would necessarily wrap a specific paid vendor (Databento, dxFeed, etc.) rather than OPRA directly, since OPRA distributes a licensed binary feed and not a queryable API. Suggested surface once built against a vendor: `get_option_quote(occ_symbol)`, `get_option_trades(occ_symbol, window)`, `list_chain(underlying_ticker, expiration)`, `get_nbbo(occ_symbol)`. The connector must abstract over OSI symbol construction/parsing, entitlement and professional/nonprofessional gating, and real-time-vs-delayed tier selection. Marked low-value for a shared MCP not because the data is niche but because the paid-licence gate means few directory consumers can actually call it; the reusable value is the symbol-parsing and entitlement layer, not the transport.

## Review notes

Potential new join key for review: OCC_OPTION_SYMBOL
  Entity type: listed_option_contract
  Pattern: OSI 21-char symbol, root (up to 6, space-padded) + YYMMDD + C/P + 8-digit strike (e.g. "AAPL  240119C00150000")
  Other datasets that would use it: any options-market source (Cboe DataShop, ORATS, Databento OPRA, dxFeed, ICE, LSEG options)

Potential new join key for review: EVENT_TIMESTAMP
  Entity type: time
  Pattern: intraday timestamp with sub-second precision (ms/ns), distinct from the existing DATE key which is ISO-8601 calendar-date only
  Other datasets that would use it: any tick/event-stream source (OPRA, equities tapes, GDELT-style event logs, exchange datafeeds). Flagged because the hint requested a TIMESTAMP join key and none exists in the registry.

License short name `OPRA-Subscriber-Agreement` is not SPDX and not in SCHEMA.md's known short-name list. Proposed as a canonical kebab-case short name for the OPRA Vendor/Subscriber agreement family; needs human confirmation or an alternative (e.g. a generic `proprietary` marker).

`type` is set to `rest-api` because that is how agents actually consume OPRA (via a vendor's API). OPRA's native form is a licensed binary multicast datafeed, for which no `type` enum value cleanly fits; consider whether a `streaming-feed` or `datafeed` enum value is warranted. Flagged, not invented.
