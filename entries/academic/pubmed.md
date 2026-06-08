---
id: pubmed
name: PubMed (NCBI E-utilities)
domain: academic
description: NCBI's biomedical literature database (~37M citations from MEDLINE, life-science journals, and online books), exposed via the Entrez E-utilities REST API and annual XML bulk releases.
homepage_url: https://pubmed.ncbi.nlm.nih.gov/
docs_url: https://www.ncbi.nlm.nih.gov/books/NBK25501/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free
license: US-Government-Public-Domain
rate_limit: "3 req/sec anon; 10 req/sec with free api_key (higher on request)"
bulk_available: true
frequency: daily
lag: "1-2 days for new citations to appear via E-utilities; annual baseline released at year-end with daily update XML files"
geography: [global]
join_keys:
  - PMID
  - PMCID
  - DOI
  - MESH_TERM
  - ISSN
primary_keys:
  - PMID
  - ENTREZ_UID
join_key_fields:
  - join_key: PMID
    fields:
      - MedlineCitation.PMID
      - "PubmedData.ArticleIdList.ArticleId[IdType=pubmed]"
      - "result.<uid>.uid"
      - "result.<uid>.articleids[idtype=pubmed].value"
  - join_key: PMCID
    fields:
      - "PubmedData.ArticleIdList.ArticleId[IdType=pmc]"
      - "result.<uid>.articleids[idtype=pmc].value"
  - join_key: DOI
    fields:
      - "MedlineCitation.Article.ELocationID[EIdType=doi]"
      - "PubmedData.ArticleIdList.ArticleId[IdType=doi]"
      - "result.<uid>.articleids[idtype=doi].value"
      - "result.<uid>.elocationid"
  - join_key: MESH_TERM
    fields:
      - MedlineCitation.MeshHeadingList.MeshHeading.DescriptorName
  - join_key: ISSN
    fields:
      - MedlineCitation.Article.Journal.ISSN
      - "result.<uid>.issn"
      - "result.<uid>.essn"
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/gradusnikov/pubmed-search-mcp-server
  - github.com/JackKuo666/PubMed-MCP-Server
  - github.com/rikab/PubMed-MCP
mcp_notes: >
  Multiple community MCPs wrap esearch/efetch for PubMed only. None abstract over the full
  E-utilities surface (ELink for cross-database citation walks, EPost for batched UID workflows,
  ECitMatch for free-text citation resolution). A higher-value connector would expose
  search_pubmed, fetch_records, link_to_pmc, link_to_clinical_trials, resolve_citation, with
  built-in api_key + tool/email handling and XML-to-clean-JSON normalisation.
agent_use_cases:
  - biomedical literature search
  - citation-to-fulltext resolution via PMCID
  - MeSH-tagged retrieval
  - cross-database walks (PubMed to Gene, Protein, ClinicalTrials, PMC)
  - bibliographic deduplication via PMID
access_test:
  command: "curl -sf 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=crispr&retmode=json&retmax=2'"
  expected_status: 200
  expected_fields: [header, esearchresult]
last_verified: 2026-06-08
build_priority: high
---

# PubMed (NCBI E-utilities)

## Why this source matters

PubMed is the canonical index of biomedical literature: ~37M citations from MEDLINE, life-science journals, and online books, curated by the US National Library of Medicine since 1996. The Entrez Programming Utilities (E-utilities) expose the underlying Entrez query system across 38 databases. PubMed itself is the most-queried but the same API reaches Gene, Protein, Nucleotide, PMC, ClinicalTrials.gov mirrors, MeSH, and others. For any agent doing biomedical literature work, this is the source of record. Secondary relevance: `clinical-biotech` (ELink can bridge PMIDs to ClinicalTrials.gov and dbGaP) and `bio-genomics` (Gene, Protein, Nucleotide live behind the same E-utilities surface).

## Agent use cases

- biomedical literature search
- citation-to-fulltext resolution via PMCID
- MeSH-tagged retrieval
- cross-database walks (PubMed to Gene, Protein, ClinicalTrials, PMC)
- bibliographic deduplication via PMID

## Join strategy

PubMed is the originator of `PMID` and a primary source of `PMCID` (via ELink from pubmed to pmc). Records carry `DOI` in the ArticleIdList, journal `ISSN`, and `MESH_TERM` annotations in MedlineCitation/MeshHeadingList. These five are the canonical keys to expose.

Author identifiers in PubMed records are heterogeneous: ORCIDs appear when authors supplied them at submission, but coverage is partial and unreliable for joining. Use OpenAlex or Crossref for author disambiguation, then come back to PubMed via PMID.

Source-internal Entrez UIDs (PubMed UID = PMID; Gene UID, Protein GI, PMC UID for other databases) are how E-utilities references records internally. Use them for direct E-utilities calls; PMID is also the canonical cross-source join key.

Pair with: OpenAlex (richer metadata, citation graph, OA links), Europe PMC (full text for OA biomedical articles, mirrors PubMed plus preprints), Crossref (DOI authority and funder metadata), ClinicalTrials.gov (NCT-to-PMID via ELink).

## Access notes

**First call:** hit ESearch on `db=pubmed` to get PMIDs, then EFetch to retrieve full records. Default EFetch returns MEDLINE XML; pass `retmode=json` to ESearch/ESummary but note EFetch does not support JSON for pubmed (XML or MEDLINE text only).

**Register an api_key.** Anonymous is capped at 3 req/sec across your IP; a free api_key (NCBI account, Settings page) lifts that to 10 req/sec and gets you priority during incidents. Always pass `tool=<yourname>` and `email=<dev@you>` parameters so NCBI can contact you before blocking instead of after.

**Large pulls:** use the annual baseline (`ftp.ncbi.nlm.nih.gov/pubmed/baseline/`, ~1300 XML files at year-end) plus daily updates (`ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/`). Faster than paginating ESearch + EFetch for anything over ~100K records. Binary mode required. Accept the README.txt Terms before use.

**Known gotchas:**

- E-utilities responses change shape across databases; do not assume schema parity between pubmed, gene, protein.
- Abstracts can be absent (no-abstract citations, embargoed records); check `Abstract/AbstractText` presence before relying.
- MeSH indexing lags publication by weeks-to-months; recent citations are in-process and unindexed.
- Daily update files can ship multiple times per day; load in numerical order or you will reintroduce deleted citations.

## MCP / connector notes

Several community MCPs exist (`pubmed-search-mcp-server`, `JackKuo666/PubMed-MCP-Server`, `rikab/PubMed-MCP`), all narrow wrappers around esearch + efetch for PubMed only. Gaps: none cover the full E-utilities surface, none handle api_key + tool/email registration, none expose ELink (the highest-value endpoint for agents doing cross-database walks), none reconstruct clean JSON from MEDLINE XML.

Suggested production connector: `search_pubmed`, `fetch_records`, `link_to_pmc`, `link_to_clinical_trials`, `resolve_citation` (ECitMatch wrapper), `summarize_records` (ESummary). Must handle api_key passthrough, XML-to-JSON normalisation, batch size limits (EFetch caps at ~10K per request, EPost preferred for larger UID sets), and the 3-vs-10 req/sec routing.

## Review notes

License: PubMed metadata is US government-produced and in the public domain, but NCBI explicitly states it does not hold copyright to the underlying article abstracts and titles, those belong to publishers. `US-Government-Public-Domain` captures the NCBI-produced wrapper accurately; downstream users redistributing abstracts at scale should consult the README.txt Terms and individual publisher rights. Flagging for human review whether this nuance warrants a separate license short name (e.g. `NLM-Data-Distribution`) or stays as-is with the caveat in this body.
