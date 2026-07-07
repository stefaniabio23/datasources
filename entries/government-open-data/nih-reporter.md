---
id: nih-reporter
name: NIH RePORTER
domain: government-open-data
entry_kind: registry
description: US NIH database of federally funded biomedical research projects, their investigators, awarding institutes, funding amounts, and linked publications.
homepage_url: https://reporter.nih.gov/
docs_url: https://api.reporter.nih.gov/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "1 request/sec; run large jobs off-peak (weekends or 9pm-5am ET); abusive IPs blocked"
bulk_available: true
frequency: weekly
lag: "projects appear after the award notice date; ExPORTER bulk files refresh weekly"
geography: [USA]
join_keys:
  - PMID
  - US_STATE_CODE
primary_keys:
  - NIH_APPL_ID
  - NIH_CORE_PROJECT_NUM
  - NIH_PROJECT_NUM
  - NIH_PI_PROFILE_ID
  - NIH_ORG_IPF_CODE
join_key_fields:
  - join_key: PMID
    fields: [pmid]
  - join_key: US_STATE_CODE
    fields: [organization.org_state]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/jbdamask/mcp-nih-reporter"
  - "github.com/GSA-TTS/nih-reporter-mcp-server"
  - "github.com/jhalsey87/MCP_NIH_Reporter"
mcp_notes: >
  Multiple community MCP servers wrap the same POST search API. Suggested surface:
  search_projects, get_project, search_publications, funding_by_pi, funding_by_org.
  Connector must abstract the POST body criteria model and paginate under the 1 req/sec cap.
agent_use_cases:
  - grant funding lookup
  - PI funding history
  - institution funding profile
  - research portfolio analysis
  - link publications to grants
access_test:
  command: "curl -sf -X POST 'https://api.reporter.nih.gov/v2/projects/search' -H 'Content-Type: application/json' -d '{\"criteria\":{\"fiscal_years\":[2023]},\"limit\":1}'"
  expected_status: 200
  expected_fields: [meta.total, results]
last_verified: 2026-07-07
build_priority: medium
structure: registry-snapshot
revisions_possible: true
---

# NIH RePORTER

## Why this source matters

NIH RePORTER (Research Portfolio Online Reporting Tools Expenditures and Results) is the authoritative public record of biomedical research funded by the US National Institutes of Health and several other federal agencies (AHRQ, CDC, FDA, VA). Run by the NIH Office of Extramural Research, it exposes every funded project with its project number, title, abstract, public-health-relevance text, funding amount, activity code, awarding institute, principal investigators, performing organization, and dates, plus a linked publications feed. The V2 REST API (`api.reporter.nih.gov`) is public and unauthenticated, and the same data ships as weekly ExPORTER bulk files. For an agent doing biotech competitive intelligence, translational-science mapping, PI/lab profiling, or tracing which grants produced which papers, this is the primary source of "who got NIH money, from which institute, for what, and what came out of it." Secondary flavours: it overlaps `academic` (grant-to-publication lineage via PMID) and `corporate-registry` (performing organizations keyed on UEI/DUNS).

## Agent use cases

- grant funding lookup
- PI funding history
- institution funding profile
- research portfolio analysis
- link publications to grants

## Join strategy

The one canonical join key RePORTER genuinely carries is `PMID`: the `/v2/publications/search` endpoint returns `{pmid, coreproject, applid}` rows that bridge each funded project to its resulting PubMed articles. Pair with PubMed, Europe PMC, or OpenAlex on `PMID` to go from a grant to full publication metadata, then onward to `DOI`. `US_STATE_CODE` is exposed as the performing organization's `org_state` (two-letter) for coarse geographic joins to Census/BLS/USASpending state data.

Note on the ORCID/ROR hint: RePORTER does **not** expose `ORCID` or `ROR` natively. Principal investigators are identified only by an NIH-internal `profile_id` and free-text names; organizations by NIH `IPF` code, `UEI`, and legacy `DUNS`. Mapping RePORTER people to `ORCID` or institutions to `ROR` requires an external resolver (ORCID's grant records, or a UEI/name-to-ROR crosswalk); those keys are deliberately left out of `join_keys` rather than invented.

Source-internal identifiers live in `primary_keys`: `NIH_APPL_ID` (per-application `appl_id`), `NIH_CORE_PROJECT_NUM` (the stable grant stem, e.g. `R01CA211546`), `NIH_PROJECT_NUM` (full number including support year and type prefix, e.g. `5R21AI156411-02`), `NIH_PI_PROFILE_ID`, and `NIH_ORG_IPF_CODE` (`org_ipf_code`/`external_org_id`). Use these for direct RePORTER lookups, not cross-source joins.

## Access notes

First call: `POST https://api.reporter.nih.gov/v2/projects/search` with a JSON body `{"criteria": {...}, "include_fields": [...], "limit": N, "offset": M}`. No auth. Criteria support `fiscal_years`, `pi_names` (first/last/any_name), `org_names`, `project_nums`, `covid_response`, activity codes, award amounts, and free-text `advanced_text_search`. Publications: `POST /v2/publications/search` filtering on `pmids` or `core_project_nums`. Hard limits: one request per second, max 500 records per page, 14,999-record deep-pagination ceiling (use fiscal-year slicing to page past it). NIH asks that large extraction jobs run weekends or 9pm-5am ET; IPs that ignore robots.txt or hammer the service get blocked. For full-portfolio pulls prefer the ExPORTER bulk CSV/XML files (annual + weekly increments) over API pagination.

## MCP / connector notes

Community MCP servers exist: `jbdamask/mcp-nih-reporter` (chat over projects + publications), and two GSA-TTS pilots (`nih-reporter-mcp-server`, `mcp-server-nih-reporter`) exposing `search_projects`, `get_search_summary`, `find_project_ids`, `get_project_information`. None is an official NIH release; treat as community maturity. A hardened connector should expose `search_projects`, `get_project`, `search_publications`, `funding_by_pi`, and `funding_by_org`, abstract the nested POST criteria model, enforce the 1 req/sec cap with backoff, and transparently switch to ExPORTER bulk files when a query would exceed the 14,999-record pagination ceiling.

## Review notes

The join-key hint named `ROR` and `ORCID`, but the RePORTER API exposes neither natively (PIs use NIH `profile_id`; orgs use `IPF`/`UEI`/`DUNS`). They are intentionally omitted from `join_keys` rather than invented.

Candidate join keys present in the payload but not in `schema/join-keys.yaml`, flagged for human review:

- Proposed key: `UEI`
  - Entity type: `legal_entity` / awardee organization
  - Pattern: `^[A-Z0-9]{12}$` (SAM.gov Unique Entity Identifier; replaced DUNS in 2022)
  - Fields: `organization.org_ueis`, `organization.primary_uei`
  - Other datasets that would use it: SAM.gov, USASpending.gov (both already flagged this same proposed key in `## Review notes`). Promoting `UEI` once would let RePORTER performing-orgs join to federal-contracting and spend data.

- Proposed key: `NIH_CORE_PROJECT_NUM`
  - Entity type: `research_grant` (NIH core project / grant number, e.g. `R01CA211546`)
  - Pattern: `^[A-Z][0-9]{2}[A-Z]{2}[0-9]{6}$` (approximate: activity code + IC code + serial)
  - Other datasets that would use it: PubMed/Europe PMC grant-support fields cite NIH grant numbers, and USASpending grant awards reference them; a canonical grant-number key would bridge grant to publication to federal-spend without going through PMID.

- Legacy `DUNS` (`organization.org_duns`) is also present but superseded by UEI; not worth registering on its own.
</content>
</invoke>
