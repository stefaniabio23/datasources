---
id: sec-ftd
name: SEC Fails-to-Deliver Data
domain: finance-markets
entry_kind: panel
description: Semi-monthly SEC files listing aggregate fails-to-deliver share balances per US equity security by settlement date, sourced from NSCC's Continuous Net Settlement system.
homepage_url: https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data
docs_url: https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data
type:
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
bulk_available: true
frequency: semi-monthly
lag: "each half-month file is published roughly two weeks after the settlement period it covers"
geography: [USA]
join_keys:
  - CUSIP
  - TICKER
  - DATE
join_key_fields:
  - join_key: CUSIP
    fields: [CUSIP]
  - join_key: TICKER
    fields: [SYMBOL]
  - join_key: DATE
    fields: ["SETTLEMENT DATE"]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - short-squeeze and settlement-fail screening
  - market-microstructure research
  - flagging persistent delivery failures per ticker
  - joining fails to price and short-interest data
access_test:
  command: "curl -sf -A 'datasources-registry research contact@example.com' -o /tmp/cnsfails.zip 'https://www.sec.gov/files/data/fails-deliver-data/cnsfails202606a.zip'"
  expected_status: 200
  expected_fields: ["SETTLEMENT DATE", "CUSIP", "SYMBOL", "QUANTITY (FAILS)", "DESCRIPTION", "PRICE"]
last_verified: 2026-07-02
structure: panel
pit_reconstructable: true
revisions_possible: false
release_lag_days: 15
build_priority: low
---

# SEC Fails-to-Deliver Data

## Why this source matters

The SEC publishes the aggregate net balance of shares that failed to be delivered on settlement date for every US equity security, tallied across all NSCC members from the Continuous Net Settlement (CNS) system. It is the canonical public record of settlement failures, the primary quantitative input for short-squeeze narratives, naked-short-selling debate, and market-microstructure research on delivery friction. Each row is one security on one settlement date, so the corpus is a security-by-date panel. Files run back to 2004; entries before 16 September 2008 include only securities with a fails balance of at least 10,000 shares, and from that date forward every security with any nonzero fails balance is listed. Secondary relevance to corporate-registry work through the CUSIP-to-issuer mapping the description column carries.

## Agent use cases

- short-squeeze and settlement-fail screening
- market-microstructure research
- flagging persistent delivery failures per ticker
- joining fails to price and short-interest data

## Join strategy

Each row exposes three registry join keys: `CUSIP` (nine-character security id), `TICKER` (the `SYMBOL` column), and `DATE` (the `SETTLEMENT DATE` column, `YYYYMMDD`). There is no source-minted surrogate row id; the natural key is the composite of settlement date and CUSIP. Pair on `CUSIP` or `TICKER` with sec-companyfacts, openfigi, nasdaq-listings, polygon-io, or finnhub to attach issuer identity, FIGI/ISIN, and daily price/volume; align on `DATE` to overlay fails against price action or short-interest series. The `DESCRIPTION` and `PRICE` columns give a human-readable issuer name and a closing price for context but are not stable join surfaces.

## Access notes

Bulk-download only; there is no REST API. Files are semi-monthly ZIPs at the stable pattern `https://www.sec.gov/files/data/fails-deliver-data/cnsfailsYYYYMMa.zip` (`a` = first half of month, `b` = second half); each unzips to a pipe-delimited `.txt` with header `SETTLEMENT DATE|CUSIP|SYMBOL|QUANTITY (FAILS)|DESCRIPTION|PRICE`. Gotcha: SEC.gov returns HTTP 403 to default or empty User-Agent strings; you must send a descriptive `User-Agent` per SEC's automated-access policy (fair-access rate limits also apply, keep to under 10 requests/second). Verify freshness by checking for the next `a`/`b` file after the current half-month at the landing page. Values are never revised once published, so each file is a fixed vintage and point-in-time reconstruction is trivially available from the archive.

## MCP / connector notes

No MCP exists. The format is a handful of predictable ZIP URLs, so an agent can ingest it directly; connector value is modest and the audience narrow (short-selling and settlement-fail analysis). A thin connector would abstract over: enumerating the `a`/`b` file URLs across a date range, sending the required User-Agent, unzipping and parsing the pipe-delimited rows, and normalising `SETTLEMENT DATE` to ISO `DATE`. Suggested surface: `list_files(start, end)`, `get_fails(date)`, `fails_for_ticker(symbol, start, end)`, `fails_for_cusip(cusip, start, end)`.

## Review notes

None. All three supplied join-key hints (CUSIP, TICKER via the `SYMBOL` column, DATE via `SETTLEMENT DATE`) already exist in `schema/join-keys.yaml`; no new canonical keys proposed. License is the standard US federal public-domain designation (17 USC 105), recorded with the existing `US-Government-Public-Domain` short name.
