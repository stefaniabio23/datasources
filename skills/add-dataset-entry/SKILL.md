---
name: add-dataset-entry
description: Create one compliant dataset entry in datasources from a URL. Writes entries/<domain>/<slug>.md; does not modify schema or registry.
---

Create ONE dataset entry in the `datasources` project from a supplied URL. Writes `entries/<domain>/<slug>.md` with YAML frontmatter + standardised markdown body. Does not modify the schema, enum lists, or join-key registry.

**Trigger phrases:** "add a dataset entry for [URL]", "add [source] to the directory", "create an entry for [URL]". Slash form: `/add-dataset-entry [URL]`. Confirm the URL with Stephanie before starting if ambiguous.

**Inputs:**
- Required: dataset/API/database URL.
- Optional: preferred `domain` (one of the 11 enum values in SCHEMA.md).
- Optional: known dataset name.
- Optional: free-text notes from Stephanie.

**Project location:** `~/Projects/datasources/`. All paths below are relative to that root.

---

## Hard rules

**The schema is immutable during entry creation.** Do not:

- Add fields to `schema/entry.schema.yaml`.
- Add enum values for `domain`, `type`, `auth_required`, `cost`, `mcp_status`, `mcp_maturity`, or `build_priority`.
- Add canonical join keys to `schema/join-keys.yaml`.

If a source needs a new field, enum value, or join key, flag it in the entry body under `## Review notes`. Stephanie reviews and PRs the change separately.

**Prefer `unknown` over hallucinated values.** Honest gaps are useful signal. Hallucinated values poison the registry. If a required string field can't be determined, write `unknown`. If an optional field is uncertain, omit it.

**One entry per invocation.** No batching. No modifying or reordering existing entries. No running the validator or the generator scripts (those are separate scripts run by Stephanie).

---

## Steps

### 1. Load the contracts

Read, in this order:

a. `SCHEMA.md` (human contract).
b. `schema/entry.schema.yaml` (machine contract).
c. `schema/join-keys.yaml` (canonical join-key vocabulary).

Then skim the three reference entries to internalise YAML-field style and prose tone (not headings; use the headings in Step 6):

- `entries/academic/openalex.md`
- `entries/corporate-registry/companies-house.md`
- `entries/news-events/gdelt.md`

### 2. Research the source

Use WebFetch on the supplied URL and follow links to:

a. Landing page (description, owner, license).
b. Developer / API docs (auth, rate limits, endpoints, field documentation).
c. Downloads / bulk page (bulk availability, formats, refresh cadence).
d. Terms / license page (license string, redistribution restrictions).
e. About / contact / FAQ (owner, funding, governance).

If a page is JS-heavy and WebFetch returns nothing useful, try the Wayback Machine, the source's GitHub README, or a community-maintained docs mirror. Never make up content the source doesn't actually publish.

### 3. Classify

**Domain.** Pick one of the 11 enum values. If none fits, stop and ask Stephanie. Multi-domain sources (SEC EDGAR covers `finance-markets` and `corporate-registry`) pick the primary; mention the secondary in `## Why this source matters`.

**Type.** Pick all access modes from the closed enum: `rest-api`, `bulk-download`, `dataset-dump`, `database`, `web-ui`, `scraper-required`, `unofficial-api`, `socrata`, `odata`, `powerbi-export`. Most real sources are multi-mode.

**MCP status.** Search for existing MCPs:

- `github.com/modelcontextprotocol` (official servers)
- `github.com/search?q=mcp+<source-name>` (community)
- `npmjs.com/search?q=@modelcontextprotocol+<source-name>`
- `pypi.org/search/?q=mcp+<source-name>`

Heuristic for `mcp-needed-high-value` vs `mcp-needed-low-value`: if three or more entries in the directory would want the same connector (overlapping audience), it's high-value.

### 4. Map identifiers

Highest-value step. Each source exposes two kinds of identifiers, both belong in YAML:

a. **Native primary keys.** Identifiers the source mints to uniquely identify its own entities (`OPENALEX_WORK_ID`, `GLOBALEVENTID`, `COMPANIES_HOUSE_OFFICER_ID`). Populate `primary_keys` (free-form, no registry constraint). When a primary key has cross-source utility AND is in the registry (e.g. Companies House mints `COMPANIES_HOUSE_NUMBER`, which is also a canonical key), list it in BOTH `primary_keys` and `join_keys`.

b. **Canonical join keys.** Identifiers from `schema/join-keys.yaml` the source exposes for cross-source joining (`DOI`, `ORCID`, `ROR`). Map source-side names ("trial id", "NCT number", "ClinicalTrialsGov ID") onto the canonical key (`NCT_ID`). Populate `join_keys` (must reference the registry).

c. **Field paths.** For each value in `join_keys`, populate `join_key_fields` with the source-side JSON paths where it actually appears:

   ```yaml
   join_key_fields:
     - join_key: DOI
       fields: [doi, ids.doi]
     - join_key: ROR
       fields: [authorships.institutions.ror]
   ```

   This is what makes the directory executable rather than descriptive. The pairwise join-graph is generated from these.

