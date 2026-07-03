---
id: drugcomb
name: DrugComb
domain: clinical-biotech
entry_kind: panel
description: Open-access portal of harmonized cancer drug-combination and single-drug screening data, reporting CSS sensitivity plus Loewe, Bliss, HSA, and ZIP synergy scores per drug-drug-cell-line experiment across dozens of studies.
homepage_url: https://drugcomb.org/
docs_url: https://drugcomb.org/help/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: unknown
rate_limit: "no published per-IP limit; JSON REST API at api.drugcomb.org and versioned static bulk files served over HTTPS"
bulk_available: true
frequency: "periodic versioned releases (data files v1.3-v1.5); update paper snapshot March 2021"
geography: [global]
structure: cross-section
join_keys:
  - CHEMBL_ID
  - DRUGBANK_ID
  - INCHI_KEY
primary_keys:
  - DRUGCOMB_DRUG_ID
  - DRUGCOMB_BLOCK_ID
  - DRUGCOMB_STUDY_ID
  - DRUGCOMB_CELL_LINE_ID
join_key_fields:
  - join_key: CHEMBL_ID
    fields: [chembl_id]
  - join_key: DRUGBANK_ID
    fields: [drugbank_id]
  - join_key: INCHI_KEY
    fields: [inchikey, "get_targets/{inchiKey} path param"]
mcp_status: mcp-needed-high-value
agent_use_cases:
  - drug-combination synergy lookup by drug pair or cell line
  - synergy-model comparison (Loewe / Bliss / HSA / ZIP)
  - combination sensitivity (CSS) benchmarking across cell lines
  - training data for drug-synergy ML models
  - cross-referencing combination response with compound targets
access_test:
  command: "curl -sf 'https://api.drugcomb.org/drugs/1'"
  expected_status: 200
  expected_fields: [dname, chembl_id, inchikey, cid, drugbank_id]
last_verified: 2026-07-02
build_priority: medium
notes: "Live access_test not confirmed: api.drugcomb.org (193.167.189.25, CSC-IT Finland) resolved but the TCP connection timed out on 2026-07-02 and 2026-07-03, and drugcomb.org itself did not respond to WebFetch/curl. Endpoint set, response shape, and expected fields were verified against Wayback snapshots of https://api.drugcomb.org/ (2025-04-10) and https://api.drugcomb.org/drugs (2024-11-07, HTTP 200). Re-run the access_test when the host is reachable."
---

# DrugComb

## Why this source matters

DrugComb is the canonical open-access portal for cancer drug-combination screening data, run by the Research Program in Systems Oncology at the University of Helsinki Faculty of Medicine and hosted at CSC-IT Center for Science, Finland. It collects, standardizes, and harmonizes drug-combination and single-drug dose-response screens across cancer cell lines from dozens of published studies (37 studies as of the March 2021 update: ~751k combination experiments, ~718k single-drug screens, ~21.6M data points, ~8,400 distinct drugs, ~2,320 cell lines spanning 225 cancer types plus malaria and COVID-19). Each drug-drug-cell-line block is annotated with a CSS combination-sensitivity score and four synergy models (Loewe, Bliss, HSA, ZIP) plus an S score, so an agent can pull consistently computed synergy for any pair without re-deriving it from raw dose-response. It is the combination-therapy complement to single-agent screens like GDSC, CTRP, and PRISM. Secondary domain: `bio-genomics`, since cell lines are keyed to Cellosaurus and carry expression from DepMap and Cell Model Passports.

## Agent use cases

- drug-combination synergy lookup by drug pair or cell line
- synergy-model comparison (Loewe / Bliss / HSA / ZIP)
- combination sensitivity (CSS) benchmarking across cell lines
- training data for drug-synergy ML models
- cross-referencing combination response with compound targets

## Join strategy

The unit of data is a `block_id`: one dose-response matrix for a given drug-row / drug-col / cell-line experiment, with CSS and per-model synergy scores attached via `/summary/{block_id}` and raw points via `/response/{block_id}`. Blocks, drugs, studies, and cell lines are keyed on DrugComb-internal integer IDs (`primary_keys`), none of which are canonical registry keys.

For compounds, the `/drugs` endpoint normalizes every external identifier it can resolve: `CHEMBL_ID` (`chembl_id`), `DRUGBANK_ID` (`drugbank_id`), and `INCHI_KEY` (`inchikey`) are all canonical registry keys and are the clean pivots into ChEMBL, DrugBank, BindingDB, and structure-based sources. The same records also carry a PubChem CID (`cid`), a KEGG id (`kegg_id`), STITCH `CIDm`/`CIDs`, and SMILES/molecular formula, none of which are in the registry yet (see Review notes). Target predictions are exposed per compound via `/get_targets/{inchiKey}` (ChEMBL ligand-based, probability > 0.3).

For cell lines, DrugComb standardizes `Cell_line_name` to Cellosaurus and links DepMap for expression, but the API surfaces the line by internal id and name rather than a canonical registry key. Cellosaurus accession and DepMap id are both flagged below as new-key candidates so cell-line joins into GDSC, CCLE/DepMap, CTRP, and Cell Model Passports can be executable rather than name-matched. Pair DrugComb with ChEMBL / DrugBank (compound bioactivity by `CHEMBL_ID` / `DRUGBANK_ID`), GDSC and CTRP (orthogonal single-agent response), and DepMap (cell-line omics).

