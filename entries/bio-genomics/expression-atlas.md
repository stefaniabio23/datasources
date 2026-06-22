---
id: expression-atlas
name: Expression Atlas (EMBL-EBI)
domain: bio-genomics
entry_kind: reference-table
description: Curated, uniformly re-analyzed gene and protein expression data across species, covering baseline (TPM by tissue/condition) and differential (log2FC, FDR) experiments, with a separate Single Cell Expression Atlas.
homepage_url: https://www.ebi.ac.uk/gxa/home
docs_url: https://www.ebi.ac.uk/gxa/help/index.html
type:
  - web-ui
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "unpublished; bulk/FTP and the Bioconductor package are the intended paths for programmatic pulls"
bulk_available: true
frequency: "periodic curated releases (data re-quantified against fixed Ensembl/Ensembl Genomes/EFO versions per release)"
lag: "months to years; raw data predates the curated re-analysis release"
geography: [global]
join_keys:
  - ENSEMBL_ID
  - GENE_SYMBOL
  - EFO_ID
  - NCBI_TAXON_ID
  - PMID
primary_keys:
  - E-MTAB-ACCESSION
  - E-GEOD-ACCESSION
join_key_fields:
  - join_key: ENSEMBL_ID
    fields: [Gene ID]
  - join_key: GENE_SYMBOL
    fields: [Gene Name]
  - join_key: EFO_ID
    fields: [factor ontology term, sample characteristic ontology term]
  - join_key: NCBI_TAXON_ID
    fields: [organism]
  - join_key: PMID
    fields: [publication PubMed ID]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No MCP today. The Bioconductor ExpressionAtlas package plus per-experiment TSV
  downloads cover most use. Suggested surface: search_experiments,
  get_baseline_expression (gene by tissue/condition, TPM), get_differential_expression
  (gene by contrast, log2FC + FDR), list_tissues, resolve_gene. Connector must
  abstract over (a) Bulk vs Single Cell Atlas split, (b) baseline vs differential
  experiment types, and (c) per-release Ensembl/EFO version pinning.
agent_use_cases:
  - tissue-specific baseline expression lookup
  - differential expression by condition (log2FC, FDR)
  - candidate-gene expression profiling
  - cross-species expression comparison
  - single-cell expression context
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/gxa/json/experiments'"
  expected_status: 200
  expected_fields: ["experiments[].experimentAccession", "experiments[].experimentType", "experiments[].species", "experiments[].experimentDescription", "experiments[].lastUpdate"]
last_verified: 2026-06-22
build_priority: low
---

# Expression Atlas (EMBL-EBI)

## Why this source matters

Expression Atlas is EMBL-EBI's curated, uniformly re-analyzed atlas of gene and protein expression across species. Unlike a raw read archive, every experiment is re-quantified through a standard pipeline (iRAP for RNA-seq) against fixed reference versions per release, so a gene's TPM in one experiment is methodologically comparable to the next. It splits into Bulk Expression Atlas (baseline expression as TPM by tissue/condition, plus differential expression as log2 fold-change with FDR-adjusted p-values) and a dedicated Single Cell Expression Atlas. For an agent answering "is this gene expressed in tissue X" or "is this gene up/down under condition Y", Expression Atlas is the curated comparable layer to reach for first, with the raw reads one accession hop away. Secondary domain: `clinical-biotech` for target-tissue and target-condition validation in drug discovery.

## Agent use cases

- tissue-specific baseline expression lookup
- differential expression by condition (log2FC, FDR)
- candidate-gene expression profiling
- cross-species expression comparison
- single-cell expression context

## Join strategy

Genes are keyed by `ENSEMBL_ID` (the primary identifier across all matrices) with `GENE_SYMBOL` carried alongside as the human-readable name; strip GENCODE version suffixes when joining against versioned Ensembl IDs from other sources. Experimental conditions and sample characteristics are annotated with `EFO_ID` (Experimental Factor Ontology), which is the natural bridge to disease/phenotype-keyed resources like Open Targets and GWAS Catalog. Each experiment records its `NCBI_TAXON_ID` (67 species), enabling cross-species filtering, and curated experiments link a source `PMID` for joins to Europe PMC, OpenAlex, and PubMed.

The reused experiment accessions (`E-MTAB-...`, `E-GEOD-...`) are source-native primary keys, listed in `primary_keys`. These trace back to ArrayExpress/BioStudies and, for `E-GEOD-` accessions, to the originating GEO series. Use them to follow a curated experiment back to its raw reads in ENA/SRA or ArrayExpress; they are provenance pointers, not cross-source canonical join keys. Pair Expression Atlas with Ensembl or NCBI Gene for gene metadata, with GTEx for an independent human baseline, and with EFO/Open Targets for disease context.

