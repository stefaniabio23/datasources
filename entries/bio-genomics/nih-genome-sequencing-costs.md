---
id: nih-genome-sequencing-costs
name: NHGRI DNA Sequencing Costs
domain: bio-genomics
entry_kind: time-series
description: NHGRI-tracked annual cost-per-genome and cost-per-megabase data for human DNA sequencing at NIH-funded genome sequencing centers, 2001 to 2022.
homepage_url: https://www.genome.gov/about-genomics/fact-sheets/Sequencing-Human-Genome-cost
docs_url: https://www.genome.gov/about-genomics/fact-sheets/DNA-Sequencing-Costs-Data
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "not applicable (bulk file download)"
bulk_available: true
frequency: "irregular; NHGRI states plans to update on a regular basis. Most recent table dated May 2022, page last updated May 2023."
lag: "approximately 12 months between cost-measurement date and table publication"
geography: [USA, global]
join_keys:
  - DATE
primary_keys:
  - NHGRI_COST_DATE
join_key_fields:
  - join_key: DATE
    fields: [Date]
mcp_status: api-direct-sufficient
mcp_maturity: none
mcp_notes: >
  Single small spreadsheet, two metrics, one time axis. No API needed.
  Agents should fetch the XLS directly and parse two columns
  (Cost per Mb, Cost per Genome) keyed by Date.
agent_use_cases:
  - sequencing cost benchmarking over time
  - illustrating Moore's-law-vs-sequencing-cost comparisons
  - economic modelling of population-scale sequencing
  - historical context for genomics-market analysis
last_verified: 2026-06-09
build_priority: low
notes: "Single XLS, ~20 rows. Treat as a reference time-series, not a queryable dataset."
---

# NHGRI DNA Sequencing Costs

## Why this source matters

The National Human Genome Research Institute (NHGRI), part of NIH, has tracked the cost of human DNA sequencing at its funded large-scale sequencing centers since 2001. The dataset is the canonical citation for the "sequencing got cheaper faster than Moore's law" claim that anchors most genomics-economics arguments: cost-per-genome fell from roughly $100 million in 2001 to under $1,000 by the late 2010s. Two metrics are tracked, "Cost per Megabase of DNA Sequence" and "Cost per Genome", measured at quarterly to annual cadence from 2001 through 2022. The dataset is small (~20 rows, one XLS), but the citation graph attached to it is enormous; any agent producing investor memos, market sizing, public-health policy, or biotech strategy on sequencing-driven workflows ends up referencing this table.

## Agent use cases

- sequencing cost benchmarking over time
- illustrating Moore's-law-vs-sequencing-cost comparisons
- economic modelling of population-scale sequencing
- historical context for genomics-market analysis

## Join strategy

The only canonical join key this source exposes is `DATE` (ISO 8601 date column in the XLS). There are no entity identifiers, no gene IDs, no organisation IDs; rows are dated cost observations. Cross-source joins are date-axis joins: pair with semiconductor cost-per-transistor series (e.g. Our World in Data's Moore's law dataset) for the classic comparison chart, with NIH RePORTER for sequencing-program funding timelines, or with SRA / GenBank submission counts for cost-to-deposit-volume correlations.

Source-internal identifier is just the observation `Date`; no row-level primary key beyond that. No proposal for new canonical join keys here.

## Access notes

Single Excel file, no API. Direct download:

```
https://www.genome.gov/sites/default/files/media/files/2023-05/Sequencing_Cost_Data_Table_May2022.xls
```

Mirror the file on first fetch; the URL embeds a version-date path segment (`2023-05`, file stem `Sequencing_Cost_Data_Table_May2022.xls`) and will rotate when NHGRI publishes the next update. To check freshness, scrape the data fact-sheet page (`/about-genomics/fact-sheets/DNA-Sequencing-Costs-Data`) and compare the file href; the page also carries a "last updated" footer. Columns: `Date`, `Cost per Mb`, `Cost per Genome`. Cost basis includes labor, reagents, sequencing-instrument amortisation over 3 years, direct informatics, database submission, and indirect costs. Excludes QC, technology development, downstream analysis, and project management. Quality floor is Phred20 with coverage targets per platform (Sanger 6x, 454 10x, Illumina/SOLiD 30x).

The page is a US federal-government work and therefore in the public domain under 17 USC 105; NHGRI explicitly invites reuse of the graphs in presentations and teaching materials. No registration, no rate limit (it is a static file). No bulk-download endpoint beyond this one file because the dataset is the one file.

## MCP / connector notes

No MCP exists and none is warranted. The data is one static XLS that fits comfortably in working memory; any agent can fetch and parse it with two lines of pandas. If a connector were built, the only useful surface would be `get_cost_per_genome(date)` and `get_cost_per_megabase(date)` with date-range queries, which is strictly worse than just shipping the parsed table. Build priority: low. The right pattern is to mirror the XLS into a project's local data tree and re-fetch quarterly.

## Review notes

- License: marked `US-Government-Public-Domain` (NHGRI is an NIH institute, 17 USC 105 applies). Consistent with the documented known-cases list in SCHEMA.md.
- `entry_kind: time-series` because the dataset is two metrics on a date axis; not a registry of entities.
- No new canonical join keys flagged. `DATE` is sufficient.
- Considered logging the file's versioned URL as a primary key, but the dataset has no row-level identifier other than `Date`, so `NHGRI_COST_DATE` is recorded as the source-native primary key (free-form, source-internal).
- Update cadence is irregular; the most recent published file is dated May 2022 with a May 2023 page refresh. NHGRI states intent to update on a regular basis but has not committed to a cadence. Agents relying on this dataset for recent benchmarks (post-2022) need to caveat that the official table lags.
