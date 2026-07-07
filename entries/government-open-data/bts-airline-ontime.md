---
id: bts-airline-ontime
name: BTS Airline On-Time Performance
domain: government-open-data
entry_kind: event-stream
description: Flight-level on-time performance records for US domestic scheduled carriers, with scheduled/actual times, delays by cause, cancellations, and diversions.
homepage_url: https://www.transtats.bts.gov/ontime/
docs_url: https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "none published; be polite with large prezip pulls"
bulk_available: true
frequency: monthly
lag: "~2-3 months after month-end (e.g. Oct data released ~Jan)"
geography: [USA]
release_lag_days: 75
revisions_possible: true
pit_reconstructable: false
structure: event-log
join_keys:
  - DATE
  - US_STATE_CODE
primary_keys:
  - DOT_ID_REPORTING_AIRLINE
  - IATA_CODE_REPORTING_AIRLINE
  - ORIGIN_AIRPORT_ID
  - DEST_AIRPORT_ID
  - ORIGIN_AIRPORT_SEQ_ID
  - DEST_AIRPORT_SEQ_ID
  - FLIGHT_NUMBER_REPORTING_AIRLINE
  - TAIL_NUMBER
join_key_fields:
  - join_key: DATE
    fields: [FlightDate]
  - join_key: US_STATE_CODE
    fields: [OriginState, DestState]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - flight delay analysis
  - airline reliability benchmarking
  - airport congestion study
  - delay-cause attribution
  - route-level punctuality lookup
access_test:
  command: "curl -sfI 'https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_10.zip' -o /dev/null -w '%{http_code}\\n'"
  expected_status: 200
  expected_fields: []
last_verified: 2026-07-03
build_priority: low
---

# BTS Airline On-Time Performance

## Why this source matters

The Bureau of Transportation Statistics (BTS), part of the US Department of Transportation, publishes flight-level on-time performance records for every US domestic scheduled flight operated by carriers with at least 0.5% of domestic scheduled-service passenger revenue (17 reporting carriers). Coverage runs from 1987 to the present, refreshed monthly. Each row is one flight, with scheduled vs actual departure/arrival times, taxi-out/taxi-in, air time, delay minutes broken out by cause (carrier, weather, NAS, security, late-aircraft), plus cancellation and diversion flags. It is the canonical public record of US aviation punctuality, the same microdata behind FAA and press delay statistics, and free of charge as a US-government public-domain work. Secondary relevance to `consumer-signal` (travel-experience proxy) and `geospatial` (airport/route networks).

## Agent use cases

- flight delay analysis
- airline reliability benchmarking
- airport congestion study
- delay-cause attribution
- route-level punctuality lookup

## Join strategy

The clean canonical join is `DATE` (`FlightDate`, `yyyymmdd`) for stitching against any time-indexed source (weather, macro travel demand, fuel prices). `US_STATE_CODE` is exposed via `OriginState` / `DestState` (two-letter USPS abbreviations) for state-level rollups.

The high-value identifiers for this domain, carrier codes and airport codes, are not yet in the canonical registry (see Review notes). BTS mints its own numeric IDs for carriers (`DOT_ID_Reporting_Airline`) and airports (`OriginAirportID`, `DestAirportID`, and their time-versioned `*SeqID` variants), alongside IATA-style codes (`IATA_CODE_Reporting_Airline`, `Origin`/`Dest` three-letter airport codes). These live in `primary_keys` and are the natural join surface for any airline/airport source; treat them as candidates for promotion rather than existing canonical keys.

## Access notes

No auth, no API key. Two paths:

- **Bulk (recommended):** stable prezipped monthly CSVs at `https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_YYYY_M.zip` (note the single-digit, non-zero-padded month, e.g. `..._2025_10.zip`). One zip per month, ~1M rows/year of flights, all ~110 columns. This is the fastest way to get the full microdata.
- **Web-UI query builder:** the `DL_SelectFields.aspx` page (Table 236, DB_ID 120) lets you pick specific fields, carriers, airports, and date ranges and export to CSV/Excel. Good for narrow slices; tedious and non-programmatic for bulk.

Gotchas: the prezip filenames are the only reliable programmatic handle; the `.aspx` pages are JS/form-heavy and not agent-friendly. Data are subject to restatement as carriers correct submissions, so treat recent months as provisional (`revisions_possible: true`, no point-in-time vintages). Field dictionary at the `Fields.asp` docs URL.

## MCP / connector notes

No MCP exists. Value is narrow (aviation punctuality), so low priority. A useful connector would abstract over: (1) resolving a month to the correct prezip URL and streaming/unzipping it, (2) a `query_flights` surface filtering by carrier / origin / dest / date range, (3) precomputed aggregates (on-time %, mean delay by cause) to avoid shipping millions of raw rows, (4) a carrier-code and airport-code lookup table (DOT ID <-> IATA <-> name). The main abstraction burden is the ~110-column schema and the non-obvious month-in-filename download convention.

## Review notes

Two high-value join keys are missing from `schema/join-keys.yaml`; flagging as candidates rather than inventing:

Potential new join key for review: IATA_AIRPORT_CODE
  Entity type: airport
  Pattern: `^[A-Z]{3}$` (three-letter IATA airport code; BTS `Origin`/`Dest` fields)
  Other datasets that would use it: FAA data, OpenFlights, OurAirports, any air-travel or geospatial airport source.

Potential new join key for review: DOT_AIRLINE_ID
  Entity type: air_carrier
  Pattern: numeric DOT-assigned carrier ID (BTS `DOT_ID_Reporting_Airline`); IATA carrier code (`IATA_CODE_Reporting_Airline`) is a related two-letter variant but is not unique over time.
  Other datasets that would use it: BTS T-100 segment data, Air Carrier Financial (Form 41), FAA carrier registries.

License is `US-Government-Public-Domain` (17 USC 105, US federal work); no SPDX code, canonical short name already in SCHEMA.md. No conflicts with existing entries.
