---
id: gdsc
name: GDSC (Genomics of Drug Sensitivity in Cancer)
domain: clinical-biotech
entry_kind: panel
description: Drug-sensitivity screen of ~400 anti-cancer compounds against ~1,000 genetically characterised human cancer cell lines, reporting ln(IC50), AUC, and Z-score per cell-line/compound pair, integrated with COSMIC genomic features.
homepage_url: https://www.cancerrxgene.org/
docs_url: https://www.cancerrxgene.org/help
type:
  - bulk-download
  - dataset-dump
  - web-ui
auth_required: none
cost: free
license: GDSC-Terms-Of-Use
rate_limit: "no published per-IP limit; static files served over HTTPS from the Sanger FTP and the cog.sanger.ac.uk object store"
bulk_available: true
frequency: "periodic major releases (release-8.x); current_release drop dated 24Jul22 (v8.4), later drop v8.5 dated Oct 2023 on the cog object store"
geography: [global]
join_keys:
  - CHEMBL_ID
  - GENE_SYMBOL
primary_keys:
  - GDSC_DRUG_ID
  - COSMIC_ID
  - SANGER_MODEL_ID
  - CELL_LINE_NAME
  - NLME_CURVE_ID
join_key_fields:
  - join_key: CHEMBL_ID
    fields:
      - "compound detail page (cancerrxgene.org/compounds/<DRUG_ID>)"
      - "gdsctools ChEMBL resolver (DRUG_NAME -> CHEMBL_ID)"
  - join_key: GENE_SYMBOL
    fields:
      - PUTATIVE_TARGET
      - TARGET
mcp_status: mcp-needed-high-value
agent_use_cases:
  - drug sensitivity lookup by cell line or compound
  - pharmacogenomic biomarker discovery
  - preclinical target validation across cancer lineages
  - cross-referencing IC50 response with COSMIC mutations
  - compound-to-cell-line response benchmarking
access_test:
  command: "curl -sf -H 'Range: bytes=0-400' 'https://ftp.sanger.ac.uk/pub/project/cancerrxgene/releases/current_release/GDSC2_fitted_dose_response_24Jul22.csv'"
  expected_status: 206
  expected_fields: [COSMIC_ID, CELL_LINE_NAME, SANGER_MODEL_ID, DRUG_ID, DRUG_NAME, PUTATIVE_TARGET, LN_IC50, AUC, Z_SCORE]
last_verified: 2026-07-02
build_priority: medium
notes: "Access test executed 2026-07-02: range GET of the current_release fitted-dose CSV over the Sanger FTP returned 206 with the expected column header row. The cancerrxgene.org web app returns HTTP 410 to non-browser clients (WebFetch/curl), so the executable surface is the static file host, not the site. Latest data drop is release 8.5 (Oct 2023) on https://cog.sanger.ac.uk/cancerrxgene/GDSC_release8.5/; the FTP current_release symlink still points at the v8.4 24Jul22 files."
---

# GDSC (Genomics of Drug Sensitivity in Cancer)

## Why this source matters

GDSC is the canonical public drug-sensitivity screen for cancer cell lines, a Wellcome-funded collaboration between the Cancer Genome Project at the Wellcome Sanger Institute (UK) and the Center for Molecular Therapeutics at Massachusetts General Hospital (USA), served through cancerrxgene.org. It reports ln(IC50), area-under-curve, and Z-score for every tested cell-line/compound pair across two release lines: GDSC1 (320 compounds x 987 lines) and GDSC2 (175 compounds x 809 lines), ~1,000 lines and ~400 distinct anti-cancer compounds in total. Response data are integrated with COSMIC genomic features (somatic mutations in cancer genes, copy-number amplification/deletion, tissue type, expression) so agents can correlate sensitivity with genotype. For any preclinical pharmacology, biomarker-discovery, or target-validation workflow, GDSC is the orthogonal drug-response reference to the Broad's CCLE/PRISM and CTRP. Secondary domain: `bio-genomics`, since each line is genomically characterised and keyed to the Sanger Cell Model Passports.

## Agent use cases

- drug sensitivity lookup by cell line or compound
- pharmacogenomic biomarker discovery
- preclinical target validation across cancer lineages
- cross-referencing IC50 response with COSMIC mutations
- compound-to-cell-line response benchmarking

## Join strategy

The primary deliverable is the fitted-dose-response matrix, one row per cell-line/compound pair, keyed internally on `COSMIC_ID` and `SANGER_MODEL_ID` (Cell Model Passports `SIDM*`) for the line and `DRUG_ID` (+ `DRUG_NAME`) for the compound. None of GDSC's line identifiers are canonical registry keys, so cell-line joins run through `COSMIC_ID` or `SANGER_MODEL_ID` in `primary_keys` (both flagged below as new-key candidates). `SANGER_MODEL_ID` is the clean pivot into CCLE/DepMap (which carries it in its model table), Cell Model Passports, and Project Score.

For compounds, GDSC's own tooling (`gdsctools`) and the per-compound web pages resolve `DRUG_NAME`/`DRUG_ID` to `CHEMBL_ID`, plus PubChem CID, SMILES, and InChIKey; use `CHEMBL_ID` to pivot into ChEMBL, BindingDB, and DrugBank. Target annotation is exposed as `PUTATIVE_TARGET`/`TARGET`, which carries HGNC `GENE_SYMBOL` for most targeted agents (EGFR, TOP1, BRAF) but also protein-complex and pathway labels (PI3K, MTORC1), so gene-symbol joins are useful but lossy and should be validated per row. Pair GDSC with Open Targets and UniProt (target biology by `GENE_SYMBOL`), ChEMBL (compound bioactivity by `CHEMBL_ID`), and CCLE/DepMap (orthogonal omics and dependency by `SANGER_MODEL_ID`).

