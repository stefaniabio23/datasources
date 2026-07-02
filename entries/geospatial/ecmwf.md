---
id: ecmwf
name: ECMWF (European Centre for Medium-Range Weather Forecasts)
domain: geospatial
entry_kind: mixed
description: Global numerical weather forecasts, ensemble products, and the ERA5 climate reanalysis from ECMWF, distributed via the free ECMWF Open Data feed, the Copernicus Climate Data Store API, and the licensed MARS archive.
homepage_url: https://www.ecmwf.int/en/forecasts/datasets
docs_url: https://www.ecmwf.int/en/forecasts/datasets/open-data
type:
  - rest-api
  - bulk-download
  - database
auth_required: api-key-free
cost: freemium
license: CC-BY-4.0
rate_limit: "CDS API: queued fair-use request system; ECMWF Open Data: none (static object storage)"
bulk_available: true
frequency: "operational forecasts run 2-4x daily; ERA5 updated ~daily with lag; monthly and seasonal products"
lag: "Open Data forecasts: hours after model run; ERA5: ~5 days preliminary, ~2-3 months quality-controlled"
geography: [global]
join_keys:
  - DATE
primary_keys:
  - ECMWF_PARAM_ID
  - MARS_KEYWORDS
mcp_status: mcp-needed-low-value
agent_use_cases:
  - medium-range weather forecast retrieval
  - ERA5 climate reanalysis for backtesting
  - historical weather for energy and agriculture models
  - extreme-event and seasonal analysis
  - gridded weather inputs for downstream simulation
access_test:
  command: "curl -sf 'https://www.ecmwf.int/en/forecasts/datasets/open-data' -o /dev/null"
  expected_status: 200
last_verified: 2026-07-02
build_priority: medium
notes: "access_test executed 2026-07-02 (open-data page → 200); the CDS API path (cds.climate.copernicus.eu) requires a free account + key and was not executed. One provider entry (ERA5 + operational/open forecasts + CAMS + seasonal); sub-datasets are discovered via the CDS catalogue and the ECMWF parameter database. License CC-BY-4.0 applies to the open layer; real-time operational forecasts and MARS require a separate ECMWF licence (flagged in Review notes)."
---

# ECMWF (European Centre for Medium-Range Weather Forecasts)

## Why this source matters

ECMWF runs the world's leading global numerical weather prediction system (IFS, plus the newer AIFS machine-learning model) and produces ERA5, the fifth-generation atmospheric reanalysis that is the de facto standard historical record of global weather and climate. For an agent, ECMWF is the authoritative source for both forward-looking forecasts (temperature, wind, precipitation, pressure at global grid resolution) and a decades-deep, hourly, gridded past record. This spans well beyond meteorology into `finance-markets` (energy demand, commodity and renewable-generation modelling), agriculture, insurance/catastrophe risk, and logistics. Governed by ECMWF, an intergovernmental organisation, with much of the open output delivered through the EU Copernicus programme.

## Agent use cases

- medium-range weather forecast retrieval
- ERA5 climate reanalysis for backtesting
- historical weather for energy and agriculture models
- extreme-event and seasonal analysis
- gridded weather inputs for downstream simulation

## Join strategy

The only canonical registry key ECMWF data carries cleanly is `DATE` (valid time / forecast reference time, ISO 8601). Weather data is fundamentally gridded, so the real join axis is space-time: latitude/longitude grid points plus time, and latitude/longitude is not a canonical registry identifier. To join ECMWF fields to place-based sources, resolve grid cells to administrative geographies (`ISO_3`, `NUTS`, `FIPS`) via a spatial lookup downstream; the registry does not model that. Native identifiers are ECMWF/GRIB parameter ids (`ECMWF_PARAM_ID`, e.g. 2t for 2m temperature) and MARS request keywords (class, stream, type, levtype), used to address specific fields in the archive.

## Access notes

Three tiers, increasing in access requirement:

- **ECMWF Open Data** (`data.ecmwf.int`): a free, no-auth subset of real-time IFS/AIFS forecasts under CC-BY-4.0, served as static GRIB2 from object storage. Best first path for current forecasts; a Python client (`ecmwf-opendata`) exists.
- **Copernicus Climate Data Store** (`cds.climate.copernicus.eu`): free account + API key (`cdsapi`) for ERA5 and many climate products, queued request system, output as GRIB or NetCDF. This is the standard path for reanalysis.
- **MARS** and full operational forecasts: licensed, restricted to ECMWF Member/Co-operating States and commercial licensees.

Outputs are GRIB/NetCDF, so any consumer needs a decoder (`cfgrib`, `xarray`, `eccodes`). Pin the model cycle and resolution for reproducibility.

## MCP / connector notes

No MCP exists; audience is specialised and the payloads are binary gridded formats, so it is low priority. A useful connector would wrap the two free tiers: fetch the latest Open Data forecast for a parameter/lead-time/bbox, and submit a CDS ERA5 request for a variable over a date range and region, returning decoded arrays rather than raw GRIB. It must abstract over GRIB/NetCDF decoding and the CDS async request queue.

## Review notes

- License is mixed. CC-BY-4.0 covers the open layer (ECMWF Open Data, Copernicus/ERA5 under the Licence to Use Copernicus Products); real-time operational forecasts and MARS need a separate ECMWF licence. Confirm using CC-BY-4.0 as the headline with the restriction noted here, or split.
- Only `DATE` is a canonical join key; the natural spatial key (lat/lon grid) has no registry entry. Consider whether a `GRID_CELL` / coordinate key is worth adding if more gridded-geospatial sources enter the directory.
- One provider entry per the one-entry-per-source rule; ERA5, CAMS, seasonal, and operational forecasts are sub-datasets discovered via the CDS catalogue, not modelled separately.
- Copernicus CDS is operated for the EU by ECMWF; if a dedicated Copernicus entry is later added, cross-link to avoid duplication.