## Access notes

No auth, free, CC-BY-4.0 content (Apache-2.0 for the code). Start at a single experiment page and use its per-experiment downloads: baseline experiments ship a TSV of expression (TPM) by gene x condition; differential experiments ship analytics TSVs of log2 fold-change and FDR-adjusted p-values per contrast, plus sample annotations and protocol files. Programmatic pulls of the expression matrices go through the Bioconductor `ExpressionAtlas` R package (raw counts for RNA-seq, normalized intensities for microarray) or the EBI FTP bulk mirror; the web UI is for browsing, not matrix-scale retrieval. There is no documented general REST query API for the per-gene expression values themselves, but Expression Atlas does serve an undocumented but stable experiment-catalogue JSON endpoint at `https://www.ebi.ac.uk/gxa/json/experiments` (and the Single Cell equivalent at `https://www.ebi.ac.uk/gxa/sc/json/experiments`), returning every experiment with `experimentAccession`, `experimentType`, `species`, `experimentDescription`, `experimentalFactors`, and `lastUpdate`. `access_test` is populated against that catalogue endpoint (verified 200 with 4,562 experiments on 2026-06-22); it lists and filters experiments but does not return expression values, so per-gene retrieval still routes through the Bioconductor package or FTP. Verify freshness via `experiments[].lastUpdate` or the pinned Ensembl/EFO version on the homepage.

Two structural gotchas. First, this is a *derived* curated layer: data is uniformly re-quantified against fixed reference versions per release, the opposite of pulling raw reads straight from GEO/SRA, so values are comparable across experiments but lag the raw deposition and follow the E-MTAB/E-GEOD accession back to ENA/SRA/ArrayExpress for raw reads. Second, Bulk and Single Cell are separate resources with separate UIs and download shapes; pick the right one before querying (bulk for TPM-by-tissue and differential contrasts, single cell for per-cell-type expression).

## MCP / connector notes

No MCP exists. Audience is genomics-literate and overlaps with GTEx and Ensembl users, so build priority is low. Suggested surface: `search_experiments` (by gene, organism, condition), `get_baseline_expression` (gene by tissue/condition, returns TPM), `get_differential_expression` (gene by contrast, returns log2FC + FDR), `list_tissues`, `resolve_gene`. The connector must abstract over (a) the Bulk vs Single Cell Atlas split behind one interface, (b) baseline vs differential experiment types (different payload shapes), (c) per-release Ensembl/Ensembl Genomes/EFO version pinning for reproducibility, and (d) the gap between the `json/experiments` catalogue endpoint (good for search/list/filter) and per-gene expression values, which still require the Bioconductor package or FTP mirror rather than a query API or UI scrape.

## Review notes

- License confirmed via `https://www.ebi.ac.uk/gxa/licence.html` on 2026-06-22: content is CC BY 4.0 International; source code is Apache License 2.0 (Copyright 2008-2026 Functional Genomics Team, EMBL-EBI). Used SPDX `CC-BY-4.0` for the content `license` field; Apache-2.0 noted in the body since the field holds the content license.
- `entry_kind: reference-table` chosen because Expression Atlas is a curated, re-quantified lookup layer over expression values rather than a raw panel; the underlying matrices are panel-shaped, but the agent-facing object is "look up the curated expression value for gene x condition." Flag for review if a different kind (`panel` or `knowledge-graph`) is preferred for consistency with GTEx (`panel`).
- Non-registered cross-source identifiers flagged (kept in `primary_keys`, not invented as join keys): `E-MTAB-` / `E-GEOD-` experiment accessions (ArrayExpress/BioStudies; `E-GEOD-` maps to a GEO series). A canonical `ARRAYEXPRESS_ACCESSION` (or `BIOSTUDIES_ACCESSION`) join key could be worth registering, since it recurs across ArrayExpress, BioStudies, Single Cell Expression Atlas, and GEO-derived datasets:
  - Potential new join key for review: ARRAYEXPRESS_ACCESSION
    - Entity type: expression_experiment
    - Pattern: `^E-[A-Z]{4}-[0-9]+$` (e.g. `E-MTAB-2836`, `E-GEOD-30352`)
    - Other datasets that would use it: ArrayExpress, BioStudies, Single Cell Expression Atlas, GEO (via E-GEOD- prefix)
