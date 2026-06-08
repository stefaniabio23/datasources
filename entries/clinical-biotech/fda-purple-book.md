---
id: fda-purple-book
name: FDA Purple Book
domain: clinical-biotech
description: FDA database of all US-licensed biological products (including biosimilars and interchangeables) with BLA numbers, reference-product relationships, exclusivity dates, and patent listings.
homepage_url: https://purplebooksearch.fda.gov/
docs_url: https://purplebooksearch.fda.gov/index.cfm?event=userguide
type:
  - web-ui
  - bulk-download
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "none documented; static monthly CSV/XLSX downloads"
bulk_available: true
frequency: monthly
lag: "monthly release reflects approvals through prior month"
geography: [USA]
join_keys: []
primary_keys:
  - PURPLE_BOOK_BLA_NUMBER
  - PURPLE_BOOK_LICENSE_NUMBER
  - PURPLE_BOOK_PRODUCT_NUMBER
  - PURPLE_BOOK_SUPPLEMENT_NUMBER
join_key_fields: []
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No MCP exists. Bulk-only source, narrow audience (biosimilar/biologic regulatory analysts).
  Better served by a small loader that ingests the monthly CSV into a queryable table than by
  a bespoke connector. If wrapped, surface should be search_biologic(core_name), get_by_bla,
  list_biosimilars_of(reference_bla), get_exclusivity_dates.
agent_use_cases:
  - biologic licensure lookup
  - biosimilar and interchangeable identification
  - reference-product exclusivity tracking
  - BLA-number resolution to proprietary and proper names
  - patent-list and exclusivity-expiry monitoring
access_test:
  command: "curl -sfI -A 'Mozilla/5.0' 'https://www.accessdata.fda.gov/drugsatfda_docs/PurpleBook/2026/purplebook-search-May-data-download.csv'"
  expected_status: 200
  expected_fields: []
last_verified: 2026-06-08
build_priority: low
notes: "No public REST API. Bulk monthly CSV/XLSX is the only programmatic surface; web UI for human search. access_test verifies the bulk CSV is reachable, not field content."
---

# FDA Purple Book

## Why this source matters

The Purple Book is the FDA's authoritative database of all US-licensed biological products: every product approved under section 351(a) of the Public Health Service Act (originator biologics) and 351(k) (biosimilars and interchangeables), plus FDA-licensed allergenic, cellular and gene therapy, hematologic, and vaccine products from CBER. Maintained jointly by CDER and CBER. It is the canonical place to look up which biosimilars and interchangeables exist for a given reference product, when each was licensed, when reference-product or interchangeable exclusivity expires, and which patents have been listed under the Biological Product Patent Transparency provisions of the Consolidated Appropriations Act of 2021. Federal-government work, so the content is US public domain. Secondary relevance to `government-open-data`.

## Agent use cases

- biologic licensure lookup
- biosimilar and interchangeable identification
- reference-product exclusivity tracking
- BLA-number resolution to proprietary and proper names
- patent-list and exclusivity-expiry monitoring

## Join strategy

The Purple Book's primary identifier is the `BLA Number` (Biologics License Application, six-digit zero-padded), with secondary `License Number`, `Product Number`, and `Supplement Number` for SKU-level disambiguation. None of these are currently in `schema/join-keys.yaml`. `BLA Number` is the same identifier exposed by openFDA's drug endpoints and Drugs@FDA, and would be the natural anchor for joining biologic regulatory data to safety, label, and pricing sources, captured by the candidate `FDA_APPLICATION_NUMBER` key flagged in `entries/clinical-biotech/openfda.md` (the BLA series is one of NDA/ANDA/BLA).

Other identifiers in the Purple Book schema are descriptive rather than registry-grade: `Proprietary Name` (brand), `Proper Name` (nonproprietary), `Core Name` (groups biosimilars with their reference product), `Applicant` (sponsor), `License Type` (351(a) vs 351(k) Biosimilar vs 351(k) Interchangeable). No `NDC` is exposed at the row level, so joins to NDC-indexed sources (openFDA NDC directory, RxNorm) require fuzzy name matching or a separate lookup. No `RXNORM_CUI`, no `UNII`, no `NCT_ID`.

