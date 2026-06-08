---
id: gdelt
name: GDELT (Global Database of Events, Language, and Tone)
domain: news-events
description: Open real-time event database extracting people, organizations, locations, themes, and tone from global news media in 100+ languages.
homepage_url: https://www.gdeltproject.org/
docs_url: https://www.gdeltproject.org/data.html
type:
  - rest-api
  - bulk-download
  - database
auth_required: none
cost: free
license: GDELT-Open-Data
rate_limit: "Not formally published. ~1 req/sec sustained for DOC API; bulk unmetered."
bulk_available: true
frequency: every 15 minutes
lag: "~15 minutes"
geography: [global]
join_keys:
  - ISO_3
  - DATE
  - URL
  - WIKIDATA_QID
primary_keys:
  - GLOBALEVENTID
  - GKGRECORDID
  - MENTION_IDENTIFIER
join_key_fields:
  - join_key: ISO_3
    fields: [Actor1CountryCode, Actor2CountryCode, ActionGeo_CountryCode]
  - join_key: DATE
    fields: [SQLDATE, DateAdded]
  - join_key: URL
    fields: [SOURCEURL, V2DocumentIdentifier]
  - join_key: WIKIDATA_QID
    fields: [V2EnhancedLocations, V2EnhancedPersons, V2EnhancedOrganizations]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  Multi-mode access (DOC API + bulk file feeds + BigQuery + GCS). MCP must route
  by query shape and prevent runaway BigQuery costs.
agent_use_cases:
  - geopolitical risk monitoring
  - narrative tracking
  - media attention as alpha signal
  - country-level event nowcasting
  - sentiment-by-region time series
access_test:
  command: 'curl -sf "https://api.gdeltproject.org/api/v2/doc/doc?query=climate&mode=ArtList&maxrecords=5&format=json"'
  expected_status: 200
  expected_fields: [articles]
last_verified: 2026-06-08
build_priority: high
notes: GDELT 2.0 only (2015-present); 1.0 has incompatible schema. DOC API window is 3 months recent; older history via bulk or BigQuery.
---

# GDELT (Global Database of Events, Language, and Tone)

## Why this source matters

Open real-time event database parsing news media in 100+ languages. Extracts events (Actor1 → EventCode → Actor2), themes (CAMEO), entities (people, organizations, locations), tone, and Goldstein scores for ~250M articles per year. The only free open dataset with near-real-time global news at extracted-event granularity.

The CAMEO event ontology (~300 codes) lets you slice "all PROTEST events in country X in the last 7 days" or "MATERIAL_CONFLICT initiated by USA against CHN over the year." Goldstein scores attach a -10/+10 conflict-cooperation scalar to every event.

## Agent use cases

- geopolitical risk monitoring
- narrative tracking
- media attention as alpha signal
- country-level event nowcasting
- sentiment-by-region time series

## Join strategy

External (registry-defined): `ISO_3` (Actor and event country), `DATE`, `URL` (source article), `WIKIDATA_QID` (GKG-linked entities where resolvable).

GDELT-internal IDs (`GLOBALEVENTID`, `GKGRECORDID`, `MENTION_IDENTIFIER`) and CAMEO event codes are intentionally outside the registry; use the codebook for those.

## Access notes

GDELT is deliberately multi-modal. Pick by query shape:

- **DOC 2.0 API (`api.gdeltproject.org/api/v2/doc/doc`)** — text-search + tone-filter for articles in the last 3 months. No auth, JSON/CSV/HTML output.
- **Bulk file feeds (`data.gdeltproject.org/gdeltv2/`)** — new tranche every 15 minutes (events, mentions, GKG). Master file list at `lastupdate.txt`.
- **BigQuery (`gdelt-bq:gdeltv2`)** — same data, SQL access. Best for cross-time aggregates. Watch the cost.
- **Google Cloud Storage (`gs://gdelt-open-data/`)** — bulk mirror, useful from GCP-resident compute.

Known gotchas:

- High-confidence event rows (`NumMentions > 5`, `NumSources > 3`) are far more reliable than raw event rows. Filter aggressively.
- GKG entity linking quality drops sharply outside English.
- Source URL link rot is ~15% over 5 years; snapshot URLs you care about.
- DOC API window is 3 months only; deeper history needs bulk or BigQuery.
- Effectively maintained by one researcher (Kalev Leetaru). Bus-factor is real.

## MCP / connector notes

No official MCP. Heaviest free news/events dataset. The MCP must route by query shape: small recent search → DOC API; full-tranche analysis → bulk file fetch; cross-time aggregate → BigQuery (with cost guardrails).

Suggested surface: `query_articles(query, tone_filter, country, date_range)`, `fetch_events_window(start, end)`, `query_gkg(theme, entity, location)`, `get_event(global_event_id)`, `track_actor(name, date_range)`.

## Review notes

None.
