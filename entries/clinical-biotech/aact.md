---
id: aact
name: AACT (Aggregate Analysis of ClinicalTrials.gov)
domain: clinical-biotech
description: Public PostgreSQL mirror of ClinicalTrials.gov, refreshed daily by CTTI at Duke, with all protocol and results data normalised into ~50 relational tables for SQL analysis.
homepage_url: https://aact.ctti-clinicaltrials.org/
docs_url: https://aact.ctti-clinicaltrials.org/learn_more
type:
  - database
  - bulk-download
auth_required: account-required
cost: free-with-registration
license: AACT-CTTI-Attribution
rate_limit: "10 concurrent connections per user account; contact CTTI for elevated limits"
bulk_available: true
frequency: daily
lag: "nightly load from ClinicalTrials.gov; static monthly snapshots also archived"
geography: [global]
join_keys:
  - NCT_ID
  - EUDRACT_NUMBER
  - EU_CT_NUMBER
  - PMID
  - MESH_TERM
primary_keys:
  - NCT_ID
  - AACT_STUDY_ID
  - AACT_SPONSOR_ID
  - AACT_FACILITY_ID
join_key_fields:
  - join_key: NCT_ID
    fields: [studies.nct_id]
  - join_key: EUDRACT_NUMBER
    fields: [id_information.id_value]
  - join_key: EU_CT_NUMBER
    fields: [id_information.id_value]
  - join_key: PMID
    fields: [study_references.pmid]
  - join_key: MESH_TERM
    fields: [browse_conditions.mesh_term, browse_interventions.mesh_term]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/navisbio/AACT_clinicaltrials_MCP
mcp_notes: >
  navisbio/AACT_clinicaltrials_MCP wraps the AACT Postgres mirror with read-only SQL.
  No official MCP. Ideal connector surface: run_query (read-only), describe_table,
  list_studies_by_condition, get_outcomes_for_study, get_sponsors_for_study, with
  schema introspection and query-budget guardrails to prevent unbounded scans.
agent_use_cases:
  - SQL-style cohort building across trial protocols and results
  - sponsor and investigator competitive analysis
  - outcomes and adverse-event aggregation across many trials
  - condition and intervention landscape mapping via MeSH
  - drug-pipeline scans joined to PubMed citations
last_verified: 2026-06-08
build_priority: medium
notes: >
  Programmatic access is via PostgreSQL connection (not REST); access_test omitted
  because the live database requires registered credentials. To verify freshness,
  check the snapshot archive index on the AACT site or query select max(updated_at)
  from ctgov.studies after connecting.
---

# AACT (Aggregate Analysis of ClinicalTrials.gov)

## Why this source matters

A free PostgreSQL mirror of the entire ClinicalTrials.gov registry, maintained by the Clinical Trials Transformation Initiative (CTTI) at Duke. Refreshed nightly from ClinicalTrials.gov, normalised into ~50 relational tables (studies, sponsors, conditions, interventions, outcomes, eligibilities, facilities, browse_conditions, browse_interventions, etc.), so analysts can write SQL across the full registry instead of paginating the REST API. For agents doing cohort analytics, competitive intelligence on trial pipelines, or large outcome aggregations, AACT is materially faster and more expressive than the upstream JSON API. Account creation is free but mandatory; raw data is the same as ClinicalTrials.gov, so this entry complements rather than duplicates `clinicaltrials-gov.md`.

## Agent use cases

- SQL-style cohort building across trial protocols and results
- sponsor and investigator competitive analysis
- outcomes and adverse-event aggregation across many trials
- condition and intervention landscape mapping via MeSH
- drug-pipeline scans joined to PubMed citations

## Join strategy

Every table in the `ctgov` schema joins on `NCT_ID` (the primary key of the `studies` table). Secondary cross-registry identifiers surface in `id_information` (sponsor-internal IDs, prior NCT IDs, `EUDRACT_NUMBER`, and the newer `EU_CT_NUMBER` from CTIS). `MESH_TERM` values populate `browse_conditions` and `browse_interventions`, refreshed nightly by the NLM's MeSH-tagging algorithm. `study_references` exposes `PMID` for linked publications, enabling joins to PubMed, OpenAlex, and Europe PMC.

