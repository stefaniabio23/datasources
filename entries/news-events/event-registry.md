---
id: event-registry
name: Event Registry
domain: news-events
entry_kind: event-stream
description: Commercial news intelligence platform that ingests 150K+ global news sources in 60+ languages, clusters articles into events, and enriches with Wikidata-linked entities, sentiment, and categories.
homepage_url: https://eventregistry.org/
docs_url: https://newsapi.ai/documentation
type:
  - rest-api
auth_required: api-key-free
cost: freemium
license: proprietary-no-redistribution
rate_limit: "Token-based: 2,000 free searches; paid plans start at $90/mo for 5K tokens. 1 token per recent article search (up to 100 articles/req); 5+ tokens for historical years."
bulk_available: false
frequency: continuous
lag: "minutes from publication"
geography: [global]
join_keys:
  - WIKIDATA_QID
  - ISO_2
  - URL
  - DATE
primary_keys:
  - EVENT_URI
  - ARTICLE_URI
  - CONCEPT_URI
  - SOURCE_URI
  - CATEGORY_URI
join_key_fields:
  - join_key: WIKIDATA_QID
    fields: [concepts.wgUri, concepts.location.wikiUri]
  - join_key: URL
    fields: [url, source.uri]
  - join_key: DATE
    fields: [date, dateTime, eventDate]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Closed/paid API with a strict no-redistribution license; MCP value gated by who
  holds the key. Suggested surface: search_articles, search_events, get_event,
  get_trending_concepts, get_article_sentiment. Connector must budget tokens and
  surface remaining quota.
agent_use_cases:
  - global news monitoring
  - event clustering across sources
  - entity-linked narrative tracking
  - sentiment and category analytics
  - trending-concept discovery
access_test:
  command: "curl -sf -X POST 'https://eventregistry.org/api/v1/article/getArticles' -H 'Content-Type: application/json' -d '{\"action\":\"getArticles\",\"keyword\":\"climate\",\"articlesPage\":1,\"articlesCount\":3,\"resultType\":\"articles\",\"apiKey\":\"'${EVENT_REGISTRY_KEY}'\"}'"
  expected_status: 200
  expected_fields: [articles]
last_verified: 2026-06-08
build_priority: low
notes: "Access test not yet executed; requires ${EVENT_REGISTRY_KEY}. Anonymous calls return HTTP 401 'User is not logged in'."
---

# Event Registry

## Why this source matters

Commercial news intelligence platform built on top of the Event Registry research system (Sasa Stojanov / Jozef Stefan Institute lineage), now operated as newsapi.ai. Ingests 150K+ news sources in 60+ languages, clusters articles into events, and enriches each item with Wikidata-linked entities (people, organizations, locations), categories, sentiment, and Goldstein-style scoring. For agents that need cleaner entity resolution than GDELT or a richer commercial alternative to NewsAPI.org, this is the main paid option; the no-redistribution license caps how much of that value can be shared downstream.

## Agent use cases

- global news monitoring
- event clustering across sources
- entity-linked narrative tracking
- sentiment and category analytics
- trending-concept discovery

## Join strategy

External (registry-defined): `WIKIDATA_QID` (every concept, person, organization, and location is resolved to a Wikidata/Wikipedia URI, the strongest entity-join surface in the space), `ISO_2` (article and source country), `URL` (canonical article URL), `DATE`.

Event-Registry-internal IDs (`EVENT_URI`, `ARTICLE_URI`, `CONCEPT_URI`, `SOURCE_URI`, `CATEGORY_URI`) are intentionally outside the registry; use them for direct Event Registry lookups, not cross-source joins. Pair with GDELT for free near-real-time global coverage, with OpenAlex when an article cites scholarly work, and with Wikidata for entity disambiguation across other sources.

## Access notes

REST + Python SDK (`pip install eventregistry`). Auth is an API key passed in the JSON body (`apiKey` field) of every request to `https://eventregistry.org/api/v1/...` or `https://newsapi.ai/api/v1/...` (same backend).

Quota model is token-based, not request-rate-based:

- Free tier: 2,000 lifetime searches, evaluation-only license.
- Paid: starts at $90/mo for 5K tokens.
- Recent article search: 1 token per call (up to 100 articles / 50 events per page).
- Historical search by year: 5+ tokens, scaling with date range.
- Enrichment add-ons: language detection 0.01 tokens/doc, categorization 0.04 tokens/doc.

No bulk download surface. All access is API-mediated. Tokens do not roll over month to month. Custom data delivery (CSV, S3) is available via sales.

License gotcha: even paid users may not redistribute the data, build a competing aggregator, or republish article content without separate rights from the original publishers. The free tier is restricted to evaluation; commercial use requires a paid plan.

## MCP / connector notes

No MCP exists. Value is gated by who holds the API key and by the no-redistribution clause, hence `mcp-needed-low-value` rather than high. Suggested surface: `search_articles(keyword, concept_uri, category, source, date_range, lang)`, `search_events(keyword, concept_uri, location, date_range)`, `get_event(event_uri)`, `get_trending_concepts(category, source)`, `get_article_sentiment(article_uri)`. Connector must budget tokens (return remaining quota on every call), default to small page sizes, and warn loudly before any historical-year query.

## Review notes

- License has no SPDX code; used `proprietary-no-redistribution` as a canonical kebab-case short name. If Stephanie prefers an existing canonical (or wants to add one), flag here. `SCHEMA.md` § License conventions doesn't yet enumerate a proprietary-news-api convention; this entry may be the first of a small cluster (NewsAPI.org, Aylien, Webhose) that would benefit from one.
- Access test constructed only; requires `${EVENT_REGISTRY_KEY}`. Anonymous POST returns HTTP 401 ("User is not logged in. Unable to execute the request.").
- Event Registry exposes its own concept URIs that effectively wrap Wikipedia article titles (e.g. `http://en.wikipedia.org/wiki/Climate_change`). Mapped to `WIKIDATA_QID` via Wikidata sitelinks; the registry already has `WIKIPEDIA_ARTICLE` if a more direct join is preferred later.
