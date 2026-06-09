---
id: gene-ontology
name: Gene Ontology
domain: bio-genomics
entry_kind: knowledge-graph
description: Canonical open ontology of gene functions (molecular function, biological process, cellular component) plus curated GO annotations linking genes and gene products to GO terms across hundreds of species.
homepage_url: https://geneontology.org/
docs_url: https://geneontology.org/docs/download-go-annotations/
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: unknown
bulk_available: true
frequency: monthly
lag: weeks
geography: [global]
join_keys:
  - GO_ID
  - UNIPROT_ACCESSION
  - ENSEMBL_ID
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
  - NCBI_TAXON_ID
  - PMID
  - DOI
primary_keys:
  - GO_ID
  - GO_CAM_ID
join_key_fields:
  - join_key: GO_ID
    fields: [id, object.id, association.object.id]
  - join_key: UNIPROT_ACCESSION
    fields: [subject.id, association.subject.id, gaf.db_object_id]
  - join_key: ENSEMBL_ID
    fields: [subject.id, gaf.db_object_id]
  - join_key: GENE_SYMBOL
    fields: [subject.label, gaf.db_object_symbol]
  - join_key: ENTREZ_GENE_ID
    fields: [subject.id, gaf.db_object_id]
  - join_key: NCBI_TAXON_ID
    fields: [subject.taxon.id, object.taxon.id, gaf.taxon]
  - join_key: PMID
    fields: [reference, evidence.reference, gaf.db_reference]
  - join_key: DOI
    fields: [reference]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/Augmented-Nature/GeneOntology-MCP-Server
  - github.com/openpharma-org/geneontology-mcp-server
  - github.com/pipeworx-io/mcp-quickgo
  - github.com/uermel/go-graph-mcp
mcp_notes: >
  Several overlapping community MCPs, none official from the GO Consortium. Most wrap
  AmiGO / api.geneontology.org search and term-lookup endpoints; the QuickGO MCP wraps
  the EBI mirror instead. Consolidated surface should expose search_term,
  get_term (with ancestors/descendants), list_annotations_for_gene,
  list_genes_for_term (with species filter), get_term_enrichment (gene list in),
  resolve_external_id (UniProt/Ensembl/symbol -> annotations), and
  fetch_ontology_snapshot (OBO/OWL by release date).
agent_use_cases:
  - gene function lookup
  - GO term enrichment analysis
  - ontology term search and disambiguation
  - cross-species functional annotation transfer
  - resolving gene/protein IDs to biological process or pathway context
access_test:
  command: "curl -sf 'https://api.geneontology.org/api/bioentity/gene/UniProtKB:P04637/function?rows=2' -H 'Accept: application/json'"
  expected_status: 200
  expected_fields: [associations, subject.id, object.id, evidence_type]
last_verified: 2026-06-09
build_priority: high
---

# Gene Ontology

## Why this source matters

The Gene Ontology is the de facto standard vocabulary for describing gene and gene-product function across species. Run by the Gene Ontology Consortium (founded 1998), with curation contributed by major Model Organism Databases (MGI, RGD, SGD, FlyBase, WormBase, ZFIN, TAIR, PomBase, dictyBase) and protein databases (UniProt-GOA, EBI). The ontology has three orthogonal aspects: molecular function, biological process, and cellular component. Annotations link gene products (mostly UniProt accessions, plus MOD identifiers) to GO terms with evidence codes and literature references. Every downstream functional-enrichment workflow, GSEA backbone, and pathway-context tool depends on GO. Secondary relevance to `academic` (literature cross-references via PMID/DOI) and `clinical-biotech` (target annotation feeding into drug discovery pipelines).

## Agent use cases

- gene function lookup
- GO term enrichment analysis
- ontology term search and disambiguation
- cross-species functional annotation transfer
- resolving gene/protein IDs to biological process or pathway context

## Join strategy

GO is the issuing authority for `GO_ID` (`GO:NNNNNNN` 7-digit form, e.g. `GO:0008285`). Annotations expose `UNIPROT_ACCESSION` as the dominant gene-product identifier, plus MOD-specific IDs (MGI, FlyBase, WormBase, etc.) and `ENSEMBL_ID`, `GENE_SYMBOL`, and `ENTREZ_GENE_ID` via mapping files. `NCBI_TAXON_ID` is mandatory on every annotation (column 13 of GAF 2.2). Evidence references resolve to `PMID` and occasionally `DOI`.

Cross-reference mapping files at `https://current.geneontology.org/ontology/external2go/` link GO terms to Enzyme Commission, KEGG, HAMAP, InterPro, MetaCyc, Reactome, Rfam, Rhea, UniProt Keywords, UniProt Subcellular Location, UniRules, and Wikipedia. These let agents pivot from GO to other functional vocabularies without round-tripping through UniProt.

GO-internal identifiers (`GO-CAM` model IDs like `gomodel:R-HSA-NNNNNNN` for causal activity models, `ECO:NNNNNNN` for evidence codes) sit outside the canonical registry; use them for direct GO-CAM browser lookups and evidence-quality filtering, not cross-source joins.

Recommended pivot pattern: resolve any gene/protein identifier to `UNIPROT_ACCESSION` first, hit `/api/bioentity/gene/{id}/function` for the GO annotation set, then pivot via `external2go` mappings to Reactome, KEGG, or InterPro depending on the question.

Pair with UniProt (canonical protein metadata), Reactome (curated pathways), Ensembl (genomic context), and OpenTargets (disease-target associations that consume GO annotations directly).

