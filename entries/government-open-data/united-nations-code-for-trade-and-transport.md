---
id: united-nations-code-for-trade-and-transport
name: UN/LOCODE (United Nations Code for Trade and Transport Locations)
domain: government-open-data
entry_kind: reference-table
description: UNECE-maintained five-character code list identifying ports, airports, rail terminals, inland depots, and border crossings worldwide, used in trade and transport documentation.
homepage_url: https://unece.org/trade/cefact/unlocode-code-list-country-and-territory
docs_url: https://unece.org/trade/cefact/UNLOCODE-Download
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: ODC-PDDL-1.0
rate_limit: "none documented; static zipped CSV download"
bulk_available: true
frequency: "biannual (July and December releases)"
lag: "current edition is 2024-2 at last verification; new editions land 6-12 months after data submitted"
geography: [global]
join_keys:
  - ISO_2
  - ISO_3
primary_keys:
  - UNLOCODE
  - ISO_3166_2_SUBDIVISION
join_key_fields:
  - join_key: ISO_2
    fields: [Country, CountryCode]
  - join_key: ISO_3
    fields: []
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Static reference table; agents can load the ~116k-row CSV once and treat it as
  an in-memory lookup. A connector would only be useful inside a broader trade
  or logistics MCP that resolves shipping documents, vessel reports, or customs
  filings to canonical locations.
agent_use_cases:
  - resolve port and airport codes in shipping documents
  - normalise location names across trade and logistics datasets
  - join customs filings, AIS vessel data, and freight manifests on UNLOCODE
  - look up function flags (port, rail, airport, border crossing) for a location
  - map UNLOCODE to ISO 3166-2 subdivision for sub-national geography
access_test:
  command: "curl -sfL -o /tmp/unlocode.zip 'https://service.unece.org/trade/locode/loc242csv.zip' && unzip -l /tmp/unlocode.zip"
  expected_status: 200
  expected_fields: ["UNLOCODE CodeListPart1.csv", "SubdivisionCodes.csv"]
last_verified: 2026-06-09
build_priority: low
notes: >
  Native UNECE downloads are zipped CSV/TXT/MDB; filename version (e.g. loc242csv.zip
  = 2024 release 2) changes each cycle. DataHub mirrors a cleaned CSV snapshot at
  datahub.io/core/un-locode under ODC-PDDL-1.0 and is the easier endpoint for
  programmatic access.
---

# UN/LOCODE (United Nations Code for Trade and Transport Locations)

## Why this source matters

UN/LOCODE is the UNECE-maintained five-character code system that names every port, airport, rail terminal, inland clearance depot, postal exchange, and border crossing relevant to international trade. About 116,000 locations across 249 countries and territories, used in shipping manifests, customs declarations, AIS vessel reports, IATA cargo systems, EDIFACT messages, and most national trade-statistics pipelines. Codes pack the ISO 3166-1 alpha-2 country code into the first two characters and a three-character location identifier into the rest (e.g. `USNYC` for New York, `GBLON` for London, `SGSIN` for Singapore), which makes them a stable join surface between geographic, customs, and freight datasets that would otherwise carry inconsistent place-name strings. Sits in `government-open-data` as a UN intergovernmental reference table; secondary relevance to `geospatial` and trade-flow analysis.

## Agent use cases

- resolve port and airport codes in shipping documents
- normalise location names across trade and logistics datasets
- join customs filings, AIS vessel data, and freight manifests on UNLOCODE
- look up function flags (port, rail, airport, border crossing) for a location
- map UNLOCODE to ISO 3166-2 subdivision for sub-national geography

## Join strategy

The source-internal `UNLOCODE` (five-character code, first two are ISO 3166-1 alpha-2) is the primary identifier and the value other trade and logistics datasets reference. Recorded in `primary_keys`. From the canonical registry, the country prefix exposes `ISO_2` directly; `ISO_3` can be derived but is not stored natively. Subdivision rows are tagged with `ISO 3166-2` codes (e.g. `US-NY`), recorded as the source-internal `ISO_3166_2_SUBDIVISION` primary key.

Pair with: UN Comtrade and US Census USA Trade (port-of-entry on UNLOCODE), AIS / vessel-tracking feeds (port calls keyed by UNLOCODE), Harmonized System codes (commodity classification, joined per shipment), Companies House and SEC EDGAR for consignor/consignee firm-level joins via address, IATA airport codes (overlap with UNLOCODE function flag 4; ~720 IATA codes diverge from UN/LOCODE per Wikipedia). The IATA three-letter set is not currently a canonical join key.

