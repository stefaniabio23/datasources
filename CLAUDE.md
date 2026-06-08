## project: datasources

## What this project is

A public, agent-readable registry of APIs, datasets, and databases. Catalogues high-signal data sources for AI agents with canonical join keys, published as a live Google Sheet. MVP scope: 50 structured entries + one Skill to add new entries + minimal scripts to validate, generate, and publish.

The structural piece that distinguishes this from `awesome-public-datasets`, `data.gov`, Kaggle is the join-key reverse index (`generated/join-key-index.md`), derived from per-entry YAML.

## Architecture

```
datasources/
├── README.md                       # public front door
├── SCHEMA.md                       # human spec
├── CLAUDE.md                       # this file
├── schema/
│   ├── entry.schema.yaml           # JSON Schema for entry YAML frontmatter
│   └── join-keys.yaml              # canonical join-key registry
├── entries/<domain>/<slug>.md      # one file per dataset, YAML + markdown body
├── skills/
│   └── add-dataset-entry/SKILL.md  # project-local Skill: URL -> compliant entry
├── scripts/
│   ├── validate_entries.py         # JSON Schema + registry + body-heading checks
│   ├── generate.py                 # rebuild generated/ outputs from entries/
│   └── publish_to_sheet.py         # overwrite a Google Sheet from dataset-table.csv
├── generated/                      # index.json, dataset-table.csv, join-key-index.md
└── .github/workflows/
    └── publish.yml                 # CI: validate, generate, publish to Sheet
```

11 domains: `academic`, `clinical-biotech`, `bio-genomics`, `public-health`, `healthcare-claims`, `finance-markets`, `corporate-registry`, `news-events`, `consumer-signal`, `government-open-data`, `geospatial`.

## Commands

Setup: `pip install jsonschema pyyaml google-api-python-client google-auth`
Validate: `python3 scripts/validate_entries.py`
Generate: `python3 scripts/generate.py`
Publish to Sheet: `GOOGLE_SERVICE_ACCOUNT_JSON=... GOOGLE_SHEET_ID=... python3 scripts/publish_to_sheet.py`
Add entry: invoke the Skill in chat ("add a dataset entry for [URL]") or `/add-dataset-entry [URL]`

## Conventions

- **The schema is immutable during entry creation.** Skills and agents do not modify `schema/entry.schema.yaml` or `schema/join-keys.yaml`. They populate values only.
- **One entry per file.** Domain folder = primary domain; secondary domains noted in body, not in YAML.
- **Join keys are canonical.** Source-side names ("trial id", "NCT", "ClinicalTrialsGov ID") map to one canonical key (`NCT_ID`). New canonical keys are PR'd separately to `schema/join-keys.yaml`.
- **License field uses SPDX where possible**, otherwise canonical kebab-case short names (`US-Government-Public-Domain`, `GDELT-Open-Data`, `OGL-3.0`, `Crown-Copyright`, `ECDC-Public-Data`). See SCHEMA.md § License conventions.
- **Body has 6 required H2 headings in canonical order:** Why this source matters / Agent use cases / Join strategy / Access notes / MCP / connector notes / Review notes. The validator soft-checks this; warnings do not block.
- **`mcp_package` is an array of strings**, not a single string. Use a list even when only one MCP exists.
- **GitHub is canonical.** The Google Sheet is a downstream render target overwritten on each publish run. No bidirectional sync.

## Skills and agents

Project-local:
- `skills/add-dataset-entry/` — takes a URL, produces one compliant entry. Does not modify schema. See `skills/add-dataset-entry/SKILL.md`.

Global skills referenced:
- None in active workflow yet.

## Notes

MVP target: 50 entries. Out-of-MVP items are listed in `README.md` § Future plans; do not expand schema, lifecycle, scoring, or generated outputs beyond MVP without explicit user confirmation.

For batch porting (50+ new entries at once), use a Workflow with parallel fan-out over the add-dataset-entry Skill. Concurrency cap is 16. Each agent reads the spec, researches its target, writes one entry. Validator runs separately after.
