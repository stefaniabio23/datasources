---
id: open-meteo
name: Open-Meteo
domain: geospatial
entry_kind: time-series
description: Free weather, climate, marine, air-quality, and historical-reanalysis API aggregating 30+ national weather models (ECMWF, NOAA GFS, DWD ICON, JMA, MeteoFrance) at 1-11 km global resolution, queried by latitude/longitude with no API key.
homepage_url: https://open-meteo.com/
docs_url: https://open-meteo.com/en/docs
type:
  - rest-api
auth_required: none
cost: free-non-commercial
license: CC-BY-4.0
rate_limit: "non-commercial free tier: 600 calls/min, 5,000 calls/hour, 10,000 calls/day per provider; unlimited on paid tiers"
bulk_available: false
frequency: "forecast updated hourly to 6-hourly depending on model; ERA5 reanalysis updated daily with ~5 day lag; historical-forecast archive continuous since 2021"
lag: "minutes for current forecast; ~5 days for ERA5 historical; ~2 days for historical-forecast archive"
geography: [global]
join_keys:
  - ISO_2
  - DATE
primary_keys: []
join_key_fields:
  - join_key: ISO_2
    fields: [country_code]
  - join_key: DATE
    fields: [time, hourly.time, daily.time, current.time]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cmer81/open-meteo-mcp
  - github.com/isdaniel/mcp_weather_server
  - github.com/gbrigandi/mcp-server-openmeteo
  - github.com/JeremyMorgan/Weather-MCP-Server
  - github.com/windsornguyen/open-meteo-mcp
mcp_notes: >
  No official Open-Meteo MCP. Several community implementations cover overlapping
  but uneven surfaces; cmer81/open-meteo-mcp is the broadest (forecast, archive,
  air-quality, marine, elevation, geocoding, DWD ICON). Most wrappers only expose
  the forecast endpoint; agents needing climate-change, ensemble, flood, or
  satellite-radiation will hit gaps.
agent_use_cases:
  - point-location weather forecast (hourly/daily)
  - historical weather reconstruction via ERA5 reanalysis (1940-present)
  - marine and air-quality conditions for a coordinate
  - geocoding place names to lat/lon
  - elevation lookup for a coordinate
access_test:
  command: "curl -sf 'https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m&hourly=temperature_2m&forecast_days=1'"
  expected_status: 200
  expected_fields: [latitude, longitude, current, hourly, hourly_units]
last_verified: 2026-06-09
build_priority: medium
---

# Open-Meteo

## Why this source matters

Open-Meteo aggregates 30+ national weather models (ECMWF IFS, NOAA GFS/HRRR, DWD ICON, JMA, MeteoFrance AROME, MetNo) and ERA5 reanalysis into a single keyless JSON API queryable by latitude/longitude. The same surface covers current conditions, hourly and daily forecasts, climate-change projections (CMIP6 downscaled to 10 km), marine, air quality, flood, and historical weather back to 1940. Run by Patrick Zippenfenig (Bremen, Germany) as an open-source project, server code is AGPL-3.0, data is CC-BY-4.0. Primary domain is `geospatial`; secondary utility for `public-health` (air-quality joins) and any agent doing location-conditioned analysis (retail demand, agriculture, energy load, insurance). The keyless free tier and high model diversity make it the default substitute for OpenWeatherMap, Visual Crossing, and Weather.com APIs in non-commercial workflows.

## Agent use cases

- point-location weather forecast (hourly/daily)
- historical weather reconstruction via ERA5 reanalysis (1940-present)
- marine and air-quality conditions for a coordinate
- geocoding place names to lat/lon
- elevation lookup for a coordinate

## Join strategy

Open-Meteo is keyed on geographic coordinates and time, not on opaque entity IDs. Cross-source joining happens via two canonical keys:

- `DATE` (ISO 8601, returned as `time` arrays on hourly/daily/current blocks).
- `ISO_2` (returned by the geocoding endpoint as `country_code`; forecast/archive endpoints do not return country codes).

