---
id: reddit
name: Reddit Data API
domain: consumer-signal
description: Official Reddit Data API exposing posts, comments, subreddits, users, and votes across the public Reddit network via OAuth2-authenticated REST endpoints.
homepage_url: https://www.reddit.com/dev/api/
docs_url: https://www.reddit.com/dev/api/
type:
  - rest-api
auth_required: oauth
cost: freemium
license: Reddit-Data-API-Terms
rate_limit: "100 QPM per OAuth client on the free tier; higher quotas on the paid Enterprise tier"
bulk_available: false
frequency: real-time
lag: "seconds-to-minutes for new posts and comments"
geography: [global]
join_keys:
  - URL
  - WIKIDATA_QID
primary_keys:
  - REDDIT_POST_FULLNAME
  - REDDIT_COMMENT_FULLNAME
  - SUBREDDIT_NAME
  - REDDITOR_USERNAME
join_key_fields:
  - join_key: URL
    fields: [data.url, data.permalink]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/karanb192/reddit-mcp-buddy
  - github.com/adhikasp/mcp-reddit
  - github.com/Arindam200/reddit-mcp
  - github.com/Hawstein/mcp-server-reddit
  - github.com/jordanburke/reddit-mcp-server
mcp_notes: >
  Multiple community MCPs cover the read surface (browse subreddits, fetch posts and
  comments, search, user profiles). No official Anthropic-maintained server. A
  consolidated MCP should abstract OAuth bootstrap, User-Agent compliance, rate-limit
  backoff, comment-tree flattening, and the free-vs-paid tier routing.
agent_use_cases:
  - subreddit and topic monitoring
  - consumer sentiment and complaint mining
  - brand and product mention tracking
  - community discovery
  - qualitative trend detection
access_test:
  command: "curl -sf -A \"${REDDIT_USER_AGENT}\" -H \"Authorization: Bearer ${REDDIT_OAUTH_TOKEN}\" 'https://oauth.reddit.com/r/programming/hot?limit=1'"
  expected_status: 200
  expected_fields: [kind, data]
last_verified: 2026-06-08
build_priority: medium
notes: "access_test not executed; requires ${REDDIT_OAUTH_TOKEN} obtained via OAuth2 client_credentials grant. Anonymous JSON endpoints (e.g. /r/sub/hot.json) return 403 from non-browser User-Agents as of 2024 anti-scraping enforcement."
---

# Reddit Data API

## Why this source matters

Reddit is the largest English-language threaded discussion network, with ~100K active subreddits covering products, software, hobbies, health, politics, regional life, and niche communities. The Data API exposes the same posts, comments, subreddits, users, and votes the site renders, plus search, listings, and moderation surfaces. For agents, Reddit is the highest-volume free-text source of unstructured consumer signal: pre-purchase research, post-purchase complaints, expert community consensus, and emerging slang or sentiment shifts that don't surface in news or formal reviews. Owned and operated by Reddit, Inc. (public since March 2024, ticker RDDT).

## Agent use cases

- subreddit and topic monitoring
- consumer sentiment and complaint mining
- brand and product mention tracking
- community discovery
- qualitative trend detection

## Join strategy

Reddit-internal identifiers (`POST_FULLNAME` e.g. `t3_abc123`, `COMMENT_FULLNAME` e.g. `t1_xyz789`, `SUBREDDIT_NAME`, `REDDITOR_USERNAME`) are the natural primary keys but sit outside the canonical registry. Use them for direct Reddit-to-Reddit lookups and comment-tree traversal, not for cross-source joins.

For cross-source work, the practical join keys are `URL` (Reddit submissions are very frequently link posts pointing at news articles, papers, GitHub repos, product pages) and `WIKIDATA_QID` for well-known subreddits or public figures mapped via Wikidata. Pair with news-events sources (GDELT) for "what did people say about this article" workflows, or with consumer-signal sources (Wikipedia pageviews, Google Trends) for triangulating attention spikes.

Potential new join keys for review: `REDDIT_POST_FULLNAME`, `REDDIT_COMMENT_FULLNAME`, `SUBREDDIT_NAME`, `REDDITOR_USERNAME`. None are likely to appear in other directory entries, so registering them is low-value unless a second Reddit-derived source (Pushshift mirror, Reddit Pulse, etc.) gets added later.

## Access notes

**OAuth2 required.** Anonymous access to the `.json` endpoints was effectively closed in mid-2023 to mid-2024 via aggressive User-Agent filtering and 403s; expect a 403 from any non-browser anonymous request today. Create an app at `https://www.reddit.com/prefs/apps`, obtain `client_id` and `client_secret`, and use the `client_credentials` grant against `https://www.reddit.com/api/v1/access_token` to get a bearer token (1-hour TTL).

**User-Agent format is enforced.** Use `<platform>:<app-id>:<version> (by /u/<username>)`. Generic UAs like `python-requests` or `curl` get drastically rate-limited or banned.

**Rate limits.** 100 QPM per OAuth client on the free tier (as of the July 2023 pricing change). Headers `X-Ratelimit-Used`, `X-Ratelimit-Remaining`, `X-Ratelimit-Reset` report current state. The free tier is for non-commercial use; commercial use requires the paid Enterprise tier (quote-based pricing, contact required).

**No bulk download.** The historical Pushshift archive (which previously offered bulk Reddit dumps) lost API access in 2023 and is now restricted to verified moderators. Archive.org hosts older Pushshift dumps but they are not maintained.

**License.** Governed by the Reddit Data API Terms (`https://www.redditinc.com/policies/data-api-terms`). Free tier allows non-commercial research, personal projects, and moderation tooling; prohibits AI model training without a commercial licence. Attribution and link-back to source content is required when displaying Reddit data.

## MCP / connector notes

Multiple community MCPs cover the read surface: `reddit-mcp-buddy` (TypeScript, ~700 stars), `mcp-reddit` (Python, ~400 stars), `reddit-mcp` (Python, ~290 stars), `mcp-server-reddit` (Python, ~180 stars), `reddit-mcp-server` (TypeScript, ~125 stars). No official Anthropic-maintained server. All target the read path (browse, search, fetch); write actions (submit, comment, vote) are inconsistent. A consolidated MCP should abstract OAuth bootstrap, User-Agent compliance, exponential backoff on 429, comment-tree flattening (Reddit's nested `Listing[t1_*]` shape is verbose), and route between free and paid tiers based on caller intent.

## Review notes

- License is non-SPDX and the canonical short name `Reddit-Data-API-Terms` is new to this directory. Confirm short-name convention.
- Reddit-internal IDs (`POST_FULLNAME`, `COMMENT_FULLNAME`, `SUBREDDIT_NAME`, `REDDITOR_USERNAME`) are flagged but registration is low-value unless a second Reddit-derived source enters the directory.
- `access_test` constructed only; not executed because OAuth credentials were not available in the entry-creation session. Anonymous fallback (`.json` endpoints) returns 403 as of 2024.
- WebFetch could not reach `reddit.com` or `redditinc.com` directly; facts cross-checked via the archived OAuth2 wiki, the archived API wiki, the PRAW docs, and GitHub MCP search. Pricing and terms specifics should be re-verified against the live `redditinc.com/policies/data-api-terms` page before publication.
