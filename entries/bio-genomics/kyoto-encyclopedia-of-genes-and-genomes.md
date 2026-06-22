---
id: kyoto-encyclopedia-of-genes-and-genomes
name: KEGG (Kyoto Encyclopedia of Genes and Genomes)
domain: bio-genomics
entry_kind: knowledge-graph
description: Integrated database of pathways, genes, compounds, reactions, diseases, and drugs maintained by Kanehisa Laboratories at Kyoto University.
homepage_url: https://www.genome.jp/kegg/
docs_url: https://www.kegg.jp/kegg/rest/keggapi.html
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: freemium
license: KEGG-Custom
rate_limit: "3 requests per second (documented; exceeding it blocks access)"
bulk_available: true
frequency: monthly
lag: weeks
geography: [global]
join_keys:
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
  - UNIPROT_ACCESSION
  - ENSEMBL_ID
  - CHEBI_ID
  - PMID
  - NCBI_TAXON_ID
  - PDB_ID
primary_keys:
  - KEGG_PATHWAY_ID
  - KEGG_ORTHOLOGY_ID
  - KEGG_COMPOUND_ID
  - KEGG_REACTION_ID
  - KEGG_GLYCAN_ID
  - KEGG_DRUG_ID
  - KEGG_DISEASE_ID
  - KEGG_MODULE_ID
  - KEGG_GENOME_ID
  - KEGG_ENZYME_EC
  - KEGG_GENE_ID
  - KEGG_BRITE_ID
  - KEGG_NETWORK_ID
  - KEGG_VARIANT_ID
join_key_fields:
  - join_key: GENE_SYMBOL
    fields: [SYMBOL, NAME]
  - join_key: ENTREZ_GENE_ID
    fields: [DBLINKS.NCBI-GeneID]
  - join_key: UNIPROT_ACCESSION
    fields: [DBLINKS.UniProt]
  - join_key: ENSEMBL_ID
    fields: [DBLINKS.Ensembl]
  - join_key: CHEBI_ID
    fields: [DBLINKS.ChEBI]
  - join_key: PMID
    fields: [REFERENCE.PMID]
  - join_key: NCBI_TAXON_ID
    fields: [TAXONOMY]
  - join_key: PDB_ID
    fields: [DBLINKS.PDB]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/Augmented-Nature/KEGG-MCP-Server
  - github.com/martinuslee/oh-my-kegg-mcp
  - github.com/Lucas-Servi/kegg-mcp-server-python
  - github.com/pipeworx-io/mcp-kegg
  - github.com/QuentinCody/kegg-mcp-server
  - github.com/openpharma-org/kegg-mcp-server
mcp_notes: >
  Six community MCPs, none official from Kanehisa Laboratories. Most wrap the seven REST
  operations (info, list, find, get, conv, link, ddi). A consolidated connector should
  expose search_entry, get_entry (flat-file or JSON parse), list_by_database,
  resolve_external_id (NCBI/UniProt/ChEBI -> KEGG), get_pathway_map (KGML),
  get_genes_in_pathway, get_compounds_in_reaction, and check_drug_drug_interaction.
  Connector must abstract over flat-file response parsing (the default get output) and
  the org-prefixed gene identifier scheme (hsa:10458).
agent_use_cases:
  - pathway lookup and traversal
  - gene to pathway mapping
  - compound and reaction enrichment
  - drug interaction screening
  - cross-organism orthology via K numbers
access_test:
  command: "curl -sf 'https://rest.kegg.jp/info/kegg'"
  expected_status: 200
  expected_fields: [kegg, pathway, orthology, genes, compound, reaction, disease, drug]
last_verified: 2026-06-22
build_priority: medium
notes: "License is custom (not SPDX). Website and REST API are free for academic users; commercial use, FTP bulk downloads, and KEGG-backed services require a paid subscription via Pathway Solutions or an academic FTP subscription. See Review notes for license short-name proposal."
---

# KEGG (Kyoto Encyclopedia of Genes and Genomes)

## Why this source matters

KEGG is the integrated reference resource for systems-level biology built and maintained by Kanehisa Laboratories at Kyoto University since 1995. Release 118.0 (June 2026) holds 586 reference pathway maps, 28,293 KEGG Orthology groups, 67M genes across 26,728 sequenced genomes, 19,572 compounds, 15,677 reactions, 12,848 drugs, 3,070 diseases, and 1,768 disease networks. KEGG PATHWAY is the canonical reference for manually drawn pathway maps in molecular biology; KEGG Orthology (KO) is the de facto cross-species functional annotation vocabulary used by metagenomics pipelines, comparative genomics tools, and most pathway-enrichment libraries. Any agent doing pathway analysis, organism-spanning gene functional inference, or drug-target context will hit KEGG within a few hops. Funding model differs from public-funded peers (UniProt, Ensembl, Reactome): KEGG is privately operated and partially supported by paid FTP subscriptions, which constrains bulk redistribution.

