# datasources

An agent-readable registry of APIs, datasets, and databases.

## What this is, in one sentence

A GitHub-hosted registry of 50+ structured API/dataset/database entries with canonical join keys, published as a live Google Sheet for browsing and sharing.

## Why this exists

Existing public-data directories (`awesome-public-datasets`, `data.gov`, Kaggle) are topic-centric human indexes. They answer "what datasets exist in this category?" but not "given a research question, which dataset should an agent reach for, how does it authenticate, what can it join on?"

This directory answers the agent question. The structural piece nobody else has is **`generated/join-key-index.md`**, a reverse index of canonical identifiers (`NCT_ID`, `DOI`, `CIK`, `ROR`, etc.) mapped to the datasets that expose them. Cross-source joins become planable.

## Layout

```
datasources/
  README.md
  SCHEMA.md
  CLAUDE.md
  schema/
    entry.schema.yaml         # JSON Schema for entries/<domain>/<slug>.md
    join-keys.yaml            # canonical join-key registry
    source.schema.yaml        # for catalog/<id>/source.yaml
    dataset.schema.yaml       # for catalog/<id>/datasets/*.yaml
    field-schema.schema.yaml  # for catalog/<id>/schemas/*.schema.yaml
  entries/
    <domain>/
      <slug>.md               # public source card
  catalog/                    # layered machine metadata for multi-dataset sources
    README.md
    <source_id>/
      source.yaml             # provider-level manifest
      datasets/*.yaml         # one per dataset/route/table
      schemas/*.schema.yaml   # field-level schema per dataset
  skills/
    add-dataset-entry/SKILL.md
  scripts/
    validate_entries.py       # validate entries/ AND catalog/
    generate.py               # rebuild generated/ outputs
    publish_to_sheet.py       # multi-tab Google Sheet push
  generated/
    index.json                # all entries flattened, machine-readable
    sources.csv               # one row per source → Sources tab
    datasets.csv              # one row per catalog dataset → Datasets tab
    fields.csv                # one row per catalog field → Fields tab
    join-keys.csv             # canonical registry as flat table → JoinKeys tab
    join-key-index.md         # human-readable reverse index
  .github/workflows/
    publish.yml               # CI: validate, generate, publish to Sheet
```

## Domains

- `academic/` — scholarly graphs, papers, citations
- `clinical-biotech/` — trials, drugs, regulatory data
- `bio-genomics/` — genes, proteins, expression
- `public-health/` — disease surveillance, indicators
- `healthcare-claims/` — claims, prescribing, utilization
- `finance-markets/` — equities, macro, FX
- `corporate-registry/` — company filings, beneficial ownership
- `news-events/` — global news graphs, event extraction
- `consumer-signal/` — search trends, social, pageviews
- `government-open-data/` — federated open-data portals
- `geospatial/` — maps, weather, biodiversity

## Contributing

The `add-dataset-entry` Skill takes a dataset URL and produces a compliant entry.

1. Run the Skill with the dataset's homepage URL.
2. Skill researches the source, identifies join keys against `schema/join-keys.yaml`.
3. Skill writes `entries/<domain>/<slug>.md`.
4. `scripts/validate_entries.py` checks the entry against `entry.schema.yaml`.
5. `scripts/generate.py` rebuilds the `generated/` outputs.
6. Open a PR with one new entry + regenerated outputs.

See `SCHEMA.md` for the full field spec.

## Publishing

GitHub is canonical. The `generated/*.csv` files are also published to a multi-tab Google Sheet as a render target. Each publish run clears each target tab and overwrites it with the current CSV; the repo stays canonical, the Sheet is downstream. Tab mapping:

| CSV | Sheet tab |
|---|---|
| `generated/sources.csv` | `Sources` |
| `generated/datasets.csv` | `Datasets` |
| `generated/fields.csv` | `Fields` |
| `generated/join-keys.csv` | `JoinKeys` |

Tabs are created if missing; existing formatting on each tab persists across runs (Sheets API `values.clear` + `values.update` preserve formatting).

**Local:**

```
pip install pyyaml google-api-python-client google-auth
export GOOGLE_SERVICE_ACCOUNT_JSON="$(cat ~/.config/datasources-sa.json)"
export GOOGLE_SHEET_ID="<the spreadsheet ID from the Sheet URL>"
python3 scripts/generate.py
python3 scripts/publish_to_sheet.py
```

**CI:** `.github/workflows/publish.yml` runs validate → generate → publish on every push to `main` (when `entries/`, `schema/`, or the relevant scripts change) and on manual workflow_dispatch. Required repo secrets (Settings → Secrets and variables → Actions):

- `GOOGLE_SERVICE_ACCOUNT_JSON` — full JSON of a service account with editor access to the target Sheet
- `GOOGLE_SHEET_ID` — the spreadsheet ID

One-time service-account setup: Google Cloud Console → IAM & Admin → Service Accounts → create account → enable Sheets API on the project → generate JSON key → share the target Sheet with the service-account email as Editor.

## Status

MVP. 50 entries, schema locked, validator green, publish step ready.

## Future plans

Out of MVP scope:

- Automated quarterly access revalidation
- Full field-level schemas per dataset
- Lifecycle states beyond `last_verified` (draft, verified, stale, deprecated)
- Quality/risk scoring model
- Access-test runner with live API calls
- Dataset embedding-based recommender
- "Find datasets joinable on X" agent tool
- Search UI / GitHub Pages site
- Slack/Discord bot for new dataset suggestions
- CI tests for link rot
- Auto-changelog
- Airtable / Notion / DuckDB export
- Contributor PR/issue templates