d. **If a useful join key isn't in the registry**, do not invent. Add to `## Review notes`:

```
Potential new join key for review: <PROPOSED_KEY>
  Entity type: <e.g. clinical_trial, drug_product, geographic_feature>
  Pattern: <regex or short description>
  Other datasets that would use it: <names if you can identify any>
```

Stephanie reviews and decides whether to PR the new key into `schema/join-keys.yaml`.

### 5. Build the access test

If the source has a programmatic API:

a. Construct a `curl -sf` one-liner against a stable, low-cost endpoint (search query, single-record fetch, count endpoint).
b. Use env-var placeholders for auth (`${SOURCE_KEY}`). Never inline credentials.
c. Run it. Confirm 200 + expected fields present.
d. Record `command`, `expected_status`, `expected_fields` under `access_test:`.

If the source requires auth and you don't have credentials:

a. Construct the command with the env-var placeholder.
b. Set `last_verified` to today.
c. Include in YAML `notes:` → `access_test not yet executed; requires ${VAR}`.

If the source has no API (bulk- or web-only):

a. Omit `access_test`.
b. In `## Access notes`, document how to verify freshness (e.g. "check the latest file date at `<url>`").

### 6. Write the entry

Path: `entries/<domain>/<slug>.md`.

Slug is kebab-case derived from the source name:

- "OpenAlex" → `openalex`
- "Companies House (UK)" → `companies-house`
- "ClinicalTrials.gov" → `clinicaltrials-gov`
- "GDELT (Global Database...)" → `gdelt`

**YAML frontmatter.** Fill every required field. Include optional fields where you have confident values. Order fields as they appear in `entry.schema.yaml`. Omit, don't invent.

**YAML gotcha:** never put unquoted `[` or `]` characters inside a flow-list `[...]`. YAML parses nested brackets as nested sequences and the file fails to parse. If a field path contains brackets (e.g. `ArticleIdList.ArticleId[IdType=pubmed]`), use block-list style with quoted strings:

```yaml
fields:
  - MedlineCitation.PMID
  - "PubmedData.ArticleIdList.ArticleId[IdType=pubmed]"
```

**Markdown body.** Required headings, in this order, no others:

```
# <Dataset Name>

## Why this source matters
One paragraph. What it is, who runs it, why an agent should care. Mention any secondary domains here.

## Agent use cases
3-5 bulleted short verb phrases. Match `agent_use_cases` in YAML.

## Join strategy
Which canonical join keys this source exposes; what to pair it with. Mention source-internal IDs here (not in YAML). If you flagged a new join key for review, name it here too.

## Access notes
Concrete path: which endpoint to hit first, auth setup, rate-limit gotchas, bulk-vs-API tradeoff. Short.

## MCP / connector notes
If `mcp-exists`: package, maturity tier, known gaps.
Otherwise: suggested MCP surface (3-5 endpoints), what's tricky, what the MCP must abstract over.

## Review notes
Anything needing human attention before merge: potential new domains, enum values, join keys, license ambiguity, conflicts with existing entries. If nothing, write `None.`
```

Keep the body tight; target under 200 lines. Prose lives in the body, structured fields in YAML.

### 7. Report

After writing the entry, report:

- Path of the file created.
- Any `## Review notes` items flagged.
- Whether `access_test` was executed (and result) or just constructed.
- One suggested next entry if Stephanie is iterating.

Do not run `scripts/validate_entries.py`. Do not regenerate `generated/` outputs. Do not commit.

---

## What this skill does NOT do

- Does not modify `schema/entry.schema.yaml` or `schema/join-keys.yaml`.
- Does not add enum values, even when a source obviously needs one. Flag in `## Review notes`.
- Does not run the validator or the generator scripts.
- Does not commit or push to git.
- Does not write more than one entry per invocation.
- Does not modify entries that already exist. A separate `update-dataset-entry` skill handles that (not yet implemented).
- Does not OCR PDFs or scrape JS-heavy pages with Playwright. If WebFetch can't read the docs, fall back to Wayback / GitHub README / community mirrors.

---

## Usage examples

Natural language:

> add a dataset entry for https://api.crossref.org/

> add Semantic Scholar to the directory: https://www.semanticscholar.org/product/api

> create an entry for https://clinicaltrials.gov/data-api/api, domain clinical-biotech

Slash command:

```
/add-dataset-entry https://api.crossref.org/
/add-dataset-entry https://www.semanticscholar.org/product/api --domain academic
```

---

## Context

The directory is the EF-facing artifact: a public agent-readable catalogue of APIs and datasets. The two structural pieces that distinguish it from `awesome-public-datasets` and `data.gov` are the join-key reverse index (`generated/join-key-index.md`) and the MCP gap map (`generated/mcp-gap-map.md`), both generated from per-entry YAML.

The Skill's job is to populate that YAML accurately so the generators can do their work. **Quality of join-key mapping is the load-bearing variable.** Bad mapping breaks the reverse index, which breaks the project's main differentiator. When in doubt about a join key, flag for review rather than guess.
