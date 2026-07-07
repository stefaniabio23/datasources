---
id: ct-ade
name: CT-ADE
domain: clinical-biotech
entry_kind: corpus
description: Curated benchmark dataset of drug-adverse-event pairs extracted from ClinicalTrials.gov monopharmacy trial results, annotated to MedDRA SOC and PT levels for multilabel ADE prediction.
homepage_url: https://github.com/ds4dh/CT-ADE
docs_url: https://www.nature.com/articles/s41597-025-04718-1
type:
  - dataset-dump
  - bulk-download
auth_required: none
cost: free
license: MIT
bulk_available: true
frequency: static
lag: "one-time research release; MedDRA 25.0, trials up to 2024 snapshot"
geography: [global]
join_keys:
  - NCT_ID
  - MEDDRA_TERM
  - ATC_CODE
  - CHEMBL_ID
  - DRUGBANK_ID
join_key_fields:
  - join_key: NCT_ID
    fields: [nctid]
  - join_key: MEDDRA_TERM
    fields: [ade_soc, ade_pt]
  - join_key: ATC_CODE
    fields: [atc_codes]
  - join_key: CHEMBL_ID
    fields: [chembl_id]
  - join_key: DRUGBANK_ID
    fields: [drugbank_id]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - adverse-event prediction benchmarking
  - drug-safety model training
  - trial-arm to MedDRA ADE lookup
  - drug-to-ADE association mining
access_test:
  command: "curl -sf 'https://huggingface.co/api/datasets/anthonyyazdaniml/CT-ADE-PT'"
  expected_status: 200
  expected_fields: [id, tags, description]
last_verified: 2026-07-03
build_priority: low
structure: cross-section
pit_reconstructable: false
revisions_possible: false
---

# CT-ADE

## Why this source matters

CT-ADE (Clinical Trial Adverse Drug Events) is a research benchmark from the Data Science for Digital Health group (ds4dh, University of Geneva / HUG) for multilabel prediction of adverse drug events in monopharmacy treatments. It links 2,497 drugs and 168,984 drug-ADE pairs extracted from ClinicalTrials.gov results sections to standardized MedDRA annotations, and enriches each study-group instance with treatment regimen, dosage, administration route, and target-population demographics. Unlike spontaneous-report resources (FAERS) or literature-mined ADE corpora, it captures both positive and negative ADE cases systematically from structured trial results, which makes it a clean supervised label source for drug-safety modeling. Published in Nature Scientific Data (2025).

## Agent use cases

- adverse-event prediction benchmarking
- drug-safety model training
- trial-arm to MedDRA ADE lookup
- drug-to-ADE association mining

## Join strategy

CT-ADE is a joinable bridge between trials, drugs, and adverse-event ontology. Each record carries the source `NCT_ID` (trial provenance), `MEDDRA_TERM` labels at both System Organ Class (SOC) and Preferred Term (PT) levels (two dataset variants, CT-ADE-SOC and CT-ADE-PT), and `ATC_CODE` for the intervention. The repo's unified chemical database consolidates DrugBank, PubChem, and ChEMBL identifiers by canonical SMILES, so `CHEMBL_ID` and `DRUGBANK_ID` are available for the drug entity (PubChem CID is also present, see Review notes). SMILES strings are included but are not a registry join key.

Pair with ClinicalTrials.gov / AACT for full trial protocol and outcomes, ChEMBL for bioactivity, and openFDA FAERS for post-market spontaneous ADE cross-checking against trial-observed events. Study-group (arm) is a source-internal grouping keyed by NCT plus group description; there is no canonical arm identifier, so join at the trial level via `NCT_ID` and disambiguate arms on the `group_description` text.

## Access notes

Two mirrors, both public and no-auth: Figshare (deposit 28142453, cite via its DOI) and HuggingFace (`anthonyyazdaniml/CT-ADE-SOC` and `anthonyyazdaniml/CT-ADE-PT`). The GitHub repo `ds4dh/CT-ADE` holds the reproduction pipeline (Python) plus the unified chemical database build. HuggingFace exposes the datasets API for metadata (access test above) and standard `datasets`-library loading for the rows. This is a static one-time release, not a live feed; there is no refresh cadence. MedDRA version is 25.0 (English).

License note: the code and dataset are MIT-licensed. However, MedDRA terminology carries its own subscription-based license from MSSO; the MedDRA-coded labels are reproduced here under the benchmark's research use, and downstream commercial redistribution of the coded terms may require a MedDRA subscription. Underlying trial text is from ClinicalTrials.gov (US Government public domain).

## MCP / connector notes

No MCP exists and the value is narrow (drug-safety ML researchers). Because it is a static file set rather than a queried API, an MCP adds little over the HuggingFace `datasets` loader. If built, a thin connector would expose: `get_ades_for_drug(atc_or_chembl)`, `get_ades_for_trial(nct_id)`, and `filter_by_meddra(soc_or_pt)`, abstracting over the SOC vs PT variant split.

## Review notes

Potential new join key for review: PUBCHEM_CID
  Entity type: chemical_compound
  Pattern: `^[0-9]+$` (PubChem Compound ID, integer)
  Other datasets that would use it: PubChem, ChEMBL, DrugBank, most cheminformatics sources. CT-ADE's unified chemical database exposes PubChem CIDs alongside ChEMBL and DrugBank IDs. Recommend adding as a canonical key given its cross-source utility; not invented into join_keys here.

`entry_kind: corpus` chosen as the closest fit for a static bulk collection of annotated records (it is a benchmark, not a live registry or time-series). Flag if a `dataset-benchmark` kind is ever wanted.

Exact HuggingFace column names for `join_key_fields` were inferred from the Nature Scientific Data paper's described fields (intervention name, ATC codes, SMILES, group description, ADE label at SOC/PT) rather than a scraped schema; verify against the actual parquet columns before relying on the paths programmatically.
