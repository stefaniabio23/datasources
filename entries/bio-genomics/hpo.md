---
id: hpo
name: Human Phenotype Ontology
domain: bio-genomics
entry_kind: knowledge-graph
description: Standardised computable vocabulary of human phenotypic abnormalities, with curated annotations linking phenotype terms to hereditary diseases and disease genes.
homepage_url: https://hpo.jax.org/
docs_url: https://hpo.jax.org/data/annotations
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: HPO-License
rate_limit: "unpublished; polite use expected"
bulk_available: true
frequency: "roughly monthly to quarterly release cadence"
lag: "new terms and disease/gene annotations appear per dated release; weeks-to-months"
geography: [global]
join_keys:
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
primary_keys:
  - HPO_ID
join_key_fields:
  - join_key: GENE_SYMBOL
    fields: [gene_symbol, genes_to_phenotype.gene_symbol, phenotype_to_genes.gene_symbol]
  - join_key: ENTREZ_GENE_ID
    fields: [ncbi_gene_id, genes_to_phenotype.ncbi_gene_id, phenotype_to_genes.ncbi_gene_id]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/seandavi/ols-mcp-server
mcp_notes: >
  No HPO-specific MCP. The EBI OLS MCP (seandavi/ols-mcp-server) covers HP term
  search and hierarchy traversal alongside GO, MONDO, and other OBO ontologies,
  but does not expose the phenotype-to-gene or phenotype-to-disease annotation
  layer, which is HPO's highest-value surface. A dedicated connector should wrap
  ontology.jax.org term/search endpoints plus the genes_to_phenotype /
  phenotype.hpoa / phenotype_to_genes annotation tables.
agent_use_cases:
  - phenotype term search and normalisation
  - phenotype-driven gene prioritisation
  - disease-to-phenotype profile lookup
  - HPO-based semantic similarity for rare-disease diagnosis
  - mapping free-text clinical findings to standardised phenotype codes
access_test:
  command: "curl -sf 'https://ontology.jax.org/api/hp/terms/HP:0001250'"
  expected_status: 200
  expected_fields: [id, name, definition, synonyms, xrefs]
last_verified: 2026-07-02
build_priority: high
structure: registry-snapshot
pit_reconstructable: true
revisions_possible: true
---

# Human Phenotype Ontology

## Why this source matters

HPO is the de facto standard vocabulary for describing human phenotypic abnormalities, maintained by the Monarch Initiative and hosted at the Jackson Laboratory. It has grown to over 18,000 terms arranged in a DAG under a small set of top-level organ-system branches, plus more than 156,000 curated annotations linking phenotypes to over 8,000 hereditary diseases and their causative genes. The ontology underpins nearly every phenotype-driven rare-disease diagnostic tool (Exomiser, LIRICAL, Phenomizer, GeneMatcher-style workflows), because encoding a patient's findings as HP terms enables semantic-similarity scoring against known disease profiles. Secondary relevance to `clinical-biotech` (variant and disease prioritisation feeding drug-target work) and `public-health` (rare-disease registries). HPO term IDs are consumed as cross-references by ClinVar, Open Targets, GWAS Catalog, MONDO, EFO, and Orphanet, which makes HPO a hub vocabulary for the deep-phenotyping layer of biomedical joins.

## Agent use cases

- phenotype term search and normalisation
- phenotype-driven gene prioritisation
- disease-to-phenotype profile lookup
- HPO-based semantic similarity for rare-disease diagnosis
- mapping free-text clinical findings to standardised phenotype codes

## Join strategy

