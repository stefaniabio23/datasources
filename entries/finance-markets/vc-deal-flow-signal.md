---
id: vc-deal-flow-signal
name: VC Deal Flow Signal
domain: finance-markets
entry_kind: panel
description: Quarterly longitudinal panel of GitHub engineering-velocity metrics across ~55 venture-backed startups and ~20 sectors, hosted on Hugging Face as three CSV/Parquet configurations.
homepage_url: https://huggingface.co/datasets/the-data-nerd/vc-deal-flow-signal
docs_url: https://huggingface.co/datasets/the-data-nerd/vc-deal-flow-signal
type:
  - dataset-dump
  - bulk-download
  - rest-api
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "Hugging Face Hub fair-use; datasets-server endpoints typically 120 req/min anonymous"
bulk_available: true
frequency: quarterly
lag: "unknown; v1.0.0 covers Q3 2025 through Q2 2026"
geography: [global, USA, GBR, EU, CAN]
join_keys:
  - DATE
join_key_fields:
  - join_key: DATE
    fields: [period]
primary_keys:
  - STARTUP_SLUG
  - SECTOR_SLUG
  - PERIOD
mcp_status: mcp-exists
mcp_maturity: official
mcp_package:
  - github.com/evalstate/hf-mcp-server
mcp_notes: >
  Hugging Face publishes an official MCP server fronting the Hub, datasets-server,
  and Spaces. It exposes dataset discovery and metadata but does not stream row
  content; for actual panel analysis an agent should download the CSV/Parquet
  files via the Hub or the datasets library directly.
agent_use_cases:
  - venture deal-flow leading-indicator backtests
  - sector-level engineering-velocity comparisons
  - startup-stage classification from commit activity
  - fundraise-timing prediction research
  - alt-data feature engineering for VC sourcing
access_test:
  command: "curl -sf 'https://datasets-server.huggingface.co/info?dataset=the-data-nerd%2Fvc-deal-flow-signal'"
  expected_status: 200
  expected_fields: [dataset_info.sector_aggregates.features.period, dataset_info.sector_aggregates.features.sector_slug, dataset_info.sector_aggregates.features.avg_commit_velocity_14d]
last_verified: 2026-06-09
build_priority: low
notes: >
  Small dataset (306 rows, 49 KB) and a thin research artefact rather than a live
  feed. Underlying signals come from the public GitHub REST API; an agent that
  wants fresh velocity numbers should hit GitHub directly. Startups are
  identified by free-text name and a kebab-case slug (e.g. paperless-ngx,
  langchain-ai); no CIK, ticker, ISIN, or domain field is published.
---

# VC Deal Flow Signal

## Why this source matters

`the-data-nerd/vc-deal-flow-signal` is a Hugging Face dataset that publishes a quarterly panel of GitHub engineering-velocity metrics for roughly 55 venture-backed startups, grouped into about 20 sectors, covering Q3 2025 through Q2 2026 at v1.0.0. The thesis the data was built to test is that sustained acceleration in commit volume, contributor count, and deploy cadence precedes fundraise announcements by 6 to 12 weeks. For an agent doing VC sourcing, deal-flow scoring, or alt-data feature engineering, this is a pre-aggregated, pre-classified starting point for that hypothesis, with the heavy lifting (signal type categorisation, sector aggregation, top-mover identification) already done.

Secondary domain: `consumer-signal`. Commit velocity is a developer-attention proxy in the same family as Hacker News and GitHub Trending; pair on the startup slug or the linked GitHub org when the goal is breadth of engineering signal rather than fundraise prediction.

## Agent use cases

- venture deal-flow leading-indicator backtests
- sector-level engineering-velocity comparisons
- startup-stage classification from commit activity
- fundraise-timing prediction research
- alt-data feature engineering for VC sourcing

## Join strategy

The only canonical join key the file format itself carries is `DATE`, exposed as a quarterly string in the `period` column (`q3-2025` through `q2-2026`). Joining at quarterly granularity is coarse; for tighter joins agents will need to resolve the startup name back to a richer identifier set externally.

Startups are identified by a free-text `top_mover_name` and (in the per-startup config) a kebab-case slug that matches the GitHub organisation handle for most entries (`paperless-ngx`, `langchain-ai`, `roboflow`, `nocobase`). That slug is the natural bridge to: the GitHub REST API (org or repo metadata), Crunchbase or PitchBook for funding rounds, Companies House or SEC EDGAR for legal-entity lookup, and OpenCorporates for cross-jurisdiction matching. None of those joins are pre-resolved in the dataset itself.

Sectors are exposed as free-text labels and kebab-case slugs (`ai-ml`, `climate-tech`, `developer-tools`); there is no GICS, NAICS, or SIC code attached, so any sector-level join to corporate-fundamentals sources requires a manual crosswalk.

