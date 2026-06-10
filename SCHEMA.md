# SCHEMA.md

Human-readable specification. Canonical machine-readable definitions live in:

- `schema/entry.schema.yaml` — JSON Schema for entry YAML frontmatter
- `schema/join-keys.yaml` — canonical join-key registry

## Design principle

Every entry answers four agent questions:

1. **Can I access this data?** (auth, cost, rate limit, bulk vs API)
2. **Can I trust and reuse this data?** (license, freshness, notes)
3. **What entities or identifiers can I join on?** (`join_keys` from the registry)
4. **Is there an MCP, API, or tooling path for autonomous use?** (`mcp_status`)

If a field does not help answer one of those four, it belongs in the markdown body, not the YAML frontmatter.

## Entry layout

Every entry is one file at `entries/<domain>/<slug>.md` with two parts:

1. **YAML frontmatter** between `---` lines. Structured fields, validated against `entry.schema.yaml`.
2. **Markdown body** with prose: why an agent cares, access patterns, join-key context, known gotchas.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `id` | string (kebab-case) | Matches filename without `.md`. |
| `name` | string | Display name. |
| `domain` | enum | Matches parent folder. |
| `entry_kind` | enum | What kind of source this is. See "Entry kinds" below. |
| `description` | string | One sentence. |
| `homepage_url` | URI | |
| `type` | list of enum | Access modes. Multi-mode is normal. |
| `auth_required` | enum | `none`, `api-key-free`, `api-key-paid`, `account-required`, `oauth`, `dars-or-equivalent`. |
| `cost` | enum | `free`, `freemium`, `paid`, `free-with-registration`, `free-non-commercial`. |
| `license` | string | SPDX code or canonical short name. |
| `join_keys` | list | Canonical join keys from `schema/join-keys.yaml`. |
| `mcp_status` | enum | See below. |
| `last_verified` | ISO date | |

## Optional fields

- `docs_url`
- `rate_limit` — free-form single line (e.g. "10 req/sec, 100K/day with polite pool")
- `bulk_available` — boolean
- `frequency` — update cadence
- `lag` — typical freshness delay
- `geography` — list (ISO-3, region names, or "global")
- `mcp_maturity` — `official` | `community` | `experimental` | `none`. Required when `mcp_status: mcp-exists`.
- `mcp_package` — list of package names or repo URLs (e.g. `["github.com/org/mcp-foo"]`). Required when `mcp_status: mcp-exists`. Use a list even when only one MCP exists; multiple community MCPs are common.
- `mcp_notes` — short design notes for the connector
- `agent_use_cases` — list of short verb phrases ("literature search", "company diligence")
- `access_test` — `{ command, expected_status, expected_fields }`. Executable for future revalidation.
- `build_priority` — `high` | `medium` | `low`. Optional, free-form ranking hint.
- `notes` — free-text catch-all; prefer the markdown body when possible.
- `primary_keys` — list of source-native identifiers the source mints (e.g. `[OPENALEX_WORK_ID, OPENALEX_AUTHOR_ID]`). Free-form; not required to be in `schema/join-keys.yaml`.
- `join_key_fields` — list of `{join_key, fields[]}` objects mapping each canonical join_key to the source-side field paths that carry it (e.g. `{join_key: DOI, fields: [doi, ids.doi]}`).

### v3 additions (2026-06-10)

Added to support consumer-side reasoning about provenance and point-in-time
reconstruction. All optional; existing entries remain valid without them.

