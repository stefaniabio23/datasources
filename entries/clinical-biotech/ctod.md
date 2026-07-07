---
id: ctod
name: Clinical Trial Outcomes (CTO)
domain: clinical-biotech
entry_kind: registry
description: Large-scale benchmark of clinical trial outcomes with machine-generated and human-annotated success/failure labels, keyed on NCT ID.
homepage_url: https://chufangao.github.io/CTOD/
docs_url: https://github.com/chufangao/ctod
type:
  - dataset-dump
  - bulk-download
auth_required: none
cost: free
license: MIT
bulk_available: true
frequency: "periodic (irregular releases; last refreshed 2025-10)"
geography: [global]
join_keys:
  - NCT_ID
primary_keys:
  - nct_id
join_key_fields:
  - join_key: NCT_ID
    fields: [nct_id]
structure: registry-snapshot
pit_reconstructable: false
revisions_possible: true
mcp_status: mcp-needed-low-value
agent_use_cases:
  - trial success/failure labeling
  - outcome-prediction model training
  - drug-development benchmark evaluation
  - phase-progression analysis
access_test:
  command: "curl -sf 'https://huggingface.co/api/datasets/chufangao/CTO'"
  expected_status: 200
  expected_fields: [id, sha, tags]
last_verified: 2026-07-03
build_priority: low
notes: "CTO/CTOD benchmark (Gao et al., arXiv:2406.10292). Distinct from the older futianfan/clinical-trial-outcome-prediction TOP benchmark, which is non-commercial; CTO is MIT-licensed."
---

# Clinical Trial Outcomes (CTO)

## Why this source matters

CTO (also called CTOD) is a large-scale, publicly available benchmark of clinical trial outcomes for drug development, from Chufan Gao, Jathurshan Pradeepkumar, Trisha Das, Shivashankar Thati, and Jimeng Sun (UIUC), published as arXiv:2406.10292. It assigns each trial a binary success/failure label (success = the trial meets its primary endpoint and advances to the next development stage; regulatory approval for Phase 3) using weak-supervision signals: LLM interpretation of linked publications, phase-progression linkage, sponsor stock-price movements, news sentiment, and reported results. It covers roughly 125K drug and biologics trials with automated labels plus a manually annotated subset of ~11K trials completed 2020-2024, and the machine labels agree strongly with expert annotation (F1 ~94 for Phase 3, ~91 across phases). For an agent, this is the ready-made ground-truth layer that ClinicalTrials.gov itself does not publish: trials there carry a status, not a validated outcome. CTO is the MIT-licensed successor to the older TOP benchmark (`futianfan/clinical-trial-outcome-prediction`).

## Agent use cases

- trial success/failure labeling
- outcome-prediction model training
- drug-development benchmark evaluation
- phase-progression analysis

## Join strategy

The load-bearing join key is `NCT_ID` (`nct_id` column), present in every file, which links each labeled trial back to ClinicalTrials.gov / AACT for full protocol, sponsor, drug, and condition metadata. That is the recommended pairing: use CTO for the outcome label and join on `NCT_ID` to `aact`, `clinicaltrials-gov`, or `who-ictrp` for trial detail, and onward to `chembl` / `drugbank` for the intervention molecule.

CTO's core prediction files (`phase{1,2,3}_CTO_rf.csv`) are keyed only on `nct_id`; the drug (SMILES / intervention name), disease/condition, phase, and outcome label are dataset attributes, not cross-source join identifiers, so they are not mapped to canonical keys. Disease-to-ICD and drug-structure mappings may be derivable from the bundled `CTTI.zip` and linkage files but are not confirmed as first-class columns in the core release; see Review notes.

## Access notes

No auth, no cost. Fastest path: the HuggingFace dataset `chufangao/CTO` (DOI 10.57967/hf/4597), which serves per-phase CSVs (`phase1_CTO_rf.csv`, `phase2_CTO_rf.csv`, `phase3_CTO_rf.csv`), the merged linkage/outcome table, human labels for 2020-2024, news/pubmed/stock signal files, and a `CTTI.zip` snapshot. Pull with `pandas.read_csv` against the `resolve/main/<file>` URLs or `datasets.load_dataset("chufangao/CTO")`. The GitHub repo `chufangao/ctod` holds the labeling and modeling code. License is MIT for the labels and code; the underlying trial records derive from CTTI's AACT mirror of ClinicalTrials.gov (US-government public-domain), with PubMed, FDA Orange Book, news, and historical stock data as auxiliary signals. Refreshed irregularly (last update 2025-10); pin a commit SHA for reproducibility.

## MCP / connector notes

No MCP exists and none is warranted as a priority: this is a static, versioned CSV benchmark that `pandas` / `datasets` already load cleanly, and the audience (trial-outcome ML researchers) is narrow. If wrapped, a thin connector would expose `get_outcome(nct_id)`, `get_phase_split(phase)`, and `get_human_labels()`, abstracting over the per-phase file layout and returning the label plus the weak-supervision signal columns.

## Review notes

- License note: CTO (this entry, `chufangao/ctod`) is MIT. The URL originally supplied for this entry, `github.com/futianfan/clinical-trial-outcome-prediction`, is a different and older benchmark (TOP) under a non-commercial license; homepage was redirected to the CTO/CTOD canonical source to match the `ctod` slug and "Clinical Trial Outcomes" name.
- Join-key hints `phase`, `label`, and `drug` do not map to any canonical key in `schema/join-keys.yaml` and were not invented: phase and outcome label are trial attributes, and the drug is carried as an intervention name / SMILES string. SMILES is not a registry key; `INCHI_KEY` exists in the registry but would require client-side structure conversion and is not shipped by the dataset, so no mapping was asserted.
- Potential additional canonical join keys (already in registry, not yet confirmed as columns in the core release): `ICD_10` for conditions and `INCHI_KEY`/`CHEMBL_ID` for interventions may be recoverable from the bundled CTTI/linkage files. Verify column presence before adding to `join_keys`.
