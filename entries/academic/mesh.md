---
id: mesh
name: MeSH (Medical Subject Headings)
domain: academic
entry_kind: knowledge-graph
description: NLM's controlled, hierarchically-organized biomedical vocabulary used to index MEDLINE/PubMed and other NLM databases, published as annual XML/RDF and queryable via a SPARQL endpoint and Linked-Data URI service.
homepage_url: https://www.nlm.nih.gov/mesh/meshhome.html
docs_url: https://hhs.github.io/meshrdf/
type:
  - rest-api
  - database
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
bulk_available: true
frequency: annual
lag: "new annual edition published ~November for the following processing year; interim descriptors are not added mid-year"
geography: [global]
join_keys:
  - MESH_TERM
primary_keys:
  - MESH_DESCRIPTOR_UI
  - MESH_QUALIFIER_UI
  - MESH_SCR_UI
  - MESH_CONCEPT_UI
  - MESH_TERM_UI
  - MESH_TREE_NUMBER
join_key_fields:
  - join_key: MESH_TERM
    fields:
      - label
      - "rdfs:label"
      - preferredTerm
mcp_status: mcp-needed-high-value
mcp_notes: >
  No dedicated MeSH connector; MeSH lookups are today embedded inside PubMed MCPs. A vocabulary
  service is high-value because many biomedical entries (PubMed, Europe PMC, ClinicalTrials.gov,
  openFDA) reference MeSH. Suggested surface: resolve_term (string to descriptor UI), expand_synonyms,
  get_tree (ancestors/descendants by tree number), list_qualifiers, map_scr_to_descriptor. Must
  abstract over SPARQL so agents pass concepts, not queries, and pin the annual edition.
agent_use_cases:
  - biomedical vocabulary normalization
  - term-to-descriptor resolution
  - synonym and entry-term expansion for literature queries
  - MeSH tree navigation (hierarchy expansion)
  - qualifier and supplementary-concept lookup
access_test:
  command: "curl -sf 'https://id.nlm.nih.gov/mesh/D000900.json'"
  expected_status: 200
  expected_fields:
    - "@id"
    - "@type"
    - label
    - treeNumber
last_verified: 2026-07-02
build_priority: medium
structure: registry-snapshot
pit_reconstructable: true
revisions_possible: true
---

# MeSH (Medical Subject Headings)

## Why this source matters

MeSH is the National Library of Medicine's controlled, hierarchically-organized thesaurus of biomedical concepts. It is the indexing vocabulary behind MEDLINE/PubMed and much of the rest of NLM's catalog, so it is the shared spine that lets biomedical sources talk about the same disease, drug, or method under one canonical heading. The vocabulary has ~30k topical descriptors arranged in a tree, plus qualifiers (subheadings), supplementary concept records for chemicals and rare diseases, and per-descriptor concepts and entry terms (synonyms). NLM publishes it annually as XML and RDF and exposes it as a Linked-Data triple store with a public SPARQL endpoint and content-negotiated URI lookups. For an agent, MeSH is the normalization layer: map free text to a stable descriptor, expand synonyms, or walk the hierarchy before querying a literature or regulatory source. Secondary relevance: `public-health` and `clinical-biotech`, since MeSH descriptors are the join vocabulary for disease/intervention tagging across those sources.

## Agent use cases

- biomedical vocabulary normalization
- term-to-descriptor resolution
- synonym and entry-term expansion for literature queries
- MeSH tree navigation (hierarchy expansion)
- qualifier and supplementary-concept lookup

## Join strategy

MeSH exposes one canonical join key: `MESH_TERM` (the descriptor label / preferred term, e.g. "Aspirin"). This is the string that appears in PubMed's `MeshHeadingList.MeshHeading.DescriptorName`, so `MESH_TERM` is the bridge from the vocabulary to any MeSH-tagged corpus. MeSH itself does not carry `PMID`: PubMed is the side that mints PMIDs and tags each article with MeSH descriptors, so the join direction is MeSH descriptor to PubMed records via `MESH_TERM`, then PMID lives on the PubMed side. For that reason `PMID` is deliberately not listed in this entry's `join_keys` (the source does not expose it).

Source-internal identifiers are MeSH-native and go in `primary_keys`: descriptor UI (D-numbers, e.g. `D000900`), qualifier UI (`Q`-numbers), supplementary concept record UI (`C`-numbers), concept UI (`M`-numbers), term UI (`T`-numbers), and tree numbers (e.g. `D27.505.954...`). The descriptor UI is a more stable join target than the label string (labels get revised across annual editions); it is flagged for review below as a candidate canonical key.

