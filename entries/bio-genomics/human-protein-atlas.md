---
id: human-protein-atlas
name: Human Protein Atlas
domain: bio-genomics
entry_kind: registry
description: Open-access atlas of human protein expression across tissues, single cells, brain regions, cancers, and blood, integrating antibody-based imaging with transcriptomics and proteomics.
homepage_url: https://www.proteinatlas.org/
docs_url: https://www.proteinatlas.org/about/help/dataaccess
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "unspecified; HEAD requests return X-Total-Results; 400 returned on excessive result sets"
bulk_available: true
frequency: "annual major release (currently v25.1, May 2026)"
lag: "release-pegged; reflects Ensembl version at build time (v25.1 = Ensembl 109)"
geography: [global]
join_keys:
  - ENSEMBL_ID
  - UNIPROT_ACCESSION
  - GENE_SYMBOL
primary_keys:
  - ENSEMBL_ID
  - HPA_ANTIBODY_ID
join_key_fields:
  - join_key: ENSEMBL_ID
    fields: [Ensembl]
  - join_key: UNIPROT_ACCESSION
    fields: [Uniprot]
  - join_key: GENE_SYMBOL
    fields: [Gene]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No MCP found. Stable per-gene REST endpoints (.json/.tsv/.xml on Ensembl ID) plus a
  search_download.php column-selection API make direct HTTP access nearly as easy as a
  connector. Suggested surface if built: get_gene, search_genes, get_tissue_expression,
  get_subcellular_location, get_pathology_summary.
agent_use_cases:
  - protein expression lookup by gene
  - tissue and single-cell localisation
  - cancer prognostic marker scan
  - antibody validation evidence
  - drug-target characterisation
access_test:
  command: "curl -sf 'https://www.proteinatlas.org/ENSG00000134057.json'"
  expected_status: 200
  expected_fields: [Gene, Ensembl, Uniprot, "Protein class", Chromosome]
last_verified: 2026-06-08
build_priority: low
---

# Human Protein Atlas

## Why this source matters

Antibody-based map of the human proteome covering ~17,400 unique proteins across tissues, single cells, brain regions, blood, and 18 cancer types. Run by SciLifeLab with KTH, Uppsala University, and Karolinska Institute, funded by the Knut and Alice Wallenberg Foundation. The standard reference for protein localisation, tissue specificity, and antibody validation evidence; useful to agents doing drug-target characterisation, biomarker scans, or cross-referencing transcript-level expression (Ensembl, GTEx) with protein-level evidence. Secondary relevance to `clinical-biotech` for the Pathology and Disease Blood atlases.

## Agent use cases

- protein expression lookup by gene
- tissue and single-cell localisation
- cancer prognostic marker scan
- antibody validation evidence
- drug-target characterisation

## Join strategy

HPA keys every entry on `ENSEMBL_ID` (the canonical access identifier in URLs), and cross-references `UNIPROT_ACCESSION` and `GENE_SYMBOL` in every record. NCBI Entrez gene IDs also appear but are not in the canonical registry. Pair with UniProt for sequence and functional annotation, Ensembl for transcript structure, GTEx for orthogonal RNA-level tissue expression, and STRING-DB for interaction context.

## Access notes

Per-gene REST is the cheapest path: `https://www.proteinatlas.org/<ENSEMBL_ID>.{json,tsv,xml}`. XML is the most complete; JSON and TSV carry the same column set (~120 fields). For filtered batches use `/api/search_download.php` with `search`, `format`, `columns`, and optional `compress=yes`. For full snapshots, the bulk files `proteinatlas.tsv.zip`, `proteinatlas.json.gz`, and `proteinatlas.xml.gz` cover the entire release; the XML bundle is the comprehensive one. Versioned archive hosts (`v16.proteinatlas.org`, etc.) preserve prior releases for reproducible analyses.

No auth, no documented rate limit. Be polite: HEAD a search first (`X-Total-Results` header) before pulling, and prefer the bulk download over thousands of per-gene calls. License is CC-BY-4.0 with the wrinkle that embedded third-party data (Ensembl, UniProt, GTEx, FANTOM, TCGA) carry their own terms; cite both HPA and the relevant upstream when redistributing.

## MCP / connector notes

No MCP found (GitHub search returned 429; npm and PyPI not searched in this run). Marked low-value because the per-gene endpoint already returns clean JSON keyed on a canonical identifier, and bulk consumers prefer the snapshot files. If a connector is built, useful surface: `get_gene(ensembl_id)`, `search_genes(query, columns)`, `get_tissue_expression(gene)`, `get_subcellular_location(gene)`, `get_pathology_summary(gene, cancer_type)`. The main thing to abstract: the search_download column vocabulary (80+ identifiers documented inline on the help page).

## Review notes

- License field set to `CC-BY-4.0`; HPA's licence page confirms this and notes downstream third-party data carries its own terms (documented in Access notes).
- NCBI Entrez Gene IDs appear in every record but no `ENTREZ_GENE_ID` canonical key exists in `schema/join-keys.yaml`. Potential new join key for review:
  - Entity type: `gene`
  - Pattern: `^[0-9]+$`
  - Other datasets that would use it: NCBI Gene, Ensembl, GTEx, GWAS Catalog, MyGene.info, most biomedical resources cross-mapping to NCBI.
- MCP search incomplete (GitHub returned 429); a second pass with `gh search repos` is worth running before promoting to `mcp-needed-high-value` if demand surfaces.
