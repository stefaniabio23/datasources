---
id: encode
name: ENCODE
domain: bio-genomics
entry_kind: registry
description: Encyclopedia of DNA Elements — international consortium portal of functional genomics experiments (ChIP-seq, RNA-seq, ATAC-seq, DNase, methylation) across human and mouse, with a REST API over experiments, files, biosamples, and candidate regulatory elements.
homepage_url: https://www.encodeproject.org/
docs_url: https://www.encodeproject.org/help/rest-api/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "10 GET requests/sec per user/group/lab; IP-level denial on abuse"
bulk_available: true
frequency: "rolling; periodic named data releases"
lag: "months from data submission to uniform-pipeline processing and release"
geography: [global]
join_keys:
  - ENSEMBL_ID
  - UBERON_ID
  - DOI
primary_keys:
  - ENCODE_EXPERIMENT_ACCESSION
  - ENCODE_FILE_ACCESSION
  - ENCODE_BIOSAMPLE_ACCESSION
  - ENCODE_ANTIBODY_ACCESSION
  - ENCODE_DONOR_ACCESSION
  - ENCODE_LIBRARY_ACCESSION
join_key_fields:
  - join_key: ENSEMBL_ID
    fields: [genes.dbxrefs, annotation.dbxrefs]
  - join_key: UBERON_ID
    fields: [biosample_ontology.term_id]
  - join_key: DOI
    fields: [doi]
mcp_status: mcp-needed-high-value
agent_use_cases:
  - functional-genomics experiment search
  - regulatory-element lookup by tissue or cell type
  - epigenomic track retrieval by assay and assembly
  - antibody and biosample provenance tracing
  - candidate cis-regulatory element (cCRE) queries
access_test:
  command: "curl -sf 'https://www.encodeproject.org/experiments/ENCSR000AKS/?frame=object&format=json'"
  expected_status: 200
  expected_fields: [accession, assay_title, biosample_ontology, assembly, files]
last_verified: 2026-07-02
build_priority: high
---

# ENCODE

## Why this source matters

ENCODE (Encyclopedia of DNA Elements) is the NHGRI-funded international consortium cataloguing functional elements in the human and mouse genomes: transcription-factor and histone ChIP-seq, RNA-seq, ATAC-seq, DNase-seq, DNA methylation, 3D chromatin, and derived candidate cis-regulatory elements (cCREs). The portal at `encodeproject.org` is a JSON-native object store: every experiment, file, biosample, antibody, donor, and library is an addressable object with a stable accession, exposed through a uniform REST search API and downloadable in bulk. It is the reference substrate for regulatory-genomics work and a natural join target for expression, variant, and anatomy datasets. This is a `bio-genomics` entry; its epigenomic tracks also serve `public-health` and disease-annotation workflows.

## Agent use cases

- functional-genomics experiment search
- regulatory-element lookup by tissue or cell type
- epigenomic track retrieval by assay and assembly
- antibody and biosample provenance tracing
- candidate cis-regulatory element (cCRE) queries

## Join strategy

ENCODE exposes three canonical join keys usable for cross-source stitching. `UBERON_ID` appears as `biosample_ontology.term_id` for tissue and anatomy biosamples (cell lines and cell types carry EFO or CL terms in the same field). `ENSEMBL_ID` (GENCODE/Ensembl gene IDs) reaches into gene and annotation `dbxrefs` and is the row key inside RNA-seq gene-quantification files. Each released dataset also mints a DataCite `DOI` (e.g. `10.17989/ENCSR000AKS`) in the `doi` field, and `references` link out to consortium publications.

Source-internal accessions are the primary retrieval handles and belong outside the canonical registry: `ENCSR` (experiment), `ENCFF` (file), `ENCBS` (biosample), `ENCAB` (antibody), `ENCDO` (donor), `ENCLB` (library). Objects also carry `dbxrefs` to external archives (e.g. `GEO:GSM733692`, `UCSC-ENCODE-hg19:...`), which are the pairing path to GEO/SRA and the UCSC Genome Browser. Pair ENCODE with GTEx and Expression Atlas on `UBERON_ID` for tissue-matched expression, and with Ensembl/GENCODE on `ENSEMBL_ID` for gene coordinates.

Genome assembly (`GRCh38`, `hg19`, `mm10`) is a first-class ENCODE dimension (the `assembly` field is a list per experiment) and is essential for correct track joining, but there is no canonical join key for it yet. See Review notes.

## Access notes

Public released objects need no auth. Fetch a single object by accession, `https://www.encodeproject.org/experiments/ENCSR000AKS/?frame=object&format=json`, or search, `https://www.encodeproject.org/search/?type=Experiment&assay_title=ATAC-seq&assembly=GRCh38&format=json`. The `frame` parameter controls embedding depth (`object` returns linked objects as identifiers; `embedded` expands them). Rate limit is 10 GET/sec per user; exceed it and the IP is blocked. Bulk metadata and file manifests are retrievable via the `/batch_download/` and `/report/` endpoints; large track pulls should go through file manifests rather than paginating search. Data-use policy is open (CC BY 4.0); cite the consortium and the specific datasets.

The ENCODE portal also hosts and harmonises Roadmap Epigenomics Consortium reference epigenomes, a complementary NIH effort focused on primary-tissue epigenomic maps. Roadmap data is queryable through the same API surface, so an agent joining on tissue or assay does not need a separate Roadmap connector.

## MCP / connector notes

No dedicated ENCODE MCP found on the official registry, npm, or PyPI as of 2026-07-02. High value: many bio-genomics consumers (Ensembl, GTEx, Expression Atlas, UCSC entries here) would share a regulatory-genomics connector. Suggested surface: `search_experiments` (by assay, biosample, target, assembly), `get_object` (by accession, with frame control), `list_files` (by experiment + file_format + output_type), `get_ccres` (candidate regulatory elements by region/assembly), `resolve_biosample` (biosample_ontology term to UBERON/CL/EFO). The connector must abstract over the frame/embedding model, trim the very verbose embedded responses, and normalise the assembly dimension so callers do not silently mix GRCh38 and hg19 tracks.

## Review notes

Potential new join key for review: `GENOME_ASSEMBLY`
  Entity type: reference_assembly
  Pattern: build accession or common name (e.g. GRCh38, hg19, mm10, GCF_000001405.40)
  Other datasets that would use it: ENCODE, Ensembl, UCSC Genome Browser, GTEx, gnomAD, dbSNP, GWAS Catalog — any track- or coordinate-bearing genomics source. Assembly-mismatched joins are a common silent error, so a canonical key here would be broadly load-bearing.

Potential new join key for review: `GEO_ACCESSION`
  Entity type: geo_series_or_sample
  Pattern: "^GS[EM][0-9]+$" (GSE series, GSM sample)
  Other datasets that would use it: ENCODE (via dbxrefs), NCBI GEO, NCBI SRA, ArrayExpress. Would let agents bridge ENCODE objects to the raw-data archives.

License note: ENCODE data is released under CC BY 4.0 with an open data-use policy; no embargo on released objects. Confirmed CC BY 4.0 from the portal footer.
