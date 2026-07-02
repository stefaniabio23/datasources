---
id: pmlr
name: Proceedings of Machine Learning Research (PMLR)
domain: academic
entry_kind: corpus
description: Open-access proceedings of machine learning conferences and workshops (ICML, AISTATS, CoRL, UAI, and many workshops), published as per-volume PDFs plus openly available BibTeX metadata without a conventional publisher.
homepage_url: https://proceedings.mlr.press/
docs_url: https://github.com/mlresearch
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: PMLR-Author-Copyright
rate_limit: "none; static GitHub Pages site + per-volume GitHub repos"
bulk_available: true
frequency: "rolling; a new volume is posted as each conference or workshop completes"
lag: "weeks-to-months between a conference and its volume going live"
geography: [global]
join_keys:
  - URL
  - ISSN
primary_keys:
  - PMLR_VOLUME
  - PMLR_PAPER_ID
join_key_fields:
  - join_key: URL
    fields: [url]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - machine-learning literature corpus building
  - title and abstract text mining
  - conference and topic trend analysis
  - metadata harvesting for ML papers
  - reproducibility and citation tracing
access_test:
  command: "curl -sf 'https://proceedings.mlr.press/feed.xml' -o /dev/null"
  expected_status: 200
last_verified: 2026-07-02
build_priority: low
notes: "access_test executed 2026-07-02 (feed.xml → 200). PMLR papers generally have no DOIs; resolve cross-source via OpenAlex / Semantic Scholar / DBLP, which index PMLR and mint their own ids. Per-volume BibTeX files live in the github.com/mlresearch/<vNNN> repos; exact raw path varies by volume (flagged in Review notes)."
---

# Proceedings of Machine Learning Research (PMLR)

## Why this source matters

PMLR is the open-access proceedings series for a large share of the machine-learning conference and workshop world: ICML, AISTATS, CoRL, UAI, ALT, and dozens of workshops, over 300 numbered volumes and thousands of papers. Begun in 2006 as *JMLR Workshop and Conference Proceedings* and rebranded to PMLR in 2017, it publishes without a conventional publisher: since Volume 26 an automated pipeline takes an editor-supplied zip of PDFs plus a BibTeX file (author names, titles, abstracts) and produces the volume. The rebrand deliberately made titles and abstracts easy to pull for analysis (Python-first), moving the corpus from low to high data-readiness. For agents, PMLR is a clean, license-permissive corpus of ML research text and metadata that sits outside the paywalled-publisher graph. Series ISSN 2640-3498 (legacy JMLR W&CP: 1938-7228).

## Agent use cases

- machine-learning literature corpus building
- title and abstract text mining
- conference and topic trend analysis
- metadata harvesting for ML papers
- reproducibility and citation tracing

## Join strategy

The reliable canonical join key is `URL`: every paper has a stable page URL (and PDF URL) carried in the `url` field of its BibTeX entry. `ISSN` applies at the series level (2640-3498), useful for tying PMLR-the-series to journal registries but not for per-paper joins.

PMLR mints no DOIs, so it does not join into DOI-keyed citation graphs directly. The practical path is to resolve each paper by title + author through `OpenAlex`, `Semantic Scholar`, or DBLP, which index PMLR, assign their own work ids, and frequently link the matching arXiv preprint. Native identifiers are the volume number (`PMLR_VOLUME`, e.g. `v119`) and the per-paper key (`PMLR_PAPER_ID`, e.g. `chen20a`); use them for PMLR-internal lookups, not cross-source joins.

## Access notes

No REST API. Three access paths: browse the website (`proceedings.mlr.press`), pull the `feed.xml` RSS for new volumes, or fetch per-volume assets. Each volume is a repo under `github.com/mlresearch/<vNNN>` containing the volume's PDFs and a BibTeX file, this bib file (titles, abstracts, authors) is the highest-value bulk-metadata target and the intended route for text analysis. There is no auth, no key, and no meaningful rate limit; it is a static GitHub Pages site plus static repos. For a full-corpus pull, iterate volumes from the homepage index and download each volume's bib rather than scraping HTML.

## MCP / connector notes

No MCP exists, and building a dedicated one is low-value: `OpenAlex` and `Semantic Scholar` already index PMLR with richer cross-references (citations, arXiv links, author disambiguation) than PMLR exposes itself, so an agent usually reaches PMLR content better through those aggregators. If a PMLR-native MCP were built, the useful surface is small: list volumes, fetch a volume's BibTeX, search papers by title/author, return an abstract. The one thing it must abstract over is the per-volume repo layout, since bib file paths are not perfectly uniform across the back catalogue.

## Review notes

- New non-SPDX license short name `PMLR-Author-Copyright`. Authors retain copyright; many recent volumes are CC-BY-4.0 but this varies per volume and per paper, and the openly reusable layer in practice is the BibTeX metadata. Confirm the short-name convention, or split into a per-volume license note.
- Exact raw BibTeX path per volume was not pinned down (guessed `.../assets/bib/vNNN.bib` and a raw GitHub path both 404); the `mlresearch/vNNN` repos exist (200). Verify the canonical bib path before building any bulk harvester.
- No DOIs is an honest gap, not an omission. `URL` + title-resolution via aggregators is the join story.
- `ISSN` is series-level; if the registry prefers per-instance join keys only, drop it. Left in because PMLR genuinely exposes it.
