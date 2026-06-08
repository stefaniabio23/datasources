---
id: stack-exchange-data-explorer
name: Stack Exchange Data Explorer
domain: consumer-signal
entry_kind: corpus
description: Web-based T-SQL query interface over a weekly read-only snapshot of every public Stack Exchange site (Stack Overflow plus 170+ communities), backed by the same data published as monthly Internet Archive dumps.
homepage_url: https://data.stackexchange.com/
docs_url: https://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede
type:
  - web-ui
  - database
  - bulk-download
auth_required: account-required
cost: free
license: CC-BY-SA-4.0
rate_limit: "no published quotas; queries run against a shared SQL Server replica with a per-query timeout, results capped at 50000 rows"
bulk_available: true
frequency: weekly
lag: "SEDE database refreshes weekly (typically Sundays); Internet Archive XML dumps refresh roughly quarterly"
geography: [global]
join_keys:
  - URL
  - DATE
  - WIKIDATA_QID
primary_keys:
  - SE_POST_ID
  - SE_USER_ID
  - SE_ACCOUNT_ID
  - SE_TAG_ID
  - SE_COMMENT_ID
  - SE_BADGE_ID
  - SE_VOTE_ID
  - SE_POSTHISTORY_ID
  - SE_POSTHISTORY_REVISION_GUID
  - SE_POSTLINK_ID
join_key_fields:
  - join_key: URL
    fields: [Users.WebsiteUrl]
  - join_key: DATE
    fields: [Posts.CreationDate, Posts.LastActivityDate, Users.CreationDate, Comments.CreationDate, Votes.CreationDate, Badges.Date, PostHistory.CreationDate]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cyanheads/stackexchange-mcp-server
  - github.com/pipeworx-io/mcp-stackexchange
  - github.com/ag2-mcp-servers/stackexchange
mcp_notes: >
  Community MCPs wrap the live api.stackexchange.com REST API (search questions, fetch
  threads, browse tags, user profiles), not the SEDE SQL surface. No MCP exposes ad-hoc
  T-SQL against SEDE; that would require either headless browser automation against
  data.stackexchange.com or running queries against a self-hosted restore of the XML dump.
agent_use_cases:
  - developer-topic trend analysis
  - tag co-occurrence and ecosystem mapping
  - user reputation and expertise lookup
  - longitudinal Q-and-A volume tracking
  - language and framework adoption signals
last_verified: 2026-06-08
build_priority: medium
notes: >
  SEDE itself has no documented machine-readable API; saved queries can be fetched as CSV
  via /query/csv/<query_id> but the run flow requires CSRF tokens, so it is not safe to
  treat as a stable programmatic surface. For agent automation, prefer the related
  api.stackexchange.com REST API (separate entry) or the Internet Archive XML dumps.
---

# Stack Exchange Data Explorer

## Why this source matters

Stack Exchange Data Explorer (SEDE) is a public, free, account-gated T-SQL query interface over a near-live read-only mirror of every Stack Exchange site: Stack Overflow, Stack Overflow for Teams' public corpus, Server Fault, Super User, Cross Validated, Mathematics, and 170+ other communities. Run by Stack Exchange, Inc. The same underlying tables are also published as anonymised XML data dumps on the Internet Archive (Posts, Users, Votes, Comments, Badges, Tags, PostHistory, PostLinks). For consumer-signal work it is the canonical record of developer attention: which languages, frameworks, libraries, and APIs people are actually asking about, who the high-reputation experts are, and how topic interest decays or compounds over time. Secondary fit with `academic` for software-engineering research and with `news-events` when tag volume is used as an adoption proxy.

## Agent use cases

- developer-topic trend analysis
- tag co-occurrence and ecosystem mapping
- user reputation and expertise lookup
- longitudinal Q-and-A volume tracking
- language and framework adoption signals

## Join strategy

SEDE's primary identifiers are all site-local integers: `Posts.Id` (question or answer), `Users.Id`, `Tags.Id`, `Comments.Id`, `Badges.Id`, plus `PostHistory.RevisionGUID`. These are SEDE-internal and intentionally outside the canonical registry; treat them as within-source keys, not cross-source joins.

Canonical join keys SEDE actually exposes:

