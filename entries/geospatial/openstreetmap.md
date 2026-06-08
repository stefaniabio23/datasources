---
id: openstreetmap
name: OpenStreetMap
domain: geospatial
entry_kind: geospatial
description: Crowdsourced global geographic database of roads, buildings, points of interest, boundaries, and natural features, with multiple read/write APIs and weekly planet dumps.
homepage_url: https://www.openstreetmap.org/
docs_url: https://wiki.openstreetmap.org/wiki/API
type:
  - rest-api
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: ODbL-1.0
rate_limit: "OSM editing API: clients blocked if degrading service. Overpass: ~10K queries/day, 1 GB/day per IP. Nominatim: 1 req/sec, custom User-Agent required."
bulk_available: true
frequency: "Planet dump weekly (Fridays); daily/hourly/minutely diffs; Overpass minutely; Nominatim daily"
lag: "minutes for Overpass mirrors of main DB; up to a week for planet snapshot"
geography: [global]
join_keys:
  - OSM_ID
  - WIKIDATA_QID
  - WIKIPEDIA_ARTICLE
  - ISO_3
  - ISO_2
primary_keys:
  - OSM_ID
  - OSM_NODE_ID
  - OSM_WAY_ID
  - OSM_RELATION_ID
  - OSM_CHANGESET_ID
  - OSM_USER_UID
join_key_fields:
  - join_key: OSM_ID
    fields: [id, type, osm_id, osm_type]
  - join_key: WIKIDATA_QID
    fields: [tags.wikidata, extratags.wikidata]
  - join_key: WIKIPEDIA_ARTICLE
    fields: [tags.wikipedia, extratags.wikipedia]
  - join_key: ISO_3
    fields: ["tags.ISO3166-1:alpha3"]
  - join_key: ISO_2
    fields: ["tags.ISO3166-1:alpha2", address.country_code]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No official MCP. High agent value: geocoding, reverse geocoding, POI lookup, boundary
  resolution, OSM_ID resolution. Suggested surface: geocode, reverse_geocode, lookup_osm_id,
  overpass_query, get_feature_by_wikidata. MCP must abstract three distinct services
  (editing API, Overpass, Nominatim) under one connector and enforce per-service rate
  limits + required User-Agent.
agent_use_cases:
  - geocoding (address to lat/lon)
  - reverse geocoding (lat/lon to address)
  - point-of-interest lookup by tag
  - administrative boundary resolution
  - cross-source feature joins via OSM_ID or WIKIDATA_QID
access_test:
  command: "curl -sf -A 'datasources/0.1 (contact@example.com)' 'https://nominatim.openstreetmap.org/search?q=Buckingham+Palace&format=json&limit=1'"
  expected_status: 200
  expected_fields: [place_id, osm_type, osm_id, lat, lon, display_name]
last_verified: 2026-06-08
build_priority: high
---

# OpenStreetMap

## Why this source matters

Volunteer-built global geodatabase covering roads, buildings, land use, POIs, administrative boundaries, and natural features at street-level detail. Maintained by the OpenStreetMap Foundation and ~10M registered mappers. ODbL-licensed, free, and the de facto open substitute for Google Maps / HERE / TomTom for any agent that needs to resolve a place name, fetch coordinates, look up a boundary polygon, or enumerate features in a region. The data spans the `geospatial` domain primarily but underpins routing, location-tagged news, retail-location joins, and government open-data geocoding workflows.

## Agent use cases

- geocoding (address to lat/lon)
- reverse geocoding (lat/lon to address)
- point-of-interest lookup by tag
- administrative boundary resolution
- cross-source feature joins via OSM_ID or WIKIDATA_QID

## Join strategy

`OSM_ID` (node/way/relation IDs) is the canonical OSM identifier and the primary join surface for any other dataset that references OSM features. `WIKIDATA_QID` is densely tagged on OSM features via the `wikidata=*` tag and is the recommended bridge to Wikidata, Wikipedia, OpenAlex, and other cross-domain sources. `WIKIPEDIA_ARTICLE` is also widely tagged (`wikipedia=lang:Article`). `ISO_3` and `ISO_2` appear on country-level `boundary=administrative` relations via `ISO3166-1:alpha3` / `ISO3166-1:alpha2` tags.

Pair with Wikidata for entity reconciliation, Overture Maps for cross-licensed POI joins, GeoNames for hierarchical place lookups, and national open-data portals (Companies House, US Census TIGER) for administrative-boundary alignment.

## Access notes

Three distinct services, all anonymous-by-default:

- **OSM editing API v0.6** (`https://api.openstreetmap.org/api/0.6/`). Read+write, intended for editor clients (iD, JOSM). Anonymous reads work for single-element fetches; bulk reads are discouraged and clients can be blocked. Use Overpass for read workloads.
- **Overpass API** (`https://overpass-api.de/api/interpreter`). Read-only query language over the OSM database. Safe budget: <10K queries/day, <1 GB/day per IP. Set a `User-Agent` or `Referer`. Multiple public mirrors and a paid Geofabrik instance for higher quotas.
- **Nominatim** (`https://nominatim.openstreetmap.org/`). Geocoding and reverse geocoding. Hard rule: 1 req/sec, custom `User-Agent` required, no heavy or commercial use. For production, self-host Nominatim or use a commercial provider (MapTiler, LocationIQ).

For large analyses, skip the APIs entirely: planet dump at `https://planet.openstreetmap.org/` (~87 GB PBF, refreshed weekly on Fridays) or regional extracts from Geofabrik. Minutely/hourly/daily diffs available for incremental updates.

Attribution is mandatory: credit "OpenStreetMap contributors" and reference the ODbL. Derivative databases inherit ODbL share-alike obligations.

## MCP / connector notes

No official MCP server. High value for any agent doing location work: a single connector should abstract the three services (editing API for OSM_ID lookup, Overpass for tag queries, Nominatim for geocoding) behind a unified interface. Suggested surface: `geocode`, `reverse_geocode`, `lookup_osm_id`, `overpass_query`, `get_feature_by_wikidata`. The MCP must enforce per-service rate limits (especially Nominatim's 1 req/sec), inject a configured `User-Agent`, route bulk workloads to planet/Geofabrik extracts instead of the live APIs, and normalise the three response shapes (OSM XML, Overpass JSON, Nominatim JSON) into a consistent feature representation.

## Review notes

- License field uses `ODbL-1.0`. SPDX lists `ODbL-1.0`; confirmed as preferred canonical form. Documentation (wiki text) is separately CC-BY-SA 2.0, not captured in YAML; noted here.
- `OSM_ID` in the registry is described as "node, way, or relation identifier" without type prefix. Real OSM IDs are namespaced by type (e.g. `node/1`, `way/12345`, `relation/5208404`). Joining across sources may require the type prefix. Flag for potential refinement of `OSM_ID` description in `schema/join-keys.yaml`, or addition of typed variants (`OSM_NODE_ID`, `OSM_WAY_ID`, `OSM_RELATION_ID`) if cross-source ambiguity becomes a problem.
- Source-internal identifiers not in the canonical registry: `OSM_CHANGESET_ID`, `OSM_USER_UID`. Use for OSM-internal lookups only.
