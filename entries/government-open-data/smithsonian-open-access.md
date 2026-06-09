---
id: smithsonian-open-access
name: Smithsonian Open Access
domain: government-open-data
entry_kind: corpus
description: Smithsonian Institution's open metadata and media for 14M+ collection records across 19 museums, 9 research centers, libraries, archives, and the National Zoo, all CC0.
homepage_url: https://www.si.edu/openaccess
docs_url: https://edan.si.edu/openaccess/apidocs/
type:
  - rest-api
  - bulk-download
  - dataset-dump
auth_required: api-key-free
cost: free
license: CC0-1.0
rate_limit: "api.data.gov tier: 1,000 req/hour per key by default; DEMO_KEY is throttled"
bulk_available: true
frequency: weekly
lag: "weekly push of new/updated metadata and images to S3"
geography: [global]
join_keys:
  - WIKIDATA_QID
  - URL
primary_keys:
  - SI_EDAN_ID
  - SI_UNIT_CODE
  - SI_RECORD_ID
  - SI_GUID
join_key_fields:
  - join_key: WIKIDATA_QID
    fields:
      - "content.indexedStructured.online_media.media.idsId"
      - "content.freetext.identifier"
  - join_key: URL
    fields:
      - url
      - "content.descriptiveNonRepeating.guid"
      - "content.descriptiveNonRepeating.record_link"
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No MCP. Stable REST search over a single endpoint; bulk dump on S3. Suggested
  surface: search_objects(q, unit, type, on_view), get_object(id),
  list_units, get_image_url(id). Connector should hide the freetext vs
  indexedStructured vs descriptiveNonRepeating split.
agent_use_cases:
  - cultural-object lookup
  - museum-collection enrichment
  - image and 3D-model retrieval (CC0)
  - taxonomy / specimen metadata pulls
  - public-domain media for downstream generative work
access_test:
  command: "curl -sf 'https://api.si.edu/openaccess/api/v1.0/search?q=*&api_key=${SI_OPENACCESS_KEY}'"
  expected_status: 200
  expected_fields: [status, responseCode, response.rowCount, response.rows]
last_verified: 2026-06-09
build_priority: low
notes: "access_test executed successfully with DEMO_KEY (HTTP 200); production use needs an api.data.gov key in SI_OPENACCESS_KEY."
---

# Smithsonian Open Access

## Why this source matters

Smithsonian Open Access publishes metadata, 2-D and 3-D images, and research data for 14M+ records spanning the Institution's 19 museums, 9 research centers, libraries, archives, and the National Zoo, all released under CC0-1.0. For agents, it is the largest CC0 cultural-heritage corpus from a single US federal trust source, covering art (SAAM, Freer-Sackler, Hirshhorn), natural history specimens (NMNH), aviation and space (NASM), and Americana (NMAH). Useful as a knowledge source for cultural-object lookups, an image source for downstream generative work, and a specimen catalogue with taxonomic and geographic fields. Secondary domain: this could also sit under `geospatial` since natural-history records carry collection locations.

## Agent use cases

- cultural-object lookup
- museum-collection enrichment
- image and 3D-model retrieval (CC0)
- taxonomy / specimen metadata pulls
- public-domain media for downstream generative work

## Join strategy

Smithsonian Open Access exposes only soft join keys to external registries. The REST API mints internal identifiers used as primary keys:

- `SI_EDAN_ID` (the `id` field, e.g. `edanmdm-saam_1968.155.8`)
- `SI_UNIT_CODE` (museum or unit acronym: `NASM`, `NMNH`, `SAAM`, `NMAH`, etc.)
- `SI_RECORD_ID` (the per-unit record number)
- `SI_GUID` (persistent URL form under `n2t.net/ark:` or `edan.si.edu`)

Cross-source joins go through `URL` (the persistent GUID or `record_link`) and, where curators have added them, `WIKIDATA_QID` references on individual records. There is no consistent DOI, ORCID, or institutional identifier coverage. For natural-history specimens, taxonomic strings and collection locations are present as text but not normalised to GBIF, NCBI Taxonomy, or ISO country codes; agents needing those joins should run their own resolver.

