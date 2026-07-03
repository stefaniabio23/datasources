---
id: prism
name: PRISM Repurposing (Broad)
domain: clinical-biotech
entry_kind: panel
description: PRISM multiplexed cell-line viability screen of ~4,500 repurposing compounds against ~580 human cancer cell lines, distributed by the Broad Institute's DepMap as bulk CSV on figshare.
homepage_url: https://www.theprismlab.org/
docs_url: https://depmap.org/repurposing/
type:
  - bulk-download
  - dataset-dump
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "no published limit; bulk CSVs served via figshare (ndownloader) and DepMap portal"
bulk_available: true
frequency: "periodic DepMap releases (19Q3, 19Q4, 20Q2 primary/secondary, then Repurposing Public 23Q2, 24Q2); each release is static"
lag: "files pinned to release date; latest public release Repurposing 24Q2"
geography: [global]
join_keys: []
primary_keys:
  - BROAD_COMPOUND_ID
  - DEPMAP_ID
  - CCLE_NAME
  - PRISM_SCREEN_ID
mcp_status: mcp-needed-high-value
mcp_notes: >
  No PRISM-specific connector. The three community DepMap MCP servers wrap gene essentiality,
  expression, mutation, and copy-number, not the repurposing drug-viability matrices. A useful
  connector would expose compound search by name/MOA/target, per-compound sensitivity across
  lines, per-line sensitivity across compounds, and secondary-screen dose-response curve
  parameters, abstracting over the primary/secondary split and the release-versioned figshare files.
agent_use_cases:
  - drug repurposing candidate discovery
  - compound sensitivity profiling across cancer cell lines
  - mechanism-of-action and target lookup for screened compounds
  - selective-killing / context-specific vulnerability analysis
  - benchmarking drug-response prediction models
access_test:
  command: "curl -sf 'https://api.figshare.com/v2/articles/20564034'"
  expected_status: 200
  expected_fields: [title, doi, license, files]
last_verified: 2026-07-02
build_priority: medium
notes: "Access test executed 2026-07-02: GET https://api.figshare.com/v2/articles/20564034 returned 200 with the PRISM Repurposing 20Q2 record (CC BY 4.0), listing 16 primary/secondary-screen CSVs with ndownloader download_url values. The DepMap portal file-manifest endpoint used by the CCLE entry (https://depmap.org/portal/download/api/downloads) now returns an HTML bot-verification page rather than JSON, so the figshare API is the reliable no-auth surface for PRISM data."
structure: cross-section
---

# PRISM Repurposing (Broad)

## Why this source matters

PRISM (Profiling Relative Inhibition Simultaneously in Mixtures) is the Broad Institute's pooled, DNA-barcoded cell-line viability platform, run by the PRISM Lab and distributed through the DepMap portal. The Repurposing dataset measures the growth-inhibitory activity of ~4,518 drugs (the Broad Repurposing Library of mostly non-oncology and clinically-advanced compounds) across ~578 barcoded human cancer cell lines in a primary single-dose screen, plus a secondary 8-point dose-response screen of ~1,448 compounds against ~499 lines. It is the largest public compound-by-cell-line viability resource and the standard starting point for anti-cancer repurposing hypotheses, MOA-informed sensitivity analysis, and drug-response model benchmarking. Because every line is keyed to a DepMap `ACH-` model ID, PRISM sits inside the DepMap/CCLE ecosystem (secondary domain: `bio-genomics`): pair the drug-response matrix with CCLE multi-omics and DepMap CRISPR essentiality on the shared cell-line key.

## Agent use cases

- drug repurposing candidate discovery
- compound sensitivity profiling across cancer cell lines
- mechanism-of-action and target lookup for screened compounds
- selective-killing / context-specific vulnerability analysis
- benchmarking drug-response prediction models

## Join strategy

PRISM exposes no canonical join key from `schema/join-keys.yaml` directly. Its identifiers are all source-native and currently unregistered:

- **Cell lines** are keyed on `depmap_id` (Broad `ACH-######`) and `ccle_name` (e.g. `A549_LUNG`) in the `*-cell-line-info.csv` files. These are the join bridge to CCLE, DepMap CRISPR/RNAi screens, and (via the DepMap model table) Sanger Cell Model Passports.
- **Compounds** are keyed on `broad_id` (`BRD-` compound IDs) in the `*-treatment-info.csv` files, which also carry `name`, `moa`, `target`, `disease.area`, `indication`, `smiles`, and `phase`. There is no `CHEMBL_ID` or `INCHI_KEY` column; the compound structure is only given as `smiles`. To join PRISM compounds to ChEMBL, PubChem, or DrugBank, canonicalise the `smiles` to an `INCHI_KEY` (a registered join key) client-side, or resolve by name against those sources.