- `is_directory` — boolean. True when this entry is a source-discovery
  directory (data.gov, FRED's catalog, Nasdaq Data Link, etc.) rather
  than a primary data source. Lets consumers treat directories without
  building a separate provenance layer.
- `discovered_via` — id of the directory or upstream source that
  surfaced this entry. Gives provenance for free: "which discovery
  channels yield signals that survive out-of-sample?"
- `structure` — enum, orthogonal to `entry_kind`: `panel | time-series
  | cross-section | event-log | registry-snapshot`. Captures what the
  data PERMITS for analysis. The binary "time-series vs registry" leaks
  at the edges (a registry kept as snapshots is an event-log when
  queried with vintage history); this is tighter.
- `pit_reconstructable` — boolean. True when the source supports
  point-in-time reconstruction (vintage data retrievable for any past
  date). False is the conservative default and forces analysts to
  curate vintage handling explicitly.
- `revisions_possible` — boolean. True when values get restated after
  first publication. A backtest against a revisions-possible target
  without vintage handling may be optimistic relative to what was
  observable in real time.
- `release_lag_days` — integer days from observation to publication.
  Distinct from the free-form `lag` (prose); when both are present,
  `release_lag_days` is the operational value the pipeline uses.

## Entry kinds

Closed enum classifying what kind of source each entry is. Required field. Lets agents filter by query shape.

| Value | What it is |
|---|---|
| `registry` | Entity directory — each row is one canonical thing (Companies House, ClinicalTrials.gov, ORCID). |
| `time-series` | Periodic value over time (FRED, FluNet, Google Trends). |
| `panel` | Multi-dimensional time series with cross-sectional + temporal axes (GTEx, EIA electricity-retail-sales). |
| `event-stream` | Discrete events tagged with time + entities (GDELT, NewsAPI). |
| `knowledge-graph` | Linked entities with relationships (Wikidata, OpenAlex, OpenTargets, Ensembl). |
| `corpus` | Bulk text / document collection (Common Crawl, arXiv, Europe PMC, Reddit). |
| `reference-table` | Small lookup vocabulary (ISO codes, currency codes, language codes). |
| `geospatial` | Geographic features / spatial data (OpenStreetMap, GBIF). |
| `mixed` | Multi-dataset source where sub-datasets span several kinds (EIA, OECD, World Bank, openFDA). |

## One entry per source

`entries/` holds public source cards, one file per provider. Multi-dataset providers (EIA, OECD, World Bank, openFDA) get one entry that points at the provider's own metadata endpoints; sub-datasets, routes, and series are not modeled in this registry. The Sheet's primary tab is one flat row per source.

## Primary keys vs join keys

Two different concepts, both in the YAML:

- **`primary_keys`** = the identifiers this source itself uses to uniquely identify its own entities. Source-internal, free-form, no registry constraint. Example: OpenAlex's `OPENALEX_WORK_ID`, Companies House's `COMPANIES_HOUSE_OFFICER_ID`, GDELT's `GLOBALEVENTID`.
- **`join_keys`** = canonical identifiers (from `schema/join-keys.yaml`) this source exposes for cross-source joining. Example: OpenAlex exposes `DOI`, `ORCID`, `ROR`.

An identifier can appear in **both** lists when a source mints it AND it is in the canonical registry. Example: Companies House mints `COMPANIES_HOUSE_NUMBER` (so it goes in `primary_keys`) and that ID is also referenced by other datasets via the registry (so it also goes in `join_keys`).

**`join_key_fields`** maps each canonical `join_key` to the source-side field paths that carry it. This is what lets the generator (and agents) know where to look in actual payloads:

```yaml
join_key_fields:
  - join_key: DOI
    fields: [doi, ids.doi]
  - join_key: ROR
    fields: [authorships.institutions.ror]
```

The pairwise join-graph is **generated** from these fields across all entries, not hand-authored. Two datasets share a join when their `join_keys` overlap.

## License conventions

Prefer SPDX identifiers where the license has one: `CC0`, `CC-BY-4.0`, `CC-BY-SA-3.0`, `MIT`, `Apache-2.0`, `OGL-3.0` (UK Open Government Licence v3.0), etc.

When a license has no SPDX code, use a canonical kebab-case short name. Known cases:

- `US-Government-Public-Domain` — US federal works under 17 USC 105
- `GDELT-Open-Data` — GDELT terms (free unlimited use with attribution)
- `ECDC-Public-Data` — ECDC public data terms (free non-commercial)
- `Crown-Copyright` — UK Crown works without a more-specific licence applicable

Do not write free-text license descriptions in the YAML. Put the canonical short name in `license`; put any nuance, restrictions, or attribution requirements in `## Access notes` in the markdown body.

## mcp_status values

- `mcp-exists` — connector exists (see `mcp_maturity`, `mcp_package`)
- `mcp-needed-high-value` — broad use, no MCP, build this
- `mcp-needed-low-value` — narrow audience
- `api-direct-sufficient` — API is clean enough that an MCP wrapper adds little
- `requires-scraping` — no programmatic access; MCP would need browser automation
- `fragile-unofficial` — works via unofficial wrapper (pytrends, yfinance)

## Domains

Top-level folders in `entries/`. Each is agent-actionable, not academic taxonomy. Closed enum:

`academic`, `clinical-biotech`, `bio-genomics`, `public-health`, `healthcare-claims`, `finance-markets`, `corporate-registry`, `news-events`, `consumer-signal`, `government-open-data`, `geospatial`, `source-discovery`.

Multi-domain datasets (SEC EDGAR is both `finance-markets` and `corporate-registry`): pick the primary, mention secondary in the markdown body.

## Join keys

Canonical registry at `schema/join-keys.yaml`. Every value in `join_keys` must reference a key there. The Skill maps source-side identifier names ("trial id", "NCT number", "ClinicalTrialsGov ID") onto canonical keys (`NCT_ID`).

Adding a new canonical join key is a separate PR to `schema/join-keys.yaml`.

## What belongs in markdown body, not YAML

- Why an agent cares (prose)
- Example queries and workflow recipes
- Long-form known issues
- MCP design sketch (recommended endpoints, response shape)
- Cross-source pairing notes ("pair with X for Y")

The YAML is for agents and validators. The body is for humans.