Potential new canonical join keys flagged in Review notes.

## Access notes

**REST API:** `https://api.si.edu/openaccess/api/v1.0/`. Key endpoints: `search?q=<query>&api_key=<key>`, `content/<id>?api_key=<key>`, `category/<category>?api_key=<key>`, `terms/<category>?api_key=<key>`. Returns JSON with the shape `{status, responseCode, response: {rows[], facets, rowCount}, message}`. Each row carries `id, title, unitCode, type, url, hash, content{freetext, indexedStructured, descriptiveNonRepeating}`.

**Auth:** Register at `https://api.data.gov/signup` for a free key. `DEMO_KEY` works for casual testing but is heavily throttled.

**Rate limits:** api.data.gov default tier is 1,000 requests/hour per key (no published bursting). DEMO_KEY is capped lower.

**Bulk:** S3 dump at `s3://smithsonian-open-access/` (us-west-2). Line-delimited JSON, organised under per-unit prefixes (e.g. `metadata/edan/nasm/`, `metadata/edan/nmnh/`), with shard files keyed by content-hash prefix. `aws s3 ls --no-sign-request s3://smithsonian-open-access/` works without an AWS account. Refreshed weekly. Use bulk for anything over ~10K records; the API paginates but is slow for full-unit scans.

**Gotchas:**

- Metadata schema is heterogeneous across units. The same conceptual field (date, place, creator) may live in `freetext`, `indexedStructured`, or `descriptiveNonRepeating` depending on the source unit.
- Only a subset of records are tagged CC0; the umbrella release is CC0 for SI-owned content but a small number of records (legacy loans, donor restrictions) are excluded. The dataset filters those out by default; the `usage.access` field marks CC0 status explicitly.
- Images and 3D models are linked via `content.descriptiveNonRepeating.online_media.media[].content` URLs; resolve and dereference on the client.
- Search uses Lucene-style syntax over indexed fields, but field names differ from the response field names; consult the search-fields page in the apidocs.

## MCP / connector notes

No MCP exists. Low-medium audience (cultural-heritage + bio specimens + image sourcing) puts this below high-value priority, but the API is stable and the bulk dump is clean enough that a connector is straightforward. Suggested MCP surface:

- `search_objects(query, unit?, type?, on_view?)`
- `get_object(id)` returning a flattened view that hides the freetext/indexedStructured/descriptiveNonRepeating split
- `list_units()` to enumerate the 25+ unit codes
- `get_image_url(id, size?)` for CC0 media dereferencing
- `bulk_unit_dump(unit)` that pulls the relevant S3 shards

Tricky bits: the response shape is verbose and varies by unit; the connector should canonicalise dates, place strings, and creator names to a flat record before returning.

## Review notes

- Potential new canonical join keys for review:
  - `SI_EDAN_ID`. Entity type: `cultural_object_record`. Pattern: `^edanmdm-[a-z]+_[A-Za-z0-9._-]+$`. Other datasets that would use it: Wikidata (P10625 "Smithsonian object ID"), DPLA, Europeana cross-references. Worth registering if more GLAM (galleries, libraries, archives, museums) sources land in the directory.
  - `GBIF_OCCURRENCE_ID` would let NMNH natural-history specimens join GBIF; not currently exposed by either side in a normalised field, so out of scope until a GLAM-bio bridge dataset shows up.
- License flag: the umbrella CC0-1.0 release covers SI-owned content. A small number of records are excluded (donor restrictions, third-party loans); the API filters these by default but agents redistributing bulk data should respect the `usage.access` field per record.
- Domain placement: `government-open-data` chosen because the Smithsonian is a US federal trust instrumentality. A future `cultural-heritage` or `glam` domain (if added) would be a cleaner home alongside DPLA, Europeana, Met Open Access, and Rijksmuseum.
- The `edan.si.edu/openaccess/apidocs/` page is JS-rendered and partially unreachable to plain fetchers; doc content was reconstructed from the GitHub README, AWS Registry of Open Data entry, and a working DEMO_KEY API call. Re-verify field paths against a live response before building the MCP.