See Review notes for `COSMIC_ID`, `SANGER_MODEL_ID`, `GDSC_DRUG_ID`, and `PUBCHEM_CID` as candidate canonical join keys.

## Access notes

There is no documented public REST API; the cancerrxgene.org web app returns HTTP 410 to non-browser clients. The reliable programmatic path is the static file host. Start at `https://ftp.sanger.ac.uk/pub/project/cancerrxgene/releases/current_release/`, which carries `GDSC1_fitted_dose_response_*.csv`, `GDSC2_fitted_dose_response_*.csv` (the IC50 tables), `Cell_Lines_Details.xlsx` (COSMIC IDs, cell-line names, TCGA classification, tissue), `screened_compounds_rel_8.4.csv` (`DRUG_ID`, `DRUG_NAME`, `SYNONYMS`, `TARGET`, `TARGET_PATHWAY`), the raw dose-point CSVs, and the ANOVA biomarker-association spreadsheets. Files are also mirrored on the `cog.sanger.ac.uk/cancerrxgene/` object store (per-release prefixes such as `GDSC_release8.5/`). Both hosts support HTTP range requests. No auth or registration for bulk download.

License is the **GDSC Terms of Use** (no SPDX code). Users get a non-exclusive, non-transferable right to use the data for internal proprietary research and education, explicitly including target, biomarker, and drug discovery, so internal commercial R&D is permitted. Excluded: resale of the data (alone or bundled with other products) and provision of commercial services built on it. Redistribution therefore carries downstream conditions; rehosting agents must propagate the terms and cite the GDSC publications (Nucleic Acids Research 2013; Cell 2016).

Freshness check: read the file dates in the `current_release/` listing, or compare against the newest `GDSC_release*.x/` prefix on `cog.sanger.ac.uk`. `access_test` populated against the current_release GDSC2 fitted-dose CSV (range GET, verified 206 on 2026-07-02).

## MCP / connector notes

No MCP exists. The CancerRxGene GitHub org ships analysis libraries (`gdsctools` Python, `gdscIC50`/`gdscdata` R) but no connector. This is high-value: CCLE, ChEMBL, Open Targets, and OncoKB entries share the same cancer-pharmacogenomics audience and would all benefit from a common GDSC surface. A connector should expose `get_drug_response(cell_line, compound)`, `search_compounds(target, pathway)`, `search_cell_lines(tissue, tcga, mutation)`, `get_biomarker_associations(drug)` (over the ANOVA tables), and `resolve_compound(drug_name -> CHEMBL_ID/PubChem CID)`, and abstract over (a) the GDSC1-vs-GDSC2 release split, (b) resolution between `COSMIC_ID`, `SANGER_MODEL_ID`, and `CELL_LINE_NAME`, and (c) the fact that the query surface is a set of versioned static CSV/XLSX files, not an API.

## Review notes

- License: no SPDX identifier. Used canonical short name `GDSC-Terms-Of-Use`. Not yet in `SCHEMA.md § License conventions`; flag for review. It is broader than the CCLE `DepMap-Terms-Of-Use` (GDSC permits internal commercial/drug-discovery use) but still forbids resale and commercial services, so `cost: free` with the resale restriction documented in Access notes rather than `free-non-commercial`.
- Domain: placed in `clinical-biotech` (drug-sensitivity / preclinical pharmacology, alongside ChEMBL and BindingDB) over `bio-genomics` (where its sibling CCLE lives). The two are cross-referenceable; secondary domain noted in the body.
- Potential new canonical join keys for review:
  - `COSMIC_ID`
    - Entity type: `cancer_cell_line` (COSMIC sample/cell-line identifier)
    - Pattern: `^[0-9]+$` (e.g. `683667`)
    - Other datasets that would use it: COSMIC Cell Lines Project, Cell Model Passports, CCLE crosswalks, older cancer cell-line panels.
  - `SANGER_MODEL_ID`
    - Entity type: `cancer_cell_line`
    - Pattern: `^SIDM[0-9]+$` (e.g. `SIDM01132`)
    - Other datasets that would use it: Cell Model Passports, CCLE/DepMap model table, Project Score (Sanger CRISPR). Already flagged in `cancer-cell-line-encyclopedia.md`; consolidating the proposal here.
  - `GDSC_DRUG_ID`
    - Entity type: `screening_compound`
    - Pattern: `^[0-9]+$` (e.g. `1003`)
    - Other datasets that would use it: PharmacoDB, GDSC-derived ML benchmarks. Source-internal; likely stays a `primary_key` rather than a canonical key.
  - `PUBCHEM_CID`
    - Entity type: `chemical_compound`
    - Pattern: `^[0-9]+$`
    - Other datasets that would use it: PubChem, ChEMBL, DrugBank, most compound-keyed sources. GDSC compound annotation carries it (alongside `CHEMBL_ID` and InChIKey); worth a general proposal since many drug datasets expose PubChem CID. Registry currently has `CHEMBL_ID`, `INCHI_KEY`, `DRUGBANK_ID`, `UNII` but not `PUBCHEM_CID`.
- `CHEMBL_ID` and `GENE_SYMBOL` are the only join keys drawn from the registry. `CHEMBL_ID` is surfaced via compound annotation / `gdsctools`, not a column in the primary fitted-dose CSV. `GENE_SYMBOL` via `PUTATIVE_TARGET` is noisy (mixes HGNC symbols with complex/pathway labels); flagged in Join strategy.
