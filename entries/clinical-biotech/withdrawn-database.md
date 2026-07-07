---
id: withdrawn-database
name: WITHDRAWN
domain: clinical-biotech
entry_kind: registry
description: Curated database of withdrawn and discontinued drugs with withdrawal reasons, toxicity classification, targets, and ATC classes.
homepage_url: https://bioinformatics.charite.de/withdrawn_3/index.php
docs_url: https://bioinformatics.charite.de/withdrawn_3/subpages/faq.php
type:
  - web-ui
  - bulk-download
auth_required: none
cost: free
license: unknown
bulk_available: true
frequency: irregular
geography: [global]
join_keys:
  - ATC_CODE
  - INCHI_KEY
  - CHEMBL_ID
  - DRUGBANK_ID
  - UNIPROT_ACCESSION
  - GENE_SYMBOL
primary_keys:
  - WITHDRAWN_ID
join_key_fields:
  - join_key: ATC_CODE
    fields: [atc_code]
  - join_key: INCHI_KEY
    fields: [inchikey]
  - join_key: CHEMBL_ID
    fields: [chembl_id, target.chembl_id]
  - join_key: DRUGBANK_ID
    fields: [drugbank_id]
  - join_key: UNIPROT_ACCESSION
    fields: [target.uniprot_accession]
  - join_key: GENE_SYMBOL
    fields: [target.gene_symbol]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - withdrawal-reason lookup
  - drug-toxicity mechanism analysis
  - target-based safety screening
  - ATC-class withdrawal-pattern analysis
  - chemical-similarity safety flagging
last_verified: 2026-07-03
build_priority: low
---

# WITHDRAWN

## Why this source matters

WITHDRAWN is a manually curated database of post-marketing drug withdrawals and discontinuations, built by the Structural Bioinformatics Group at Charité, Universitätsmedizin Berlin. The current release (WITHDRAWN 2.0) holds 626 withdrawn drugs with withdrawal history, toxicity classification, side effects, structures, physico-chemical properties, protein targets, and signaling pathways. Roughly half the drugs were pulled for safety reasons, and those withdrawal reasons are hand-classified into organ-level toxicity types, which makes this one of the few sources that connects a specific chemical structure and target to a documented real-world safety failure. For an agent reasoning about drug safety, target liability, or the reference class of "why do drugs get pulled", it is a small but high-purity signal. It is free and needs no registration. Secondary relevance to `bio-genomics` (target and pathway mapping via ChEMBL, UniProt, HGNC, KEGG).

## Agent use cases

- withdrawal-reason lookup
- drug-toxicity mechanism analysis
- target-based safety screening
- ATC-class withdrawal-pattern analysis
- chemical-similarity safety flagging

## Join strategy

WITHDRAWN exposes several canonical keys for cross-source joining. `ATC_CODE` (512 drugs carry a level-5 ATC code) and `INCHI_KEY` are the primary structure- and class-level joins. Target relationships (1,628 drug-target pairs over 409 targets) are drawn from ChEMBL 32, so `CHEMBL_ID` (molecules and targets), `UNIPROT_ACCESSION` (target proteins via UniProt), and `GENE_SYMBOL` (HGNC gene mapping) join out to genomics and pharmacology sources. `DRUGBANK_ID` maps drug identity to DrugBank. Pair with openFDA FAERS for adverse-event counts, ChEMBL for bioactivity, Open Targets for target-disease evidence, and DailyMed/DrugBank for current labeling. The source mints an internal record id (referred to here as `WITHDRAWN_ID`) for direct lookups; use it only for WITHDRAWN itself, not for cross-source joins.

The organ-level toxicity classification (e.g. cardiotoxicity, hepatotoxicity) is a curated categorical field with no canonical key in the registry; it is flagged below as a new-key candidate rather than mapped.

## Access notes

Web-only interface plus a full CSV export; there is no documented programmatic API. The site offers name/ID lookup, structure similarity and substructure search, alphabetical browse, an ATC classification tree, target/protein-class search, mechanism-of-action analysis, and KEGG pathway enrichment. The complete dataset is downloadable as a single CSV that includes SMILES, InChI, molecular formula, and withdrawal/toxicity information; grab that once rather than scraping per-drug pages. The homepage is JavaScript-rendered, so `curl` on `index.php` returns HTTP 200 with an empty body; use a headless browser or the CSV export for programmatic access. To check freshness, compare the version banner and drug count against the FAQ page (`subpages/faq.php`, currently 626 drugs, ChEMBL 32). The legacy `https://bioinformatics.charite.de/withdrawn/` path redirects to the current `withdrawn_3` release.

Terms of use / license are not explicitly stated on the site. Treat redistribution as unknown until confirmed; cite the source publications (NAR 2016, 44:D1080 and NAR 2024, 52:D1503).

## MCP / connector notes

No MCP exists. Value is narrow (drug-safety and pharmacovigilance audience), and the whole corpus is a single small CSV, so the cheapest connector just loads that CSV and indexes it. If wrapped, a useful surface would be: `get_drug(name|withdrawn_id)`, `search_by_target(uniprot|gene|chembl)`, `search_by_atc(code)`, `list_by_toxicity_type(class)`, and `structure_search(smiles, similarity)`. The connector must abstract over the JS-rendered UI (no JSON API) and normalise the curated toxicity-type vocabulary.

## Review notes

Potential new join key for review: `TOXICITY_CLASS`
  Entity type: adverse_effect_class (organ-level toxicity category)
  Pattern: controlled vocabulary of curated toxicity types (e.g. cardiotoxicity, hepatotoxicity, immunotoxicity); no standard code system, not MedDRA-coded
  Other datasets that would use it: SIDER, openFDA FAERS (post-mapping), ProTox toxicity endpoints, Open Targets safety liabilities. Consider whether existing `MEDDRA_TERM` covers the use case before adding.

License is `unknown`: the site states free public access without registration but publishes no explicit license or redistribution terms. Confirm with the maintainers (webmaster: Mathias Dunkel, Charité) before any redistribution of the CSV.