A `STARTUP_GITHUB_ORG` join key is flagged below as a potential future addition once a second GitHub-keyed source lands in the directory.

## Access notes

**Start at:** `https://huggingface.co/datasets/the-data-nerd/vc-deal-flow-signal` for the dataset card and a row preview. The dataset is published as three configurations: `startup_signals` (~275 rows, per-startup per-quarter), `sector_aggregates` (~100 rows, per-sector per-quarter), and `signal_type_timeseries` (~80 rows, per-signal-type per-quarter).

**Bulk download:** Each configuration is auto-converted to Parquet by the Hub and is also available as the original CSV. Pull via the `datasets` Python library (`datasets.load_dataset("the-data-nerd/vc-deal-flow-signal", "startup_signals")`) or the Hub HTTP API.

**Auth:** None for public datasets. A free account token raises rate limits and is recommended for repeated programmatic access via the Hub API.

**Rate limits:** Standard Hugging Face Hub fair-use applies. The `datasets-server` metadata endpoints are anonymous-friendly; large bulk pulls should use the `huggingface_hub` client which handles caching and resumption.

**Freshness check:** The dataset card lists the version (currently v1.0.0) and the covered quarter range. The dataset is also archived to Zenodo: concept DOI `10.5281/zenodo.19650919`, v1.0.0 DOI `10.5281/zenodo.19650920`. No published refresh cadence beyond the quarterly sampling implicit in the data; treat as a static research artefact unless the operator publishes a new version.

**License nuance:** `CC-BY-4.0`. Attribution to `the-data-nerd` (Hugging Face handle) is required. The underlying GitHub data was collected via the public REST API and is subject to GitHub's own terms; the dataset's licence only covers the derived metrics, not republication of raw repository content.

**Companion surfaces:** A live dashboard at `https://signals.gitdealflow.com` and a Hugging Face Space (`the-data-nerd/vc-deal-flow-explorer`) front the same data interactively; for programmatic work the dataset files are the canonical source.

## MCP / connector notes

Hugging Face publishes an official MCP server (`evalstate/hf-mcp-server`, also surfaced via the Hub's MCP feature) that exposes dataset, model, and Space discovery plus metadata reads. That covers the "find this dataset, read its card, list its configs" path. It does not stream row content, so an agent doing actual panel analysis should download the CSV or Parquet files via the `datasets` library or the Hub HTTP API and load them into a dataframe locally.

A bespoke MCP wrapper for this specific dataset would add little: there are three small CSV files at stable URLs and the schema is documented. The higher-value connector in this space is a generic GitHub-engineering-velocity MCP that computes the same signals (commit velocity, contributor counts, deploy cadence) live against the GitHub REST API for any org, with this dataset usable as a labelled training set or baseline.

## Review notes

- License `CC-BY-4.0` is on the standard SPDX list and matches schema convention.
- Owner is the Hugging Face handle `the-data-nerd`; no legal entity, funding source, or governance statement is disclosed on the dataset card or the linked `gitdealflow.com` site. The dataset is archived to Zenodo with DOIs, which is a positive provenance signal, but treat the operator as unverified.
- Geography codes used: ISO_3 (`USA`, `GBR`, `CAN`) plus the region label `EU`. The source publishes `US / UK / EU / APAC / Canada / LATAM / MENA`; mapped to the closest ISO_3 codes where unambiguous, kept `global` and `EU` as region labels.
- Potential new join key for review: `STARTUP_GITHUB_ORG`
  - Entity type: github_organisation
  - Pattern: `^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$` (GitHub's org-handle rule: 1-39 chars, alphanumeric or single hyphens, no leading or trailing hyphen)
  - Other datasets that would use it: GitHub Archive on BigQuery, GH Archive, GitHub Trending exports, ossinsight.io, the public GitHub REST API itself, and any future commit-activity or developer-attention dataset. Skip unless a second GitHub-keyed source justifies promotion.
- Potential new join key for review: `CRUNCHBASE_ORG_PERMALINK` or `CRUNCHBASE_UUID`
  - Entity type: venture_backed_company
  - Pattern: kebab-case permalink (`stripe`, `openai`) or UUID
  - Other datasets that would use it: Crunchbase, Dealroom, PitchBook, Tracxn, CB Insights. Useful once any private-markets entity source is catalogued.
- The `entry_kind: panel` choice fits the three-axis (startup x quarter x signal-type) structure; an argument for `time-series` exists if only the sector-aggregate config is loaded, but the per-startup config has clear cross-sectional structure.
- `access_test` executed at last_verified date: `curl -sf https://datasets-server.huggingface.co/info?dataset=the-data-nerd%2Fvc-deal-flow-signal` returned 200 with the full schema for all three configs.
