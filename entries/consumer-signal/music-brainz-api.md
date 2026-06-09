---
id: music-brainz-api
name: MusicBrainz API
domain: consumer-signal
entry_kind: knowledge-graph
description: Community-maintained open music metadata database for artists, releases, recordings, works, labels, and places, exposed via REST API and full PostgreSQL bulk dumps.
homepage_url: https://musicbrainz.org/
docs_url: https://musicbrainz.org/doc/MusicBrainz_API
type:
  - rest-api
  - bulk-download
  - database
auth_required: none
cost: free-non-commercial
license: CC0
rate_limit: "1 req/sec per IP for the public web service; descriptive User-Agent header mandatory; commercial users routed to the Live Data Feed under a paid agreement"
bulk_available: true
frequency: weekly
lag: "weekly full + incremental Postgres dumps; live web-service reflects edits within seconds"
geography: [global]
join_keys:
  - ISNI
  - ISO_2
  - WIKIDATA_QID
  - URL
primary_keys:
  - MBID_ARTIST
  - MBID_RELEASE
  - MBID_RELEASE_GROUP
  - MBID_RECORDING
  - MBID_WORK
  - MBID_LABEL
  - MBID_AREA
  - MBID_PLACE
  - MBID_EVENT
  - ISRC
  - ISWC
  - GTIN
  - DISC_ID
join_key_fields:
  - join_key: ISNI
    fields: [isnis]
  - join_key: ISO_2
    fields: [area.iso-3166-1-codes, begin-area.iso-3166-1-codes]
  - join_key: WIKIDATA_QID
    fields: ["relations[type=wikidata].url.resource"]
  - join_key: URL
    fields: ["relations[].url.resource"]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/zas/mcp-musicbrainz
  - github.com/usercourses63/musicbrainz-mcp-server
  - github.com/chrischall/musicbrainz-mcp
  - github.com/pipeworx-io/mcp-musicbrainz
  - github.com/volspan-deployments/borewit-musicbrainz-api-mcp
mcp_notes: >
  Several community MCPs cover the read surface (search, lookup, browse). No
  Anthropic-maintained server. A consolidated connector should abstract the
  1-req/sec throttle, paginate browse results, inject the descriptive User-Agent,
  expand relation edges to ISRC/ISWC/Wikidata/Discogs, and handle MBID merge
  redirects transparently.
agent_use_cases:
  - artist and release metadata lookup
  - cross-platform music identifier resolution (ISRC, ISWC, MBID, Wikidata)
  - discography and label catalogue enumeration
  - canonical track identification for audio recognition pipelines
  - music knowledge-graph construction
access_test:
  command: "curl -sf -A '${MUSICBRAINZ_USER_AGENT}' 'https://musicbrainz.org/ws/2/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3?fmt=json'"
  expected_status: 200
  expected_fields: [id, name, sort-name, type, isnis, area]
last_verified: 2026-06-09
build_priority: low
notes: "access_test executed 2026-06-09 against the Queen artist MBID; returned 200 with isnis, ipis, area.iso-3166-1-codes populated. Commercial users must move to the MetaBrainz Live Data Feed (paid)."
---

# MusicBrainz API

## Why this source matters

MusicBrainz is the open, community-maintained canonical registry of recorded music metadata, run by the non-profit MetaBrainz Foundation since 2000. It covers artists, release-groups, releases, individual recordings, works (compositions), labels, places, events, areas, instruments, and series, with stable UUID identifiers (MBIDs) and dense relation edges to ISRC, ISWC, IPI, ISNI, Discogs, Wikidata, Wikipedia, IMDb, AllMusic, and dozens more external IDs. The core catalogue is released CC0 (public domain), which makes it the practical anchor for any agent that needs to resolve a song or artist to a canonical identifier across streaming services, royalty registries, or knowledge graphs. For consumer-signal work it pairs naturally with Wikipedia pageviews, Reddit mentions, and Google Trends to attach attention metrics to a clean entity ID.

## Agent use cases

- artist and release metadata lookup
- cross-platform music identifier resolution (ISRC, ISWC, MBID, Wikidata)
- discography and label catalogue enumeration
- canonical track identification for audio recognition pipelines
- music knowledge-graph construction

## Join strategy

The native key is the **MBID**, a 36-character UUID minted per entity type (artist, release, release-group, recording, work, label, area, place, event). MBIDs are stable; merged entities redirect to the surviving MBID. Cross-source joins go through MusicBrainz's external-relation graph: every entity carries a `relations[]` array linking to other databases. Canonical join keys actually exposed:

- `ISNI`, present as the top-level `isnis[]` array on artist documents (covers both persons and organisations, complementing ORCID for non-researchers).
- `ISO_2`, returned in `area.iso-3166-1-codes[]` for country areas; map to `ISO_3` if joining against sources that use alpha-3.
- `WIKIDATA_QID`, exposed as a Wikidata URL inside the `relations[]` array (type `wikidata`); strip the URL prefix to recover the Q-id.
- `URL`, generic last-resort join via any URL relation (Discogs, Bandcamp, official site, Wikipedia article).