Pair with: PubMed / Europe PMC (MeSH-tagged retrieval), ClinicalTrials.gov and openFDA (condition/intervention MeSH tags), and UMLS Metathesaurus (to reach `UMLS_CUI` and cross-vocabulary mappings, which MeSH RDF does not itself contain).

## Access notes

**First call, single concept:** content-negotiated URI lookup, no auth: `GET https://id.nlm.nih.gov/mesh/D000900.json` returns the descriptor as JSON-LD (`@id`, `label`, `treeNumber`, `concept`, `allowableQualifier`, `broaderDescriptor`). Swap the extension for `.rdf`, `.ttl`, or use an `Accept` header.

**Anything relational:** the SPARQL endpoint at `https://id.nlm.nih.gov/mesh/sparql` (append `&format=JSON`) supports SELECT (HTML/XML/CSV/TSV/JSON) and CONSTRUCT (JSON-LD/RDF-XML/Turtle/N3). Note the endpoint is versioned: default queries hit the current graph, and year-namespaced URIs (e.g. `.../mesh/2015/D018021`) let you query a specific annual edition, which is what makes point-in-time reconstruction possible at annual granularity.

**Bulk:** full XML and RDF releases at `https://www.nlm.nih.gov/databases/download/mesh.html` and the RDF FTP tree at `https://nlmpubs.nlm.nih.gov/projects/mesh/rdf/`. Take the bulk file for anything that walks the whole tree; the SPARQL endpoint is best for targeted lookups.

**MeSH Browser** (`https://meshb.nlm.nih.gov/`) is the human web UI, plus MeSH on Demand for auto-suggesting descriptors from free text.

License nuance: MeSH is a US-government work, effectively public domain in copyright, but NLM's data terms ask redistributors to acknowledge "Courtesy of the U.S. National Library of Medicine", keep versions current (or disclose staleness), and not imply NLM endorsement. No API key or rate limit is documented for `id.nlm.nih.gov`; stay polite.

## MCP / connector notes

No dedicated MeSH MCP exists. MeSH functionality today is a side feature of PubMed MCP servers (major-topic filtering, displaying assigned headings), not a standalone vocabulary service. This is high-value to build because MeSH is referenced by three-plus entries in this directory (PubMed, Europe PMC, ClinicalTrials.gov, openFDA), all of which want the same term-normalization primitive. Suggested surface: `resolve_term` (free text to descriptor UI + label), `expand_synonyms` (entry terms), `get_tree` (ancestors/descendants via tree numbers), `list_qualifiers`, `map_scr_to_descriptor`. The connector should abstract over SPARQL so agents pass concepts rather than queries, pin a specific annual edition for reproducibility, and normalize JSON-LD to flat JSON.

## Review notes

Potential new join key for review: `MESH_DESCRIPTOR_UI`
  Entity type: biomedical_concept
  Pattern: `^[CDMQ][0-9]{6,9}$` (D = descriptor, C = supplementary concept record, Q = qualifier, M = concept)
  Rationale: the descriptor UI (e.g. `D000900`) is a stabler cross-source join target than the free-text `MESH_TERM` label, which is revised across annual editions. PubMed, UMLS, ClinicalTrials.gov, and openFDA all carry descriptor UIs alongside or instead of the string.
  Other datasets that would use it: PubMed, Europe PMC, ClinicalTrials.gov, openFDA, UMLS.

Potential new join key for review: `UMLS_CUI`
  Entity type: biomedical_concept
  Pattern: `^C[0-9]{7}$`
  Rationale: requested in the task hints as a candidate. Note MeSH RDF does NOT itself expose UMLS CUIs; the MeSH-to-CUI mapping lives in the UMLS Metathesaurus (auth-gated, UMLS licence). So `UMLS_CUI` would attach to a future UMLS entry, not to this one. Flagging the key for the registry, but not adding it to this entry's `join_keys` because MeSH does not carry it.

License: used `US-Government-Public-Domain` for consistency with the `pubmed` entry, but NLM's download terms add an attribution + no-endorsement obligation that pure public domain does not. Same open question flagged on `pubmed`: whether a dedicated `NLM-Data-Distribution` short name is warranted, or the caveat stays in this body.

Domain: placed in `academic` alongside `pubmed` (bibliographic indexing infrastructure). Defensible alternatives are `public-health` or `clinical-biotech`; noted as secondary in the body.
