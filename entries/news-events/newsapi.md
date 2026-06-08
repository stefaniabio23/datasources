---
id: newsapi
name: NewsAPI
domain: news-events
description: Commercial REST API aggregating current and historic news articles from 150,000+ global publisher sources across 55 countries and 14 languages.
homepage_url: https://newsapi.org/
docs_url: https://newsapi.org/docs
type:
  - rest-api
auth_required: api-key-free
cost: freemium
license: proprietary-newsapi-tos
rate_limit: "100 req/day free dev tier; 250K/mo Business ($449); 2M/mo Advanced ($1,749); unlimited Enterprise"
bulk_available: false
frequency: continuous
lag: "minutes for top headlines; varies by source for Everything endpoint"
geography: [global]
join_keys:
  - URL
  - DATE
primary_keys:
  - NEWSAPI_SOURCE_ID
join_key_fields:
  - join_key: URL
    fields: [articles.url]
  - join_key: DATE
    fields: [articles.publishedAt]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Free tier is dev-only (no staging or production), so any agent built around this needs
  a paid key for real work. Suggested surface: search_everything, get_top_headlines,
  list_sources. Most agents are better served by GDELT (free, unlimited, no commercial
  restrictions) for the same job; NewsAPI's edge is publisher coverage in the long tail
  and a cleaner article body than GDELT's event-extraction format.
agent_use_cases:
  - breaking news monitoring
  - keyword-triggered news alerts
  - publisher-specific feed pulls
  - topic search across mainstream sources
access_test:
  command: "curl -sf 'https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey=${NEWSAPI_KEY}'"
  expected_status: 200
  expected_fields: [status, totalResults, articles]
last_verified: 2026-06-08
build_priority: low
notes: "access_test not executed; requires ${NEWSAPI_KEY}. Endpoint shape confirmed via 401 response to anonymous request."
---

# NewsAPI

## Why this source matters

Commercial REST aggregator over 150,000 publisher sources covering 55 countries and 14 languages. Two endpoints: `/v2/top-headlines` (curated breaking news, filterable by country, category, source) and `/v2/everything` (full article search by keyword, date range, domain, language). The free Developer tier is hard-capped at 100 requests/day and explicitly forbidden in staging or production, so any agent that needs sustained access pays from $449/month. For most news-events workloads GDELT covers the same need at zero cost with no commercial restrictions; NewsAPI earns its slot when an agent needs structured article bodies from named mainstream publishers rather than GDELT's event-extracted records.

## Agent use cases

- breaking news monitoring
- keyword-triggered news alerts
- publisher-specific feed pulls
- topic search across mainstream sources

## Join strategy

NewsAPI exposes article `URL` as the only stable cross-source identifier, plus publication `DATE` (`publishedAt`, ISO 8601). The internal `source.id` field (e.g. `bbc-news`, `the-verge`) is a NewsAPI-curated slug, not a registry key; use it for filtering within NewsAPI but not for joins. There are no DOIs, no canonical article IDs, and no entity-level identifiers (people, organisations, locations) in the response. To enrich a NewsAPI result with structured event data, pair on `URL` with GDELT's `SOURCEURL` field or hash-match on canonicalised URL.

## Access notes

First hit: `GET https://newsapi.org/v2/top-headlines?country=us&apiKey=${NEWSAPI_KEY}`. Free key signup at `newsapi.org/register`. Response is `{status, totalResults, articles: [{source, author, title, description, url, urlToImage, publishedAt, content}]}`. The `content` field is truncated to 200 characters on all tiers below Enterprise. Historic search (`/everything`) is restricted to the last month on Developer tier; paid tiers extend to 5 years. Rate-limit responses are HTTP 429 with `code: rateLimited`; auth failures are HTTP 401 with `code: apiKeyInvalid` or `apiKeyMissing`. Terms forbid building a competing news database and republishing copyrighted article text, so any downstream agent storing results should keep snippets short and link out to the original `url`.

## MCP / connector notes

No existing MCP. Connector value is low because the use case overlaps almost entirely with GDELT (free, unlimited, MCP-eligible) and because the free tier is too constrained for production agents. If built: expose `search_everything`, `get_top_headlines`, `list_sources`, with built-in pagination (max 100 per page, max 100 pages per query on paid tiers), key rotation if multiple keys are configured, and a hard reminder that the free tier is dev-only.

## Review notes

License field uses `proprietary-newsapi-tos` because NewsAPI's terms are a custom commercial ToS with no SPDX identifier and no canonical short name in SCHEMA.md's known-cases list. Stephanie may want to either (a) add `proprietary-newsapi-tos` (or a more generic `proprietary-commercial`) to the License conventions section, or (b) pick a different convention for closed commercial APIs. Several other commercial news/finance sources likely to be added later will hit the same gap.
