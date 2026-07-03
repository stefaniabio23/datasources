---
id: lincs-l1000
name: LINCS / CMap L1000 (CLUE)
domain: bio-genomics
entry_kind: panel
description: Perturbational gene-expression signatures from the Broad Institute's L1000 assay (>1M replicate-collapsed signatures over >5,000 compounds and genetic perturbations across a core panel of human cell lines), served through the CLUE platform, GEO, and Google BigQuery.
homepage_url: https://clue.io/
docs_url: https://clue.io/developer-resources
type:
  - rest-api
  - bulk-download
  - dataset-dump
  - database
  - web-ui
auth_required: api-key-free
cost: free-non-commercial
license: CLUE-Terms-Of-Use
rate_limit: "no published per-key limit; large signature pulls routed to GCTx bulk files or BigQuery rather than the REST API"
bulk_available: true
frequency: "static major releases (GSE92742 Phase I 2017, GSE70138 Phase II, 2020 beta release); no rolling refresh"
lag: "archival; signatures pinned to their release, not updated after publication"
geography: [global]
join_keys:
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
  - INCHI_KEY
primary_keys:
  - BRD_ID
  - PERT_INAME
  - SIG_ID
  - CELL_ID
join_key_fields:
  - join_key: GENE_SYMBOL
    fields: [gene_symbol, pr_gene_symbol]
  - join_key: ENTREZ_GENE_ID
    fields: [gene_id, pr_gene_id]
  - join_key: INCHI_KEY
    fields: [inchi_key, pert_info.inchi_key]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - compound mechanism-of-action lookup by connectivity
  - drug-repurposing candidate discovery
  - query a gene-expression signature against the reference database
  - retrieve perturbagen signatures for a target gene knockdown/overexpression
  - build feature matrices of perturbation response for ML models
access_test:
  command: "curl -sf -H \"user_key: ${CLUE_USER_KEY}\" 'https://api.clue.io/api/perts?filter=%7B%22where%22%3A%7B%22pert_iname%22%3A%22vorinostat%22%7D%7D'"
  expected_status: 200
  expected_fields: [pert_id, pert_iname, pert_type, inchi_key]
last_verified: 2026-07-02
build_priority: medium
notes: "access_test not executed against an authenticated response; requires ${CLUE_USER_KEY} (free with academic CLUE registration). Unauthenticated probe on 2026-07-02 returned HTTP 401 with body {\"error\":\"User Key must be specified in the request header\"}, confirming the endpoint is live and gated on the user_key header. clue.io landing returned 200 the same day; a previously announced site retirement (Jan 2026) had not taken the API offline as of the verification date, but GEO remains the durable access path."
---

# LINCS / CMap L1000 (CLUE)

## Why this source matters

L1000 is the perturbational half of gene expression: instead of measuring transcriptomes across tissues or patients, it measures how the transcriptome shifts after a defined perturbation. The Broad Institute's Connectivity Map (CMap) team, funded under the NIH Common Fund LINCS program, ran the L1000 assay (Luminex bead readout of 978 landmark genes, ~11,350 further genes computationally inferred) across >5,000 small-molecule and genetic (shRNA/CRISPR/overexpression) perturbagens and a core panel of human cell lines (A375, A549, HEPG2, HCC515, HA1E, HT29, MCF7, PC3, VCAP, plus extensions), producing >3M profiles collapsed into >1M signatures. The signal is connectivity: query any up/down gene-expression signature and retrieve the perturbations whose signatures are most (anti-)correlated, which is the engine behind mechanism-of-action inference and drug repurposing. Any agent doing target deconvolution, MOA hypothesis generation, or repurposing diligence should treat L1000/CMap as the reference perturbation atlas. Secondary domain: `clinical-biotech`, since the compound annotations (targets, MOA, clinical phase) drive preclinical pharmacology and repurposing workflows.

## Agent use cases

- compound mechanism-of-action lookup by connectivity
- drug-repurposing candidate discovery
- query a gene-expression signature against the reference database
- retrieve perturbagen signatures for a target gene knockdown/overexpression
- build feature matrices of perturbation response for ML models

## Join strategy

L1000 keys genes on both `GENE_SYMBOL` (HGNC, `pr_gene_symbol`) and `ENTREZ_GENE_ID` (`pr_gene_id`), so gene-level joins into NCBI Gene, GTEx, Expression Atlas, Open Targets, and CCLE are direct. Small-molecule perturbagens carry `INCHI_KEY` (and canonical SMILES / PubChem CID) in the compound annotation table, which is the reliable structural join into PubChem, ChEMBL, and DrugBank; use it rather than the compound name, since `pert_iname` values are Broad-internal and not canonical.

The load-bearing native identifiers sit outside the canonical registry. Each perturbagen has a Broad `BRD_ID` (`pert_id`, e.g. `BRD-K34157611`), each signature a `SIG_ID`, and each cell context a `CELL_ID` (cell line name such as `A375`, `MCF7`). The `BRD_ID` is the same Broad compound namespace used by DepMap, PRISM, and the Drug Repurposing Hub, and `CELL_ID` maps to Cellosaurus (`CVCL_*`) and DepMap line identifiers, so both are strong cross-source join candidates. They are flagged in Review notes as proposed canonical keys rather than invented into `join_keys`.

