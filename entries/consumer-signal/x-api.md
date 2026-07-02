---
id: x-api
name: X (Twitter) API
domain: consumer-signal
entry_kind: event-stream
description: Real-time and full-archive access to X (Twitter) posts, users, search, trends, and news stories via the v2 REST API, exposed to agents through X's official hosted MCP server.
homepage_url: https://docs.x.com/x-api
docs_url: https://docs.x.com/tools/mcp
type:
  - rest-api
auth_required: oauth
cost: paid
license: X-Developer-Agreement
rate_limit: "Pay-per-use: $0.005 per post read (2M reads/month cap), $0.001 per owned read, $0.010 per user read; per-endpoint rate limits still apply; writes stricter, expect 429s"
bulk_available: false
frequency: real-time
lag: "seconds for new posts"
geography: [global]
join_keys:
  - URL
  - ISO_639_1
primary_keys:
  - TWEET_ID
  - X_USER_ID
  - X_HANDLE
  - WOEID
join_key_fields:
  - join_key: URL
    fields: [entities.urls.expanded_url, entities.urls.unwound_url]
  - join_key: ISO_639_1
    fields: [lang]
mcp_status: mcp-exists
mcp_maturity: official
mcp_package:
  - github.com/xdevplatform/xmcp
  - github.com/xdevplatform/xurl
  - https://api.x.com/mcp
mcp_notes: >
  Official X-hosted Streamable HTTP MCP at https://api.x.com/mcp, plus a
  self-hostable FastMCP server (xdevplatform/xmcp, Python 3.9+) and the xurl
  CLI/OAuth bridge (xdevplatform/xurl). Covers the full read surface (search,
  counts, timelines, mentions, trends, news) and writes (post, like, repost,
  bookmark). Streaming and webhooks are excluded. No native sentiment tool;
  sentiment is a downstream agent/LLM step on retrieved post text.
agent_use_cases:
  - topic and keyword post monitoring
  - real-time sentiment mining on brands, tickers, and events
  - post-volume time-series for a query via the counts endpoints
  - trend and news-story tracking by location
  - account timeline and mention tracking
access_test:
  command: "curl -sf -H \"Authorization: Bearer ${X_BEARER_TOKEN}\" 'https://api.x.com/2/tweets/counts/recent?query=nvidia'"
  expected_status: 200
  expected_fields: [data, meta]
last_verified: 2026-07-01
build_priority: medium
notes: "access_test constructed, not executed; requires paid X API credentials (pay-per-use, ~$0.005 per post read) and an OAuth2 app. No free tier for new signups as of 2026-02-06; legacy Basic ($200/mo) and Pro ($5,000/mo) remain only for existing subscribers."
---

# X (Twitter) API

## Why this source matters

X is the highest-velocity public source of real-time reaction to news, markets, politics, and product events, with posts surfacing minutes ahead of formal news wires. The v2 REST API exposes posts, full-text search (recent and full-archive), post-volume counts, user timelines and mentions, location trends, and curated news stories. In February 2026 X moved to pay-per-use billing and, alongside it, shipped an official hosted MCP server (`https://api.x.com/mcp`) plus a self-hostable FastMCP build, making X directly agent-addressable with per-account permissions. This is the primary consumer-signal source for fast-moving sentiment; secondary domain is `news-events` via the `getNews` / `searchNews` and trends tools.

## Agent use cases

- topic and keyword post monitoring
- real-time sentiment mining on brands, tickers, and events
- post-volume time-series for a query via the counts endpoints
- trend and news-story tracking by location
- account timeline and mention tracking

## Join strategy

X-native identifiers (`TWEET_ID`, `X_USER_ID`, `X_HANDLE`, and `WOEID` for trend locations) are the primary keys but sit outside the canonical registry; use them for X-to-X traversal (reply chains, quote graphs, author timelines), not cross-source joins.

For cross-source work the practical canonical keys are `URL` and `ISO_639_1`. Posts carry expanded outbound links in `entities.urls.expanded_url` (and `unwound_url` after redirect resolution), which join X reaction directly to news-events sources (GDELT, NewsAPI, Event Registry) and to Reddit link posts for "what did people say about this article" workflows. The `lang` field is BCP-47 (mostly ISO 639-1 two-letter, plus `und` for undetermined), so treat it as `ISO_639_1` with a fallback for non-two-letter values. Public figures and organisations can be bridged to `WIKIDATA_QID` externally, but X does not mint that ID, so it is not listed here.