## Agent use cases

- pathway lookup and traversal
- gene to pathway mapping
- compound and reaction enrichment
- drug interaction screening
- cross-organism orthology via K numbers

## Join strategy

KEGG mints a dense family of internal identifiers, none of which are in the canonical registry: pathway maps (`map00010`, `hsa00010`), KO orthology groups (`K00500`), compounds (`C01290`), reactions (`R00100`), glycans (`G00092`), drugs (`D00564`), diseases (`H00001`), modules (`M00001`), genomes (`T01001`), enzymes (`EC 1.1.1.1`), org-prefixed genes (`hsa:10458`), BRITE hierarchies (`br08901`), networks (`N00001`), and variants. These are KEGG-internal primary keys; use them for direct REST lookups rather than as cross-source joins.

For cross-source joining, use the `conv` and `link` REST operations to map between KEGG identifiers and canonical keys exposed via DBLINKS in flat-file entries: `GENE_SYMBOL` and `ENTREZ_GENE_ID` (NCBI GeneID), `UNIPROT_ACCESSION`, `ENSEMBL_ID`, `CHEBI_ID` (compounds and drugs), `NCBI_TAXON_ID` (genome organisms), `PDB_ID` (enzyme structures), and `PMID` for literature references. `conv` is the workhorse for outside-to-KEGG identifier translation (e.g. `/conv/hsa/ncbi-geneid`); `link` returns related entries within KEGG (e.g. `/link/pathway/hsa` returns all human gene to pathway edges).

Pair with Reactome and WikiPathways for alternative pathway scaffolds, UniProt for protein-level annotation, ChEMBL and DrugBank for drug-target activity, OpenTargets for disease-target evidence, and NCBI Gene or Ensembl for genomic context. KEGG is often the bridging vocabulary (via KO) when joining microbial metagenomics output to higher-level pathway analysis.

Potential new canonical join keys flagged in Review notes: `KEGG_PATHWAY_ID`, `KEGG_ORTHOLOGY_ID`, `KEGG_COMPOUND_ID`, `KEGG_REACTION_ID`, `KEGG_DRUG_ID`, `KEGG_DISEASE_ID`, `EC_NUMBER`.

## Access notes

**Primary entry point:** REST API at `https://rest.kegg.jp/`. No authentication. KEGG documents a limit of 3 API calls per second; exceeding it blocks access. Seven operations cover most use cases: `info` (release statistics), `list` (entry IDs and names), `find` (keyword search), `get` (full entry retrieval), `conv` (KEGG to outside identifier mapping), `link` (related-entry traversal), `ddi` (drug-drug interaction check). Default `get` response is KEGG flat-file format; append `/json` to a `get` URL for structured output where supported, `/kgml` for pathway XML, `/image` for PNG pathway maps.

**Identifier patterns to know:** organism-prefixed genes (`hsa:10458` for human, `eco:b0001` for E. coli, `sce:` for budding yeast), reference pathway maps (`map00010`), organism-specific pathway maps (`hsa00010`), KO groups (`K00500`), compounds (`C01290`), reactions (`R00100`), drugs (`D00564`).

**Bulk:** FTP downloads of the full KEGG release require an **academic subscription** (or commercial subscription via Pathway Solutions). The free REST API surfaces the same content but is not designed for full-database export. Any workflow that needs more than a few hundred thousand entry pulls should procure FTP access rather than crawl REST. Releases are monthly.

**License nuance:** Custom license. The KEGG website and REST API are free for individual academic users. Anyone providing services on top of KEGG (including hosted MCPs, downstream redistribution, or commercial products) needs a license: academic service providers get one bundled with the KEGG FTP academic subscription; commercial entities license through Pathway Solutions. Database content is explicitly described as "not a public database, nor a publicly funded database." Cite the standard Kanehisa et al. KEGG paper in publications.

