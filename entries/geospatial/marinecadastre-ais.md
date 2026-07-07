---
id: marinecadastre-ais
name: MarineCadastre AIS Vessel Traffic
domain: geospatial
entry_kind: event-stream
description: US Coast Guard Nationwide AIS vessel position broadcasts for US coastal and ocean waters, cleaned and republished as bulk CSV and GeoParquet by NOAA's MarineCadastre.
homepage_url: https://hub.marinecadastre.gov/pages/vesseltraffic
docs_url: https://github.com/ocm-marinecadastre/ais-vessel-traffic
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC0
bulk_available: true
frequency: "annual bulk CSV; experimental daily/monthly GeoParquet for 2024-2025"
lag: "months-to-a-year for annual CSV; GeoParquet products released periodically"
geography: [USA]
structure: event-log
join_keys:
  - DATE
primary_keys:
  - MMSI
  - IMO
  - CALL_SIGN
join_key_fields:
  - join_key: DATE
    fields: [BaseDateTime]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - vessel-track reconstruction
  - port-call and traffic-density analysis
  - offshore-activity monitoring
  - vessel-type spatial filtering
  - fishing-effort estimation
access_test:
  command: "curl -sfI 'https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2022/AIS_2022_01_01.zip'"
  expected_status: 200
  expected_fields: []
last_verified: 2026-07-03
build_priority: low
---

# MarineCadastre AIS Vessel Traffic

## Why this source matters

The US Coast Guard collects Automatic Identification System (AIS) broadcasts from its Nationwide AIS network, and NOAA's MarineCadastre project (a joint effort of NOAA, the Bureau of Ocean Energy Management, and the USCG Navigation Center) cleans, deduplicates, and republishes them for public use. Each record is a timestamped vessel position with speed, course, heading, and static attributes (vessel name, type, dimensions, draft). It is the authoritative free source for historical vessel movement in US coastal and ocean waters, spanning 2009 to present. Secondary relevance to `finance-markets` (commodity-flow and port-throughput signals) and `government-open-data`.

## Agent use cases

- vessel-track reconstruction
- port-call and traffic-density analysis
- offshore-activity monitoring
- vessel-type spatial filtering
- fishing-effort estimation

## Join strategy

The one canonical join key this source exposes is `DATE`, carried by the `BaseDateTime` column (a full timestamp; truncate to the ISO-8601 date to join against other time-indexed sources).

Vessel identity is carried by `MMSI`, `IMO`, and `CallSign`. None of these are in the canonical registry today, so they are recorded in `primary_keys` only. `MMSI` is the de-facto row key for a vessel within the dataset (present on every broadcast), `IMO` is the durable hull identifier (sparser, often blank for smaller craft), and `CallSign` is a weaker alternate. All three are flagged as new-join-key candidates in Review notes because they are the natural bridge to any other maritime or vessel-registry source (e.g. Equasis, ITU MARS, GFW). Spatial joins go through LAT/LON rather than a canonical key.

## Access notes

Two access paths, no auth:

- **Bulk annual CSV.** Stable, predictable URLs under `https://coast.noaa.gov/htdata/CMSP/AISDataHandler/<year>/`. Since 2015 files are one-minute-filtered daily CSVs (Zstd-compressed) for all US coastal waters; the access test HEADs the 2022-01-01 daily zip (~284 MB). Older years (2009-2014) are geodatabase format.
- **AccessAIS web UI** at `https://marinecadastre.gov/accessais/` is a map-driven custom-extract order tool (pick area + timeframe, ~2 GB order cap, delivered as zipped CSV). Good for a single region-of-interest, not for programmatic pulls.
- **Experimental GeoParquet** for 2024-2025 lives in Azure Blob storage (`https://ocmgeodatastor1.blob.core.windows.net/marinecadastre/ais2024/` for daily broadcast points, `.../aistrack/` for monthly vessel tracks). These are the most analysis-ready products and query cleanly with DuckDB, GeoPandas, or GPQ. The bare container path is not directory-listable over HTTP (returns 404); you need known blob paths or the Azure listing API.

There is no query REST API; all access is file download or the order UI. Freshness: check the latest available year directory at the bulk base URL, or the GeoParquet container for the most recent monthly track file.

## MCP / connector notes

No MCP exists. Value is moderate: the useful surface would be (1) resolve a bounding box + date range to the set of bulk/GeoParquet files that cover it, (2) stream-download and filter by MMSI or vessel type, (3) reconstruct a per-MMSI track, (4) submit an AccessAIS order. A connector must abstract over three storage layouts (legacy geodatabase, annual CSV, Azure GeoParquet) and push spatial/temporal predicates down to DuckDB against the Parquet so it does not pull hundreds of MB of CSV per query. Low audience overlap with the rest of the registry keeps this low priority.

## Review notes

Potential new join keys for review:

Potential new join key for review: MMSI
  Entity type: vessel (maritime mobile station)
  Pattern: ^[0-9]{9}$
  Other datasets that would use it: Global Fishing Watch, ITU MARS, AISHub, most AIS/vessel-tracking sources

Potential new join key for review: IMO
  Entity type: vessel (durable hull identifier, IMO ship number)
  Pattern: ^(IMO)?[0-9]{7}$
  Other datasets that would use it: Equasis, IMO GISIS, Global Fishing Watch, port-registry and P&I sources

Potential new join key for review: CALL_SIGN
  Entity type: vessel/station radio call sign
  Pattern: alphanumeric, variable length (no fixed canonical form)
  Other datasets that would use it: ITU MARS, aviation/maritime station registries; weaker than MMSI/IMO

License is unambiguous CC0 1.0 (public-domain dedication); no new short name needed.
