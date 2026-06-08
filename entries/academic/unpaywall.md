---
id: unpaywall
name: Unpaywall
domain: academic
entry_kind: registry
description: Open database of free, legal open-access (OA) full-text locations for scholarly articles, keyed by DOI.
homepage_url: https://unpaywall.org/
docs_url: https://unpaywall.org/products/api/v2
type:
  - rest-api
  - dataset-dump
auth_required: none
cost: freemium
license: CC0
rate_limit: "100K calls/day per email (soft); requires ?email= identifier on every call"
bulk_available: true
frequency: continuous (API); periodic JSONL snapshot
lag: "weeks for newly published DOIs to acquire OA locations"
geography: [global]
join_keys:
  - DOI
  - ISSN
primary_keys:
  - DOI
join_key_fields:
  - join_key: DOI
    fields: [doi]
  - join_key: ISSN
    fields: [journal_issn_l, journal_issns]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Single useful endpoint shape (lookup by DOI, search by title); thin wrapper.
  Most agents that need Unpaywall are already calling OpenAlex, which embeds
  Unpaywall's OA-location data. Standalone MCP only worth building if an agent
  must filter or rank OA copies by repository, license, or version without the
  OpenAlex overhead.
agent_use_cases:
  - find legal open-access PDF for a DOI
  - resolve best OA location across publisher and repository copies
  - check OA status of a journal or article
  - enrich bibliographies with OA-availability flags
access_test:
  command: "curl -sf \"https://api.unpaywall.org/v2/10.1038/nature12373?email=${UNPAYWALL_EMAIL}\""
  expected_status: 200
  expected_fields: [doi, is_oa, oa_status, best_oa_location, oa_locations, journal_issn_l]
last_verified: 2026-06-08
build_priority: low
---

# Unpaywall

## Why this source matters

Unpaywall is the canonical open database of legal OA full-text locations for scholarly articles. Run by OurResearch (the same nonprofit behind OpenAlex), it crawls publisher sites, institutional repositories, preprint servers, and PMC to record where a given DOI is freely and legally readable. The data is CC0. For an agent doing literature work, Unpaywall is the lowest-friction way to turn a DOI into a working PDF URL without hitting paywalls. OpenAlex already ingests Unpaywall's OA locations into its `open_access` block, so Unpaywall stands alone mainly when an agent needs the raw per-location detail (repository, version, license) or a DOI-keyed lookup faster than a full OpenAlex work fetch.

## Agent use cases

- find legal open-access PDF for a DOI
- resolve best OA location across publisher and repository copies
- check OA status of a journal or article
- enrich bibliographies with OA-availability flags

## Join strategy

Primary key is `DOI`. Every record is a DOI lookup; there is no Unpaywall-internal ID. Journal metadata exposes `ISSN` via `journal_issn_l` (linking ISSN) and `journal_issns` (comma-separated list of print + electronic). Each entry in `oa_locations[]` includes a `repository_institution` string and `endpoint_id` that point at OAI-PMH endpoints, useful for repository-level filtering but not part of the canonical join-key registry.

Natural pairings: OpenAlex for the full work record (OpenAlex embeds Unpaywall OA data already, so use Unpaywall standalone when you want a thinner, DOI-only fetch); Crossref for DOI metadata authority; Europe PMC and PubMed for biomedical-specific full-text routing.

## Access notes

**API.** `https://api.unpaywall.org/v2/{doi}?email=you@example.com`. No API key. The `email=` parameter is mandatory on every call, used for contact in case of misuse rather than authentication. Soft limit ~100K calls/day per email; bulk users should download the snapshot instead. Title search at `/v2/search?query={q}&email=...`. Returns JSON with `is_oa`, `oa_status` (gold, green, hybrid, bronze, closed), `best_oa_location`, and a full `oa_locations[]` array.

**Snapshot.** A periodic JSONL dump of every record is offered as the Unpaywall Data Feed, gated behind an institutional subscription (paid) despite the underlying data being CC0. Subscribers download from `https://unpaywall-data-snapshots.s3.us-west-2.amazonaws.com/`. For free bulk access, the OpenAlex snapshot (also CC0, S3-hosted) carries the same OA-location data inside each work record.

Gotchas:

- The May 2025 rewrite aligned Unpaywall records with OpenAlex; some long-tail DOIs got materially re-classified. Cached OA statuses from before mid-2025 should be re-fetched.
- The `evidence` and `updated` fields on `oa_locations` currently return `"deprecated"` for many records under the new codebase; do not rely on them.
- "Bronze" OA (freely readable but no clear license) is common and frequently confused with green or gold. Filter on `license` if you need redistribution rights.

## MCP / connector notes

No official or community MCP found. Suggested surface if built: `get_by_doi`, `search_by_title`, `best_oa_pdf_url`. Most agents that want Unpaywall are also already pulling OpenAlex, which embeds the same OA-location data. Standalone connector is low-value unless an agent needs to filter or rank OA copies by repository, license, or version without the full OpenAlex work payload. Build the OpenAlex MCP first; Unpaywall belongs as an optional fast-path inside it.

## Review notes

- License field set to `CC0` (the API/data are explicitly CC0; only the bulk snapshot delivery is paid). Confirm wording matches the SPDX convention used elsewhere in the directory.
- `cost: freemium` reflects: API free, snapshot paid. If the directory's convention is to classify by the primary access mode (API), `free` may be more accurate. Flagging for Stephanie to standardise.
- Sister-project relationship with OpenAlex: cross-link in any future "scholarly hub" MOC.
