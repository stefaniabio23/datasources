---
id: wikipedia-pageviews
name: Wikipedia Pageviews API
domain: consumer-signal
description: Wikimedia REST endpoints exposing per-article and aggregate pageview counts for all Wikimedia projects, daily/monthly granularity, back to July 2015.
homepage_url: https://wikimedia.org/api/rest_v1/
docs_url: https://doc.wikimedia.org/analytics-api/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC0
rate_limit: "100 req/sec per client recommended; set a descriptive User-Agent or contact email per Wikimedia policy"
bulk_available: true
frequency: daily
lag: "24-48h for daily aggregates; monthly aggregates finalised early next month"
geography: [global]
join_keys:
  - URL
  - DATE
  - ISO_3
  - WIKIDATA_QID
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No dedicated pageviews MCP. Suggested surface: get_article_views, get_top_articles,
  get_top_by_country, get_aggregate_views, resolve_article_to_wikidata. Connector should
  handle date-range chunking, project-code normalisation (en.wikipedia vs en.wikipedia.org),
  and inject a contact User-Agent automatically.
agent_use_cases:
  - attention measurement for public events
  - trend detection across topics or people
  - cross-language interest comparison
  - traffic-weighted entity prioritisation
  - news-cycle decay analysis
access_test:
  command: "curl -sf -A 'api-dataset-directory (contact@example.org)' 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/Albert_Einstein/daily/20240101/20240107'"
  expected_status: 200
  expected_fields: [project, article, granularity, timestamp, access, agent, views]
last_verified: 2026-06-08
build_priority: medium
---

# Wikipedia Pageviews API

## Why this source matters

Wikimedia exposes article-level reader traffic for every Wikipedia (and sister-project) page as a free, no-auth REST API backed by the Analytics Query Service. It is the cleanest public proxy for global attention on people, organisations, products, places, and concepts, with daily granularity back to July 2015 and 300+ language editions. For consumer-signal work it complements Google Trends (search intent) and GDELT (news volume) by capturing post-click reader behaviour rather than query interest. Run by the Wikimedia Foundation; data and code released CC0 / CC BY-SA.

## Agent use cases

- attention measurement for public events
- trend detection across topics or people
- cross-language interest comparison
- traffic-weighted entity prioritisation
- news-cycle decay analysis

## Join strategy

The native key is the article URL slug per project (e.g. `en.wikipedia.org/wiki/Albert_Einstein`), captured as canonical `URL`. Every observation carries a `DATE` (daily timestamps, ISO-able). The `top-by-country` and `top-per-country` endpoints add ISO 3166-1 alpha-2 country codes; map to `ISO_3` via lookup, flagged below. Article slugs round-trip cleanly to `WIKIDATA_QID` via the MediaWiki action API (`action=wbgetentities&sites=enwiki&titles=Albert_Einstein`), making Wikidata the recommended bridge for joining pageviews against any non-Wikipedia identifier (GTIN, CIK, NCT_ID, etc.). Pair with OpenAlex for scholarly attention overlays, GDELT for news-driven spike attribution, and Google Trends for query-vs-readership divergence.

## Access notes

Base URL: `https://wikimedia.org/api/rest_v1/metrics/pageviews/`. Primary endpoints:

- `per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}` — single article time series
- `aggregate/{project}/{access}/{agent}/{granularity}/{start}/{end}` — project-wide totals
- `top/{project}/{access}/{year}/{month}/{day}` — top 1000 articles for a day or month
- `top-by-country/{project}/{access}/{year}/{month}` — top countries by views
- `top-per-country/{country}/{access}/{year}/{month}/{day}` — top articles per country

`{access}` ∈ `all-access | desktop | mobile-app | mobile-web`. `{agent}` ∈ `all-agents | user | spider | automated`. No auth, but Wikimedia asks every client to send a descriptive `User-Agent` with a contact email and stay under ~100 req/sec; aggressive clients get rate-limited or blocked. Article titles are case-sensitive and URL-encoded; underscores replace spaces. For bulk work, raw hourly dumps live at `https://dumps.wikimedia.org/other/pageviews/` (gzip, ~50 MB/hour) and are cheaper than paginating the API for multi-year backfills.

## MCP / connector notes

No dedicated MCP exists. Several general Wikipedia MCPs wrap article text but ignore the analytics endpoints. Suggested surface: `get_article_views(project, article, start, end, granularity)`, `get_top_articles(project, date)`, `get_top_by_country(project, year, month)`, `get_aggregate_views(project, start, end)`, `resolve_article_to_wikidata(project, article)`. The connector must abstract over: project-code normalisation (`en.wikipedia` vs `en.wikipedia.org`), date-range chunking past the API's per-call limits, retry on 429, automatic User-Agent injection, and bot-vs-human disambiguation via the `agent` parameter (`user` excludes spiders, which materially changes signal quality).

## Review notes

Potential new join key for review: `WIKIPEDIA_ARTICLE`
  Entity type: wikipedia_article (project + title pair)
  Pattern: `^[a-z-]+\.wikipedia\.org/wiki/.+$` or composite `{project}:{title}`
  Other datasets that would use it: Wikidata, DBpedia, Wikipedia Clickstream, ORES quality scores, future Wikimedia analytics entries.

Country codes returned by the `top-by-country` and `top-per-country` endpoints are ISO 3166-1 alpha-2; the registry only defines `ISO_3` (alpha-3). Worth deciding whether to add `ISO_2` or rely on consumer-side mapping.
