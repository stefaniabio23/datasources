---
id: europe-pmc
name: Europe PMC
domain: academic
entry_kind: corpus
description: Open archive of life-sciences literature covering ~48M articles, preprints, and full-text open-access biomedical papers, mirrored from PubMed Central with European deposit and funder linkage.
homepage_url: https://europepmc.org/
docs_url: https://europepmc.org/RestfulWebService
type:
  - rest-api
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "no hard published cap; polite use expected. Bulk fetches must go through API or FTP, not crawler"
bulk_available: true
frequency: weekly
lag: "days for new PubMed records; weeks-to-months for full-text deposits"
geography: [global]
join_keys:
  - DOI
  - PMID
  - PMCID
  - ORCID
  - ROR
  - ISSN
  - MESH_TERM
  - CHEMBL_ID
  - UNIPROT_ACCESSION
  - ENSEMBL_ID
primary_keys:
  - EUROPE_PMC_ARTICLE_ID
  - EUROPE_PMC_SOURCE
join_key_fields:
  - join_key: DOI
    fields: [resultList.result.doi]
  - join_key: PMID
    fields: [resultList.result.pmid]
  - join_key: PMCID
    fields: [resultList.result.pmcid]
  - join_key: ORCID
    fields: [resultList.result.authorIdList.authorId.value, resultList.result.authorList.author.authorId.value]
  - join_key: ISSN
    fields: [resultList.result.journalInfo.journal.issn, resultList.result.journalInfo.journal.essn]
  - join_key: MESH_TERM
    fields: [resultList.result.meshHeadingList.meshHeading.descriptorName, resultList.result.meshHeadingList.meshHeading.meshQualifierList.meshQualifier.qualifierName]
  - join_key: CHEMBL_ID
    fields: [annotations.tags.uri]
  - join_key: UNIPROT_ACCESSION
    fields: [annotations.tags.uri]
  - join_key: ENSEMBL_ID
    fields: [annotations.tags.uri]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No official MCP. Stable, well-documented REST API. Suggested surface: search_articles,
  get_article, get_full_text, get_citations, get_references, get_annotations,
  resolve_id (DOI/PMID/PMCID mapping).
agent_use_cases:
  - biomedical literature search
  - full-text open-access retrieval
  - citation and reference graph traversal
  - text-mined entity lookup (genes, chemicals, diseases)
  - preprint discovery
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=malaria&format=json&pageSize=1&resultType=core'"
  expected_status: 200
  expected_fields: [hitCount, resultList, id, pmid, doi, title]
last_verified: 2026-06-08
build_priority: high
---

# Europe PMC

## Why this source matters

Europe PMC is the European mirror and extension of PubMed Central, run by EMBL-EBI with funding from the Europe PMC Funders' Group (Wellcome, MRC, CRUK, and others) in collaboration with the US NLM. It indexes ~48M items spanning peer-reviewed biomedical articles, preprints, patents (EPO), agricultural literature (Agricola), and NICE guidance, with ~3.2M full-text open-access articles, ~6.4M full-text records, and ~37.8M abstracts. Designated ELIXIR Core Data Resource and Global Core Biodata Resource. For agents working biomedical literature, it is the highest-coverage free source that combines abstracts, full text, citation links, grant linkage, and text-mined annotations under one API, with broader European preprint and funder coverage than PubMed alone. Secondary domain overlap with `clinical-biotech` (preprint and trial literature) and `public-health` (surveillance journals like Emerging Infectious Diseases).

## Agent use cases

- biomedical literature search
- full-text open-access retrieval
- citation and reference graph traversal
- text-mined entity lookup (genes, chemicals, diseases)
- preprint discovery

## Join strategy

Europe PMC exposes the core scholarly identifier set: `DOI`, `PMID`, `PMCID` for articles; `ORCID` for authors; `ROR` for affiliations; `ISSN` for journals. The Annotations API surfaces text-mined entity references that join onto `MESH_TERM`, `CHEMBL_ID`, `UNIPROT_ACCESSION`, `ENSEMBL_ID`, and `GENE_SYMBOL` (gene symbols appear in annotations but vary in normalisation, so prefer Ensembl IDs when present).