Source-internal identifiers that are widely cross-referenced but not in the registry: `ISRC` (recordings), `ISWC` (works), `GTIN` (release barcode), `DISC_ID` (CD TOC hash), `IPI` (composer/publisher). These belong in `primary_keys` for now and are good candidates for promotion. Pair with Spotify, Apple Music, Discogs, and Wikidata via the relation graph; pair with Wikipedia pageviews for attention overlays on canonical artist or release entities.

## Access notes

Base URL: `https://musicbrainz.org/ws/2/`. Three request modes:

- `lookup`: `/{entity}/{mbid}` fetches a single entity by MBID. Use `inc=` to expand relations, aliases, tags, ratings, ISRCs, etc.
- `browse`: `/{entity}?{linked-entity}={mbid}` lists entities linked to another (e.g. all releases by an artist).
- `search`: `/{entity}?query={lucene-query}` runs a Lucene-style full-text search.

Format selection via `fmt=json` (or default XML). No authentication is required for reads; OAuth2 or HTTP digest is only needed for write submissions and user-info reads. The **1 req/sec per IP** ceiling is hard-enforced; sustained violations get the IP blocked. A descriptive User-Agent (`AppName/Version ( contact@example.org )`) is mandatory and unauthenticated requests with the default `curl`/`python-requests` UA can be throttled or denied.

For bulk work, the **MetaBrainz datasets page** publishes weekly full PostgreSQL dumps plus daily incrementals (`mbdump.tar.bz2` and friends), restorable into a local MusicBrainz Server or replayable via `mbslave`. The core dump is CC0; derived/edit-history dumps are CC-BY-NC-SA 3.0. Commercial use of the live web service is prohibited; the MetaBrainz Foundation routes commercial users to the paid **Live Data Feed** subscription. Mirror/local-copy users avoid the 1 req/sec ceiling entirely.

## MCP / connector notes

Multiple community MCPs already cover the read surface: `zas/mcp-musicbrainz` (Python, FastMCP), `usercourses63/musicbrainz-mcp-server` (Python), `chrischall/musicbrainz-mcp` (TypeScript, also wraps cover-art and write surfaces), `pipeworx-io/mcp-musicbrainz` (TypeScript), and `volspan-deployments/borewit-musicbrainz-api-mcp` (Python wrapper around the `musicbrainz-api` Node library). No official MetaBrainz-maintained server. A consolidated MCP should abstract: the 1 req/sec throttle (queue + backoff on 503), automatic descriptive User-Agent injection, MBID merge-redirect resolution, relation-graph expansion (`inc=url-rels+release-rels+work-rels+artist-rels`), pagination over browse endpoints, and a single `resolve(identifier, type)` surface that accepts ISRC, ISWC, GTIN, Discogs ID, or Wikidata QID and returns the canonical MBID.

## Review notes

Potential new join keys for review:

- `ISRC`
  Entity type: sound_recording
  Pattern: `^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$`
  Other datasets that would use it: Spotify, Apple Music, Deezer, SoundCloud, royalty collection societies, Discogs.

- `ISWC`
  Entity type: musical_work
  Pattern: `^T-[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]$` (also seen unhyphenated `T[0-9]{10}`)
  Other datasets that would use it: ASCAP, BMI, PRS, GEMA, SACEM, MLC, any songwriter/publisher rights system.

- `MBID`
  Entity type: music_entity (artist, release, recording, work, label, area, place, event)
  Pattern: `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`
  Other datasets that would use it: ListenBrainz, AcousticBrainz, Last.fm, Cover Art Archive, BookBrainz, any future MetaBrainz-derived entry. Probably worth registering even before a second entry lands, since MBIDs are the de facto cross-app music identifier.

- `GTIN` (release barcode, EAN-13/UPC-A)
  Entity type: retail_product
  Pattern: `^[0-9]{8,14}$`
  Other datasets that would use it: GS1, Open Food Facts, retail catalogues, Discogs. Cross-domain (not music-specific).

- `IPI`
  Entity type: composer_or_publisher
  Pattern: `^[0-9]{9,11}$`
  Other datasets that would use it: CISAC societies, ASCAP, BMI, IPI database.

License is a split model: core catalogue CC0 (recorded in YAML), derived/edit-history data CC-BY-NC-SA 3.0. The single-string `license` field can't represent both; flagged for whether the schema should support a list or a primary/secondary split. Body documents the nuance.

Domain placement: MusicBrainz is borderline between `consumer-signal` (music as a media/consumer reference) and a hypothetical `cultural-heritage` or `media-metadata` domain. Filed under `consumer-signal` for now since it pairs most naturally with Wikipedia pageviews, Google Trends, and Reddit for attention/discovery workflows. Flag if a `media-metadata` domain becomes a recurring need.

`access_test` executed 2026-06-09 against the Queen artist MBID; 200 OK with `isnis`, `ipis`, `area.iso-3166-1-codes` populated.