Because the shared axis with the rest of the DepMap ecosystem is the cell-line identifier (`DEPMAP_ID` / `CCLE_NAME`) and the compound bridge is `BROAD_COMPOUND_ID`, promoting those three to canonical join keys (see Review notes) is what would make PRISM joinable in the reverse index. Pair with CCLE and DepMap on the cell-line key; pair with ChEMBL / PubChem / DrugBank on a derived `INCHI_KEY` or compound name.

## Access notes

Data is bulk CSV, no auth, no query API. Two paths:

1. **figshare (recommended, scriptable).** Each release is a figshare article. PRISM Repurposing 20Q2 is `10.6084/m9.figshare.20564034` (CC BY 4.0); the latest public release is Repurposing 24Q2 (`figshare.com/articles/dataset/Repurposing_Public_24Q2/25917643`). The figshare v2 API is no-auth JSON: `GET https://api.figshare.com/v2/articles/20564034` returns the file list with `download_url` values (`ndownloader.figshare.com/files/...`). Always pull `*-primary-screen-cell-line-info.csv` (resolves `depmap_id`, `ccle_name`, tissue) and `*-primary-screen-replicate-collapsed-treatment-info.csv` (resolves `broad_id`, `name`, `moa`, `target`, `smiles`, `phase`) alongside the log-fold-change matrix. Large files: primary/secondary log-fold-change and MFI matrices run 45-300 MB.
2. **DepMap portal.** `https://depmap.org/repurposing/` has an interactive compound/line explorer and links the same files. The generic DepMap download-manifest endpoint (`/portal/download/api/downloads`) now returns a bot-verification HTML page rather than JSON, so prefer the figshare API for programmatic access.

License on the figshare records is **CC BY 4.0** (attribution only, commercial use permitted), which is more permissive than the general DepMap Terms of Use that govern the CCLE/CRISPR files; cite the PRISM Repurposing publication (Corsello et al., *Nature Cancer* 2020) and the release. Freshness check: list DepMap's figshare releases or the 24Q2 article date; each release is static once posted.

## MCP / connector notes

No PRISM-specific MCP. The three community DepMap servers noted in the CCLE entry (`openpharma-org/depmap-mcp-server`, `QuentinCody/depmap-mcp-server`, `Saurabhsing21/Deepmap-mcp`) wrap gene-level essentiality/expression/mutation/copy-number, not the repurposing drug-viability matrices. Suggested connector surface: `search_compounds(name|moa|target|phase)`, `get_compound_sensitivity(broad_id, lines)`, `get_line_sensitivity(depmap_id, compounds)`, `get_dose_response(broad_id, depmap_id)` (secondary screen), and `resolve_line(depmap_id|ccle_name)`. It must abstract over (a) the primary vs secondary screen split, (b) the replicate vs replicate-collapsed file variants, (c) the release-versioned figshare layout, and (d) SMILES-to-InChIKey canonicalisation so compounds can be joined to ChEMBL/PubChem.

## Review notes

- **join_keys is empty by design.** PRISM exposes no key currently in `schema/join-keys.yaml`. Its structure identifier is `smiles` (not a registered key); `INCHI_KEY` (registered) is derivable from it but not present in the payload, so it is documented in Join strategy rather than asserted in YAML.
- **License:** figshare records are CC BY 4.0. This is more permissive than the `DepMap-Terms-Of-Use` short name used for the CCLE entry; the PRISM figshare drops are genuinely CC-BY, so `CC-BY-4.0` / `cost: free` is correct here. Flag if the registry wants a consistency note that different DepMap-hosted datasets carry different licences.
- **Potential new canonical join keys for review** (the "cell-line/compound candidates" flagged for this source):
  - `DEPMAP_ID`
    - Entity type: `cancer_cell_line`
    - Pattern: `^ACH-[0-9]{6}$`
    - Other datasets that would use it: CCLE, DepMap CRISPR/RNAi, PRISM, Cell Model Passports. Already flagged in `cancer-cell-line-encyclopedia.md`; re-affirming.
  - `CCLE_NAME`
    - Entity type: `cancer_cell_line`
    - Pattern: `^[A-Z0-9]+_[A-Z_]+$` (e.g. `A549_LUNG`)
    - Other datasets that would use it: CCLE, GDSC, CTRP, legacy Broad screens. Already flagged in `cancer-cell-line-encyclopedia.md`.
  - `BROAD_COMPOUND_ID`
    - Entity type: `chemical_compound`
    - Pattern: `^BRD-[A-Z0-9-]+$` (e.g. `BRD-K12345678-001-01-9`)
    - Other datasets that would use it: PRISM, Broad Repurposing Hub, Connectivity Map (CMap/LINCS L1000), CTRP. New candidate not previously flagged; the Broad compound ID is the natural join across all Broad small-molecule resources.
  - `PRISM_SCREEN_ID` is source-internal (per-screen batch id) and left in `primary_keys` only; not proposed as a cross-source key.
- `entry_kind: panel` (compound x cell-line x dose viability matrix); `structure: cross-section` because each release is a snapshot with no temporal axis.