Europe PMC also exposes a maintained `PMID-PMCID-DOI` mapping file via FTP, which is the cleanest cross-walk between the three scholarly ID spaces for any agent stitching scholarly sources together.

Source-internal IDs (`EUROPE_PMC_SOURCE` like `MED`, `PMC`, `PPR`, `AGR`, `PAT`, plus internal article IDs) are intentionally outside the canonical registry; use them for direct Europe PMC lookups, not cross-source joins.

Grant identifiers via the GRIST API (grant numbers, funder IDs) potentially join onto `FUNDER_DOI` (Crossref Open Funder Registry), though Europe PMC uses its own funder vocabulary that does not always map cleanly. See review notes.

Recommended pairings: OpenAlex for citation graph at scale, Crossref for DOI metadata authority, ClinicalTrials.gov on trial registry IDs found in abstracts, ChEMBL on text-mined molecule IDs.

## Access notes

**Low-volume queries:** REST API at `https://www.ebi.ac.uk/europepmc/webservices/rest/search`, no auth. Add `&format=json` for JSON, `&resultType=core` for full metadata (default `lite` strips abstracts and annotations). Use cursor pagination via `cursorMark=*` then the returned `nextCursorMark` for deep pagination.

**Full text:** `/PMC{pmcid}/fullTextXML` returns JATS XML for open-access articles. Annotations API at `https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds` returns text-mined entity hits per article.

**Bulk:** FTP at `europepmc.org/ftp/` provides Open Access XML, author manuscripts, preprint subset, full-text metadata XML, PMID/PMCID/DOI mappings, accession numbers per article, and deposition dates. Use bulk for any analysis touching >1k full-text articles; the API is rate-friendly but slower for sustained pulls.

Known gotchas:

- Crawlers and scraping are explicitly forbidden; all automated retrieval must go through the REST/SOAP/OAI APIs or FTP.
- Licensing varies per article. Open Access subset is CC-BY (or similar Creative Commons) when funder-mandated, but other articles remain under publisher copyright with metadata-only access. The YAML `license: CC-BY-4.0` reflects the OA subset; check `licenseDetails` per article before redistributing full text.
- Five US Government journals (incl. *Emerging Infectious Diseases*) are public domain.
- Citation counts come from the EPMC citation network, which is narrower than OpenAlex/Crossref; treat as a lower bound.
- SOAP and OAI services exist but REST + FTP is the recommended path; SOAP is legacy.

## MCP / connector notes

No official or community MCP found as of 2026-06-08. High value: stable API, broad biomedical audience, overlap with OpenAlex / Crossref / ClinicalTrials.gov / ChEMBL connectors that agents will commonly chain. Suggested surface: `search_articles` (with field-scoped queries and cursor pagination), `get_article` (core metadata by PMID/PMCID/DOI), `get_full_text` (JATS XML, OA only), `get_citations` / `get_references`, `get_annotations` (text-mined entities), `resolve_id` (PMID ↔ PMCID ↔ DOI mapping). MCP should abstract over the source-type prefixes (`MED:`, `PMC:`, `PPR:`, `AGR:`, `PAT:`), trim verbose author/affiliation blobs, and route bulk requests to the FTP mirror when over a threshold.

## Review notes

Potential new join key for review: `EUROPE_PMC_GRANT_ID`
  Entity type: funding_grant
  Pattern: composite of funder code + grant number (e.g. `WT_104955`, `MRC_MR/T002182/1`); free-form, no fixed regex
  Other datasets that would use it: NIH RePORTER (different scheme), UKRI Gateway to Research, Dimensions grants. Europe PMC GRIST is the cleanest cross-funder grant index but identifier shape is funder-specific. May not be worth promoting to canonical unless a second source uses the same vocabulary.

Potential new join key for review: `PREPRINT_SERVER_ID`
  Entity type: preprint
  Pattern: server-specific (bioRxiv `10.1101/...` DOI, medRxiv `10.1101/...` DOI, Research Square `rs-...`, SSRN numeric)
  Other datasets that would use it: bioRxiv, medRxiv, Research Square, Semantic Scholar. In practice these are all DOIs and `DOI` already covers them; flag only if a non-DOI preprint server becomes prominent.
