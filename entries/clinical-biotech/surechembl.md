---
id: surechembl
name: SureChEMBL
domain: clinical-biotech
entry_kind: knowledge-graph
description: EMBL-EBI database of chemistry text-mined from patent documents, linking compounds extracted from patent full text and images to the patents that disclose them.
homepage_url: https://www.surechembl.org/
docs_url: https://chembl.gitbook.io/surechembl-documentation
type:
  - web-ui
  - bulk-download
  - rest-api
auth_required: none
cost: free
license: CC0
rate_limit: "none; bulk download + UniChem REST for structure lookups"
bulk_available: true
frequency: "rolling; reprocessed as new patents publish (SureChEMBL 2.0 pipeline)"
lag: "days-to-weeks after patent publication"
geography: [global]
join_keys:
  - INCHI_KEY
  - CHEMBL_ID
primary_keys:
  - SURECHEMBL_ID
mcp_status: mcp-needed-low-value
agent_use_cases:
  - chemistry extraction from patents
  - compound-to-patent mapping
  - chemical patent landscaping and prior-art search
  - linking disclosed compounds to patent families
  - feeding small-molecule IP analysis
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/unichem/rest/inchikey/RYYVLZVUVIJVGH-UHFFFAOYSA-N' -o /dev/null"
  expected_status: 200
last_verified: 2026-07-07
build_priority: low
notes: "SureChEMBL 2.0 (2025 major update): rebuilt annotation pipeline, AI annotations, expanded global coverage (USPTO/EPO/WIPO full text, JPO titles/abstracts, CNIPA translated). No first-class REST API yet (stated future development); UniChem provides InChI-based REST cross-referencing (SureChEMBL is UniChem source 15) and is the access_test path. Data was donated to the public domain (2013); CC0 used pending confirmation (flagged). PATENT_PUBLICATION_NUMBER is the key join here but is not yet in the registry, proposed in PR #1; flagged in Review notes."
---

# SureChEMBL

## Why this source matters

SureChEMBL is the patent-chemistry sibling of ChEMBL: an EMBL-EBI resource that text-mines chemical structures out of patent documents, from both the full text and the embedded images, and links each extracted compound to the patents that disclose it. It answers a question no structured chemistry database can: "which patents disclose this molecule (or molecules like it), and who filed them?" That makes it the backbone of small-molecule freedom-to-operate and competitive-IP analysis. The 2025 SureChEMBL 2.0 release rebuilt the annotation pipeline with AI extraction and broadened coverage (full text from USPTO, EPO, and WIPO; titles/abstracts from JPO; translated full text from CNIPA). Secondary domain overlap with `government-open-data` (patents) and `bio-genomics` (chemistry).

## Agent use cases

- chemistry extraction from patents
- compound-to-patent mapping
- chemical patent landscaping and prior-art search
- linking disclosed compounds to patent families
- feeding small-molecule IP analysis

## Join strategy

The canonical structure keys are `INCHI_KEY` (SureChEMBL is keyed on InChI, the basis of its UniChem cross-referencing) and `CHEMBL_ID` (resolvable via UniChem to tie a patent-disclosed compound to its ChEMBL bioactivity record). The native primary key is the SureChEMBL compound id (`SURECHEMBL_ID`, e.g. `SCHEMBL######`). The other load-bearing join is the patent side: each compound carries the patent publication numbers that disclose it, which is the bridge to `epo-ops`, `the-lens`, `google-patents-bigquery`, and `uspto-patents`. That patent key (`PATENT_PUBLICATION_NUMBER`) is not yet in the canonical registry; it is proposed in PR #1, once merged, add it to `join_keys` here.

## Access notes

Two practical paths. `UniChem` (`ebi.ac.uk/unichem/rest/`) gives InChI/InChIKey structure lookups that return SureChEMBL ids and cross-references to ChEMBL and other sources, use it for programmatic structure-to-patent resolution today. Bulk data ships in the SureChEMBL 2.0 unified download format (compound-patent annotations) from the EBI download servers; pull the bulk files for whole-corpus analysis. The web UI at `surechembl.org` is for interactive search. A first-class SureChEMBL REST API is a stated future development, so for now favour UniChem for lookups and the bulk files for scale. No authentication.

## MCP / connector notes

No MCP exists; patent-chemistry is a specialised audience, so it is low priority. A useful connector would resolve a structure (SMILES/InChIKey) to its SureChEMBL id and disclosing patents, and pull the compounds annotated to a given patent. It should abstract over the UniChem lookup layer and the bulk-file schema until the native API ships.

## Review notes

- License `CC0` is used on the basis of the 2013 public-domain donation; confirm the exact current terms for SureChEMBL 2.0 (the wider ChEMBL family uses CC-BY-SA, but SureChEMBL was released to the public domain).
- `PATENT_PUBLICATION_NUMBER` is the highest-value join key for this source and is proposed in PR #1 (`schema/join-keys.yaml`). Add it to `join_keys` once that PR merges.
- `SURECHEMBL_ID` flagged as a primary key; cross-source utility is low outside SureChEMBL/UniChem, so registering it is not warranted yet.
- access_test uses UniChem (SureChEMBL source 15) since SureChEMBL has no public REST endpoint of its own.
