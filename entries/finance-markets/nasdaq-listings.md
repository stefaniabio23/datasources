---
id: nasdaq-listings
name: Nasdaq Trader Symbol Directory
domain: finance-markets
entry_kind: registry
description: Authoritative directory of Nasdaq-listed and other US exchange-listed securities published daily as pipe-delimited files by Nasdaq Trader.
homepage_url: https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
docs_url: https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
type:
  - bulk-download
auth_required: none
cost: free
license: unknown
rate_limit: "no published limit; small text files (<1MB each) refreshed periodically through the trading day"
bulk_available: true
frequency: "multiple times per trading day"
lag: "intraday; each file embeds a File Creation Time line in mmddyyyyhhmm format"
geography: [USA]
join_keys:
  - TICKER
primary_keys:
  - NASDAQ_SYMBOL
  - ACT_SYMBOL
  - CQS_SYMBOL
  - MPID
join_key_fields:
  - join_key: TICKER
    fields: [Symbol, ACT Symbol, NASDAQ Symbol, CQS Symbol]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Static daily files; a thin loader (download, parse pipe-delimited, drop the
  File Creation Time footer) is enough. Suggested surface: list_nasdaq_symbols,
  list_other_listed_symbols, lookup_symbol, get_financial_status, list_mutual_funds.
agent_use_cases:
  - canonical ticker universe construction
  - exchange and security-type lookup
  - ETF flag and mutual-fund classification
  - delisting and add/delete tracking
  - financial-status flagging (deficient, delinquent, bankrupt)
access_test:
  command: "curl -sf 'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt' | head -1"
  expected_status: 200
  expected_fields:
    - Symbol
    - Security Name
    - Market Category
    - Test Issue
    - Financial Status
    - Round Lot Size
    - ETF
    - NextShares
last_verified: 2026-06-09
build_priority: medium
---

# Nasdaq Trader Symbol Directory

## Why this source matters

Nasdaq Trader's symbol directory is the canonical, free, daily-refreshed list of every security trading on Nasdaq plus every other US-listed security (NYSE, NYSE American, NYSE Arca, BATS, IEX). Published by Nasdaq itself as plain pipe-delimited text files on a public web server, no auth, no rate limit. For any agent building a US equities universe, it is the ground-truth seed: which tickers exist today, which exchange they trade on, whether they are ETFs, mutual funds, test issues, or in deficient/delinquent/bankrupt financial status. Pairs naturally with OpenFIGI (ticker to FIGI/ISIN), SEC EDGAR (ticker to CIK), and price APIs like Polygon, Alpha Vantage, or FRED.

## Agent use cases

- canonical ticker universe construction
- exchange and security-type lookup
- ETF flag and mutual-fund classification
- delisting and add/delete tracking
- financial-status flagging (deficient, delinquent, bankrupt)

## Join strategy

The only canonical cross-source key the directory exposes is `TICKER`. It is exposed under four source-side names that map to the same canonical key:

- `Symbol` in `nasdaqlisted.txt` (Nasdaq-traded securities)
- `ACT Symbol` and `CQS Symbol` and `NASDAQ Symbol` in `otherlisted.txt` (the three variants reflect the same underlying ticker rendered for different downstream systems; differences are punctuation, e.g. `BRK.A` vs `BRK A`)
- Fund symbols in `mfundslist.txt`

Source-internal IDs not in the canonical registry: `MPID` (Market Participant Identifier from `mpidlist.txt`), and the options root symbols in `options.txt` / `phlxoptions.csv`. Useful for Nasdaq-internal joins, not cross-source.

The directory does not expose `CUSIP`, `ISIN`, `FIGI`, `CIK`, or `LEI`. To enrich, route tickers through OpenFIGI (TICKER to FIGI/ISIN/CUSIP) or SEC EDGAR's company tickers JSON (TICKER to CIK).

Potential new join key for review: `MPID` (Market Participant Identifier). Entity type: broker_dealer_or_market_participant. Pattern: 4-letter uppercase code (e.g. `GSCO`, `MLCO`). Other datasets that would use it: FINRA OTC transparency feeds, SEC Rule 605/606 reports, Nasdaq TotalView ITCH feeds.

## Access notes

Files live at `https://www.nasdaqtrader.com/dynamic/SymDir/<file>.txt`. Confirmed pulls today:

- `nasdaqlisted.txt` (~340 KB) — Nasdaq securities
- `otherlisted.txt` — NYSE / NYSE American / Arca / BATS / IEX securities
- `mfundslist.txt` — mutual funds and similar
- `mpidlist.txt` — market participants
- `options.txt`, `phlxoptions.csv`, `phlxstrikes.zip` — options reference
- `TradingSystemAddsDeletes.txt` — daily add/delete log

Format is pipe-delimited UTF-8 with a header row and a trailing `File Creation Time:mmddyyyyhhmm` footer line that must be stripped before parsing. Files are refreshed multiple times per trading day; the footer timestamp is the freshness check. Historic FTP at `ftp://ftp.nasdaqtrader.com/symboldirectory/` mirrors the same files for batch syncs.

Gotchas:

- The trailing `File Creation Time` line will break naive `pandas.read_csv` unless skipped (use `skipfooter=1, engine='python'`).
- Symbol punctuation differs across the three columns in `otherlisted.txt`; pick the one that matches your downstream system.
- Test issues (`Test Issue = Y`) are dummy securities used for system testing and should be filtered out for production universes.
- Financial Status codes (`D`, `E`, `Q`, `H`, `J`, `K`, `N`, plus combinations) flag deficiency / delinquency / bankruptcy / halted status; useful screening signal.

## MCP / connector notes

No existing MCP found in npm, PyPI, or GitHub for `nasdaqtrader` or `nasdaq symbol directory` as of last verification. The data is static enough that a thin loader (download, strip footer, parse pipe-delimited, cache for the trading session) is sufficient. If an MCP were built, suggested surface: `list_nasdaq_symbols`, `list_other_listed_symbols`, `lookup_symbol(ticker)`, `get_financial_status(ticker)`, `list_mutual_funds`, `get_recent_adds_deletes`. Low-value as a standalone MCP, the existing `curl + pandas` flow already meets agent needs.

## Review notes

- License: Nasdaq Trader does not publish explicit redistribution terms on the symbol directory pages, and the linked Terms page returns a 404 on the current site. The files are publicly served without auth, and downstream use across the industry treats them as freely usable reference data, but a canonical SPDX or short-name license string cannot be assigned without explicit confirmation. Set `license: unknown` pending review.
- Potential new canonical join key for review: `MPID` (Market Participant Identifier). 4-letter uppercase broker/dealer code. Would also be exposed by FINRA OTC feeds, SEC Rule 605/606 reports, and Nasdaq market-data products.
- Source-internal IDs (`NASDAQ_SYMBOL`, `ACT_SYMBOL`, `CQS_SYMBOL`, `MPID`) are listed in `primary_keys`; only `TICKER` is in `join_keys`. Confirm whether the three ticker-symbol variants should be folded into one `TICKER` field or surfaced separately.
