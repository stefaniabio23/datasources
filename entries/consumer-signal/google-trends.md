---
id: google-trends
name: Google Trends
domain: consumer-signal
description: Google's public search-interest explorer, exposing normalised relative-search-volume time series and geographic breakdowns for any query, topic, or category back to 2004.
homepage_url: https://trends.google.com/trends/
docs_url: https://support.google.com/trends/
type:
  - web-ui
  - unofficial-api
auth_required: none
cost: free
license: Google-Terms-Of-Service
rate_limit: "no documented quota; unofficial pytrends users hit IP throttling after a few hundred sequential calls"
bulk_available: false
frequency: daily
lag: "near-real-time for trending searches; 2-3 day lag for stable historical series"
geography: [global]
join_keys:
  - DATE
  - ISO_2
  - ISO_3
  - WIKIDATA_QID
primary_keys:
  - KG_MID
  - GOOGLE_TRENDS_CATEGORY_ID
  - GOOGLE_TRENDS_GEO_CODE
join_key_fields:
  - join_key: DATE
    fields: [date, refresh_date, week]
  - join_key: ISO_2
    fields: [geoCode, country_code]
mcp_status: fragile-unofficial
mcp_maturity: none
mcp_notes: >
  No official API. pytrends was the de-facto Python wrapper; archived April 2025 and no
  longer maintained. Any MCP would inherit pytrends' fragility (unannounced backend
  changes, IP throttling, CAPTCHA walls). Better treated as a scraping connector with
  retry, proxy rotation, and result caching than a thin API wrapper.
agent_use_cases:
  - search-intent measurement
  - trend detection across topics or brands
  - cross-region interest comparison
  - seasonality and event-spike attribution
  - related-query discovery for content or product research
last_verified: 2026-06-08
build_priority: low
notes: "Values are normalised relative-search-volume (0-100), not raw query counts; series are not directly comparable across separate API calls without shared anchor terms."
---

# Google Trends

## Why this source matters

Google Trends is the public face of Google's search query stream, normalised to a 0-100 relative-search-volume scale and exposed by region, time window, category, and topic. It is the most-cited proxy for consumer attention and search intent, with daily granularity back to 2004 and 250+ country-level breakdowns. For agents working on brand monitoring, demand forecasting, event-spike attribution, or content research, it answers questions no other free source can ("did interest in X spike before or after Y happened?"). The catch: Google publishes no official public API, the terms forbid automated access, and the most-used unofficial wrapper (`pytrends`) was archived in April 2025. Pair with Wikipedia Pageviews for click-through validation and GDELT for news-volume context to triangulate around the missing raw counts.

## Agent use cases

- search-intent measurement
- trend detection across topics or brands
- cross-region interest comparison
- seasonality and event-spike attribution
- related-query discovery for content or product research

## Join strategy

Google Trends is identifier-poor by design. The native handles are: a query string (free text), a topic ID (Google Knowledge Graph mid like `/m/0dl567`), a category ID (Google's internal taxonomy), a geography code (ISO 3166-1 alpha-2 for countries; sub-region codes are Google-internal), and a date range.

Of those, only `DATE` and `ISO_2` map cleanly to canonical join keys; `ISO_3` is the standard fallback after alpha-2 to alpha-3 conversion. Topic IDs are Freebase / Knowledge Graph machine IDs and round-trip to `WIKIDATA_QID` via the Wikidata `P646` property ("Freebase ID"), making Wikidata the recommended bridge when joining Trends series against any other entity-keyed source.

Google-internal IDs (topic mid, category ID, sub-region code) stay out of the canonical registry; document them in connector code, not in YAML. There is no per-query identifier and no stable join across separate Trends calls unless you re-anchor with shared comparison terms.

Pair with Wikipedia Pageviews (post-click readership), GDELT (news volume), and Reddit / X first-party APIs (social conversation) to triangulate intent vs attention vs discussion.

## Access notes

**Web UI:** `https://trends.google.com/trends/explore`. Free, no auth, supports CSV download per chart. Manual for one-off lookups; rate-limited and CAPTCHA-walled at modest volume.

**Unofficial API (`pytrends`):** Python wrapper around Trends' undocumented JSON backend. Exposes `interest_over_time`, `interest_by_region`, `related_topics`, `related_queries`, `trending_searches`, `realtime_trending_searches`, `top_charts`, `historical_hourlies`, `suggestions`, `categories`. Repository archived 2025-04-17 with an open "Looking for maintainers" notice; community forks exist but none is canonical. Practical limits: ~1,400 sequential requests at four-hour windows triggers a soft block; recovery requires ~60s sleeps between calls or proxy rotation. Treat any pipeline as fragile.

**Restricted alpha (Google Trends API):** Google announced a limited-access alpha API in 2024; access is gated by application and not general-availability. Do not depend on it for public agent workflows until GA.

**BigQuery Google Trends dataset:** Google publishes `bigquery-public-data.google_trends.international_top_terms` and `top_terms` (US) with weekly snapshots of the top 25 / top 25 rising terms per region. These are not the full interest-over-time series, but they are queryable under standard BigQuery public-dataset terms (compute billed to caller's project). Useful when raw API access is too fragile.

**License:** No explicit data licence published; Google ToS apply to all access modes and explicitly prohibit "automated means to access content in violation of machine-readable instructions". Treat redistribution as restricted; cite Google Trends as the source and link back to the underlying explore URL. The BigQuery snapshot is governed by the BigQuery public-dataset terms.

## MCP / connector notes

No official MCP. `pytrends` is the only mature wrapper and is now archived, putting it in `fragile-unofficial` territory. Building an MCP around it would need to bake in: retry-with-backoff for 429s, optional proxy-pool rotation, CAPTCHA-failure detection, response caching keyed on (query, geo, timeframe, category), shared-anchor reweighting so multi-query comparisons stay on the same 0-100 scale, and graceful degradation to the BigQuery `google_trends` tables when the live backend is throttled. Suggested surface if anyone takes it on: `get_interest_over_time`, `get_interest_by_region`, `get_related_queries`, `get_trending_searches`, `resolve_topic_to_wikidata`, `query_bigquery_top_terms`. Realistic build priority is low until either Google opens the alpha API or a new community wrapper takes over from `pytrends`.

## Review notes

License field uses non-SPDX placeholder `Google-Terms-Of-Service`; not in the canonical short-name list in SCHEMA.md. Worth deciding whether to add it (Google operates several other datasets the directory will likely catalogue: YouTube, Maps Places, Knowledge Graph Search) or to inline a generic `proprietary-terms` token.

No `access_test` recorded. The web UI is not testable via `curl -sf`, the unofficial backend is rate-limited and CAPTCHA-walled, and the BigQuery dataset requires a billable Google Cloud project. Manual freshness check: visit `https://trends.google.com/trends/trendingsearches/daily` and confirm today's date appears.

Potential new join key for review: `KG_MID`
  Entity type: knowledge_graph_entity (Google / former Freebase machine ID like `/m/0dl567`)
  Pattern: `^/[a-z]/[0-9a-z_]+$`
  Other datasets that would use it: YouTube Data API, Google Knowledge Graph Search API, Wikidata (via P646), any future Google-operated source. Currently round-trippable to `WIKIDATA_QID` so adding it is optional, not blocking.
