---
id: myvariant
name: MyVariant.info
domain: bio-genomics
entry_kind: knowledge-graph
description: BioThings API aggregating genetic-variant annotations from dozens of sources (dbSNP, ClinVar, dbNSFP, CADD, and more) behind one fast REST query interface keyed on variants.
homepage_url: https://myvariant.info/
docs_url: https://docs.myvariant.info/
type:
  - rest-api
  - bulk-download
auth_required: none
cost: free
license: BioThings-Aggregate-Terms
rate_limit: "fair-use; batch POST up to 1000 ids per request"
bulk_available: true
frequency: "weekly annotation refresh"
lag: "days-to-weeks behind upstream source releases"
geography: [global]
join_keys:
  - RSID
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
primary_keys:
  - HGVS_VARIANT_ID
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/genomoncology/biomcp
mcp_command:
  - "uvx --from biomcp-python biomcp run"
agent_use_cases:
  - variant annotation lookup
  - rsID to clinical-significance resolution
  - pharmacogenomic and functional annotation
  - batch variant enrichment
  - cross-source variant harmonisation
access_test:
  command: "curl -sf 'https://myvariant.info/v1/query?q=rs58991260' -o /dev/null"
  expected_status: 200
last_verified: 2026-07-02
build_priority: low
notes: "access_test executed 2026-07-02 (query → 200). Covered by the biomcp MCP (MyVariant is one of its sources). License is aggregate: MyVariant is free for research but each annotation carries its upstream source's license; flagged in Review notes."
---

# MyVariant.info

## Why this source matters

MyVariant.info is a BioThings API (Su/Wu labs, Scripps Research) that consolidates dozens of variant-annotation resources, dbSNP, ClinVar, dbNSFP, CADD, COSMIC-derived fields, gnomAD frequencies, and more, into a single, fast, variant-keyed query service. Instead of querying each database separately, an agent can resolve one variant (by rsID or HGVS) and get clinical significance, predicted functional impact, allele frequencies, and gene context in one call. Annotations refresh weekly.

## Agent use cases

- variant annotation lookup
- rsID to clinical-significance resolution
- pharmacogenomic and functional annotation
- batch variant enrichment
- cross-source variant harmonisation

## Join strategy

The canonical join keys are `RSID` (dbSNP identifiers, the most common variant lookup key), `GENE_SYMBOL`, and `ENTREZ_GENE_ID` for gene-level joins. The native primary key is the MyVariant `_id`, an HGVS-style genomic string (`HGVS_VARIANT_ID`, e.g. `chr7:g.140453136A>T`), used for exact variant addressing across genome builds (hg19/hg38). Pair with `clinvar`, `dbsnp`, `gnomad`, and `ensembl` to move from a variant to its clinical, population, and gene context.

## Access notes

Free, no authentication. REST at `myvariant.info/v1/`: `/variant/<id>` for a single variant, `/query?q=` for search, and a batch `POST /v1/variant` accepting up to 1000 ids. Bulk annotation snapshots are downloadable. Specify the assembly (hg19 default; `assembly=hg38`) explicitly. Fair-use rate limits apply; use batch endpoints for scale.

## MCP / connector notes

Covered by `biomcp` (`uvx --from biomcp-python biomcp run`), which wraps MyVariant among several biomedical sources. No dedicated MyVariant MCP; biomcp is the practical path. A dedicated connector would add little over the clean REST API.

## Review notes

- License `BioThings-Aggregate-Terms` is a placeholder short name: MyVariant is free for research, but each field inherits its upstream source's license (ClinVar, COSMIC, etc. differ). Confirm the convention or split per-source.
- `HGVS_VARIANT_ID` is flagged as a primary key; if a second HGVS-keyed source enters, consider promoting an `HGVS` canonical key.