## Access notes

**Primary REST entry point:** `https://api.geneontology.org/api/`. No auth. Returns JSON. Useful first-hit endpoints:

- `/api/bioentity/gene/{id}/function` — GO annotations for a gene/protein (e.g. `UniProtKB:P04637` for TP53)
- `/api/bioentity/function/{GO_ID}/genes` — gene products annotated to a term
- `/api/ontology/term/{GO_ID}` — term metadata, definition, synonyms
- `/api/ontology/term/{GO_ID}/subgraph` — local DAG neighbourhood
- `/api/ontol/labeler` — bulk ID-to-label resolution

Note: `http://api.geneontology.org` 301-redirects to HTTPS; always use the HTTPS form to avoid the redirect hop.

**AmiGO web UI:** `http://amigo.geneontology.org/` for faceted human browsing of terms and annotations.

**QuickGO (EBI mirror):** `https://www.ebi.ac.uk/QuickGO/` offers an alternative REST surface (`/services/`) with different ergonomics; useful when the GO Consortium API is rate-limited or down.

**Bulk downloads:** Monthly releases.

- Ontology files at `https://purl.obolibrary.org/obo/go/` in three flavours: `go-basic` (acyclic, recommended for most users; OBO/JSON/OWL), `go` (with `has_part`/`occurs_in`; OBO/JSON/OWL), `go-plus` (fully axiomatised with ChEBI/Cell Ontology/Uberon imports; JSON/OWL only).
- GAF 2.2 annotation files per species/MOD at `https://current.geneontology.org/products/pages/downloads.html`. GPAD and GPI companion formats also published.
- All releases archived on Zenodo with persistent DOIs from 2018-07-02 onward (e.g. `10.5281/zenodo.NNNNNNNN`); older releases at `http://release.geneontology.org/` back to 2004-03-01.

**Coverage gaps:** GO annotations are not available through NCBI for archaea, bacteria, viruses, or GenBank-only genomes. For prokaryotes use UniProt-GOA directly.

**Rate limits:** Not publicly documented. Behave politely on the API; for any analysis touching more than a few thousand genes, pull the GAF/OBO snapshot and run locally.

**Reproducibility:** GAF headers carry the release date and the ontology version (`!date-generated:` and `!go-version:`). Always log both alongside results. The citation policy requires both for any published analysis.

**License nuance:** All data and data products are CC-BY 4.0. Attribution must cite the Ashburner et al. (2000) founding paper and the most recent GO Consortium update paper, plus the specific release date (or Zenodo DOI). Tool-specific citations (GO Enrichment Analysis, AmiGO, GO-CAMs) apply when those surfaces are used.

## MCP / connector notes

Four community MCP servers exist as of June 2026, none designated official:

- `github.com/Augmented-Nature/GeneOntology-MCP-Server` — JavaScript, broad ontology-analysis surface
- `github.com/openpharma-org/geneontology-mcp-server` — JavaScript, term search and gene annotation tools
- `github.com/pipeworx-io/mcp-quickgo` — TypeScript, wraps the QuickGO EBI mirror rather than api.geneontology.org
- `github.com/uermel/go-graph-mcp` — Python, local KuzuDB-backed search with synonym/definition augmentation

Suggested canonical surface for a consolidated connector: `search_term` (text query against labels/synonyms), `get_term` (definition, aspect, ancestors, descendants), `list_annotations_for_gene` (UniProt/Ensembl/symbol input, species filter, evidence filter), `list_genes_for_term` (term ID + species), `run_enrichment_analysis` (gene list + background, ORA/GSEA), `resolve_external_id` (UniProt/Ensembl/symbol -> annotations), `fetch_ontology_snapshot` (pinned OBO/OWL by release date), and `lookup_external2go` (Enzyme Commission/KEGG/InterPro/Reactome -> GO term mapping). Connector must abstract over evidence-code filtering (manual vs IEA-only is the load-bearing distinction for any rigorous analysis) and species/taxon handling.

## Review notes

Potential new join keys for review:

- `ECO_ID` — Evidence and Conclusion Ontology identifier (e.g. `ECO:0000250`); pattern `^ECO:[0-9]{7}$`. Used by GO, UniProt, GOA, and any source that distinguishes manual from electronic evidence. Filtering on evidence codes is the single most common GO-side analysis step.
  Entity type: evidence_code
  Pattern: `^ECO:[0-9]{7}$`
  Other datasets that would use it: GO, UniProt-GOA, OpenTargets, AmiGO

- `INTERPRO_ID` is already in the canonical registry; GO maps to it via `interpro2go`, so existing InterPro and UniProt entries could expose this transit edge.

- `KEGG_PATHWAY_ID` and `ENZYME_EC_CODE` are flagged in other entries (Reactome) and would land naturally if KEGG and ENZYME entries are added later. GO already publishes mapping files for both.

Other items needing review:

- `GO_ID` is already in the canonical registry as `entity_type: ontology_term`. That description is correct but generic; an agent looking for "the ontology that owns GO_IDs" reaches this entry, which is the intended pivot.
- The Augmented Nature MCP family is also present for UniProt, Reactome, and other bio sources; consider noting this family as a vendor pattern in a separate review (one author maintains many overlapping single-API MCPs, which complicates the "official vs community" heuristic).
- Rate-limit guidance is not published; the entry marks `rate_limit: unknown`. The QuickGO mirror at EBI has documented limits and may be the better target for high-volume workflows.
