---
id: openaire
name: OpenAIRE Graph
domain: academic
entry_kind: knowledge-graph
description: Open scholarly knowledge graph linking research products (publications, data, software, other) to authors, organizations, funders, projects, and data sources across global research.
homepage_url: https://graph.openaire.eu/
docs_url: https://graph.openaire.eu/docs/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "anonymous requests rate-limited per terms of use; register an OpenAIRE personal token (OAuth) for higher hourly limits"
bulk_available: true
frequency: "versioned graph releases (~bi-monthly); API continuously updated"
geography: [global]
join_keys:
  - DOI
  - PMID
  - PMCID
  - ARXIV_ID
  - ORCID
  - ROR
  - ISNI
primary_keys:
  - OPENAIRE_ID
join_key_fields:
  - join_key: DOI
    fields:
      - "pids[scheme=doi].value"
      - "instances.pids[scheme=doi].value"
  - join_key: PMID
    fields:
      - "pids[scheme=pmid].value"
  - join_key: PMCID
    fields:
      - "pids[scheme=pmc].value"
  - join_key: ARXIV_ID
    fields:
      - "pids[scheme=arxiv].value"
  - join_key: ORCID
    fields:
      - "authors.pid[scheme=orcid].value"
  - join_key: ROR
    fields:
      - "organizations.pids[scheme=ror].value"
  - join_key: ISNI
    fields:
      - "organizations.pids[scheme=isni].value"
mcp_status: mcp-needed-high-value
agent_use_cases:
  - literature and dataset search
  - funder and grant attribution
  - project-to-output linkage
  - organization research profiling
  - open-access status lookup
access_test:
  command: "curl -sf -H 'accept: application/json' 'https://api.openaire.eu/graph/v1/researchProducts?search=climate&pageSize=1'"
  expected_status: 200
  expected_fields: [header, results]
last_verified: 2026-07-07
build_priority: medium
---

# OpenAIRE Graph

## Why this source matters

OpenAIRE Graph is a CC-BY global scholarly knowledge graph of ~377M research products (publications, research data, software, other), run by the OpenAIRE non-profit infrastructure (an EU-funded e-infrastructure). Its distinguishing edge over other scholarly graphs is first-class modelling of the funding chain: it links research outputs to projects, grant codes, funders, organizations, and data sources, with provenance tracked at every level. For an agent that needs to answer "what did this grant produce" or "which institution funded this dataset", OpenAIRE covers ground that pure citation graphs do not. It overlaps with the `academic` domain but its funder/project linkage also touches `government-open-data` (public research-funding attribution).

## Agent use cases

- literature and dataset search
- funder and grant attribution
- project-to-output linkage
- organization research profiling
- open-access status lookup

## Join strategy

Research products expose external PIDs in a `pids` array of `{scheme, value}` objects: `DOI` (scheme `doi`), `PMID` (`pmid`), `PMCID` (`pmc`), `ARXIV_ID` (`arxiv`), plus Handle for repository deposits. Authors carry an ORCID via their `pid` field. Organizations expose `ROR` and `ISNI` (and PIC/GRID) in their own `pids` array. DOI is confirmed present in live responses; the remaining schemes are documented pid schemes and appear conditionally.

The OpenAIRE-internal id (`OPENAIRE_ID`, format `sourcePrefix::md5(localId)`) uniquely keys every entity for direct lookups but is source-internal, so it lives in `primary_keys`, not the canonical registry.

Best paired with OpenAlex and Crossref for DOI-level metadata cross-checks, and with Crossref's Open Funder Registry (`FUNDER_DOI`) or CORDIS for the funding side. OpenAIRE is the recommended hub when the join runs through grants and projects rather than citations.

## Access notes

Hit the Graph API first: base `https://api.openaire.eu/graph/v1/`, endpoints `researchProducts`, `organizations`, `projects`, `dataSources`. Anonymous GET works (verified 200) and returns `{header, results}`; paginate with `page` + `pageSize` and filter with `search=` plus entity-specific params. Register an OpenAIRE account and mint a personal OAuth token for materially higher hourly rate limits; anonymous traffic is throttled under the terms of use. Swagger: `https://api.openaire.eu/graph/swagger-ui/index.html`.

Bulk: full-graph dumps are published on Zenodo as tar archives of gz'd JSONL (one JSON per line, files capped ~10GB), licensed CC-BY-4.0. Current graph versions are sometimes exposed via API and added-value services only, with bulk access to the very latest data available on request through the OpenAIRE helpdesk. Check `https://graph.openaire.eu/docs/category/downloads/` for the latest dump version and date.

## MCP / connector notes

No MCP found on the official registry, npm, or PyPI as of 2026-07-07. High value: a scholarly-graph connector overlapping OpenAlex, Crossref, and funding-attribution users. Suggested surface: `search_research_products`, `get_research_product`, `search_organizations`, `search_projects`, `get_project_outputs`. The connector should abstract over the `{header, results}` envelope, cursor/page pagination, PID-scheme extraction (flatten the `pids` array into typed keys), and anonymous-vs-token rate-limit routing.

## Review notes

- Two potential canonical join keys OpenAIRE exposes but the registry lacks. Do not invent; flagging for review:
  - Potential new join key: `HANDLE`
    - Entity type: repository_deposit / scholarly_work
    - Pattern: `^[0-9]+(\.[0-9]+)*/.+$` (Handle System, e.g. `11245/1.123456`)
    - Other datasets that would use it: DSpace/EPrints repositories, Dryad, most institutional repositories
  - Potential new join key: `PIC`
    - Entity type: organisation (EU participant identification code)
    - Pattern: `^[0-9]{9}$`
    - Other datasets that would use it: CORDIS, EU Funding & Tenders portal, any EU-grant source
- License is CC-BY-4.0 overall because some input sources are CC-BY; OpenAIRE states parts of the graph are re-usable as CC0. Kept `CC-BY-4.0` as the conservative single value; CC0 sub-parts noted here rather than in YAML.
- `auth_required: none` reflects that anonymous API access returns 200; authentication is optional and only raises rate limits. No enum value distinguishes "optional auth for higher limits", so `none` is the closest fit.