Pair L1000 with the Drug Repurposing Hub and ChEMBL (compound annotation and bioactivity by `INCHI_KEY` / `BRD_ID`), CCLE and DepMap (baseline omics and dependency for the same `CELL_ID` lines), and Open Targets or GTEx (gene-level context by `ENTREZ_GENE_ID` / `GENE_SYMBOL`).

## Access notes

Two practical paths. (1) The **CLUE REST API** at `https://api.clue.io/api/` exposes `/perts`, `/cells`, `/genes`, `/sigs`, `/profiles`, and a `/query` (connectivity job) service. Every request needs a `user_key` header; the key is free after registering an academic CLUE account. LoopBack-style query strings pass a URL-encoded JSON `filter` (e.g. `?filter={"where":{"pert_iname":"vorinostat"}}`). Start with `GET /api/perts` for a compound annotation, then `/api/sigs` for signature metadata, then a `/query` job for connectivity scoring. (2) **Bulk** GCTx matrices and metadata tables are deposited in NCBI GEO (`GSE92742` Phase I, `GSE70138` Phase II, plus the 2020 beta release) and mirrored to Google BigQuery via the `cmapBQ` toolkit; use these for anything beyond single-record lookups, since the full signature matrix is billions of data points. The `cmapPy` / `cmapBQ` Python libraries read GCTx and stream BigQuery.

License is **research use only**: access keys, code, and data files are for non-commercial research; commercial use requires contacting the Broad. Data deposited in GEO carries GEO's standard public-domain terms and is the durable access route regardless of CLUE portal status. A CLUE site retirement was announced for early 2026; as of 2026-07-02 the landing page and API were still responding (see YAML `notes`), but agents should treat GEO + BigQuery as the stable long-term surface and the REST API as convenient-but-possibly-transient.

## MCP / connector notes

No MCP server exists for LINCS/CMap L1000 (searched modelcontextprotocol, GitHub, npm, PyPI, 2026-07-02). Marked `mcp-needed-low-value`: the audience is narrower than a general omics source, and the practical access is already served by `cmapPy` / `cmapBQ`. A useful connector would expose `get_perturbagen(brd_id | name)`, `get_signature(sig_id)`, `query_connectivity(up_genes, down_genes)`, `list_signatures(pert, cell)`, and `get_gene(symbol | entrez)`, and would have to abstract over (a) the `user_key` header auth, (b) the GCTx/BigQuery split for large pulls versus the REST API for metadata, and (c) resolution between `BRD_ID`, `pert_iname`, `INCHI_KEY`, and `CELL_ID` so callers do not hand-map perturbagens and cell lines.

## Review notes

- License: the CLUE/CMap "research use only" terms have no SPDX identifier. Used canonical short name `CLUE-Terms-Of-Use`; not yet in `SCHEMA.md § License conventions`. Flag for review, and note the split: the API/CLUE-hosted files are research-use-only, while the same data mirrored in GEO is effectively public domain under GEO terms. `cost: free-non-commercial` chosen over `free-with-registration` because commercial use is explicitly gated behind a separate agreement, even though registration is also required.
- Potential new canonical join keys for review:
  - `BRD_ID`
    - Entity type: `perturbagen` (small molecule or genetic reagent)
    - Pattern: `^BRD-[A-Z][0-9A-Z]+$` (e.g. `BRD-K34157611`)
    - Other datasets that would use it: Drug Repurposing Hub, PRISM, DepMap, CTRP, other Broad compound screens.
  - `CELL_ID`
    - Entity type: `cell_line`
    - Pattern: cell line short name, e.g. `A375`, `MCF7` (no fixed regex; free-text short name)
    - Other datasets that would use it: DepMap/CCLE (`CCLE_NAME`, `DEPMAP_ID`), Cellosaurus (`CVCL_*`), GDSC. Overlaps the cell-line-identity proposal already raised in `cancer-cell-line-encyclopedia.md`; consolidate into a single Cellosaurus-anchored cell-line key rather than adopting the CMap short name directly.
  - `SIG_ID` and `PERT_INAME` are CMap-internal and left in `primary_keys` only; no cross-source utility, so not proposed as canonical keys.
- `entry_kind`: chose `panel` (genes measured across a cross-section of perturbagen x cell-line x dose x time conditions), matching the GTEx-style multi-dimensional expression cube, over `knowledge-graph` or `mixed`.
- `access_test` constructed with a `${CLUE_USER_KEY}` placeholder and not executed against an authenticated response. Unauthenticated probe returned HTTP 401 ("User Key must be specified in the request header"), confirming the endpoint is live and auth-gated. Freshness is not a concern (archival releases); durability is, given the announced clue.io retirement, hence GEO/BigQuery flagged as the stable path.
