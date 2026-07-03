---
id: retraction-watch
name: Retraction Watch Database
domain: academic
entry_kind: registry
description: Curated registry of retracted, corrected, and otherwise flagged scholarly papers, with structured reasons, dates, and linked DOIs/PubMed IDs.
homepage_url: http://retractiondatabase.org/
docs_url: https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: crossref-metadata-free
rate_limit: "Crossref REST API: ~50 req/sec polite pool (add ?mailto=); no separate limit on the bulk CSV"
bulk_available: true
frequency: "updated every working day by Retraction Watch"
lag: "days from public retraction notice to database entry"
geography: [global]
join_keys:
  - DOI
  - PMID
primary_keys:
  - RETRACTION_WATCH_RECORD_ID
join_key_fields:
  - join_key: DOI
    fields:
      - DOI
      - update-to.DOI
      - OriginalPaperDOI
      - RetractionDOI
  - join_key: PMID
    fields:
      - OriginalPaperPubMedID
      - RetractionPubMedID
mcp_status: mcp-exists
mcp_maturity: experimental
mcp_package:
  - "retractionwatch-mcp (Zenodo 20023896)"
  - "github.com/JackKuo666/Crossref-MCP-Server"
mcp_notes: >
  retractionwatch-mcp wraps Crossref's redistribution of the database and exposes single-DOI
  checks, batch screening, search, recent-retraction feeds, and author-level integrity checks.
  Generic Crossref MCPs also surface retraction status via the update-type:retraction filter.
agent_use_cases:
  - retraction status check
  - citation hygiene screening
  - research-integrity auditing
  - author retraction history
  - reason-of-retraction analysis
access_test:
  command: "curl -sf 'https://api.crossref.org/works?filter=update-type:retraction&rows=1&mailto=you@example.com'"
  expected_status: 200
  expected_fields: [DOI, title, update-to]
last_verified: 2026-07-02
build_priority: medium
---

# Retraction Watch Database

## Why this source matters

The Retraction Watch Database is the most complete open registry of retracted, withdrawn, and corrected scholarly papers, started by the Center for Scientific Integrity and acquired by Crossref in September 2023, which made the full dataset public. Each record captures the retracted paper (title, authors, journal, publisher, subject, country), the retraction notice, dates, article type, a controlled set of retraction reasons, and cross-links to the original and notice DOIs and PubMed IDs. For any agent generating citations or building on the literature, this is the reference layer that catches the silent failure mode of confidently citing a retracted work. It sits in `academic` but is equally relevant to biomedical and clinical retrieval workflows.

## Agent use cases

- retraction status check
- citation hygiene screening
- research-integrity auditing
- author retraction history
- reason-of-retraction analysis

## Join strategy

The two canonical join keys are `DOI` and `PMID`, and both appear twice per record: once for the original paper (`OriginalPaperDOI`, `OriginalPaperPubMedID`) and once for the retraction notice (`RetractionDOI`, `RetractionPubMedID`). Missing DOIs are recorded as blank or `Unavailable`; missing PubMed IDs as blank or `0`. Via the Crossref REST API the retracted work's own `DOI` carries the join, and the notice points back through `update-to.DOI`. Pair on `DOI` with OpenAlex, Crossref, Europe PMC, or Semantic Scholar to flag retracted items in a result set; pair on `PMID` with PubMed/Europe PMC for biomedical corpora.

Each record also carries a source-internal `RETRACTION_WATCH_RECORD_ID` (the "Record ID" column). It uniquely identifies a database row but is not in the canonical registry; it is flagged below as a new-key candidate.

## Access notes

Two access paths, both no-auth. Fastest for status lookups: the Crossref REST API with `filter=update-type:retraction` (e.g. `https://api.crossref.org/works?filter=update-type:retraction`); add `?mailto=` to enter the polite pool. For the full corpus, download the bulk CSV from the Crossref Labs endpoint `https://api.labs.crossref.org/data/retractionwatch?name@email.org` (append your mailto), which returns every record with the full column set (Title, Subject, Institution, Journal, Publisher, Country, Author, ArticleType, RetractionDate, RetractionNature, Reason, Paywalled, Notes, plus the DOI/PubMed columns). The legacy web UI at `retractiondatabase.org` still serves interactive search but is HTTP-only and not built for programmatic pulls; prefer the API or CSV.

## MCP / connector notes

A dedicated `retractionwatch-mcp` server (2026, academic preprint on Zenodo) exposes six tools: single-DOI check, batch screening, search, recent-retraction feed, and author-level integrity checks, over Crossref's redistribution. Maturity is experimental (single-author, recent). Generic Crossref MCPs (e.g. `JackKuo666/Crossref-MCP-Server`) also reach the data through the `update-type:retraction` filter but do not specialise in retraction semantics. A production connector should abstract over both access paths (REST filter for lookups, CSV for bulk), normalise the `Unavailable`/`0`/blank sentinels in the DOI and PubMed columns, and split original-paper versus notice identifiers so a caller can resolve both directions.

## Review notes

Potential new join key for review: `RETRACTION_WATCH_RECORD_ID`
  Entity type: retraction_record
  Pattern: integer (source "Record ID" column)
  Other datasets that would use it: none identified; source-internal today, but it is the stable key for citing a specific retraction record and may gain cross-source utility if other integrity tools adopt it. Currently held in `primary_keys` only.

New license short name flagged: `crossref-metadata-free`. Crossref states the retraction metadata is not subject to copyright (facts), so it is freely reusable without a formal license; a citation to the source is requested when used in published work. This is not CC0 (Crossref explicitly declines to frame it as a copyright waiver), so no SPDX code fits. If the registry prefers, this could be aliased to the existing pattern used for other public-facts sources; needs a canonical decision before merge.
