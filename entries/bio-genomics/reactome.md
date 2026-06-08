---
id: reactome
name: Reactome
domain: bio-genomics
entry_kind: knowledge-graph
description: Free, open-source, curated, and peer-reviewed pathway database covering human biology with orthology projections to model organisms.
homepage_url: https://reactome.org/
docs_url: https://reactome.org/dev
type:
  - rest-api
  - bulk-download
  - database
auth_required: none
cost: free
license: CC0
rate_limit: unknown
bulk_available: true
frequency: quarterly
lag: months
geography: [global]
join_keys:
  - UNIPROT_ACCESSION
  - ENSEMBL_ID
  - GENE_SYMBOL
  - CHEMBL_ID
  - PMID
  - DOI
primary_keys:
  - REACTOME_STABLE_ID
  - REACTOME_DB_ID
join_key_fields:
  - join_key: UNIPROT_ACCESSION
    fields: [referenceEntity.identifier]
  - join_key: GENE_SYMBOL
    fields: [referenceEntity.geneName, name]
  - join_key: CHEMBL_ID
    fields: [referenceEntity.identifier]
  - join_key: PMID
    fields: [literatureReference.pubMedIdentifier]
  - join_key: DOI
    fields: [doi, hasEvent.doi]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/reactome/reactome-mcp
  - github.com/Augmented-Nature/Reactome-MCP-Server
  - github.com/openpharma-org/reactome-mcp-server
  - github.com/pipeworx-io/mcp-reactome
  - github.com/ron-42/reactome-mcp-python
mcp_notes: >
  Multiple community MCPs exist (including a Reactome-authored prototype), none yet
  designated official or stable. Suggested surface: search_pathway, get_pathway,
  list_pathways_for_gene, run_analysis (enrichment), get_participants,
  resolve_external_id (UniProt/Ensembl/ChEBI -> Reactome stId).
agent_use_cases:
  - pathway enrichment analysis
  - gene-to-pathway lookup
  - protein interaction context
  - drug target pathway mapping
  - cross-species ortholog pathway projection
access_test:
  command: "curl -sf 'https://reactome.org/ContentService/data/query/R-HSA-1640170' -H 'Accept: application/json'"
  expected_status: 200
  expected_fields: [dbId, stId, displayName, speciesName, schemaClass]
last_verified: 2026-06-08
build_priority: medium
---

# Reactome

## Why this source matters

Curated, peer-reviewed pathway knowledge base for human biology with computationally inferred projections to 14+ model organisms. Co-developed by EMBL-EBI, NYU Langone, OHSU, and the Ontario Institute for Cancer Research; funded by NIH (U24 HG012198) and EMBL. As of v96 (April 2026): 2,870 human pathways, 16,338 reactions, 11,677 proteins, 2,198 small molecules, 1,102 drugs, 42,784 literature references. The most-cited free pathway database alongside KEGG, and unlike KEGG it is fully open (CC0 for data, Apache 2.0 for code). Default backbone for over-representation and gene-set enrichment workflows.

## Agent use cases

- pathway enrichment analysis
- gene-to-pathway lookup
- protein interaction context
- drug target pathway mapping
- cross-species ortholog pathway projection

## Join strategy

Reactome exposes external identifiers as first-class cross-references: `UNIPROT_ACCESSION` (primary protein identifier), `ENSEMBL_ID` (genes and proteins), `GENE_SYMBOL` (HGNC for human), `CHEMBL_ID` (small molecules and drugs), `PMID` and `DOI` (literature references). Mapping tables are published per release as flat files at `/download-data` (UniProt, Ensembl, NCBI Gene, ChEBI, miRBase, GtoP to pathways at multiple hierarchy levels).

Reactome-internal stable identifiers (`R-HSA-NNNNNNN` for human, `R-XXX-NNNNNNN` for other species, plus `dbId` integers) are intentionally outside the canonical registry; use them for direct ContentService lookups, not for cross-source joins.

