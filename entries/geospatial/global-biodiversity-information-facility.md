---
id: global-biodiversity-information-facility
name: Global Biodiversity Information Facility (GBIF)
domain: geospatial
entry_kind: mixed
description: International network and integrated infrastructure aggregating species occurrence records, taxonomic backbone, datasets, and publishing organisations from thousands of natural-history collections, surveys, and citizen-science feeds, each occurrence carrying lat/lon, eventDate, taxonomic keys, and Darwin Core fields.
homepage_url: https://www.gbif.org/
docs_url: https://techdocs.gbif.org/en/openapi/
type:
  - rest-api
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "Search endpoints throttled when load is high (HTTP 429). For workloads longer than ~15 min, use the asynchronous Occurrence Download API instead of paged search. POST/PUT/DELETE require HTTP Basic auth with a GBIF user account."
bulk_available: true
frequency: "Continuous ingestion from publishers; species backbone rebuilt periodically (months); occurrence index updated as datasets are re-crawled"
lag: "minutes to days from publisher update to appearance in the GBIF index, depending on crawl schedule"
geography: [global]
join_keys:
  - NCBI_TAXON_ID
  - WIKIDATA_QID
  - DOI
  - ORCID
  - ISO_3
  - ISO_2
  - DATE
primary_keys:
  - GBIF_OCCURRENCE_ID
  - GBIF_TAXON_KEY
  - GBIF_DATASET_KEY
  - GBIF_PUBLISHING_ORG_KEY
  - GBIF_INSTALLATION_KEY
  - GBIF_DOWNLOAD_KEY
  - DWC_OCCURRENCE_ID
join_key_fields:
  - join_key: NCBI_TAXON_ID
    fields: [identifiers.identifier]
  - join_key: WIKIDATA_QID
    fields: [identifiers.identifier]
  - join_key: DOI
    fields: [doi, citation.identifier]
  - join_key: ORCID
    fields: [recordedByIDs.value, identifiedByIDs.value]
  - join_key: ISO_3
    fields: [gbifRegion, publishingCountry]
  - join_key: ISO_2
    fields: [countryCode, publishingCountry]
  - join_key: DATE
    fields: [eventDate, year]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "@cyanheads/gbif-biodiversity-mcp-server"
  - "@pipeworx/mcp-gbif"
  - pipeworx-mcp-gbif
mcp_notes: >
  Three community Node MCPs wrap the public v1 endpoints (species, occurrence,
  dataset, publisher). No official server. Existing surfaces cover synchronous
  search well but typically do not orchestrate the asynchronous Occurrence
  Download API (predicate JSON -> download key -> poll -> fetch DwC-A) which is
  the correct path for any job over a few thousand records.
agent_use_cases:
  - species occurrence search by name, taxon, geography, or date
  - taxonomic name resolution and backbone lookup
  - dataset and publisher discovery
  - reproducible biodiversity download via citable DOI
  - cross-source joins on NCBI taxon, country, or geographic feature
access_test:
  command: "curl -sf 'https://api.gbif.org/v1/occurrence/search?limit=1'"
  expected_status: 200
  expected_fields: [offset, limit, endOfRecords, count, results]
last_verified: 2026-06-09
build_priority: high
---

# Global Biodiversity Information Facility (GBIF)

## Why this source matters

International intergovernmental network coordinated by a secretariat in Copenhagen, funded by participating countries and organisations, that aggregates georeferenced species occurrence records and the underlying taxonomic backbone from thousands of natural-history collections, monitoring schemes, environmental sequencing pipelines, and citizen-science platforms (iNaturalist, eBird, OBIS, BOLD). Every occurrence carries a `gbifID`, taxonomic keys at each rank, `decimalLatitude`/`decimalLongitude`, `eventDate`, country, basis-of-record, and the raw Darwin Core fields the publisher contributed. For any agent that needs "where has species X been observed", "what species occur in region Y", or "which datasets cover taxon Z", GBIF is the canonical entry point. Primary domain `geospatial` (lat/lon-keyed observations at planetary scale); secondary relevance to `bio-genomics` (NCBI taxon mapping, environmental DNA), `academic` (every download mints a citable DOI), and `public-health` (vector and zoonotic-host distributions).

