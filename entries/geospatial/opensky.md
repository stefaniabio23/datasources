---
id: opensky
name: OpenSky Network
domain: geospatial
entry_kind: event-stream
description: Crowdsourced ADS-B/Mode-S air traffic data — live aircraft state vectors and historical flight tracks from a global receiver network.
homepage_url: https://opensky-network.org/
docs_url: https://openskynetwork.github.io/opensky-api/
type:
  - rest-api
  - database
  - bulk-download
auth_required: oauth
cost: free-non-commercial
license: OpenSky-Data-License
rate_limit: "anon 400 credits/day (10s resolution); OAuth account 4000 credits/day (5s resolution); credits per query scale with bounding-box area"
bulk_available: true
frequency: real-time
lag: "seconds for live state vectors; historical flights queryable via Trino/Impala shell"
geography: [global]
structure: event-log
join_keys:
  - DATE
primary_keys:
  - ICAO24
  - CALLSIGN
  - OPENSKY_AIRPORT_ICAO
join_key_fields:
  - join_key: DATE
    fields: [time, firstSeen, lastSeen, time_position, last_contact]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/patpil/cloudflare-mcp-opensky"
mcp_notes: >
  Community/unofficial connectors only; no first-party MCP. Suggested surface: get_states_by_bbox,
  track_by_icao24, airport_arrivals, airport_departures, aircraft_track. Must abstract OAuth token
  refresh, credit budgeting, and the two-dimensional untagged state-vector row array into named fields.
agent_use_cases:
  - live aircraft tracking by bounding box
  - flight arrival/departure lookup by airport
  - aircraft trajectory reconstruction
  - airspace and congestion analysis
  - callsign-to-position resolution
access_test:
  command: "curl -sf 'https://opensky-network.org/api/states/all?lamin=45.8389&lomin=5.9962&lamax=47.8229&lomax=10.5226'"
  expected_status: 200
  expected_fields: [time, states]
last_verified: 2026-07-03
build_priority: medium
---

# OpenSky Network

## Why this source matters

OpenSky Network is a non-profit, community-run research infrastructure (hosted at the University of Bern / originating from armasuisse and academic partners) that crowdsources raw ADS-B and Mode-S transponder messages from thousands of volunteer receivers worldwide. It exposes live aircraft state vectors (position, altitude, velocity, heading, on-ground status) and historical flight records (arrivals, departures, tracks) through a free REST API for research and non-commercial use. It is the open substitute for commercial feeds like Flightradar24 or FlightAware, and it is the aviation analogue of open vessel-AIS data, hence the geospatial domain. The historical archive of raw messages back to 2013 is queryable via a Trino/Impala shell for registered research institutions.

## Agent use cases

- live aircraft tracking by bounding box
- flight arrival/departure lookup by airport
- aircraft trajectory reconstruction
- airspace and congestion analysis
- callsign-to-position resolution

## Join strategy

OpenSky exposes no scholarly/corporate identifiers; its useful cross-source keys are temporal and aviation-native. The only canonical registry key it carries is `DATE`, and only coarsely: every record is stamped with Unix-epoch second timestamps (`time`, `time_position`, `last_contact` on state vectors; `firstSeen`, `lastSeen` on flights), which must be converted to ISO 8601 before joining against date-keyed event sources.

The high-value identifiers are source-native and NOT in the registry: `ICAO24` (24-bit transponder hex address, the durable aircraft identifier), `CALLSIGN` (flight/operator callsign, 8-char, nullable and reused across flights), and the ICAO 4-letter airport codes returned as `estDepartureAirport` / `estArrivalAirport`. These are flagged below as new-key candidates because they would let an agent join OpenSky to aircraft registries (FAA/EASA registries keyed on ICAO24 hex), airline/route datasets (callsign), and airport reference tables (ICAO airport code). Until registered, use them for OpenSky-internal lookups only.

## Access notes

Hit `GET /api/states/all` first with a bounding box (`lamin,lomin,lamax,lomax`) to keep credit cost at 1; unbounded global pulls cost up to 4 credits. Anonymous access works (verified 200 above) but is capped at 400 credits/day with 10s time resolution. Register a free research account and use the OAuth2 client-credentials flow (exchange `client_id`/`client_secret` for a 30-minute Bearer token) to get 4000 credits/day and 5s resolution. Flight endpoints (`/flights/arrival`, `/flights/departure`, `/flights/aircraft`) cap the query window at 2 days; `/flights/all` at 2 hours. Note the terms: any commercial or operational/automated use (even internal, even non-profit) requires a prior written agreement with OpenSky; the free tier is research and personal non-commercial only. State-vector responses are untagged 2-D arrays (`states[i][0]` = icao24, `[1]` = callsign, `[3]` = time_position, `[5]/[6]` = lon/lat), so field positions must be mapped client-side.

## MCP / connector notes

No official first-party MCP. Community/unofficial connectors exist (e.g. a Cloudflare-hosted OpenSky MCP offering ICAO lookup and geographic search, and broader "Aviation MCP" servers that wrap OpenSky alongside METAR/TAF weather). Treat these as experimental. A robust connector should expose `get_states_by_bbox`, `track_by_icao24`, `airport_arrivals`, `airport_departures`, and `aircraft_track`, and must abstract over OAuth token refresh, the daily credit budget, bounding-box credit scaling, and the positional state-vector array (decode into named fields).

## Review notes

License short name `OpenSky-Data-License` is NOT in the SCHEMA.md known-short-names list. OpenSky uses its own "General Terms of Use & Data License Agreement" (free for academic/governmental/non-profit research; written license required for any commercial or operational use), with no SPDX code. Flagging for a canonical short-name decision.

Potential new join keys for review (all aviation-native, none in `schema/join-keys.yaml`):

Potential new join key for review: ICAO24
  Entity type: aircraft
  Pattern: ^[0-9a-f]{6}$  (24-bit transponder address, lowercase hex)
  Other datasets that would use it: FAA aircraft registry, EASA registry, ADS-B Exchange, Flightradar24, opensky aircraft-metadata database

Potential new join key for review: CALLSIGN
  Entity type: flight_callsign
  Pattern: up to 8 chars, alphanumeric (operator ICAO prefix + flight number); nullable and reused
  Other datasets that would use it: airline/route schedules, ADS-B Exchange, flight-status APIs

Potential new join key for review: AIRPORT_ICAO
  Entity type: airport
  Pattern: ^[A-Z]{4}$  (ICAO 4-letter location indicator, e.g. EDDF, KJFK)
  Other datasets that would use it: OurAirports, OpenFlights, airport reference tables, any arrivals/departures dataset

The `DATE` mapping is coarse: OpenSky timestamps are Unix-epoch seconds, not ISO 8601, and require conversion before joining. A finer `UNIX_TIMESTAMP` / `EPOCH_SECONDS` canonical key (if the registry ever wants sub-day temporal joins) is a possible future addition, flagged not invented.