HPO is the issuing authority for `HP:NNNNNNN` phenotype term identifiers (the source's native primary key; not yet a canonical join key, see Review notes). The directly joinable identifiers HPO exposes are gene identifiers on its annotation tables: `genes_to_phenotype.txt` and `phenotype_to_genes.txt` carry both `ENTREZ_GENE_ID` (NCBI Gene ID) and `GENE_SYMBOL` for every phenotype-gene association. These are the clean pivot into NCBI Gene, Ensembl, UniProt, GWAS Catalog, and Open Targets.

The disease-annotation file (`phenotype.hpoa`) keys diseases by prefixed identifiers: `OMIM:`, `ORPHA:`, and `DECIPHER:`. These disease codes and the HP term IDs themselves are high-value cross-source keys but are not in the canonical registry yet; they are flagged in Review notes rather than invented into `join_keys`. Term records also publish `xrefs` to SNOMED CT, UMLS, MeSH, and MONDO for onward mapping.

Recommended pattern: resolve clinical findings to HP term IDs via the ontology search endpoint, pull the phenotype-to-gene table to get `ENTREZ_GENE_ID` / `GENE_SYMBOL` candidate lists, then pivot to Ensembl/UniProt/Open Targets for the molecular layer. Pair with MONDO or Orphanet for disease-entity resolution and with ClinVar for variant-level evidence.

## Access notes

**REST API (recommended first hit):** `https://ontology.jax.org/api/`. No auth, returns JSON. `GET /api/hp/terms/{HP:ID}` returns definition, synonyms, xrefs, and descendant counts; search and gene/disease-annotation endpoints are documented at the same host. A lightweight alternative autocomplete API is the NIH Clinical Tables service at `https://clinicaltables.nlm.nih.gov/api/hpo/v3/search?terms=...` (no auth, no HPO annotation payload, useful only for term lookup).

**Bulk downloads:** the ontology (`hp.obo`, `hp.owl`, `hp.json`) and the annotation tables (`phenotype.hpoa`, `genes_to_phenotype.txt`, `phenotype_to_genes.txt`) are published on each release. Canonical release archive is the GitHub repo `obophenotype/human-phenotype-ontology` (every release tagged and dated; most recent release June 2026), with stable PURLs under `http://purl.obolibrary.org/obo/hp/`. For any analysis touching more than a handful of terms, pull the release snapshot and work locally rather than paginating the API.

**Reproducibility:** every release is dated and archived, so vintage reconstruction is possible; always log the release version because terms are added, renamed, and obsoleted between releases (annotations get restated).

**License nuance:** HPO is distributed under a custom license (`https://hpo.jax.org/license`), free for academic and commercial use with attribution, but it prohibits altering the content or the logical relationships within the HPO files and requires that modifications be made by the HPO developers. This is not a standard SPDX license; verify redistribution terms before republishing a modified ontology.

## MCP / connector notes

No HPO-specific MCP server exists as of July 2026. The closest is the EBI OLS MCP (`github.com/seandavi/ols-mcp-server`), a community server that wraps the Ontology Lookup Service and can search and traverse HP terms alongside GO, MONDO, Uberon, and other OBO ontologies. It covers ontology navigation only; it does not expose HPO's phenotype-to-gene or phenotype-to-disease annotations, which are the load-bearing surface for diagnostic and prioritisation workflows.

Suggested dedicated surface: `search_phenotype` (text -> HP terms with synonyms), `get_term` (definition, xrefs, ancestors, descendants), `genes_for_phenotype` (HP ID -> gene list with ENTREZ/symbol), `phenotypes_for_gene` (gene -> HP terms), `phenotypes_for_disease` (OMIM/ORPHA -> HP profile), `phenotype_similarity` (two HP term sets -> semantic-similarity score), and `fetch_release_snapshot` (pinned ontology + annotation tables by release date). The connector must abstract over the ontology-vs-annotation split and handle the disease-ID prefixing (`OMIM:` / `ORPHA:` / `DECIPHER:`).

## Review notes

Potential new join keys for review (all exposed by HPO, none currently in `schema/join-keys.yaml`; do not invent into `join_keys`):

- `HPO_ID` — Human Phenotype Ontology term identifier. HPO is the issuing authority; consumed as a cross-reference by ClinVar, Open Targets, GWAS Catalog, MONDO, EFO, Orphanet, and clinical deep-phenotyping pipelines. Currently stored in this entry's `primary_keys`.
  Entity type: phenotype_term
  Pattern: `^HP:[0-9]{7}$`
  Other datasets that would use it: ClinVar, Open Targets, GWAS Catalog, MONDO, EFO, Orphanet, GTEx (sample phenotype tags)

- `OMIM_ID` — Online Mendelian Inheritance in Man disease/gene identifier (in HPO as the `OMIM:` prefix on `phenotype.hpoa`).
  Entity type: mendelian_disease_or_gene
  Pattern: `^[0-9]{6}$` (often written `OMIM:######`)
  Other datasets that would use it: ClinVar, Orphanet, MONDO, Open Targets, ClinGen

- `ORPHA_CODE` — Orphanet rare-disease identifier (in HPO as the `ORPHA:` prefix).
  Entity type: rare_disease
  Pattern: `^[0-9]+$` (often written `ORPHA:######`)
  Other datasets that would use it: Orphanet, MONDO, EU rare-disease registries, Open Targets

- `MONDO_ID` — Mondo Disease Ontology identifier (appears in HPO term `xrefs` and is the emerging disease-integration hub).
  Entity type: disease
  Pattern: `^MONDO:[0-9]{7}$`
  Other datasets that would use it: MONDO, Open Targets, EFO, ClinGen, disease-annotation layers generally

License short name `HPO-License` is a new non-SPDX canonical name proposed here (custom Jackson Laboratory / Monarch HPO terms; free academic + commercial use with attribution, no-alteration clause). Confirm the short name before merge; nuance is documented in Access notes.
