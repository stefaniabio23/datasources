---
id: defillama-stablecoins
name: DefiLlama Stablecoins
domain: finance-markets
entry_kind: time-series
description: Open API tracking circulating supply, chain distribution, peg mechanism, and historical market cap of stablecoins across every supported blockchain, run as the stablecoins module of the DefiLlama TVL aggregator.
homepage_url: https://defillama.com/stablecoins
docs_url: https://api-docs.defillama.com/
type:
  - rest-api
auth_required: none
cost: freemium
license: DefiLlama-Terms
rate_limit: "no published per-key cap on the free host; informal fair-use throttling, Pro plan ($300/mo) raises limits and unlocks /api/chainAssets and other TVL Pro endpoints"
bulk_available: false
frequency: "circulating supply refreshed hourly per chain; historical mcap and price series updated daily"
lag: "near real-time for current supply (intra-hour); daily series lag ~24h"
geography: [global]
join_keys:
  - DATE
  - ISO_4217
primary_keys:
  - DEFILLAMA_STABLECOIN_ID
  - DEFILLAMA_CHAIN_SLUG
  - DEFILLAMA_PROTOCOL_SLUG
  - GECKO_ID
join_key_fields:
  - join_key: DATE
    fields:
      - "peggedAssets[].circulating"
      - "peggedAssets[].circulatingPrevDay"
      - "peggedAssets[].circulatingPrevWeek"
      - "peggedAssets[].circulatingPrevMonth"
      - "tokens[].date"
  - join_key: ISO_4217
    fields:
      - "peggedAssets[].pegType"
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No widely adopted MCP server as of last verify. Suggested surface: list_stablecoins,
  get_stablecoin(asset_id), get_stablecoin_chain_history(chain), get_stablecoinchains_snapshot,
  get_stablecoinprices. Connector should normalise pegType strings (peggedUSD, peggedEUR,
  peggedVAR) to ISO_4217 where possible, expose chain slugs as a closed enum loaded from
  /v2/chains, and surface the free api.llama.fi vs stablecoins.llama.fi host split so callers
  don't hit 404s.
agent_use_cases:
  - stablecoin circulating supply lookup per chain
  - stablecoin market-cap time series
  - peg-mechanism classification
  - de-peg detection from historical price series
  - cross-chain stablecoin distribution snapshot
access_test:
  command: "curl -sf 'https://stablecoins.llama.fi/stablecoins?includePrices=true'"
  expected_status: 200
  expected_fields: [peggedAssets]