Pair with openFDA (label and adverse-event signals for the same biologic), Drugs@FDA (approval history and review documents), ClinicalTrials.gov (pivotal trials supporting BLA), Medicare/Medicaid drug pricing files (cost data on biosimilars).

## Access notes

Two access surfaces, both free, no auth:

- **Web UI** at `https://purplebooksearch.fda.gov/`. Simple search by proprietary or proper name; Advanced Search supports strength, dosage form, route, presentation, and exports the result table as CSV, XLSX, or PDF. ColdFusion-backed (`index.cfm?event=...`), suggestions API embedded in the homepage. Bot-detection on the host: WebFetch with a default UA gets 404-redirected to an abuse-detection page; a browser-style User-Agent header is required for any programmatic access.
- **Bulk monthly downloads** at `https://purplebooksearch.fda.gov/index.cfm?event=downloads`. Each month's release is a single CSV and XLSX file at predictable URLs of the form `https://www.accessdata.fda.gov/drugsatfda_docs/PurpleBook/<YYYY>/purplebook-search-<month>-data-download.{csv,xlsx}` (month name lowercase for most files; case is inconsistent, some months are capitalised, check both). Archives go back to at least 2023. Each file has a header section listing N/R/U (newly approved / added in current release / updated) for that month, followed by the full database snapshot. Roughly 1,500-2,000 product rows, ~470 KB per CSV. No incremental diff format, just full snapshots, but the leading N/R/U flag column lets you reconstruct changes since prior release.

No REST API, no JSON endpoint, no Socrata mirror. Patent List is a separate sub-page (`index.cfm?event=patentlist`) and not included in the monthly CSV.

No documented rate limit on the bulk files. Polite use means caching the monthly snapshot rather than re-downloading per query.

## MCP / connector notes

No MCP exists. The source is narrow (biosimilar and biologic regulatory analysts, IP litigation, formulary teams) so build priority is low. The cleanest pattern is a small loader that pulls the latest monthly CSV into a local table (DuckDB, SQLite, Parquet) and exposes parameterised lookups: `search_biologic(core_name)`, `get_by_bla(bla_number)`, `list_biosimilars_of(reference_bla)`, `get_exclusivity_dates(bla)`, `list_changes_since(month)`. An MCP wrapper would mostly abstract over (a) the predictable but case-inconsistent file-name pattern, (b) the two-section CSV layout (skip header N/R/U section to get the full snapshot), and (c) date-string normalisation (`3-Nov-03` style). Web UI scraping is unnecessary given the bulk files cover every public field.

## Review notes

- Potential new join key for review: `FDA_APPLICATION_NUMBER`. Entity type: `drug_approval`. Pattern: `^(NDA|ANDA|BLA)[0-9]{6}$` or six-digit bare form. Other datasets that would use it: Drugs@FDA, Orange Book, Purple Book, openFDA drug endpoints, Medicare drug pricing. Same candidate key already flagged in `entries/clinical-biotech/openfda.md`. Purple Book is the canonical source for the `BLA` subspace, so adoption would let this entry expose at least one registry key. Until registered, `join_keys: []` here.
- License recorded as `US-Government-Public-Domain` per FDA convention; no per-page license statement on the Purple Book site itself, inferred from federal-works status under 17 USC 105. Confirm if the project prefers a stricter `unknown` when no explicit license is published.
- Bot-detection on `purplebooksearch.fda.gov` blocks tools that don't send a browser-style User-Agent. The access_test targets the bulk CSV on `accessdata.fda.gov` instead, which is the actually stable surface; the search-UI host should not be used for automated checks.
- `type` includes `bulk-download` and `web-ui`. There is no `rest-api`, `database`, `socrata`, or `odata` surface despite the source being a government regulatory database.
