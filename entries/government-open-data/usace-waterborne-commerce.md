---
id: usace-waterborne-commerce
name: USACE Waterborne Commerce Statistics (WCSC)
domain: government-open-data
entry_kind: mixed
description: Official US Army Corps of Engineers statistics on domestic and foreign waterborne cargo tonnage and vessel trips, by port, commodity, and waterway.
homepage_url: https://www.iwr.usace.army.mil/about/technical-centers/wcsc-waterborne-commerce-statistics-center/
docs_url: https://ndc.ops.usace.army.mil/wcsc/webpub/
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
bulk_available: true
frequency: "annual final report; monthly preliminary indicators"
lag: "monthly indicators are near-current; final annual waterborne-commerce data typically lags ~1-2 years"
geography: [USA]
structure: panel
revisions_possible: true
pit_reconstructable: false
join_keys:
  - DATE
  - US_STATE_CODE
primary_keys:
  - WCSC_PORT_CODE
  - WCSC_WATERWAY_CODE
  - WCSC_COMMODITY_CODE
  - WCSC_DOCK_ID
join_key_fields:
  - join_key: DATE
    fields: [year, month]
  - join_key: US_STATE_CODE
    fields: [state]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - port throughput lookup
  - commodity tonnage trends
  - waterway freight-volume analysis
  - trade-flow macro signal
  - infrastructure / dock characteristics
access_test:
  command: "curl -sf -A 'Mozilla/5.0' -o /dev/null -w '%{http_code}' 'https://ndc.ops.usace.army.mil/wcsc/webpub/'"
  expected_status: 200
last_verified: 2026-07-03
build_priority: low
---

# USACE Waterborne Commerce Statistics (WCSC)

## Why this source matters

The Waterborne Commerce Statistics Center (WCSC), a technical center within the US Army Corps of Engineers Institute for Water Resources (IWR), is the authoritative US source for waterborne cargo and vessel-trip statistics. It collects, processes, and archives vessel trips and cargo movements through the Oracle Waterborne System and the Lock Performance Monitoring System, then publishes monthly indicators and the annual Waterborne Commerce of the United States (WCUS) report. Coverage spans domestic and foreign tonnage by principal US port, by commodity group, and by link along the national waterway network, plus reference data on port/lock/dock facility characteristics and vessel characteristics. For an agent, this is the primary-source series behind US inland and coastal freight volumes, useful as a slow-moving macro/trade signal and as ground truth for port throughput. Secondary domain: the facility, waterway-node, and link-tonnage layers are inherently geospatial and are also redistributed as geospatial layers via BTS's National Transportation Atlas Database.

## Agent use cases

- port throughput lookup
- commodity tonnage trends
- waterway freight-volume analysis
- trade-flow macro signal
- infrastructure / dock characteristics

## Join strategy

The reliable canonical join dimensions are `DATE` (annual, with monthly preliminary indicators) and `US_STATE_CODE` for the state-level tonnage tables and the principal-ports summary. Note that WCSC labels states by name, so joining on `US_STATE_CODE` requires a state-name to USPS-abbreviation map.

Most of the analytically interesting identifiers are WCSC-native and not in the canonical registry: port codes, waterway codes, commodity classification codes (published as the Commodity Code Cross Reference and Public Domain Commodity File), and dock/facility IDs. These are the actual keys that join a tonnage row to a place or a commodity, but they are USACE-internal schemes with no cross-source registry equivalent yet. Use them for within-WCSC joins (tonnage to port name, tonnage to commodity name) via the published "Waterway and Port Codes and Names" and commodity cross-reference tables. See Review notes for new-key candidates.

## Access notes

No REST API. Access is two paths: (1) the WCSC web portal and Ports & Waterways web tools at `https://ndc.ops.usace.army.mil/wcsc/webpub/` (returns 200, no auth); (2) downloadable data files, published as databases, Excel workbooks, and text files, covering Ports Summary, Manuscript Cargo and Trips files, Commodity Code Cross Reference, Public Domain Commodity File, Waterway and Port Codes and Names, and link tonnages by commodity and direction. The IWR "Waterborne Data Analyzer and Pre-Processor" (W-DAPP) tool selects and pre-processes WCSC extracts. The main IWR landing pages block automated fetchers (HTTP 403 to bots), so verify freshness against the `ndc.ops.usace.army.mil` portal and its file-download pages rather than the marketing site. Check freshness by comparing the latest published WCUS report year and the monthly-indicator release date on the portal.

## MCP / connector notes

No MCP exists. Narrow audience (freight/logistics/trade analysts), so low priority. A connector would need to abstract over file downloads (Excel/text/DBF-style tables) and the interactive web tool rather than a clean API. Suggested surface if built: `get_port_tonnage(port_code, year)`, `get_commodity_tonnage(commodity_code, year)`, `list_ports`, `list_commodities`, `get_link_tonnages(year)`. The connector must bundle the port-code and commodity-code cross-reference tables so callers can resolve human names to WCSC codes, and must handle the annual-vs-monthly release distinction.

## Review notes

License: tagged `US-Government-Public-Domain` (17 USC 105; CISA explicitly lists WCSC as public-domain data). Not a new short name.

`US_STATE_CODE` is included in `join_keys` but the source encodes states as names, not USPS two-letter codes; a name-to-code map is required before joining. Flagging in case reviewers prefer to drop it until the field form is confirmed.

`primary_keys` names (`WCSC_PORT_CODE`, `WCSC_WATERWAY_CODE`, `WCSC_COMMODITY_CODE`, `WCSC_DOCK_ID`) and the `join_key_fields` column names (`year`, `month`, `state`) are inferred from product descriptions; exact column labels vary across the individual WCSC data files and were not confirmed against a downloaded file.

Potential new join keys for review (not invented into `join_keys`):

Potential new join key for review: WCSC_PORT_CODE
  Entity type: us_port_or_waterway_facility
  Pattern: USACE-assigned numeric port/waterway code (unconfirmed exact format)
  Other datasets that would use it: BTS NTAD waterway/port layers, USACE navigation facilities, any port-throughput source keyed to US ports

Potential new join key for review: WCSC_COMMODITY_CODE
  Entity type: commodity_class
  Pattern: USACE waterborne-commodity classification code (published in the Commodity Code Cross Reference)
  Other datasets that would use it: BTS freight commodity data, any tonnage-by-commodity source; conceptually mappable to standard commodity classifications (SCTG / Census Schedule B) but is its own scheme