Pair AACT with: OpenFDA (adverse events by drug name to NCT), PubMed via `PMID`, EU CTIS via `EU_CT_NUMBER`, OpenAlex for citation-context on trial publications, and DrugBank or RxNorm for intervention-to-drug-concept resolution.

A `WHO_UTN` field is present in some `id_information` rows but not in the canonical join-key registry yet, see Review notes.

## Access notes

Sign up at `/users/sign_up` (free, name + email + password). After login, the connection page exposes host, port, database name, and the user-specific credentials. Connect with any PostgreSQL client (psql, pgAdmin, DBeaver, R `RPostgres`, Python `psycopg2`, SAS, Tableau). Read-only role; queries are capped at 10 concurrent connections per account, contact CTTI via `/contactus` for elevated limits on legitimate research projects.

For reproducible workloads, prefer the static snapshot archive over the live database: CTTI publishes a daily full Postgres dump plus a separate pipe-delimited file bundle, plus dated monthly archives, downloadable without auth. Use the snapshot date as the citation anchor. The live database is fine for ad-hoc analysis but its contents change nightly, so analyses against the live DB are not reproducible without recording the snapshot date.

Attribution is required: cite "Aggregate Analysis of ClinicalTrials.gov (AACT) Database. Clinical Trials Transformation Initiative (CTTI)." The terms are non-SPDX; commercial use is not explicitly prohibited but also not blanket-authorised, see Review notes.

## MCP / connector notes

`navisbio/AACT_clinicaltrials_MCP` wraps the Postgres mirror with read-only SQL helpers and is the only AACT-specific MCP found. Generic Postgres MCPs (e.g. `modelcontextprotocol/servers/postgres`) also work once credentials are configured. An ideal dedicated AACT MCP would expose: `run_query` (read-only, with row-cap), `describe_table`, `list_studies_by_condition`, `get_outcomes_for_study`, `get_sponsors_for_study`, `cross_registry_lookup` (NCT to EudraCT/EU CT via `id_information`), with schema introspection, query-cost estimation, and connection-pool management to stay within the 10-connection cap. The connector should abstract over (a) live DB vs. dated snapshot, (b) the verbose `ctgov` schema, and (c) MeSH-tag traversal in `browse_conditions`.

## Review notes

- `license`: AACT terms are non-SPDX. Used `AACT-CTTI-Attribution` as a canonical kebab-case short name; the underlying data is US Government public domain (it is a mirror of ClinicalTrials.gov), but CTTI's redistribution terms add an attribution requirement. Flag if the project prefers `US-Government-Public-Domain` (truer to source) or wants a new canonical short name added.
- `cost`: chose `free-with-registration` because an account is mandatory for live database access, even though static snapshots are downloadable anonymously. Both access modes are no-charge.
- `type`: classified as `database` (Postgres) + `bulk-download` (snapshot archives). No REST API surface; agents must use a SQL client or download a dump.
- `access_test`: omitted. The standard test pattern is a `curl` HTTP call, but AACT exposes only a PostgreSQL endpoint requiring registered credentials. A future revalidation pattern would be a `psql -c "select count(*) from ctgov.studies"` call with `${AACT_USER}` / `${AACT_PASSWORD}` env vars, but that doesn't fit the current `access_test` shape cleanly. Consider whether the schema should support `connection_test` for DB-only sources.
- Potential new join key for review: `WHO_UTN` (Universal Trial Number, ICMJE-recommended). Entity type: clinical_trial. Pattern: `^U[0-9]{4}-[0-9]{4}-[0-9]{4}$`. Already flagged in `clinicaltrials-gov.md`; AACT exposes it in `id_information.id_type = 'OTHER'` rows where the value matches the WHO UTN pattern. Re-flagging for emphasis.
- Duplicate-coverage check: `clinicaltrials-gov.md` already exists for the upstream source. AACT is a distinct access surface (relational SQL vs. REST JSON), worth its own entry per the project's "one entry per file, one file per access surface" intuition. Confirm this is the right call vs. merging into the existing entry.
