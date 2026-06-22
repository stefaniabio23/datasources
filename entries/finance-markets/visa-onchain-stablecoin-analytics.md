---
id: visa-onchain-stablecoin-analytics
name: Visa Onchain Analytics Dashboard
domain: finance-markets
entry_kind: panel
description: Free public web dashboard, built by Visa with Allium Labs, charting fiat-backed stablecoin supply, transfers, addresses, and lending across 19+ public blockchains.
homepage_url: https://visaonchainanalytics.com/
docs_url: https://docs.allium.so/historical-data/stablecoins
type:
  - web-ui
auth_required: none
cost: free
license: visa-onchain-dashboard-proprietary-display-only
rate_limit: "no documented quota; static dashboard, charts render from pre-aggregated Allium tables"
bulk_available: false
frequency: "daily (per Allium upstream aggregation; not stated on dashboard itself)"
lag: "unknown; cadence not published on the dashboard"
geography: [global]
join_keys:
  - DATE
  - ISO_4217
primary_keys:
  - VISA_ONCHAIN_CHAIN_NAME
  - VISA_ONCHAIN_STABLECOIN_TICKER
join_key_fields:
  - join_key: DATE
    fields: [date]
  - join_key: ISO_4217
    fields: [currency]
mcp_status: requires-scraping
mcp_maturity: none
mcp_notes: >
  No API. All data is rendered client-side on the visaonchainanalytics.com SPA from
  pre-computed Allium aggregates. An MCP would need browser automation or HTML / chart-JSON
  scraping to read values; the higher-value connector targets Allium directly (paid)
  rather than the Visa dashboard surface. Treat this entry as a discovery surface
  pointing at the upstream paid Allium tables.
agent_use_cases:
  - stablecoin market-share monitoring across chains
  - adjusted-versus-raw stablecoin transfer volume context
  - L1-versus-L2 stablecoin activity comparison
  - stablecoin lending TVL and average loan-size snapshots
  - chain-level active-address trends per stablecoin
last_verified: 2026-06-09
build_priority: low
notes: >
  Display-only dashboard. Raw queryable data lives upstream at Allium and is a
  paid product; Visa exposes the visualisations free, no API, no bulk download,
  no published data-licence. Adjusted tab strips bot/MEV/CEX-internal flows. ~10
  stablecoins and ~19 chains tracked at last verify; full list in body.
---

# Visa Onchain Analytics Dashboard

## Why this source matters

Visa's onchain analytics dashboard is a free, no-auth web surface that charts fiat-backed stablecoin supply, transfer volume, transfer count, active addresses, and lending activity across roughly 19 public blockchains and 10-plus issuers (USDC, USDT, RLUSD, PYUSD, USDP, FDUSD, mUSD, USDG, EURC, USDtb, USDH). Visa operates the front end; the underlying data pipeline is run by Allium Labs and matches Allium's paid `crosschain.metrics.stablecoin_volume` and related tables. The signature feature is the adjusted-versus-raw toggle: Allium applies heuristics to strip out bot, MEV, and centralised-exchange-internal flows, so the same 30-day window can swing from trillions in raw transfer volume to hundreds of billions adjusted. For agents researching stablecoin market structure, this is the clearest public single-pane view of which chain hosts which stablecoin, and how that mix is moving over time. Secondary domain: `consumer-signal` (stablecoin adoption metrics feed crypto-attention dashboards alongside Google Trends and prediction-market odds), though the primary fit is finance-markets.

## Agent use cases

- stablecoin market-share monitoring across chains
- adjusted-versus-raw stablecoin transfer volume context
- L1-versus-L2 stablecoin activity comparison
- stablecoin lending TVL and average loan-size snapshots
- chain-level active-address trends per stablecoin

## Join strategy

The dashboard is identifier-poor by design. Native handles are a chain name (free-text, lowercased: `ethereum`, `solana`, `tron`, `base`, `arbitrum`, `optimism`, `polygon`, `bsc`, `avalanche`, ...), a stablecoin ticker (`USDC`, `USDT`, `PYUSD`, `EURC`, ...), and a date bucket (1D, 1W, 1M, 3M, 12M, all-time). Of the canonical registry, only `DATE` and `ISO_4217` apply cleanly: each stablecoin pegs to a currency (`USD` for the USD-backed set, `EUR` for EURC), and the date axis on every chart is ISO-8601. Chain names and stablecoin tickers do not have canonical join keys in the registry today; both are good candidates if more onchain entries land. Pair with FRED on `DATE` and `ISO_4217` for stablecoin supply versus fiat M2 comparisons, with World Bank commodity prices on `DATE` for risk-on / risk-off context, and with the upstream Allium tables (paid) when an agent needs the per-transfer row data rather than the pre-aggregated chart series.

## Access notes

