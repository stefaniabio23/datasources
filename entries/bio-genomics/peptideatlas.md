---
id: peptideatlas
name: PeptideAtlas
domain: bio-genomics
entry_kind: knowledge-graph
description: Compendium of peptides and proteins identified from uniformly reprocessed public mass-spectrometry proteomics data, with protein-existence evidence and genome mappings; the Human build is the flagship.
homepage_url: https://peptideatlas.org/
docs_url: https://peptideatlas.org/builds/human/
type:
  - web-ui
  - bulk-download
auth_required: none
cost: free
license: ISB-PeptideAtlas-Terms
rate_limit: "none; static bulk files + query interface"
bulk_available: true
frequency: "annual builds per organism"
lag: "reprocessed data lags original ProteomeXchange deposition by months to years"
geography: [global]
join_keys:
  - UNIPROT_ACCESSION
  - ENSEMBL_ID
  - GENE_SYMBOL
primary_keys:
  - PEPTIDEATLAS_PEPTIDE_ACCESSION
  - PEPTIDEATLAS_BUILD
  - PXD_IDENTIFIER
mcp_status: mcp-needed-low-value
agent_use_cases:
  - protein-existence evidence lookup
  - mass-spec proteomics evidence mining
  - peptide-to-protein and peptide-to-genome mapping
  - Human Proteome Project coverage checks
  - cross-referencing UniProt / Ensembl / neXtProt
access_test:
  command: "curl -sf 'https://peptideatlas.org/builds/human/' -o /dev/null"
  expected_status: 200
last_verified: 2026-07-02
build_priority: low
notes: "access_test executed 2026-07-02 (build page → 200). Data processed by the Trans-Proteomic Pipeline (TPP, tppms.org), which is analysis software, not a dataset, so it is not a separate registry entry. Underlying spectra come from ProteomeXchange (PXD ids). License is non-SPDX; flagged in Review notes."
---

# PeptideAtlas

## Why this source matters

PeptideAtlas is a proteomics evidence resource built by the Institute for Systems Biology (Seattle Proteome Center): it takes thousands of publicly deposited mass-spectrometry datasets, reprocesses them uniformly through a single pipeline, and publishes the peptides and proteins observed, with statistical confidence and genome coordinates. The Human build (2026-01) covers roughly 1.75 billion peptide-spectrum matches, 5.3 million distinct peptides, and ~17,553 canonical proteins across ~1,246 datasets. For an agent, it answers a question UniProt alone cannot: "is there real experimental protein-level evidence that this gene's protein exists, and from which experiments?" It is a primary input to the Human Proteome Project's protein-existence (PE) tiers. Builds exist for other organisms too; Human is the flagship.

## Agent use cases

- protein-existence evidence lookup
- mass-spec proteomics evidence mining
- peptide-to-protein and peptide-to-genome mapping
- Human Proteome Project coverage checks
- cross-referencing UniProt / Ensembl / neXtProt

## Join strategy

The strong canonical join keys are `UNIPROT_ACCESSION` (PeptideAtlas maps observed peptides to UniProt protein accessions) and `ENSEMBL_ID` (peptides carry Ensembl gene/transcript context and chromosomal coordinates); `GENE_SYMBOL` is available for human-readable joins. Pair with `uniprot`, `ensembl`, and `human-protein-atlas` to go from "protein exists / where expressed" to "protein observed by MS". neXtProt is cross-referenced but is not in the canonical registry.

Native identifiers are the PeptideAtlas peptide accession (`PAp########`), the build identifier, and the source `PXD_IDENTIFIER` (ProteomeXchange dataset id) for provenance back to the raw experiment. Use `PXD_IDENTIFIER` to join into ProteomeXchange / PRIDE for the original spectra.

## Access notes

No authentication for public builds (an optional login exposes additional/private builds). Two practical paths: the web query interface at `peptideatlas.org` for interactive protein/peptide lookups, and bulk downloads per build (FASTA of identified proteins, TSV tables of peptides and mappings, and MySQL dumps) for whole-build analysis. There is no clean REST API; the query surface is CGI-driven, so for programmatic work prefer the bulk TSV/FASTA files over scraping the query pages. Builds are versioned by date (e.g. `2026-01`); pin the build for reproducibility.

## MCP / connector notes

No MCP exists and the audience is specialised (proteomics), so it is low priority. A useful connector would expose: look up a protein's evidence by UniProt accession, list peptides for a protein, map a peptide to genome coordinates, and resolve a build's provenance datasets (PXD ids). The main thing to abstract over is the CGI query layer and the per-build file layout.

## Review notes

- New non-SPDX license short name `ISB-PeptideAtlas-Terms`. The site carries an ISB copyright notice while builds are openly downloadable for research and the underlying spectra are public (ProteomeXchange). Confirm the short-name convention or split source-data vs build license.
- `PXD_IDENTIFIER` (ProteomeXchange) is flagged as a primary key; it has genuine cross-source utility (PRIDE, ProteomeXchange, MassIVE) and may be worth promoting to the canonical registry if a second proteomics source is added.
- TPPMS (Trans-Proteomic Pipeline) was requested alongside this but is analysis software, not a dataset; recorded here rather than as its own entry.
- `join_key_fields` omitted: PeptideAtlas payload field paths were not verified against a live download. Add them when the bulk TSV schema is confirmed.
