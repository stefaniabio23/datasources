---
id: google-patents-bigquery
name: Google Patents Public Datasets (BigQuery)
domain: government-open-data
entry_kind: registry
description: BigQuery collection of worldwide patent bibliographic data (90M+ publications from 17 countries) plus research-layer enrichments, queryable in SQL.
homepage_url: https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data
docs_url: https://github.com/google/patents-public-data
type:
  - database
  - bulk-download
auth_required: account-required
cost: freemium
license: CC-BY-4.0
bulk_available: true
frequency: quarterly
geography: [global]
join_keys: []
primary_keys:
  - PATENT_PUBLICATION_NUMBER
  - PATENT_APPLICATION_NUMBER
  - PATENT_FAMILY_ID
mcp_status: mcp-needed-low-value
agent_use_cases:
  - patent prior-art search
  - assignee patent-portfolio analysis
  - technology-trend analysis by CPC class
  - patent-to-literature linking
  - citation-network analysis
access_test:
  command: "bq query --use_legacy_sql=false 'SELECT publication_number FROM `patents-public-data.patents.publications` LIMIT 1'"
  expected_status: 200
  expected_fields: [publication_number]
last_verified: 2026-07-07
notes: "access_test not yet executed; requires a Google Cloud account and project (bq CLI authenticated via gcloud). Querying beyond the 1 TB/month free tier is billed."
---

# Google Patents Public Datasets (BigQuery)

## Why this source matters

A hosted BigQuery collection of worldwide patent bibliographic data covering 90M+ patent publications from 17 countries, with US full text, sourced from IFI CLAIMS Patent Services and published by Google Cloud as a public dataset. The core `patents-public-data.patents.publications` table appears as one wide, flat, deeply-nested table so most analysis avoids JOINs: publication and application numbers, patent family, filing/priority/grant dates, harmonized inventor and assignee names, and five classification systems (CPC, IPC, USPC, FI, F-term). A companion `google_patents_research.publications` table adds machine-translated English titles/abstracts, extracted top terms, semantic similarity vectors, forward citations, and ML embeddings. It sits at the boundary of `corporate-registry` (assignee ownership) and `academic` (patent-to-paper citation linking), but the primary agent value is government-originated open patent data at query-scale.

## Agent use cases

- patent prior-art search
- assignee patent-portfolio analysis
- technology-trend analysis by CPC class
- patent-to-literature linking
- citation-network analysis

## Join strategy

The natural cross-source identifier is the DOCDB-compatible patent publication number (e.g. `US-7650331-B1`), exposed as `publication_number` and used as the primary join across every table in the collection and against external patent sources (The Lens, USPTO, EPO OPS). Application number (`application_number`) and `family_id` group related filings. None of these three are in the canonical join-key registry yet, so they are recorded in `primary_keys` and flagged under Review notes as new-key candidates. CPC classification codes (`cpc.code`, e.g. `A61K`) and harmonized assignee names (`assignee_harmonized.name`) are strong grouping axes but are also not canonical keys; CPC is flagged as a candidate below. Assignee is a name string, not a stable identifier, so it is a fuzzy join at best (pair with a corporate registry or GLEIF LEI resolution for entity matching).

## Access notes

Access is via BigQuery, which requires a Google Cloud account and an active project for billing/quota. First query target: `patents-public-data.patents.publications` (98M rows, ~900 GB). Google hosts the dataset storage for free; you pay only for bytes scanned by your queries, with the standard 1 TB/month free query tier. Because the table is very large and wide, always select specific columns and filter early (e.g. on `country_code` or `publication_date`) to avoid full-table scans and runaway cost. Authenticate the `bq`/`gcloud` CLI or use a service account; the dataset can also be queried from the BigQuery console web UI or exported to GCS for bulk pulls. The main dataset historically refreshes on roughly a quarterly cadence; confirm the current snapshot date from the table's `Last modified` metadata in the BigQuery console before treating freshness as current.

## MCP / connector notes

No dedicated Google Patents MCP found. Generic BigQuery MCP servers can query this dataset given GCP credentials, so a bespoke connector is low-priority. A useful thin surface if built: `search_patents` (by keyword/CPC/date), `get_publication` (by publication_number), `get_assignee_portfolio` (by harmonized assignee name), `get_citations` (forward/backward), and `find_similar` (via the research-layer embeddings). The connector must abstract over SQL cost control (column pruning, partition/date filters, dry-run byte estimates) and the flat-but-deeply-nested `REPEATED RECORD` shape of columns like `cpc`, `assignee_harmonized`, and `title_localized`.

## Review notes

License short name `CC-BY-4.0` is SPDX-standard; no new short name introduced.

Potential new join keys for review (none currently in `schema/join-keys.yaml`):

Potential new join key for review: PATENT_PUBLICATION_NUMBER
  Entity type: patent_publication
  Pattern: DOCDB-format country-number-kind, e.g. "US-7650331-B1" (`^[A-Z]{2}-[A-Z0-9]+-[A-Z][0-9]?$`)
  Other datasets that would use it: The Lens, USPTO PatentsView, EPO OPS, Google Patents

Potential new join key for review: PATENT_APPLICATION_NUMBER
  Entity type: patent_application
  Pattern: office-specific application number (heterogeneous across patent offices)
  Other datasets that would use it: The Lens, USPTO, EPO OPS

Potential new join key for review: CPC_CODE
  Entity type: patent_classification
  Pattern: Cooperative Patent Classification symbol, e.g. "A61K" / "H04L9/32" (`^[A-H][0-9]{2}[A-Z]([0-9]+/[0-9]+)?$`)
  Other datasets that would use it: The Lens, USPTO, EPO, any patent classification analysis

Assignee is a harmonized name string, not a stable identifier; recommend resolving to LEI or a corporate-registry key at join time rather than adding an "assignee" join key.
