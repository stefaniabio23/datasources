---
id: hacker-news
name: Hacker News API
domain: consumer-signal
description: Official Hacker News API exposing every story, comment, job post, Ask HN, Show HN, poll, and user profile as JSON via Firebase, with live update feeds and walk-the-entire-corpus access from item 1.
homepage_url: https://github.com/HackerNews/API
docs_url: https://github.com/HackerNews/API/blob/master/README.md
type:
  - rest-api
auth_required: none
cost: free
license: MIT
rate_limit: "no published limit; documentation states 'There is currently no rate limit' but expect Firebase-level throttling under abuse"
bulk_available: false
frequency: real-time
lag: "near real-time; Firebase emits change events within seconds of post/edit/vote"
geography: [global]
join_keys:
  - URL
  - DATE
primary_keys:
  - HN_ITEM_ID
  - HN_USERNAME
join_key_fields:
  - join_key: URL
    fields: [url]
  - join_key: DATE
    fields: [time, created]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/pskill9/hn-server
  - github.com/devabdultech/hn-mcp
  - github.com/rawveg/hacker-news-mcp
  - github.com/karanb192/hn-mcp
mcp_notes: >
  Multiple community MCPs exist; none official. Most wrap topstories/item lookup; karanb192/hn-mcp
  also fronts the Algolia HN Search API which the official Firebase API lacks. Suggested combined
  surface: search_stories (via Algolia), get_item, get_user, get_topstories, walk_recent_items,
  resolve_url_to_discussions.
agent_use_cases:
  - tech-community attention signal
  - launch and Show HN detection
  - founder and engineer profile lookup
  - URL discussion discovery
  - comment-thread sentiment sampling
access_test:
  command: "curl -sf 'https://hacker-news.firebaseio.com/v0/item/8863.json'"
  expected_status: 200
  expected_fields: [id, by, type, time, title, url, score, descendants]
last_verified: 2026-06-08
build_priority: medium
---

# Hacker News API

## Why this source matters

Hacker News is the dominant attention market for the tech and startup audience: an upvote on the front page reliably drives tens of thousands of pageviews and is treated by founders, VCs, and engineering leaders as a real-time signal of what their peers are reading. The official API (run by Y Combinator in partnership with Firebase, MIT-licensed) exposes every item ever posted as JSON, including stories, comments, polls, jobs, Ask HN, and Show HN, plus user profiles and live feeds. For consumer-signal work it is the cleanest free proxy for early developer-tools traction, launch reception, and technical-community sentiment; pair with `wikipedia-pageviews` for general attention and (when added) Reddit or Google Trends for broader consumer signal.

## Agent use cases

- tech-community attention signal
- launch and Show HN detection
- founder and engineer profile lookup
- URL discussion discovery
- comment-thread sentiment sampling

## Join strategy

Two canonical join keys: `URL` (every story carries the linked external URL in the `url` field, which is the natural pivot for joining a HN discussion to any other source that mentions the same page) and `DATE` (every item carries a Unix `time`, ISO-able). HN-internal identifiers (item id integer, case-sensitive `by` username) live outside the canonical registry; use them for direct HN lookups, not cross-source joins. The unofficial Algolia HN Search API (`https://hn.algolia.com/api/v1/search?query=...`) is the standard way to find discussions of a given URL or keyword without walking maxitem, and most community MCPs use it.

Potential new join keys flagged for review below: `HN_ITEM_ID` and `HN_USERNAME` would be useful if a second HN-centric source is ever added (e.g. Algolia search index, hnrankings.info), but with one HN entry they are source-internal and stay in this body.

## Access notes

Base URL: `https://hacker-news.firebaseio.com/v0/`. Primary endpoints:

- `/item/{id}.json` — single item (story, comment, job, poll, pollopt)
- `/user/{username}.json` — user profile (case-sensitive)
- `/topstories.json`, `/newstories.json`, `/beststories.json` — up to 500 ids each
- `/askstories.json`, `/showstories.json`, `/jobstories.json` — up to 200 ids each
- `/maxitem.json` — current highest item id; walk backward for full-corpus traversal
- `/updates.json` — recently changed items and profiles

No auth. The docs state there is no published rate limit, but this is Firebase-fronted: expect 429s or short bans if you hammer it. Be polite (a few req/sec, exponential backoff on errors). For real-time use, subscribe to Firebase change events on `/v0/updates` rather than polling. For backfills, walking maxitem downward is the only path: there is no official bulk dump, no S3 snapshot, and no archived JSONL. Community dumps exist on Kaggle and BigQuery (`bigquery-public-data.hacker_news`) and are the practical choice for analyses over a few hundred thousand items. Items can be edited or deleted after posting; `deleted: true` and `dead: true` flags are common in older items. Comments use parent/kids pointers for threading; reconstructing a full discussion requires recursive fetches.

## MCP / connector notes

Multiple community MCPs exist, none official. Notable: `pskill9/hn-server` (JavaScript, basic story/item endpoints), `devabdultech/hn-mcp` (JavaScript), `rawveg/hacker-news-mcp` (Python), `karanb192/hn-mcp` (TypeScript, includes Algolia search), `paabloLC/mcp-hacker-news`, `imprvhub/mcp-claude-hackernews`, `isteamhq/hackernews-mcp`, `devrelopers/hackernews-mcp` (Rust), `hungran/hyper-mcp-hackernews-tool` (Go). Most expose `get_topstories` + `get_item`; only a subset front Algolia search, which is the practical entry point for any URL-or-keyword lookup. A best-in-class connector would unify both APIs and expose: `search_stories(query, tags, date_range)`, `get_item(id)`, `get_user(username)`, `get_topstories(limit)`, `walk_recent_items(since)`, `resolve_url_to_discussions(url)`, with built-in comment-thread expansion and dead/deleted filtering.

## Review notes

Potential new join key for review: `HN_ITEM_ID`
  Entity type: hacker_news_item
  Pattern: `^[0-9]+$` (integer, currently 8-digit range)
  Other datasets that would use it: BigQuery public `hacker_news` dataset, Algolia HN Search API, future HN ranking or moderation datasets. Skip unless a second HN-centric source lands.

Potential new join key for review: `HN_USERNAME`
  Entity type: hacker_news_user
  Pattern: `^[A-Za-z0-9_-]{2,15}$` (case-sensitive)
  Other datasets that would use it: BigQuery `hacker_news`, Algolia. Same caveat: source-internal until a second HN source justifies promotion.

Rate-limit field is best-effort; the docs say "no rate limit" but Firebase enforces unstated thresholds. Set conservatively in any production connector.
