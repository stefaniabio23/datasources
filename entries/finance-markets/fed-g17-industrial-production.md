---
id: fed-g17-industrial-production
name: Federal Reserve G.17 Industrial Production and Capacity Utilization
domain: finance-markets
entry_kind: panel
description: Monthly Federal Reserve Board indexes of US industrial production, capacity, and capacity utilization for manufacturing, mining, and electric and gas utilities, broken out by market group and NAICS industry.
homepage_url: https://www.federalreserve.gov/releases/g17/current/default.htm
docs_url: https://www.federalreserve.gov/releases/g17/g17_technical_qa.htm
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "none published; polite scraping of the DDP endpoints assumed"
bulk_available: true
frequency: monthly
lag: "released mid-month (~15-17 days) for the prior reference month; preliminary value revised over the following months, plus a full annual revision each autumn"
geography: [USA]
join_keys:
  - DATE
primary_keys:
  - FRB_G17_SERIES_NAME
  - FRB_IP_INDUSTRY_CODE
join_key_fields:
  - join_key: DATE
    fields: [TIME_PERIOD, obs.TIME_PERIOD]
mcp_status: mcp-needed-low-value
mcp_notes: >
  No dedicated MCP for the Fed's own G.17 DDP. In practice agents reach these
  series (INDPRO, TCU, and the industry breakouts) through FRED, which has
  several community MCPs, so a standalone G.17 connector is low marginal value.
  A generic Federal Reserve DDP MCP covering G.17 alongside H.15, G.19, Z.1 etc.
  would be the more sensible surface if built.
agent_use_cases:
  - industrial output tracking
  - capacity utilization monitoring
  - manufacturing cycle analysis
  - macro nowcasting features
  - industry-level output comparison
access_test:
  command: "curl -sf 'https://www.federalreserve.gov/datadownload/Output.aspx?rel=G17&filetype=zip' -o /dev/null"
  expected_status: 200
last_verified: 2026-07-03
build_priority: low
structure: panel
pit_reconstructable: false
revisions_possible: true
release_lag_days: 17
notes: "access_test executed 2026-07-03: full-release ZIP package returned HTTP 200 (~8.5 MB, application/x-zip-compressed). Per-package CSV/SDMX endpoints (Output.aspx?rel=G17&series=<hash>&filetype=csv) and the current-release text file (releases/g17/current/g17.txt, HTTP 200, ~158 KB) also confirmed reachable with no auth."
---

# Federal Reserve G.17 Industrial Production and Capacity Utilization

## Why this source matters

The G.17 is the Federal Reserve Board's monthly measure of real output for the US industrial sector: manufacturing (NAICS 31-33, plus logging and publishing), mining (NAICS 21), and electric and gas utilities (NAICS 2211-2212). It publishes the Industrial Production index (IP), capacity indexes, and capacity utilization rates, broken out by market group (final products, materials) and by NAICS industry group. IP and capacity utilization are among the most-watched US business-cycle indicators, so this is a primary macro series an agent wants for nowcasting, cycle dating, and manufacturing analysis. It sits in finance-markets as a macro series alongside FRED; its secondary character is government-open-data, since the Board publishes it as a public statistical release.

## Agent use cases

- industrial output tracking
- capacity utilization monitoring
- manufacturing cycle analysis
- macro nowcasting features
- industry-level output comparison

## Join strategy

The only canonical join key this source exposes is `DATE`: every observation is a monthly time point (`TIME_PERIOD` in the SDMX-ML output, and the date column of the DDP CSV). Join on `DATE` to pair G.17 with other monthly macro series (BLS employment, BEA GDP-by-industry, ISM PMI, EIA electricity).

The cross-sectional axis is industry, and this is where the interesting join potential lives but no registry key yet covers it. G.17 series are labelled with the NAICS code of the industry (e.g. "Machinery (NAICS = 333)", "Primary metal (NAICS = 331)"), and the Fed also carries legacy SIC-based aggregates in parallel. A `NAICS_CODE` canonical key would let G.17 join to BEA GDP-by-industry, Census County Business Patterns / Economic Census, and BLS QCEW on the industry dimension. That key is not in the registry, so it is flagged in Review notes, not invented into `join_keys`.