**Known gotchas:**
- Documented limit of 3 API calls per second; exceeding it blocks access. The API is shared infrastructure, so behave politely and cache aggressively.
- Flat-file is the default response format; JSON is only supported on a subset of `get` endpoints. Parsers must handle the section-header flat format (`ENTRY`, `NAME`, `DEFINITION`, `DBLINKS`, etc.).
- Pathway map identifiers come in reference (`map`) and organism-specific (`hsa`, `eco`, etc.) flavours; agents pivoting between species need to translate the organism prefix.
- DBLINKS cross-references in flat-file entries are the primary join surface but are unevenly populated across databases.

## MCP / connector notes

Six community MCP servers exist as of June 2026, none designated official:

- `github.com/Augmented-Nature/KEGG-MCP-Server` (JavaScript, comprehensive REST coverage)
- `github.com/martinuslee/oh-my-kegg-mcp` (Python, 30+ tools, LangChain integration)
- `github.com/Lucas-Servi/kegg-mcp-server-python` (Python, 33 tools, Pydantic output, TTL caching)
- `github.com/pipeworx-io/mcp-kegg` (TypeScript)
- `github.com/QuentinCody/kegg-mcp-server` (TypeScript)
- `github.com/openpharma-org/kegg-mcp-server` (JavaScript)

Suggested canonical surface for a consolidated connector: `search_entry` (find across databases), `get_entry` (parsed flat-file or JSON), `list_by_database` (KO, pathway, compound, etc.), `resolve_external_id` (NCBI Gene / UniProt / ChEBI -> KEGG), `get_pathway_map` (KGML XML), `get_genes_in_pathway`, `get_compounds_in_reaction`, `check_drug_drug_interaction`. Must abstract over flat-file parsing, organism prefixes on gene IDs, and the reference-vs-organism-specific pathway-map split. Connector authors targeting non-academic users should surface the licensing constraint clearly: hosting an MCP that serves KEGG data to third parties is a service-provider use case and may require a subscription.

## Review notes

License: `KEGG-Custom` is a placeholder; no SPDX identifier exists for the Kanehisa custom license. Proposed canonical short name `KEGG-Custom` (or `KEGG-Academic-Free` to signal the academic-free-and-otherwise-paid split). Stephanie to decide which kebab-case short name to canonicalise in SCHEMA.md § License conventions.

Potential new join keys for review (KEGG mints many cross-source-useful identifiers not yet in the registry):

- `KEGG_PATHWAY_ID`
  Entity type: pathway
  Pattern: `^(map|[a-z]{3,4})[0-9]{5}$`
  Other datasets that would use it: Reactome (cross-references KEGG pathways), WikiPathways, OpenTargets, MetaCyc-comparable tools
- `KEGG_ORTHOLOGY_ID` (K numbers)
  Entity type: ortholog_group
  Pattern: `^K[0-9]{5}$`
  Other datasets that would use it: KofamKOALA, eggNOG, MicrobesOnline, most metagenomics pipelines (HUMAnN, PICRUSt2, MetaPhlAn-paired tools)
- `KEGG_COMPOUND_ID`
  Entity type: chemical_compound
  Pattern: `^C[0-9]{5}$`
  Other datasets that would use it: ChEBI, PubChem, MetaCyc, HMDB, MetaboLights
- `KEGG_REACTION_ID`
  Entity type: biochemical_reaction
  Pattern: `^R[0-9]{5}$`
  Other datasets that would use it: Rhea (EBI), MetaCyc, BiGG Models, Reactome
- `KEGG_DRUG_ID`
  Entity type: drug
  Pattern: `^D[0-9]{5}$`
  Other datasets that would use it: DrugBank, ChEMBL, openFDA, DailyMed
- `KEGG_DISEASE_ID`
  Entity type: disease
  Pattern: `^H[0-9]{5}$`
  Other datasets that would use it: DisGeNET, OpenTargets, MalaCards, Orphanet
- `EC_NUMBER`
  Entity type: enzyme_activity
  Pattern: `^[0-9]+(\.[0-9-]+){3}$`
  Other datasets that would use it: UniProt, BRENDA, ExplorEnz, Rhea, ChEMBL, Reactome (extremely widely cited)

Rate limit is documented at 3 API calls per second on https://www.kegg.jp/kegg/rest/ ; exceeding it blocks access. Entry now records `rate_limit: "3 requests per second (documented; exceeding it blocks access)"`.

`access_test` was executed: `curl -sf 'https://rest.kegg.jp/info/kegg'` returned 200 with the expected release/statistics block (Release 118.0+, June 2026, including pathway, orthology, genes, compound, reaction, disease, drug counts).