- `URL` — every post resolves to a stable `https://stackoverflow.com/q/<post_id>` (or per-site equivalent) link; this is the last-resort key for cross-source citation
- `DATE` — every post, vote, comment, and badge carries a `CreationDate` timestamp, joinable against any time-indexed series
- `WIKIDATA_QID` — Stack Exchange and Stack Overflow themselves have Wikidata QIDs (Q1346110, Q549037), and many high-volume tags map to Wikidata entities (programming languages, frameworks, companies), enabling bridge joins to Wikipedia pageviews, OpenAlex, and GDELT

Pair with Wikipedia Pageviews and Google Trends for the three-way "ask / read / search" developer-attention triangle, with GitHub's repo metadata API for "tag versus repo" adoption divergence, and with PyPI/npm download stats for upstream package signal versus downstream question volume.

## Access notes

**Interactive use:** sign in with any Stack Exchange account at `https://data.stackexchange.com/`, pick a site, write or fork a T-SQL query. Results are capped at 50000 rows and queries hit a per-statement timeout; long-running analytics require breaking into windowed queries. Results can be exported as CSV from the UI, and any cached query result is fetchable at `https://data.stackexchange.com/<site>/csv/<query_id>` once it has been run by some user.

**Bulk / programmatic use:** the Internet Archive mirror at `https://archive.org/details/stackexchange` publishes the full 7zip-bzip2 XML dumps (Posts, Users, Votes, Comments, Badges, Tags, PostHistory, PostLinks) for every site. April 2024 snapshot was 92.3 GB across 371 files. Restoring locally into Postgres or SQL Server gives the same schema SEDE exposes, without rate limits or row caps. Refresh cadence shifted from quarterly to "irregular" in 2023; check the latest snapshot date on the archive.org page before relying on freshness.

**For live, simple lookups:** use `api.stackexchange.com` (separate entry) rather than SEDE. SEDE is for ad-hoc joins, aggregations, and historical analysis that the REST API does not support.

**License:** all user content is CC BY-SA 4.0 (CC BY-SA 3.0 for content posted before 2018-05-02). Attribution requires linking back to the original question, the author profile, and a visible "from Stack Overflow" or per-site marker. Site names, logos, and trademarks are not licensed.

## MCP / connector notes

Community MCPs exist but wrap the `api.stackexchange.com` REST surface (search, fetch threads as markdown, browse tag FAQs, look up users), not SEDE itself. Most mature options:

- `cyanheads/stackexchange-mcp-server` — search, fetch full Q&A threads as clean markdown, tag FAQs, user profiles
- `pipeworx-io/mcp-stackexchange` — Stack Overflow question/answer search
- `ag2-mcp-servers/stackexchange` — auto-generated MCP server

For the SEDE-specific surface (ad-hoc T-SQL against the warehouse) no MCP exists. A useful connector would either:

1. Run the Internet Archive dump into a local SQL Server / Postgres and expose `run_sql(query, site)`, `get_schema(site)`, `list_sites()`, `get_top_tags(site, since)`, `get_user_activity(user_id)`. This is the cleanest path because it removes the per-query timeout, the 50000-row cap, and the CSRF dance.
2. Drive the SEDE web UI via headless browser; brittle, account-bound, and likely against the site's terms for sustained use.

The dump-restore path is the recommended MCP surface; mark as `mcp-needed-high-value` for the SEDE-specific connector if that distinction is added later.

## Review notes

License nuance: SEDE returns user-contributed prose under CC BY-SA 4.0 (or 3.0 for pre-2018 content). The schema itself, query results in aggregate, and Stack Exchange's metadata are not separately licensed; treat any text returned from `Posts.Body` or `Comments.Text` as CC BY-SA with attribution requirements.

`auth_required` is set to `account-required` because SEDE will not run queries without a signed-in Stack Exchange account, though no API key is involved. No SEDE-specific token is issued.

Stack Exchange API (`api.stackexchange.com`) is a closely related but distinct source. It is REST, has a 10000-request daily quota with a free key, exposes a different (read-optimised, denormalised) view, and warrants its own entry under `consumer-signal` or potentially a dedicated developer-signal sub-domain.

No new canonical join keys proposed. The internal `Posts.Id`, `Users.Id`, `Tags.Id` are SEDE-local and intentionally not promoted.

`access_test` is omitted because SEDE has no stable unauthenticated API; freshness should be verified by loading the homepage and checking the "Database last updated" banner, or by checking the latest snapshot date on `https://archive.org/details/stackexchange`.