Source-internal identifiers stay in `primary_keys`: `FRB_G17_SERIES_NAME` (the DDP series mnemonic, e.g. an `IP.B50001.S`-style name inside the `G17/...` SDMX path) and `FRB_IP_INDUSTRY_CODE` (the Fed's own IP industry code embedded in the CSV rows). These are for direct G.17 lookups, not cross-source joins.

## Access notes

No authentication, no API key. Three no-auth paths, all confirmed reachable 2026-07-03:

1. **Full-release package (most stable programmatic URL):** `https://www.federalreserve.gov/datadownload/Output.aspx?rel=G17&filetype=zip` returns the entire release as a ZIP (~8.5 MB) containing SDMX-ML data and structure files. This is the "direct download for automated systems" URL and is the recommended endpoint for a pipeline.
2. **Custom / preformatted packages:** build a package at `https://www.federalreserve.gov/datadownload/Build.aspx?rel=G17`, then pull it via `Output.aspx?rel=G17&series=<hash>&lastobs=<n>&filetype=csv&label=include&layout=seriescolumn&type=package`. Formats are CSV, Excel, and XML (SDMX). The `series=<hash>` token identifies the package definition and can drift, so prefer the full-release ZIP for durable automation.
3. **Human-readable current release:** `https://www.federalreserve.gov/releases/g17/current/g17.txt` (and `g17.pdf`) is the full narrative + tables for the latest month; good for a quick freshness check (contains the reference-month headline, e.g. IP percent change).

Files refresh each month as part of the release. Data is heavily revised: the preliminary monthly value is restated over the following months, and an annual revision each autumn re-benchmarks against Census manufacturing data and rebases the index (next base year 2022). Treat any backtest as revisions-exposed; the Board's DDP does not serve point-in-time vintages (use FRED/ALFRED for as-of snapshots of INDPRO and TCU).

**License nuance:** Federal Reserve Board statistical releases are published as public-domain works free to reproduce with attribution. The Board is not strictly a covered "agency" under 17 USC 105, so `US-Government-Public-Domain` is applied by convention rather than statute; see Review notes.

## MCP / connector notes

No dedicated MCP. The pragmatic access path for these series is FRED (`INDPRO`, `TCU`, and the industry-level IP/capacity series), which already has several community MCPs, so a standalone G.17 connector is low marginal value. If built, the higher-leverage surface is a generic Federal Reserve DDP connector covering G.17 alongside H.15, G.19, and Z.1: `list_releases`, `list_series(release)`, `get_series(release, series, from, to, format)`, plus a `download_full_package(release)` helper. It would need to abstract the SDMX-ML structure/data split and the volatile `series=<hash>` package tokens, and expose a NAICS-tagged industry index for the cross-sectional dimension.

## Review notes

Potential new join key for review: NAICS_CODE
  Entity type: industry_classification
  Pattern: ^[0-9]{2,6}$ (2-6 digit North American Industry Classification System)
  Other datasets that would use it: BEA GDP-by-industry, Census County Business Patterns / Economic Census, BLS QCEW, SEC EDGAR (via SIC crosswalk). G.17 embeds NAICS codes in its series labels (e.g. "NAICS = 333") and also carries parallel legacy SIC aggregates, so a documented NAICS<->SIC crosswalk would be needed. This is the same NAICS_CODE candidate already flagged in the BEA entry; consolidate into one PR if adopting.

License: `US-Government-Public-Domain` is applied to Federal Reserve Board content by convention. The Board is an independent agency and its public-domain status derives from Board policy and practice rather than 17 USC 105 directly. Confirm this treatment is acceptable, or add a Fed-specific short name if the distinction matters for the registry.

Domain call: filed under finance-markets as a macro series (consistent with the FRED entry). Secondary domain government-open-data noted in the body. Flagging in case the registry prefers Fed statistical releases under government-open-data alongside BEA/BLS.
