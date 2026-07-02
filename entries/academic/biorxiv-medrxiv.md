---
id: biorxiv-medrxiv
name: bioRxiv / medRxiv
domain: academic
entry_kind: corpus
description: Preprint servers for the life sciences (bioRxiv) and health sciences (medRxiv), exposing preprint metadata (DOI, title, authors, abstract, license, funding) and preprint-to-publication status via a free REST API.
homepage_url: https://www.biorxiv.org/
docs_url: https://api.biorxiv.org/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: Author-Selected-CC
rate_limit: "fair-use; 30 preprints per details call, cursor-paginated"
bulk_available: true
frequency: "continuous; new preprints posted daily"
lag: "hours-to-days from submission to posting"
geography: [global]
join_keys:
  - DOI
  - ROR
join_key_fields:
  - join_key: DOI
    fields: [doi, published]
  - join_key: ROR
    fields: [funder.ror]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/genomoncology/biomcp
  - "@futurelab-studio/latest-science-mcp (npm)"
mcp_command:
  - "uvx --from biomcp-python biomcp run"
  - "npx -y @futurelab-studio/latest-science-mcp@latest"
agent_use_cases:
  - preprint monitoring by date and category
  - early research-signal detection
  - abstract and metadata text mining
  - preprint-to-publication tracking
  - funder analysis via ROR
access_test:
  command: "curl -sf 'https://api.biorxiv.org/details/biorxiv/2024-01-01/2024-01-02/0' -o /dev/null"
  expected_status: 200
last_verified: 2026-07-02
build_priority: low
notes: "access_test executed 2026-07-02 (details endpoint → 200). One entry covers both bioRxiv and medRxiv (shared api.biorxiv.org). Covered by biomcp and scientific-papers MCPs. Preprint license varies per author (the API's per-record `license` field carries the specific CC licence); headline short name is a placeholder, flagged."
---

# bioRxiv / medRxiv

## Why this source matters

bioRxiv (life sciences) and medRxiv (health sciences) are the dominant preprint servers for biology and medicine, the place where results surface months before peer-reviewed publication. Their shared API exposes structured metadata for every preprint, DOI, title, authors and institutions, abstract, subject category, funding (with funder ROR ids), and the crucial preprint-to-published DOI mapping once a paper is accepted. For an agent, this is the earliest machine-readable signal of new biomedical research and a clean way to track a preprint through to its journal version.

## Agent use cases

- preprint monitoring by date and category
- early research-signal detection
- abstract and metadata text mining
- preprint-to-publication tracking
- funder analysis via ROR

## Join strategy

The strong canonical keys are `DOI` (every preprint has one; the API also returns the *published* DOI once a preprint is peer-reviewed, enabling preprint→publication joins into Crossref/OpenAlex/PubMed) and `ROR` (funder identifiers in the funding metadata). Use the preprint/published DOI pair to link bioRxiv/medRxiv into the wider scholarly graph, and `ROR` to join funders across `openalex` and `crossref`.

## Access notes

Free, no authentication, at `api.biorxiv.org`. Main endpoints: `/details/{server}/{from}/{to}/{cursor}` for date-range metadata (30 per page, cursor-paginated), `/details/{server}/{doi}` for a single preprint, and `/pubs/` for preprint-to-publication mappings. `{server}` is `biorxiv` or `medrxiv`. JSON by default; OAI-PMH XML and some CSV endpoints exist. Bulk full-text is available via a requester-pays S3 bucket.

## MCP / connector notes

Covered by two MCPs: `biomcp` (`uvx --from biomcp-python biomcp run`) and `scientific-papers` (`npx -y @futurelab-studio/latest-science-mcp@latest`), both of which include bioRxiv/medRxiv among their sources. No dedicated preprint-server MCP is needed given the clean API.

## Review notes

- License `Author-Selected-CC` is a placeholder: each preprint carries its own CC licence (CC-BY, CC-BY-NC, CC-BY-ND, CC0), returned in the API's per-record `license` field. Confirm the short-name convention or drop to per-record.
- One entry covers both servers (shared API + infrastructure); if a consumer needs them separated, revisit.
- `ROR` join uses the funding metadata; verify the exact field path (`funder.ror`) against a live response before relying on it for joins.