last_verified: 2026-06-09
build_priority: medium
notes: >
  The URL Stephanie supplied (api-docs.defillama.com/#tag/tvl/get/api/chainAssets) points at
  a Pro-only TVL endpoint, but the slug scopes this entry to the broader Stablecoins data
  product, which is on the free tier. See Review notes for the host-split gotcha.
---

# DefiLlama Stablecoins

## Why this source matters

DefiLlama is the dominant open aggregator for on-chain DeFi metrics, run as a public good by DefiLlama Limited (UAE-incorporated) and funded by a Pro tier plus token-ecosystem grants. The Stablecoins module tracks every meaningful stablecoin across every chain it supports, exposing circulating supply, peg type (USD, EUR, gold, variable), peg mechanism (fiat-backed, crypto-backed, algorithmic), per-chain distribution, and historical market cap. For agents researching crypto market structure, stablecoin flows are the closest thing to an on-chain payments and macro signal, so this is the obvious free starting point. Secondary domain coverage: TVL across protocols and chains (the broader DefiLlama API at `api.llama.fi`), prices (`coins.llama.fi`), and yield pools (`yields.llama.fi`) live in the same docs and are reachable from the same host pattern.

## Agent use cases

- stablecoin circulating supply lookup per chain
- stablecoin market-cap time series
- peg-mechanism classification
- de-peg detection from historical price series
- cross-chain stablecoin distribution snapshot

## Join strategy

DefiLlama exposes few standard canonical identifiers. `DATE` carries over for any time-series join; `pegType` ("peggedUSD", "peggedEUR", "peggedJPY") maps trivially to `ISO_4217` for the issuing-currency join, useful when stitching stablecoin float against FX or sovereign-rate series from FRED or Alpha Vantage.

DefiLlama-internal identifiers belong in `primary_keys`, not canonical joins: `DEFILLAMA_STABLECOIN_ID` (integer string like `"1"` for Tether, `"2"` for USDC), `DEFILLAMA_CHAIN_SLUG` (capitalised names like `Ethereum`, `Arbitrum`, `Solana`), `DEFILLAMA_PROTOCOL_SLUG` (kebab or compact form like `aave-v3`, `lido`), and `GECKO_ID` (the CoinGecko coin slug, present on most chain and asset payloads). None are in the canonical registry; see Review notes for candidates.

Practical pairing: pair with CoinGecko (via `gecko_id`) for off-chain price benchmarks, with Alpha Vantage or FRED (via `ISO_4217` and `DATE`) for fiat-peg comparisons, and with on-chain explorers (Etherscan, etc.) for address-level supply reconciliation. No direct ticker or ISIN bridge exists; treat stablecoin IDs as a parallel namespace.

## Access notes

**Host split (gotcha).** The Stablecoins surface lives on `https://stablecoins.llama.fi`, not the documented `https://api.llama.fi` base. The OpenAPI lists paths like `/stablecoins`, `/stablecoincharts/all`, `/stablecoincharts/{chain}`, `/stablecoin/{asset}`, `/stablecoinchains`, `/stablecoinprices` without the host prefix; calling them against `api.llama.fi` returns 404. Prices live on `https://coins.llama.fi`. TVL lives on `https://api.llama.fi`. Pro endpoints (including the `/api/chainAssets` URL in this entry's research brief) live on `https://pro-api.llama.fi/{API_KEY}/...`.

**Start at:** `https://stablecoins.llama.fi/stablecoins?includePrices=true` for the full peggedAssets list, then drill in with `/stablecoin/{id}` for per-asset historical mcap and chain breakdown. For chain-level rollups use `/stablecoinchains`. For peg-deviation analysis use `/stablecoinprices`.

**Auth + cost:** free tier requires no key. The Pro plan is $300/month, raises rate limits, and unlocks ~38 Pro-only endpoints (including `/api/chainAssets`, `/api/tokenProtocols/{symbol}`, and `stablecoins/stablecoindominance/{chain}`). Most agent workloads on stablecoin float fit inside the free tier.

**License nuance.** DefiLlama Terms (UAE Limited) grant a non-commercial personal use license. The terms explicitly forbid resale of the data, republication, or commercial scraping without written consent, with liquidated damages of up to USD 100K per violation. For research and personal-use agents this is fine; for any product surfacing DefiLlama data to paying users, either subscribe to Pro and confirm redistribution rights in writing or move to a permissively licensed alternative.

**Bulk.** No flat-file download. Whole-history pulls happen via the `/stablecoincharts/all` endpoint, which returns the full time series in one JSON payload (a few MB) and is the closest thing to a bulk surface here.

## MCP / connector notes

No widely adopted MCP server tracks the DefiLlama API as of last verify. Surface suggestion for a high-value community MCP:

- `list_stablecoins(include_prices=False)` — wrap `/stablecoins`
- `get_stablecoin(asset_id)` — wrap `/stablecoin/{asset}`
- `get_stablecoin_chain_history(chain)` — wrap `/stablecoincharts/{chain}`
- `get_stablecoinchains_snapshot()` — wrap `/stablecoinchains`
- `get_stablecoin_prices(asset_id=None)` — wrap `/stablecoinprices`

Things the connector must abstract: the host split (api/stablecoins/coins/yields/pro), `pegType` to `ISO_4217` normalisation, capitalised vs lowercase chain slugs (the API mixes both depending on endpoint), and the free-vs-Pro path remapping (Pro requests prefix the path with the API key). An MCP that bundled TVL + Stablecoins + Prices + Yields under one tool surface would justify the high-value rating, since DefiLlama is the de facto open source for DeFi metrics.

## Review notes

- License field `DefiLlama-Terms` is not in SCHEMA.md's canonical short-name list. Other freemium crypto-data vendors (CoinGecko, CoinMarketCap if added later) would likely also need bespoke license short names. Flag for review whether to canonicalise this as one of `DefiLlama-Terms`, `Crypto-Vendor-Terms-Of-Service`, or keep per-vendor.
- Potential new join keys for review:
  - `COINGECKO_ID`
    - Entity type: cryptoasset
    - Pattern: kebab-case slug, e.g. `tether`, `usd-coin`, `dai`, `bitcoin`
    - Other datasets that would use it: CoinGecko API, DefiLlama (chains, coins, stablecoins, yields), Dune, Token Terminal, Etherscan token labels.
  - `DEFILLAMA_CHAIN_SLUG`
    - Entity type: blockchain
    - Pattern: capitalised display name in most payloads (`Ethereum`, `Arbitrum`, `Solana`), lowercase in path params for some endpoints
    - Other datasets that would use it: DefiLlama TVL, Stablecoins, Yields, Prices.
  - `DEFILLAMA_PROTOCOL_SLUG`
    - Entity type: defi_protocol
    - Pattern: kebab or compact lowercase (`aave-v3`, `lido`, `uniswap`)
    - Other datasets that would use it: DefiLlama TVL, Yields, Fees, Volumes.
- Domain placement: filed under `finance-markets` since stablecoin float is a market-structure signal. Could equally argue for a new `crypto-onchain` domain once more crypto sources land. Not adding new domain values per the schema-immutable rule; flag for consideration if 3+ crypto sources arrive.
- `access_test` executed: `curl -sf 'https://stablecoins.llama.fi/stablecoins?includePrices=true'` returned HTTP 200 with full `peggedAssets[]` payload (USDT id=1 first, ~187B USD circulating).
- `mcp_status: mcp-needed-high-value` with `mcp_maturity: none` (no MCP exists yet; `mcp_package` is omitted since it is required only when `mcp_status: mcp-exists`). Re-check on next pass; the DefiLlama ecosystem is active enough that a community MCP may land soon, at which point flip to `mcp-exists` and record the package.