## Access notes

Two programmatic paths. The REST API base is `https://api.drugcomb.org` (Swagger-documented, JSON): `GET /drugs`, `/drugs/{id}`, `/cell_lines`, `/cell_lines/{id}`, `/studies`, `/studies/{id}`, `/response`, `/response/{block_id}`, `/summary`, `/summary/{block_id}`, `/get_targets/{inchiKey}`. No auth or key. Start with `/drugs/{id}` for a single compound record or `/summary/{block_id}` for a scored combination block. For whole-database analysis, use the versioned bulk files on `https://drugcomb.org/download/` (e.g. `drugcomb_data` v1.5 ~1.3 GB summary data, v1.4 raw dose-response ~1.9 GB, `summary_table` ~185 MB); the web portal at drugcomb.org also offers interactive upload-and-analyze of user dose-response matrices.

License is unresolved: the portal describes itself as "open-access, community-driven" and the update paper states the synergy and sensitivity scores are "freely available for download", but no explicit license statement (SPDX or otherwise) was found on the site. The `Apache 2.0` string on `api.drugcomb.org` is the Swagger/OpenAPI spec boilerplate, not a data-license grant. Treated as `license: unknown` pending confirmation; flagged in Review notes. Cite the DrugComb papers (Zagidullin et al., NAR 2019; Zheng et al., NAR 2021).

Freshness / reachability: at verification (2026-07-02 and 2026-07-03) both `api.drugcomb.org` and `drugcomb.org` resolved (CSC-IT Finland, 193.167.189.25) but did not complete a TCP connection, so the `access_test` was constructed and its shape verified against Wayback (2024-11-07 `/drugs` returned HTTP 200 with the expected fields) rather than run live. Re-run `curl -sf https://api.drugcomb.org/drugs/1` when the host is up; check the newest version label on the download page for data freshness.

## MCP / connector notes

No MCP exists, and no community connector was found. This is high-value: the cancer-pharmacology cluster already in the registry (GDSC, CTRP, DepMap, ChEMBL, Open Targets) shares DrugComb's audience, and combination synergy is the one axis those single-agent sources do not cover, so a shared connector would serve several entries. The API is clean, keyed JSON, so `api-direct-sufficient` is defensible, but the block/summary/response split and the four-model synergy vocabulary reward abstraction. A connector should expose `search_combinations(drug_a, drug_b, cell_line)`, `get_block_summary(block_id)` (CSS + Loewe/Bliss/HSA/ZIP + S), `get_dose_response(block_id)`, `resolve_drug(name -> CHEMBL_ID/DRUGBANK_ID/InChIKey/PubChem CID)`, `get_targets(inchikey)`, and `list_studies()`, and abstract over (a) the block-as-unit model, (b) internal-id-to-canonical-id resolution for both drugs and cell lines, and (c) API-vs-bulk routing for large synergy pulls.

## Review notes

- **License is unknown.** Portal is self-described open-access with freely downloadable scores, but no explicit license text was located. `license: unknown` per the prefer-honest-gap rule; needs a human to confirm the actual grant (and whether redistribution/commercial use is permitted) before this can be relied on for reuse. The `Apache 2.0` on the API page is the OpenAPI spec license, not the data license.
- **Access test not executed live.** Host unreachable (TCP timeout) at verification on 2026-07-02/03; endpoint set and field names verified via Wayback 200 snapshots. `last_verified` reflects the Wayback-confirmed structure, not a live 200.
- Potential new canonical join keys for review:
  - `CELLOSAURUS_ID`
    - Entity type: `cell_line` (Cellosaurus accession)
    - Pattern: `^CVCL_[A-Z0-9]{4}$` (e.g. `CVCL_0031`)
    - Other datasets that would use it: DrugComb, GDSC, CCLE/DepMap, CTRP, Cell Model Passports, ATCC. Strong candidate: this is the standard cross-source cell-line key and multiple existing entries name-match cell lines today.
  - `DEPMAP_ID`
    - Entity type: `cancer_cell_line`
    - Pattern: `^ACH-[0-9]{6}$` (e.g. `ACH-000001`)
    - Other datasets that would use it: DepMap, CCLE, PRISM, DrugComb, Cell Model Passports crosswalks.
  - `PUBCHEM_CID`
    - Entity type: `chemical_compound`
    - Pattern: `^[0-9]+$`
    - Other datasets that would use it: PubChem, ChEMBL, DrugBank, GDSC, and most compound-keyed sources. Already flagged in `gdsc.md`; DrugComb carries it in the `cid` field. Consolidate one proposal.
  - `KEGG_COMPOUND_ID`
    - Entity type: `chemical_compound_or_drug`
    - Pattern: `^[CD][0-9]{5}$` (e.g. `D00584`, `C00002`)
    - Other datasets that would use it: KEGG, DrugComb (`kegg_id`), various drug-annotation sources. Lower priority.
- `CHEMBL_ID`, `DRUGBANK_ID`, and `INCHI_KEY` are the only join keys drawn from the registry; all three are surfaced by the `/drugs` compound records (`InChIKey` also as the `/get_targets/{inchiKey}` path param).
- Domain: placed in `clinical-biotech` alongside GDSC, CTRP, ChEMBL, and BindingDB (preclinical drug-response pharmacology) over `bio-genomics` (where CCLE/DepMap live); the two are cross-referenceable and the secondary domain is noted in the body.
