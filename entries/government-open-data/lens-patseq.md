---
id: lens-patseq
name: Lens PatSeq
domain: government-open-data
entry_kind: corpus
description: Bulk collection of DNA, RNA, and protein sequences disclosed in patent documents worldwide, with linked patent metadata, searchable by sequence similarity.
homepage_url: https://www.lens.org/lens/bio/patseqfinder
docs_url: https://support.lens.org/knowledge-base/patseq-bulk-download/
type:
  - bulk-download
  - rest-api
  - web-ui
auth_required: account-required
cost: free-non-commercial
license: Lens-PatSeq-Terms
rate_limit: "monthly query quotas on PatSeq Finder; up to 5 API access tokens per user"
bulk_available: true
geography: [global]
join_keys:
  - PATENT_PUBLICATION_NUMBER
  - CPC_CODE
primary_keys:
  - LENS_PATENT_ID
  - PATENT_PUBLICATION_NUMBER
  - PATSEQ_SEQUENCE_ID
mcp_status: mcp-needed-low-value
agent_use_cases:
  - patent sequence similarity search
  - freedom-to-operate sequence checks
  - link genes and proteins to patent filings
  - bulk patent sequence corpus retrieval
  - prior-art sequence search
last_verified: 2026-07-07
---

# Lens PatSeq

## Why this source matters

PatSeq is the biological-sequence layer of The Lens (Lens.org PTY LTD, a not-for-profit Australian operator), indexing more than 500 million DNA, RNA, and protein sequences disclosed in patent documents across many jurisdictions. It bridges two domains agents rarely join: intellectual property (patent grants and applications) and molecular biology (the actual sequences claimed). PatSeq Finder runs BLAST+ similarity search over the corpus; PatSeq Explorer and PatSeq Data provide faceted browsing and bulk export. For any agent asking "which patents claim this gene / protein / construct?" or doing freedom-to-operate and prior-art work on a sequence, this is the canonical aggregation. Secondary relevance to `bio-genomics` (the payload is sequence data) and `academic` / patent-analytics workflows.

## Agent use cases

- patent sequence similarity search
- freedom-to-operate sequence checks
- link genes and proteins to patent filings
- bulk patent sequence corpus retrieval
- prior-art sequence search

## Join strategy

The load-bearing identifier is the patent publication number (e.g. `US_7510834_B2`), which is NOT yet a canonical key in `schema/join-keys.yaml`; it is flagged below as a candidate. Until that key exists, PatSeq cannot expose a registry join key, so `join_keys` is empty.

Source-internal identifiers (kept in `primary_keys`, not for cross-source joins): the Lens patent record ID (`LENS_PATENT_ID`), the patent publication number (`PATENT_PUBLICATION_NUMBER`), and per-sequence PatSeq sequence IDs (`PATSEQ_SEQUENCE_ID`). The Rich export (an EMBL-based annotated format) carries patent titles, filing dates, priority dates, inventors, applicants, and organism information; sequence accession numbers appear per record. Whether those accessions include `UNIPROT_ACCESSION` cross-references is unconfirmed, so it is flagged for review rather than asserted.

Natural pairing once a patent-number key lands: patent-metadata sources (Lens patent records, USPTO/EPO patent APIs) on `PATENT_PUBLICATION_NUMBER`, and genomic sources (UniProt, Ensembl) on protein/gene identifiers if those turn out to be present in the Rich records.

## Access notes

Non-commercial (academic) use is free; commercial use is paid and tiered by organisation size. All access requires a registered Lens account and an approved request through the API & Data → PatSeq tab. Two access paths:

- **UI bulk export:** PatSeq Data app provides "Sequence download" buttons per jurisdiction or for the entire database. No programming required. Files ship as FASTA (organised by sequence type nucleotide/peptide, document type grant/application, and location claims-only vs all) and as the Rich annotated format. Sample files hold ~1,000 sequences.
- **Bulk Download API:** for scheduled/automated pulls. Requires a personal access token (up to 5 per user) generated in the Sequence Bulk Download tab; the token is passed as an `access_token` request parameter or via the HTTP `Authorization` header.

No `access_test` is recorded here: the bulk endpoint is token-gated and its exact URL is not published on the public docs excerpt reviewed. To verify freshness, sign in and check the current dataset build date on the PatSeq Data app / bulk download request form. Docs were last updated 2026-03-18.

## MCP / connector notes

No known MCP. Audience is narrow (IP + biotech sequence work) and access is auth-gated, so low build priority. A useful connector surface would be: `blast_search(sequence, db)` over PatSeq Finder, `get_patent_sequences(publication_number)`, `bulk_request(jurisdiction, seq_type, doc_type, format)`, and `download_status(token)`. The connector must abstract over the token lifecycle, the FASTA-vs-Rich format split, and the request-and-approve gate before any bulk pull is available.

## Review notes

- **Potential new join key for review: `PATENT_PUBLICATION_NUMBER`**
  - Entity type: `patent_document`
  - Pattern: jurisdiction-prefixed alphanumeric publication number; PatSeq renders as `US_7510834_B2` (underscore-delimited: country / number / kind code). Canonical form more commonly `US7510834B2` or `US-7510834-B2`.
  - Other datasets that would use it: Lens patent records, USPTO PatentsView, EPO OPS, Google Patents, WIPO PATENTSCOPE. High cross-source utility; recommend PR to `schema/join-keys.yaml`.
- **UNIPROT_ACCESSION** was listed as a candidate in the task hints. Not confirmed present in PatSeq exports; the Rich format's accession numbers may be GenBank/patent-sequence accessions rather than UniProt. Left out of `join_keys` pending confirmation of a UniProt cross-reference field.
- **License short name `Lens-PatSeq-Terms` is new** and not yet in SCHEMA.md's canonical short-name list. It stands in for the Lens.org PatSeq access terms (free non-commercial, paid commercial). Needs a canonical short name decision before merge.
- `access_test` omitted because the bulk API is token-gated and no public endpoint URL was confirmed.