## Access notes

**On the user's two asks specifically:**

- **Sentiment analysis is not a native tool.** No MCP tool or v2 endpoint returns a sentiment score. The pattern is: retrieve posts on a topic (`searchPostsRecent` for the last 7 days, `searchPostsAll` for full archive, or `getUsersMentions`), then classify sentiment downstream with the agent's own LLM. X supplies the text and metadata; the sentiment layer is yours to add.

- **Aggregate news flow configured on topics is buildable natively.** Define one query string per topic using v2 boolean operators (keywords, exact phrases, hashtags, `@mentions`, `lang:`, `-is:retweet`, `from:`). Then combine three tools: `getPostsCountsRecent` / `getPostsCountsAll` return post-volume bucketed over time for that query, giving the flow metric without reading (or paying for) individual post bodies; `searchNews` and `getNews` return curated news stories; `getTrendsByWoeid` returns what is trending in a location. A topic monitor is a saved set of queries polled against the counts endpoints for volume, `searchNews` for the news layer, and a small `searchPostsRecent` pull for representative posts to run sentiment on.

**Cost shape matters.** Billing is pay-per-use: ~$0.005 per post read (2M/month cap), $0.001 per owned read, $0.010 per user read. Reading full post bodies at scale is the expensive path; the counts endpoints are the cheap way to track topic volume because they return aggregate buckets, not post text. There is no free tier for new signups as of 2026-02-06; legacy Basic ($200/mo) and Pro ($5,000/mo) persist only for existing subscribers, Enterprise starts ~$42,000/mo.

**Auth.** OAuth 2.0 PKCE via the `xurl` bridge (caches and refreshes tokens in `~/.xurl`) for user-context actions, or an app-only bearer token for read-only. Hosted MCP needs an X developer app and a one-time OAuth flow; the self-hosted `xmcp` server needs `X_OAUTH_CONSUMER_KEY`, `X_OAUTH_CONSUMER_SECRET`, and `X_BEARER_TOKEN`.

## MCP / connector notes

Official and mature. Three components:

- **Hosted MCP** at `https://api.x.com/mcp` (Streamable HTTP), works with any MCP client (Claude, Cursor, Grok).
- **`xdevplatform/xmcp`** — self-hostable FastMCP server, Python 3.9+, exposes v2 as tools grouped as posts (`createPosts`, `getPostsById`, likers/reposters/quoters), search (`searchPostsRecent`, `searchPostsAll`, `getPostsCountsRecent`, `getPostsCountsAll`), users (`getUsersByUsername`, `getUsersPosts`, `getUsersTimeline`, `getUsersMentions`, `searchUsers`), bookmarks, trends/news (`getTrendsByWoeid`, `getTrendsPersonalizedTrends`, `getNews`, `searchNews`), DMs, and analytics (`getPostsAnalytics`, `getInsightsHistorical`). Streaming and webhooks excluded. Supports `X_API_TOOL_ALLOWLIST` to load a subset.
- **`xdevplatform/xurl`** — official CLI and stdio-to-HTTP OAuth bridge.

Gaps an integrator should abstract: no sentiment (add an LLM classification step), no filtered-stream tool (poll `searchPostsRecent` instead of a live stream), and per-call cost accounting (route pure-volume questions to the counts tools, not full post reads).

## Review notes

- **New license short name** `X-Developer-Agreement` (non-SPDX). Confirm the canonical short-name convention before publish; X's terms govern redistribution and prohibit most content storage and resale.
- `access_test` constructed only, not executed: no paid X API credentials in the entry-creation session. Re-verify the counts-recent endpoint path and pay-per-use rates against live docs before publish (pricing changed 2026-02-06 and may move again).
- X-native IDs (`TWEET_ID`, `X_USER_ID`, `X_HANDLE`, `WOEID`) flagged as primary keys; registering them as canonical is low-value unless a second X-derived source enters the directory.
- `lang` is BCP-47, not strictly ISO 639-1; mapped to `ISO_639_1` with a documented fallback. Confirm this is acceptable or whether a separate `BCP_47` key is warranted.
