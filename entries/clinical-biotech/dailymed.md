---
id: dailymed
name: DailyMed
domain: clinical-biotech
entry_kind: registry
description: NLM's authoritative repository of FDA-submitted Structured Product Labels (SPLs) for prescription, OTC, homeopathic, animal, and other regulated drug products in the US.
homepage_url: https://dailymed.nlm.nih.gov/
docs_url: https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "not published; GET-only service, paginate via pagesize and page params"
bulk_available: true
frequency: "daily, weekly, and monthly delta archives; full snapshots refreshed periodically"
lag: "days after FDA submission"
geography: [USA]
join_keys:
  - NDC
  - RXNORM_CUI
primary_keys:
  - SETID
  - UNII
  - FDA_APPLICATION_NUMBER
join_key_fields:
  - join_key: NDC
    fields: [data.ndcs.ndc, ndc]
  - join_key: RXNORM_CUI
    fields: [rxcui]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/RowanErasmus/dailymed-mcp-server
  - github.com/pipeworx-io/mcp-dailymed
  - github.com/QuentinCody/dailymed-mcp-server
mcp_notes: >
  Three community TypeScript MCPs (RowanErasmus, pipeworx-io, QuentinCody). None official.
  Suggested surface: search_spls, get_spl, get_spl_history, lookup_ndc, lookup_rxcui, get_packaging.
  Connector should abstract over XML vs JSON, paginate the 156K-document corpus, and extract
  human-readable label sections from SPL XML.
agent_use_cases:
  - FDA drug label lookup
  - NDC to product resolution
  - RxNorm to product resolution
  - drug packaging and dosage form discovery
  - label version history tracking
access_test:
  command: "curl -sf 'https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?pagesize=1'"
  expected_status: 200
  expected_fields: [data, metadata]
last_verified: 2026-06-08
build_priority: medium
---

# DailyMed

## Why this source matters

The official NLM repository of FDA-submitted Structured Product Labels (SPLs), covering 156K+ drug products including prescription, OTC, homeopathic, animal, medical gases, devices, cosmetics, dietary supplements, and medical foods. Run by the National Library of Medicine (part of NIH); the source the FDA itself points to for current package insert content. SPLs are the regulatory ground truth for drug indications, dosing, contraindications, adverse reactions, packaging, and active/inactive ingredients. Any agent answering "what does this drug do, what's on its label, who makes it, what's in the package" should start here rather than scraping pharma sites.

## Agent use cases

- FDA drug label lookup
- NDC to product resolution
- RxNorm to product resolution
- drug packaging and dosage form discovery
- label version history tracking

## Join strategy

DailyMed exposes `NDC` (National Drug Code, via the `/ndcs` endpoint and per-SPL `/spls/{SETID}/ndcs`) and `RXNORM_CUI` (via `/rxcuis`, product-level CUIs). Pair with openFDA for adverse events keyed on the same NDC, with RxNorm for drug-concept normalisation, with ClinicalTrials.gov for trial-drug crosswalks, and with FDA Orange Book for therapeutic-equivalence ratings.

DailyMed-internal identifiers (`SETID` for an SPL document, `UNII` for substance unique ingredients, NDA/ANDA `applicationnumber`) are intentionally outside the canonical registry; use them for direct DailyMed lookups, not cross-source joins. `SETID` is the stable key for resolving label version history (`/spls/{SETID}/history`).

## Access notes

**Quick agent queries:** REST API at `https://dailymed.nlm.nih.gov/dailymed/services/v2/`, no auth. Append `.json` or `.xml` to any path; GET only. Paginate with `pagesize` (max 100) and `page` query params. Useful first endpoints: `/spls.json?drug_name=<name>` for fuzzy search, `/spls/{SETID}.json` for a full record, `/ndcs.json?ndc=<code>` to resolve an NDC to its SPL.

**Bulk pulls:** ZIP archives via HTTPS or FTP at `spl-resources-all-drug-labels.cfm`. Full corpus split across categories: Human Prescription (~16 GB / 6 parts), Human OTC (~32 GB / 11 parts), Homeopathic (5.4 GB), Animal (1.15 GB), Remainder (619 MB). Daily, weekly, and monthly delta archives also published. MD5 checksums alongside each file.

Known gotchas:

- SPL content itself is HL7 v3 SPL XML; the REST API returns metadata and child resources (NDCs, packaging, media, history), not parsed label sections. To read indications, dosing, adverse reactions, etc. you must fetch the SPL XML and parse it.
- Rate limits not published; the service is GET-only and is courteous-pool norms apply. Throttle to ~5 req/sec to be safe.
- `total_pages` in metadata reflects pagesize=1 unless you set pagesize, so cross-check with `total_elements`.
- License coverage is FDA submissions only, not every product on the market.

## MCP / connector notes

Three community MCPs (RowanErasmus, pipeworx-io, QuentinCody), all TypeScript, none official. Coverage varies; most expose SPL search and fetch but few abstract SPL XML parsing into structured label sections. Ideal connector surface: `search_spls`, `get_spl`, `get_spl_history`, `lookup_ndc`, `lookup_rxcui`, `get_packaging`, plus an `extract_label_section(setid, section)` helper that resolves the underlying SPL XML and returns parsed indications, dosing, warnings, adverse reactions, or ingredients.

## Review notes

Potential new join keys for review:

```
Potential new join key for review: SETID
  Entity type: spl_document
  Pattern: UUID v4 (e.g. 327f6b60-1a5d-49e6-acff-18603d0ee9d0)
  Other datasets that would use it: FDA SPL submissions, openFDA drug label endpoint references SETID

Potential new join key for review: UNII
  Entity type: substance
  Pattern: ^[A-Z0-9]{10}$
  Other datasets that would use it: openFDA (already lists UNII outside the registry), FDA GSRS, NCI Thesaurus, PubChem cross-refs
```

Both are widely used across FDA-adjacent sources and would unlock cleaner joins between DailyMed, openFDA, GSRS, and RxNorm. Flagged for Stephanie to PR into `schema/join-keys.yaml`.