Potential additional join keys exposed but not in the registry: ChEBI compound IDs, GO term IDs, KEGG compound IDs, miRBase mature miRNA IDs. See Review notes.

Pair with UniProt for protein sequence and function, Ensembl for genomic context, ChEMBL for drug-target activity data, and OpenTargets for disease-target associations layered on Reactome pathway scaffolds.

## Access notes

**Primary entry point:** ContentService REST API at `https://reactome.org/ContentService/`. No auth. Returns JSON. Stable identifiers follow the `R-HSA-NNNNNNN` pattern; use the `data/query/{id}` endpoint for any database object (pathway, reaction, entity).

**Pathway enrichment / over-representation:** AnalysisService at `https://reactome.org/AnalysisService/`. POST a gene/protein list, get a token, retrieve enrichment results paged by token. Tokens persist server-side for ~7 days.

**Bulk:** Quarterly releases (since v89, June 2024) on Zenodo and at `/download-data` in BioPAX L3, SBML L3v1, SBGN, GMT (pathways as gene sets), and full Neo4j graph database dumps (also packaged as Docker images on AWS ECR). Identifier mapping flat files (UniProt/Ensembl/NCBI/ChEBI to pathways) published per release.

**Rate limits:** Not publicly documented. Behave politely; for any analysis touching more than a few thousand entities, prefer the Neo4j dump or GMT files over the API.

**License nuance:** Database content is CC0 (no attribution required, but encouraged). Pathway diagrams, illustrations, icons, and branding are CC-BY 4.0 (attribution required). Code repos under Apache 2.0. Cite the standard Reactome paper when used in publications regardless of CC0.

## MCP / connector notes

Five community MCP servers exist as of June 2026 (none designated official):

- `github.com/reactome/reactome-mcp` (Reactome-authored, marked prototype)
- `github.com/Augmented-Nature/Reactome-MCP-Server`
- `github.com/openpharma-org/reactome-mcp-server` (production-ready fork of the Augmented Nature server)
- `github.com/pipeworx-io/mcp-reactome`
- `github.com/ron-42/reactome-mcp-python`

Suggested canonical surface for a consolidated connector: `search_pathway`, `get_pathway`, `list_pathways_for_gene` (UniProt/Ensembl/symbol input), `run_enrichment_analysis` (gene list in, token + paged results out), `get_participants` (pathway -> proteins/molecules/drugs), `resolve_external_id` (UniProt/Ensembl/ChEBI -> Reactome stId). Connector must abstract over the two-step token flow on AnalysisService and the verbose nested response shape on ContentService.

## Review notes

Potential new join keys for review:

- `CHEBI_ID` (small-molecule and drug identifier; widely used across UniProt, ChEMBL, PubChem, Reactome, OpenTargets)
  Entity type: chemical_compound
  Pattern: `^CHEBI:[0-9]+$`
  Other datasets that would use it: UniProt, ChEMBL, OpenTargets, MetaboLights, PubChem
- `GO_ID` (Gene Ontology term identifier; ubiquitous across functional annotation sources)
  Entity type: ontology_term
  Pattern: `^GO:[0-9]{7}$`
  Other datasets that would use it: UniProt, Ensembl, AmiGO, OpenTargets, Reactome
- `KEGG_COMPOUND_ID` and `KEGG_PATHWAY_ID` (KEGG cross-references; useful if KEGG is added later)
  Entity type: chemical_compound / pathway
- `MIRBASE_ID` (mature miRNA identifier; relevant for non-coding RNA pathways)
  Entity type: mirna

Other items needing review:

- Reactome publishes both stable IDs (`R-HSA-NNNNNNN`) and numeric `dbId` integers; neither is currently in the registry. Both are Reactome-internal and probably belong in body prose rather than canonical join keys, but flagging in case enough pathway-DB entries land to justify a `REACTOME_ID` canonical key.
- Rate-limit guidance is not published; the entry marks `rate_limit: unknown`. Consider reaching out to the Reactome team or testing empirically to fill this in.
