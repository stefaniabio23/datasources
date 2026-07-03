---
id: pubpeer
name: PubPeer
domain: academic
entry_kind: corpus
description: Post-publication peer review platform hosting reader comments and integrity discussions attached to individual scientific publications.
homepage_url: https://pubpeer.com/
docs_url: https://www.pubpeer.com/static/faq
type:
  - rest-api
  - web-ui
auth_required: api-key-free
cost: free
license: unknown
rate_limit: "unknown; keyed API, limits set per devkey on request"
frequency: continuous
geography: [global]
join_keys:
  - DOI
  - PMID
  - ARXIV_ID
primary_keys:
  - PUBPEER_PUBLICATION_ID
  - PUBPEER_THREAD_ID
join_key_fields:
  - join_key: DOI
    fields: [doi]
  - join_key: PMID
    fields: [pubmed_id]
  - join_key: ARXIV_ID
    fields: [arxiv_id]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - research-integrity screening
  - retraction and misconduct signal lookup
  - flagging papers with community concerns
  - reference-list due diligence
access_test:
  command: "curl -sf -A 'Mozilla/5.0' -o /dev/null -w '%{http_code}' 'https://pubpeer.com/search?q=10.1038/s41586-020-2649-2'"
  expected_status: 200
  expected_fields: []
last_verified: 2026-07-02
build_priority: low
structure: event-log
---

# PubPeer

## Why this source matters

PubPeer is the main public venue for post-publication peer review: readers (usually anonymous) post comments raising methodological, statistical, or image-integrity concerns about specific published papers, keyed to the paper's DOI, PubMed ID, or arXiv ID. Run by the PubPeer Foundation, a California 501(c)(3) (EIN 47-4729597, tax-exempt since 2015; leadership includes Brandon Stell, Boris Barbour, and Retraction Watch co-founder Ivan Oransky), it is the de-facto early-warning layer for research-integrity problems. Many retractions and misconduct investigations trace back to a PubPeer thread. For an agent doing literature due diligence, a hit on PubPeer is a signal that a paper's findings may be contested before any formal correction or retraction exists. Secondary relevance to `clinical-biotech` and `public-health`, since flagged papers often sit in biomedical literature.

## Agent use cases

- research-integrity screening
- retraction and misconduct signal lookup
- flagging papers with community concerns
- reference-list due diligence

## Join strategy

PubPeer indexes each discussion thread against the publication's external identifiers, so it joins cleanly on `DOI`, `PMID`, and `ARXIV_ID`. Per PubPeer's own docs, "the only requirement is for the publication to have an ID that we recognize. Such IDs include the DOI and IDs for PubMed and the arXiv." Use it as an overlay: resolve a paper set through OpenAlex, Crossref, or PubMed, then check each `DOI`/`PMID` against PubPeer to attach a "has community concerns" flag. Pair with Retraction Watch / the Retraction Watch Database for formal retraction status and with OpenAlex for citation context. PubPeer's own thread/publication identifiers (`PUBPEER_PUBLICATION_ID`, `PUBPEER_THREAD_ID`) are source-internal and not canonical join keys; use them only for direct PubPeer deep-links.

## Access notes

The public site (`https://pubpeer.com/search?q=<DOI>`) is a JS web UI; it returns 200 for a browser user-agent but bot-blocks default agents (plain WebFetch got 403), so treat the UI as scraper-hostile. The supported path is the keyed REST API: PubPeer states the API is "keyed" and access is granted by contacting them (contact@pubpeer.com). It reports, for a given identifier, the number of PubPeer comments and a link to the thread. The historical bulk dump endpoint (`api.pubpeer.com/v1/publications/dump/...?devkey=`) and the browser-extension check both require a devkey. Inject the key at runtime as `${PUBPEER_DEVKEY}`; never inline it. The access_test above is only a liveness check against the search UI (executed, returned 200); the comment-count API was not exercised because it requires a key.

## MCP / connector notes

No MCP exists. Value is real but the audience is narrow (research-integrity workflows) and the API is gated behind a manual key request, so this is lower-priority than open scholarly hubs. A useful connector surface would be a single `get_pubpeer_concerns(id, id_type)` tool taking a DOI/PMID/arXiv ID and returning comment count, first/last comment dates, and the thread URL, plus a batch variant for reference-list screening. The connector must hold the devkey server-side and abstract over the three identifier types.

## Review notes

- License is `unknown`: PubPeer publishes no explicit open-data license for user comments; comment text is user-contributed and access is API-key gated. Confirm terms with PubPeer before any redistribution; do not assume reuse rights.
- `auth_required: api-key-free` is the best-fit enum. The key is free but not self-service; it requires emailing PubPeer, which no enum value captures. Consider whether a `contact-required` or `api-key-by-request` value is worth adding.
- `join_key_fields` paths (`doi`, `pubmed_id`, `arxiv_id`) are plausible but unverified against a live keyed API response; correct once a devkey is available.
- No new canonical join keys needed. The source-native thread id maps to `primary_keys` (`PUBPEER_THREAD_ID`), not the join-key registry.