`UNLOCODE` is a strong candidate for the canonical join-key registry; see Review notes.

## Access notes

Two practical access paths:

- **UNECE native zip.** `https://service.unece.org/trade/locode/loc<NNN>csv.zip` where the filename encodes year+release (e.g. `loc242csv.zip` for the 2024-2 December edition). The archive contains `UNLOCODE CodeListPart1.csv`, `Part2.csv`, `Part3.csv`, and `SubdivisionCodes.csv`. Roughly 2 MB compressed. Older editions are addressable by changing the filename. Also available in `.txt` and Microsoft Access `.mdb` from the same download index page. No auth, no rate limit, no API. Encoding is Latin-1, not UTF-8; expect mojibake on non-ASCII place names if read as UTF-8.

- **DataHub mirror.** `https://datahub.io/core/un-locode` republishes a cleaned single-CSV snapshot under ODC-PDDL-1.0, generally easier to consume programmatically. Maintained at `github.com/datasets/un-locode`. Refresh lags the UNECE release by weeks.

Freshness check: the UNECE landing page lists the current edition under "Latest version of UN/LOCODE"; new editions appear in July and December. Function column flags (`1`=port, `2`=rail terminal, `3`=road terminal, `4`=airport, `5`=postal exchange, `6`=inland clearance depot, `7`=fixed transport, `B`=border crossing) determine which transport modes each code serves.

WebFetch could not retrieve the UNECE landing pages directly (403); details corroborated against Wikipedia and the DataHub mirror's README.

## MCP / connector notes

No MCP and limited value as a standalone connector. The full dataset is ~5 MB uncompressed, rarely changes mid-cycle, and lookups are O(1) on the code string once loaded; an agent that needs UN/LOCODE resolution can keep it in memory. A higher-value design is a broader trade-and-logistics MCP combining UN/LOCODE, Harmonized System, UN Comtrade flow queries, and AIS vessel tracking, with endpoints like `resolve_locode`, `lookup_port_calls`, `walk_country_locations`, `match_iata_to_locode`. The MCP would need to abstract over (a) the biannual filename rotation, (b) Latin-1 encoding, (c) the divergence between UNECE current edition and the DataHub mirror lag.

## Review notes

Potential new join key for review: `UNLOCODE`
  Entity type: trade_or_transport_location
  Pattern: `^[A-Z]{2}[A-Z0-9]{3}$` (first two chars ISO 3166-1 alpha-2; last three letters or digits 2-9)
  Other datasets that would use it: UN Comtrade, US Census USA Trade Online, Eurostat Comext, AIS vessel feeds (MarineTraffic, AISHub), Lloyd's List, IATA cargo, EDIFACT/EANCOM messages, customs declarations data globally

Potential new join key for review: `IATA_AIRPORT_CODE`
  Entity type: airport
  Pattern: `^[A-Z]{3}$`
  Other datasets that would use it: OpenFlights, Aviationstack, Cirium, FlightAware, AviationStack; ~720 IATA codes diverge from the UN/LOCODE function-4 codes so a separate canonical key is justified if `clinical-biotech` or `consumer-signal` aviation sources land in the directory.

Potential new join key for review: `ISO_3166_2_SUBDIVISION`
  Entity type: subnational_subdivision (state, province, region)
  Pattern: `^[A-Z]{2}-[A-Z0-9]{1,3}$`
  Other datasets that would use it: World Bank subnational, OECD regions, UN Comtrade reporter subdivisions, OpenStreetMap admin level 4 boundaries, Companies House addresses.

License: `ODC-PDDL-1.0` is SPDX-valid and consistent with the DataHub mirror's declared terms. UNECE's own download page does not state an explicit licence; treat as public-domain on the strength of the DataHub maintainers' due-diligence note and UN data norms. Flag if Stephanie wants a tighter license attestation before merge.

WebFetch returned 403 on the canonical UNECE pages. Latest-edition string (`2024-2`, filename `loc242csv.zip`) and download-format set (`mdb`, `txt`, `csv`) are corroborated from the DataHub README and Wikipedia rather than directly observed; reverify against the UNECE site with a browser before relying on the version pin.