Joining at the place level requires the agent to first resolve a name or boundary to a coordinate (via Open-Meteo's geocoding endpoint, Nominatim, or GeoNames), then call the data endpoint with that lat/lon. There is no native organisation, station, or administrative identifier; pair with OpenStreetMap (`OSM_ID`) or Wikidata (`WIKIDATA_QID`) when joining weather to specific named locations.

Open-Meteo mints no primary keys of its own. Each response is identified solely by the request tuple (`latitude`, `longitude`, `model`, time range).

## Access notes

**Base URLs** vary by endpoint:

- Forecast: `https://api.open-meteo.com/v1/forecast`
- Historical archive (ERA5, 1940-present): `https://archive-api.open-meteo.com/v1/archive`
- Historical-forecast (continuous since 2021): `https://historical-forecast-api.open-meteo.com/v1/forecast`
- Marine: `https://marine-api.open-meteo.com/v1/marine`
- Air quality: `https://air-quality-api.open-meteo.com/v1/air-quality`
- Climate change: `https://climate-api.open-meteo.com/v1/climate`
- Ensemble: `https://ensemble-api.open-meteo.com/v1/ensemble`
- Flood: `https://flood-api.open-meteo.com/v1/flood`
- Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
- Elevation: `https://api.open-meteo.com/v1/elevation`

Mandatory params on data endpoints: `latitude`, `longitude`, and at least one of `hourly`, `daily`, or `current` specifying which variables to return. Format defaults to JSON; CSV and XLSX available via `?format=`. Time zones via `?timezone=auto` (uses coordinate) or IANA name.

No auth, no signup, no API key. Free tier caps: 600 calls/min, 5,000 calls/hour, 10,000 calls/day per provider IP. The 10K daily ceiling is per provider IP, so distributed clients share the budget. Abuse triggers silent IP blocking. For commercial use or higher volumes, swap base host to `customer-api.open-meteo.com` and pass `&apikey=` (Standard, Professional, Enterprise tiers).

No bulk download path; the archive endpoint covers historical needs by query. For region-wide historical extraction, batch by tiling coordinates. ERA5 lag is ~5 days.

Attribution: data is CC-BY-4.0; cite "Weather data by Open-Meteo.com" or equivalent. Underlying model providers (ECMWF, NOAA, DWD, etc.) have their own terms preserved through Open-Meteo's CC-BY licensing.

## MCP / connector notes

No official Open-Meteo MCP exists; several community wrappers cover overlapping pieces:

- `cmer81/open-meteo-mcp` is the broadest surface: forecast, archive, air-quality, marine, elevation, geocoding, DWD ICON.
- `isdaniel/mcp_weather_server` (Python, supports stdio/SSE/streamable-HTTP transports) and `gbrigandi/mcp-server-openmeteo` (Rust) wrap the core forecast endpoint cleanly.
- `JeremyMorgan/Weather-MCP-Server` and `windsornguyen/open-meteo-mcp` are smaller forecast-only wrappers.

None of the community MCPs covers the climate-change (CMIP6), ensemble, satellite-radiation, or flood endpoints comprehensively. A consolidated MCP should expose one tool per logical surface (`forecast`, `archive`, `air_quality`, `marine`, `climate_projection`, `flood`, `geocode`, `elevation`), normalise the timezone handling, and pre-validate variable names against the (very large) per-endpoint variable lists. Rate-limit enforcement (10K/day shared across the connector) belongs in the MCP, not the tool layer.

## Review notes

- License is unambiguously CC-BY-4.0 for data; server code is AGPL-3.0 (separate, not captured in YAML).
- Cost recorded as `free-non-commercial`. Free tier is keyless and uncapped on signup but limited to non-commercial use per the terms; commercial use requires a paid subscription. This matches the existing enum value; no schema change needed.
- `primary_keys` is empty: Open-Meteo mints no source-native identifiers. All addressing is by (lat, lon, time, model) tuples. Confirmed against schema (empty array is valid for an optional field).
- `DATE` is the time-axis join key per registry; flagged because most existing entries treat time as implicit. Worth confirming `DATE` is the right canonical for hourly/15-minutely resolutions (registry pattern is YYYY[-MM[-DD]], i.e. day-precision); sub-day timestamps may need a separate canonical key (`TIMESTAMP` or `DATETIME`) if cross-source joining at hourly resolution becomes common. Flag only, no schema edit.
- `geography: [global]` is accurate at the model level, though resolution and coverage vary (HRRR is US-only, AROME is France/Europe). The API picks the best available model per coordinate by default; agents can pin a specific model via `?models=` if needed.
- No bulk-download path: `bulk_available: false`. Historical extraction for a region requires tiled per-coordinate queries against the archive endpoint.
