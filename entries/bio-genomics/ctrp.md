---
id: ctrp
name: Cancer Therapeutics Response Portal (CTRP)
domain: bio-genomics
entry_kind: panel
description: Small-molecule sensitivity screen linking hundreds of cancer cell lines to compound area-under-curve responses alongside their genomic, lineage, and expression features.
homepage_url: https://portals.broadinstitute.org/ctrp/
docs_url: https://portals.broadinstitute.org/ctrp.v2/
type:
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CTD2-Open-Access
bulk_available: true
frequency: "static; v2 final release 2015 (v1 2013)"
join_keys:
  - INCHI_KEY
  - GENE_SYMBOL
primary_keys:
  - CTRP_MASTER_CPD_ID
  - CTRP_BROAD_CPD_ID
  - CTRP_MASTER_CCL_ID
  - CTRP_EXPERIMENT_ID
  - CCL_NAME
join_key_fields:
  - join_key: INCHI_KEY
    fields: [inchi_key]
  - join_key: GENE_SYMBOL
    fields: [gene_symbol_of_protein_target]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - drug-sensitivity lookup by cell line
  - compound mechanism-of-action inference
  - biomarker discovery from AUC vs genotype
  - cell-line panel selection for screening
  - pharmacogenomic benchmark data
access_test:
  command: "curl -sfL -o /dev/null -w '%{http_code}' 'https://portals.broadinstitute.org/ctrp.v2/'"
  expected_status: 200
last_verified: 2026-07-02
build_priority: low
---

# Cancer Therapeutics Response Portal (CTRP)

## Why this source matters

CTRP quantitatively measures the sensitivity of genetically characterized cancer cell lines to a curated "Informer Set" of small molecules, then links the resulting area-under-curve (AUC) responses back to each line's mutations, copy number, expression, and lineage. It is run by the Broad Institute's Chemical Biology and Therapeutics Science program (Schreiber and Clemons labs), with support from the NCI's Cancer Target Discovery and Development (CTD2) Network. v2 (2015) covers 545 compounds and combinations across 907 lines; v1 (2013) covered 354 compounds across 242 lines. It is one of the canonical preclinical pharmacogenomics datasets, sitting alongside GDSC, CCLE, and DepMap, and is a staple benchmark for drug-response prediction models, so it also serves a clinical-biotech (drug discovery, mechanism-of-action) audience.

## Agent use cases

- drug-sensitivity lookup by cell line
- compound mechanism-of-action inference
- biomarker discovery from AUC vs genotype
- cell-line panel selection for screening
- pharmacogenomic benchmark data

## Join strategy

The two registry-canonical keys CTRP exposes both live in the per-compound metadata (`v20.meta.per_compound.txt`): `INCHI_KEY` (via `inchi_key`) and `GENE_SYMBOL` (via `gene_symbol_of_protein_target`, the annotated protein target). Use `INCHI_KEY` to join compounds to ChEMBL, PubChem, DrugBank, and openFDA; use `GENE_SYMBOL` to join targets to Ensembl, UniProt, and Open Targets. The per-compound file also carries `cpd_smiles` (SMILES, not a canonical key here) which can be canonicalised to an InChIKey when `inchi_key` is missing.

Source-internal identifiers stay in `primary_keys`: `CTRP_MASTER_CPD_ID` and `CTRP_BROAD_CPD_ID` (Broad `BRD-` compound id) for compounds, `CTRP_MASTER_CCL_ID` and `CCL_NAME` (the CCLE cell-line name) for lines, and `CTRP_EXPERIMENT_ID` tying an assay to a line. AUC is the measured response value in `v20.data.curves_post_qc.txt` (`area_under_curve`), not an identifier, so it is not a join key.

There is no canonical registry key for a cancer cell line, and none for the Broad `BRD-` compound id, both of which have strong cross-source utility (CCLE, GDSC, DepMap, PharmacoDB). Both are flagged below as new-key candidates.

## Access notes

No REST API. Data is distributed as tab-delimited flat files (the CTRPv2 "ExpandedDataset": per-compound, per-cell-line, per-experiment metadata plus post-QC curve/AUC and genomic-feature tables). The original Broad FTP and `ctd2-data.nci.nih.gov` download hosts have been retired; the CTD2 data now routes through the NCI Index of NCI Studies catalog (`studycatalog.cancer.gov`) and the CTD2 Dashboard, and mirrored copies ship inside PharmacoDB and the DepMap/PharmacoGx ecosystem. The dataset is frozen (v2 is the final 2015 release), so freshness is not a concern; verify availability by confirming the portal loads and by locating the current ExpandedDataset mirror rather than checking a file date. The interactive portal itself is JS-heavy and read-only; bulk files are the practical path for any analysis.

## MCP / connector notes

No MCP exists. Value is low: the data is a small, static set of flat files that an agent can load directly, and the surrounding pharmacogenomics ecosystem (PharmacoGx in R, PharmacoDB's API, DepMap) already offers programmatic access to the same measurements. If built, a connector would abstract over the scattered mirror hosts and expose three surfaces: `get_sensitivity(cell_line, compound)` returning AUC, `compounds_for_target(gene_symbol)`, and `cell_lines_for_lineage(primary_site)`, joining the per-compound / per-cell-line / per-experiment tables behind the scenes.

## Review notes

Potential new join key for review: `DEPMAP_ID`
  Entity type: cancer_cell_line
  Pattern: `^ACH-[0-9]{6}$` (DepMap accession; CTRP itself carries the CCLE name `CCL_NAME`, which maps to a DepMap id)
  Other datasets that would use it: CCLE, GDSC, DepMap, PharmacoDB, Achilles. No canonical cell-line key currently exists in the registry; this is the highest-value gap for the pharmacogenomics domain.

Potential new join key for review: `BROAD_CPD_ID`
  Entity type: small_molecule_compound
  Pattern: `^BRD-[A-Z0-9]+` (Broad compound id, source column `broad_cpd_id`)
  Other datasets that would use it: CCLE, Broad Drug Repurposing Hub, PRISM. `INCHI_KEY` already covers structural joins, so this is lower priority.

License: used the canonical short name `CTD2-Open-Access` for the openly available NCI CTD2 / Broad sensitivity data. This short name is not yet in SCHEMA.md's known-license list; confirm or replace. The `remontoire-pac/ctrp-reference` analysis code is separately MIT-licensed, but that governs the code, not the data. No explicit SPDX license statement was found on the portal for the data itself, so this is a best-effort canonicalisation, not a verified SPDX code.