**Start at:** the dashboard tabs at `https://visaonchainanalytics.com/` (Overview, Supply, Transactions, Addresses, Lending, Insights). Each tab renders pre-aggregated charts client-side; there is no public JSON endpoint, no documented API, and no bulk download. The site is a single-page app rendered against Allium's backend.

**Auth:** none. Public dashboard; no account, no key.

**Cadence:** the dashboard footer does not publish a refresh cadence. Allium's upstream `crosschain.metrics.stablecoin_volume` is documented as a daily-aggregate table at `docs.allium.so/historical-data/stablecoins`. Treat as daily until clearer.

**Raw queryable data:** lives upstream at Allium, behind their paid product. Three relevant tables: `crosschain.stablecoin.list` (issuer + contract directory), `crosschain.stablecoin.transfers` (per-transfer rows), `crosschain.metrics.stablecoin_volume` (daily aggregates). Coverage is documented to span 45-plus chains in the directory; full transfer and volume coverage is documented across roughly 20 fully-supported chains. Contact `https://globalclient.visa.com/crypto-contact` for Visa-side enquiries; contact Allium directly for data access.

**License nuance:** no data-licence string published on the dashboard. Footer contains "Legal", "Privacy Notice", "Cookie Preferences", "Intellectual Property Rights" links but no machine-readable licence. Visa retains brand and IP rights. Treat redistribution of charts or extracted figures as restricted until clarified; attribute "Visa Onchain Analytics Dashboard, powered by Allium" when citing.

**Freshness check:** open the Supply tab and confirm the right-most date on the largest USDC or USDT chart reads within the last few days.

## MCP / connector notes

No MCP found in `modelcontextprotocol/servers`, npm, or PyPI as of last verify. Building a connector around the Visa dashboard adds low value: there is no documented JSON surface, no auth handle to manage, and the charts are derived series rather than raw rows. A scraping connector would need to either parse the rendered SPA via browser automation or reverse-engineer the internal chart-data calls Allium serves to the front end; both are fragile and would breach the spirit of the IP terms. The high-value connector here is an Allium-direct MCP (paid, gated by API key) exposing `list_stablecoins`, `query_stablecoin_supply`, `query_stablecoin_transfers`, `query_stablecoin_volume_adjusted`, `query_stablecoin_lending` against the canonical `crosschain.stablecoin.*` tables; that would let agents query the same data the Visa dashboard renders, with filters, pagination, and per-transfer granularity. Visa's surface should be treated as a discovery and verification surface pointing at that connector rather than its own MCP target.

## Review notes

- License set to `visa-onchain-dashboard-proprietary-display-only`: the dashboard publishes no machine-readable data-licence string. Visa's footer carries Legal / Privacy / IP-Rights links and retains brand and IP rights, with no redistribution grant. The kebab short-form records the proprietary display-only status (chart extraction / redistribution restricted, attribute "Visa Onchain Analytics Dashboard, powered by Allium"). Raw data licensing is governed by Allium's paid terms upstream. Flagging for human confirmation of the short-form token.
- Cadence and lag are not stated on the dashboard. The Allium upstream is documented as daily aggregation; I recorded `frequency: daily` on that basis and left `lag` as `unknown`. Worth confirming.
- `entry_kind: panel` chosen because the dashboard is a multi-dimensional time-series view (chain x stablecoin x metric x time). Could also be argued as `mixed` if the Lending tab is treated as a distinct sub-dataset.
- Primary domain: `finance-markets`. Secondary: `consumer-signal` (stablecoin adoption sits next to other crypto-attention series). Mentioned in the body, not duplicated in YAML.
- No `access_test` recorded. The site is a JS SPA with no stable JSON endpoint to curl; `curl -sf https://visaonchainanalytics.com/` returns 200 but only the HTML shell. Manual freshness check documented above.
- Potential new join keys for review:
  - `STABLECOIN_TICKER`
    - Entity type: stablecoin
    - Pattern: short uppercase string, typically 3-6 chars (`USDC`, `USDT`, `PYUSD`, `RLUSD`, `EURC`)
    - Other datasets that would use it: Allium direct, DefiLlama stablecoins, Dune stablecoin dashboards, CoinGecko, CoinMarketCap, Artemis. Probably worth adding once a second stablecoin-aware source lands.
  - `EVM_CHAIN_ID`
    - Entity type: blockchain_network
    - Pattern: positive integer (`1` for Ethereum mainnet, `137` for Polygon, `8453` for Base, `42161` for Arbitrum, `10` for Optimism)
    - Other datasets that would use it: any EVM-data source (Etherscan, Allium, Dune, DefiLlama, Covalent, Alchemy). Strong cross-source candidate but only useful for EVM chains; non-EVM chains (Solana, Tron, TON, Sui) need a parallel free-form chain-slug field.
- Potential new license short-name for review: a `Visa-Onchain-Dashboard-Terms` (or generic `proprietary-display-only`) token would let the YAML carry the real status instead of `unknown`. Defer until a second dashboard-only source lands.