## Agent use cases

- species occurrence search by name, taxon, geography, or date
- taxonomic name resolution and backbone lookup
- dataset and publisher discovery
- reproducible biodiversity download via citable DOI
- cross-source joins on NCBI taxon, country, or geographic feature

## Join strategy

GBIF mints its own integer keyspace: `gbifID` per occurrence, `taxonKey`/`speciesKey`/`genusKey`/... per rank in the GBIF backbone, UUIDs for `datasetKey`, `publishingOrgKey`, `installationKey`, and a `downloadKey` (plus a Crossref DOI) for every Occurrence Download. Source-publisher identifiers ride along in `occurrenceID`, `catalogNumber`, `institutionCode`, and `collectionCode`.

Canonical cross-source bridges this source exposes:

- `NCBI_TAXON_ID` appears on backbone taxa whose names map to NCBI Taxonomy, surfaced in the species record's `identifiers` array (and in the species `/identifier` endpoint). Use it to fan out from a GBIF taxon to UniProt, Ensembl, NCBI Gene, NCBI SRA, BioSample, BOLD.
- `WIKIDATA_QID` is present on a subset of backbone taxa via the same identifiers channel and is the recommended bridge to Wikipedia, Wikidata, and downstream cross-domain reconciliation.
- `DOI` is the citable identifier for every dataset (registry record's `doi`) and every Occurrence Download. Pair with OpenAlex, Crossref, and DataCite for literature citing the data.
- `ORCID` appears in the Darwin Core `recordedByIDs` and `identifiedByIDs` arrays when publishers supply it; pair with OpenAlex and ORCID for researcher-level joins.
- `ISO_3` / `ISO_2`: occurrences carry `countryCode` (ISO 3166-1 alpha-2); the registry surfaces `publishingCountry`. Pair with World Bank, OECD, national open-data portals.
- `DATE`: `eventDate` is ISO 8601 (range supported); pair with climate, land-use, and surveillance time series.

Pair with NCBI Taxonomy (canonical organism keyspace), OpenStreetMap (boundary polygons for spatial joins), iNaturalist and eBird (upstream publishers for raw observation context), IUCN Red List (conservation status by species), WorldClim and Copernicus (environmental rasters for species-distribution modelling).

## Access notes

**Programmatic access:** seven public REST APIs at `https://api.gbif.org/v1/` (Maps at `v2`), JSON responses, no auth for GET. Core entry points:

- `GET /occurrence/search?...` — paged search over the occurrence index. Predicate parameters: `taxonKey`, `scientificName`, `country`, `hasCoordinate`, `decimalLatitude` range, `geometry` (WKT), `eventDate`, `basisOfRecord`, `datasetKey`, `publishingOrg`, `mediaType`. Hard cap on offset-paging at ~100K results; for anything larger, use download.
- `POST /occurrence/download/request` — asynchronous Occurrence Download. Submit a predicate JSON, poll the `downloadKey`, fetch the DwC-A (or SIMPLE_CSV / SIMPLE_PARQUET) when ready. Each download is assigned a Crossref DOI that must be cited. This is the correct path for any pipeline over a few thousand records.
- `GET /species/match?name=...` — fuzzy name match against the GBIF backbone, returns `usageKey` and full lineage with confidence score.
- `GET /species/{key}` and `/species/{key}/related|children|parents|synonyms|vernacularNames|identifier|references` — backbone traversal and cross-identifier surfacing.
- `GET /dataset/search` and `/dataset/{key}` — dataset discovery, license, DOI, publisher.
- `GET /organization/{key}`, `/installation/{key}`, `/network/{key}`, `/node/{key}` — registry graph.
- `GET /maps/v2/...` — tile rendering for spatial visualisation (vector and raster tiles).
- `GET /literature/search` — peer-reviewed papers citing GBIF data.

**Rate limiting:** search endpoints return HTTP 429 under load. There is no published per-second quota; the documented guidance is to push any workload exceeding ~15 minutes through the asynchronous Occurrence Download API instead of paged search.

**Bulk:** the canonical bulk path is the Occurrence Download API; each download yields a DwC-A archive (or simple CSV / Parquet) plus a citation DOI. GBIF also publishes the full occurrence snapshot on the AWS Open Data Registry as monthly Parquet under `s3://gbif-open-data-<region>/occurrence/<YYYY-MM-DD>/occurrence.parquet/` and the species backbone on the FTP/HTTP mirror at `https://hosted-datasets.gbif.org/`.

**Licensing:** GBIF itself does not own the data; each constituent dataset declares one of `CC0-1.0`, `CC-BY-4.0`, or `CC-BY-NC-4.0` (the only three licences GBIF accepts since 2014). Per-occurrence `license` is in every search response. Aggregate downloads inherit the most restrictive licence of any constituent dataset. Every download DOI must be cited; constituent datasets are listed in the download's citation manifest. Sensitive species (e.g. endangered taxa with poaching risk) may have coordinates obscured by the publisher.

**Auth:** unauthenticated for read; HTTP Basic with a free GBIF user account for POST/PUT/DELETE, including submitting Occurrence Downloads (anonymous downloads are technically possible via the registry but a registered account preserves download history and DOIs against the user).

## MCP / connector notes

Three community Node MCPs exist on npm: `@cyanheads/gbif-biodiversity-mcp-server`, `@pipeworx/mcp-gbif`, and `pipeworx-mcp-gbif`. They wrap the synchronous v1 endpoints (species, occurrence, dataset, publisher) and are appropriate for interactive lookups. No official GBIF server.

A purpose-built MCP would expose:

- `match_taxon(name, rank?, kingdom?)` -> `usageKey`, lineage, confidence, alternatives.
- `get_taxon(key, include=[children|synonyms|vernaculars|identifiers|references])`.
- `search_occurrences(predicates, limit, offset)` for small queries (cap enforced).
- `request_download(predicate_json, format=DWCA|SIMPLE_CSV|PARQUET)` -> `download_key`, then `poll_download(key)` and `fetch_download(key)`, returning the citable DOI alongside the payload.
- `get_dataset(key)`, `search_datasets(filters)`, `get_publisher(key)`.
- `map_tile(z, x, y, taxonKey|datasetKey, style)` for spatial rendering.

Tricky bits the MCP must abstract: the predicate-JSON grammar for Occurrence Download (more expressive than the search query string), the asynchronous download lifecycle (PREPARING -> RUNNING -> SUCCEEDED -> FILE_ERASED), the implicit citation obligation on every download DOI, and the per-dataset licence floor when an aggregate result spans heterogeneous licences.

## Review notes

- Potential new canonical join key for review: `GBIF_TAXON_KEY`
  Entity type: organism (GBIF backbone)
  Pattern: positive integer
  Other datasets that would use it: GBIF itself (issuer); cross-referenced by IUCN Red List API, Catalogue of Life (downstream), iNaturalist, eBird via dataset mappings. NCBI Taxonomy partially overlaps but uses its own integer space.

- Potential new canonical join key for review: `GBIF_OCCURRENCE_ID`
  Entity type: species occurrence record
  Pattern: positive integer (the `gbifID`)
  Other datasets that would use it: GBIF issuer; cited in literature linked via the Literature API and in derived analyses on AWS Open Data and BigQuery public datasets.

- Potential new canonical join key for review: `DWC_OCCURRENCE_ID`
  Entity type: species occurrence record (publisher-side)
  Pattern: free-form string (URN, UUID, or publisher-defined)
  Other datasets that would use it: any Darwin Core publisher reachable outside GBIF (OBIS, iDigBio, ALA, regional GBIF nodes); useful when reconciling the same record across aggregators.

- For now `NCBI_TAXON_ID`, `WIKIDATA_QID`, `DOI`, `ORCID`, `ISO_2`, `ISO_3`, and `DATE` cover the cross-source surface; the GBIF-native keys above are listed under `primary_keys` so they are not lost.

- License field set to `CC-BY-4.0` as the modal aggregate licence; constituent datasets can also be `CC0-1.0` or `CC-BY-NC-4.0`, and the per-occurrence `license` field is the authoritative answer per record. If the registry wants to capture multi-licence sources more precisely, that is a schema discussion.
