---
id: faa-aspm
name: FAA Aviation System Performance Metrics (ASPM)
domain: government-open-data
entry_kind: panel
description: FAA online system reporting flight, delay, taxi-time, and airport-efficiency metrics for ~77 US ASPM airports and ~40 major ASPM carriers.
homepage_url: https://aspm.faa.gov/
docs_url: https://www.aspm.faa.gov/aspmhelp/index/Main_Page.html
type:
  - web-ui
  - scraper-required
auth_required: account-required
cost: free-with-registration
license: US-Government-Public-Domain
bulk_available: false
frequency: daily
lag: "next-day preliminary (login); public web access to Airport/City-Pair/Taxi-Time data within ~60 days after month end"
geography: [USA]
join_keys:
  - DATE
primary_keys:
  - FAA_AIRPORT_LOCID
  - ASPM_CARRIER_CODE
join_key_fields:
  - join_key: DATE
    fields: [Date, Day, Month, Year]
mcp_status: requires-scraping
mcp_maturity: none
mcp_notes: >
  No public API; access is web-UI report builder behind a login for preliminary and
  flight-level data. An MCP would need authenticated browser automation to drive the
  report forms and retrieve the emailed/exported files, or a scheduled scrape of the
  public 60-day-lag Airport/City-Pair/Taxi-Time reports.
agent_use_cases:
  - airport on-time and delay analysis
  - taxi-time (actual vs unimpeded) benchmarking
  - carrier operational performance comparison
  - city-pair demand and delay lookup
  - airport capacity and throughput monitoring
last_verified: 2026-07-03
notes: "No programmatic API; web-UI report builder only. Reports export as DBF, comma-separated, tab-separated, or fixed-length files, delivered via emailed download link. Public tier (no login) covers Airport Analysis, City Pair Analysis, and Taxi Time at ~60-day lag; preliminary next-day and Individual Flights require an account."
---

# FAA Aviation System Performance Metrics (ASPM)

## Why this source matters

ASPM is the FAA's authoritative online system for measuring how well the US National Airspace System performs. It reports flight-level and aggregated metrics for roughly 77 ASPM airports (including the Core 30 and OEP 35 subsets) and roughly 40 major "ASPM carriers", covering departures, arrivals, delays against schedule and flight plan, OOOI times (Out/Off/On/In), actual vs unimpeded taxi times, runway configuration, weather, and airport arrival/departure rates. The FAA compiles it from TFMS, ASQP, ARINC/OOOI feeds, and CountOps (which also feeds OPSNET). For an agent reasoning about US air-traffic efficiency, congestion, or airline operational quality, ASPM is the primary government source. Secondary relevance to consumer-signal (airline on-time reliability) and finance-markets (airline operational KPIs).

## Agent use cases

- airport on-time and delay analysis
- taxi-time (actual vs unimpeded) benchmarking
- carrier operational performance comparison
- city-pair demand and delay lookup
- airport capacity and throughput monitoring

## Join strategy

The only canonical registry key ASPM exposes is `DATE` (daily/monthly/yearly report granularity). Its two dominant entity axes, airport and carrier, have no canonical key in the registry yet.

- Airport is identified by FAA facility LOCID (e.g. `ATL`, `ORD`), captured here as the source-native `FAA_AIRPORT_LOCID`. This aligns with IATA/ICAO airport codes and would join to BTS T-100, OpenSky, and OpenFlights.
- Carrier is identified by an ASPM carrier code (a small ~40-member set of major US passenger carriers), captured as source-native `ASPM_CARRIER_CODE`, aligned with IATA/ICAO airline codes.

Both are strong cross-source join candidates; see Review notes for the proposed new canonical keys. Pair ASPM with BTS On-Time Performance / ASQP for carrier-reported delay causes on the same airport-carrier-date grid.

## Access notes

Web-UI only, no programmatic API. Start at `https://aspm.faa.gov/` and use the report builders (Airport Analysis, City Pair Analysis, Taxi Times, Individual Flights, APM). Reports are generated per query and returned as a downloadable file (DBF, comma-separated, tab-separated, or fixed-length), typically delivered via an emailed link.

Tiered access:

- Public (no login): Airport Analysis, City Pair Analysis, and Taxi Time data, available within ~60 days after the end of the month.
- Login required: preliminary next-day ASPM data, Individual Flights, and flight-level detail (restricted modules).

There is no bulk snapshot; each pull is a filtered query. To verify freshness without an account, run a public Airport Analysis report and confirm the most recent complete month is present (~60-day lag). No public no-auth endpoint exists, so no automated `access_test` is included.

## MCP / connector notes

No MCP exists. Because there is no API and the useful modules sit behind a login with an email-delivery step, a connector cannot be a thin REST wrapper. Two viable surfaces: (1) authenticated browser automation that fills the report forms, submits, and retrieves the exported file; (2) a scheduled scrape of the public 60-day-lag reports for airport/city-pair/taxi-time series. Suggested tools: `get_airport_metrics(locid, start, end)`, `get_city_pair(origin, dest, start, end)`, `get_taxi_times(locid, start, end)`, `list_aspm_airports()`, `list_aspm_carriers()`. The MCP must abstract over form-driven queries, the export-format choice, and the async email/download step.

## Review notes

Potential new join key for review: `AIRPORT_CODE`
  Entity type: airport
  Pattern: 3-letter IATA (`^[A-Z]{3}$`) or 4-letter ICAO (`^[A-Z]{4}$`); FAA LOCID is typically the IATA form for major US airports
  Other datasets that would use it: BTS On-Time / T-100, OpenSky, OpenFlights, FAA OPSNET, any aviation source

Potential new join key for review: `AIRLINE_CODE`
  Entity type: airline_carrier
  Pattern: 2-char IATA (`^[A-Z0-9]{2}$`) or 3-letter ICAO (`^[A-Z]{3}$`); ASPM uses its own carrier codes aligned to these
  Other datasets that would use it: BTS ASQP / On-Time, OpenSky, OpenFlights, DOT airline financial data

License: FAA-produced data is a US federal government work, treated as US public domain (`US-Government-Public-Domain`); the site publishes no explicit alternate license. Confirm no redistribution restriction on account-gated flight-level data before bulk republication.
