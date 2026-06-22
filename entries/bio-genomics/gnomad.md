---
id: gnomad
name: gnomAD (Genome Aggregation Database)
domain: bio-genomics
entry_kind: reference-table
description: Population-scale reference of human allele frequencies aggregated from hundreds of thousands of exomes and genomes, used to gauge how common a variant is in the general population.
homepage_url: https://gnomad.broadinstitute.org
docs_url: https://gnomad.broadinstitute.org/help
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: MIT
rate_limit: "GraphQL API unpublished, throttled, explicitly not for bulk/programmatic harvesting; use cloud buckets for scale"
bulk_available: true
frequency: "approximately annual major releases; v4.1 released 2024-04-19"
lag: "months-to-years; aggregated joint callsets, not a live feed"
geography: [global]
join_keys:
  - RSID
  - ENSEMBL_ID
  - GENE_SYMBOL
primary_keys:
  - GNOMAD_VARIANT_ID
  - GNOMAD_DATASET_VERSION
join_key_fields:
  - join_key: RSID
    fields: [rsid, rsids]
  - join_key: ENSEMBL_ID
    fields: [transcript_consequences.gene_id, transcript_consequences.transcript_id, gene_id, transcript_id]
  - join_key: GENE_SYMBOL
    fields: [transcript_consequences.gene_symbol, symbol]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  GraphQL endpoint is clean for single-variant and single-gene lookups but is throttled and
  explicitly off-limits for bulk pulls; an MCP must front-load the variant-ID normalisation
  (chrom-pos-ref-alt, chr-stripped, MT->M) and route large queries to the Hail Tables on the
  cloud buckets. Suggested surface: get_variant, get_gene_constraint, lookup_by_rsid,
  region_variants, resolve_variant_id.
agent_use_cases:
  - variant allele-frequency lookup
  - filter rare vs common variants
  - gene constraint and loss-of-function intolerance lookup
  - population-stratified frequency comparison
  - clinical-variant pathogenicity triage
access_test:
  command: "curl -sf -X POST 'https://gnomad.broadinstitute.org/api' -H 'Content-Type: application/json' -d '{\"query\":\"{ variant(variantId: \\\"1-55051215-G-GA\\\", dataset: gnomad_r4) { variant_id rsids genome { ac an af } exome { ac an af } } }\"}'"
  expected_status: 200
  expected_fields: [data.variant.variant_id, data.variant.genome.af, data.variant.exome.af]
last_verified: 2026-06-22
build_priority: high
---

# gnomAD (Genome Aggregation Database)

## Why this source matters

gnomAD is the reference standard for how common a human genetic variant is in the general population. Run by the Broad Institute, it aggregates exome and genome sequencing from large disease and population studies into harmonised joint callsets, then publishes per-variant allele counts and frequencies with the individual-level data stripped out. The current release, v4.1 (2024-04-19, GRCh38), draws on roughly 730,947 exomes and 76,215 genomes to report about 91M variants. For any agent doing clinical-variant interpretation, rare-disease diagnosis, or target triage, gnomAD is the first stop: a variant absent or vanishingly rare in gnomAD is a candidate to take seriously, while one at high population frequency is almost never the cause of a severe Mendelian disease. Secondary domains: clinical-biotech (variant pathogenicity triage feeds drug-target validation) and academic (the underlying callsets are heavily cited).

## Agent use cases

- variant allele-frequency lookup
- filter rare vs common variants
- gene constraint and loss-of-function intolerance lookup
- population-stratified frequency comparison
- clinical-variant pathogenicity triage

## Join strategy

gnomAD's native primary key is the gnomAD variant ID, `chrom-pos-ref-alt` (the chromosome `chr` prefix is stripped and `MT` is written `M`, e.g. `1-55051215-G-GA`). This is not a registered canonical key, so it lives in `primary_keys` and is flagged below. Because allele frequencies are release- and build-specific, the dataset-version string (`gnomad_r4`, `gnomad_r2_1`, etc.) is also a primary key, pairing the variant ID with the genome build it was called against.

For cross-source joining, gnomAD exposes registered keys via its VEP annotation: `RSID` (dbSNP), `ENSEMBL_ID` (genes and transcripts), and `GENE_SYMBOL` (HGNC). These make gnomAD the population-frequency layer to bolt onto Ensembl, ClinVar, OpenTargets, and any variant table keyed on rsID. Per-variant fields carry the standard allele counts and frequencies (`AC`/`AN`/`AF`), group-maximum frequency (`grpmax`), filtering allele frequency (`FAF`), and VEP consequence/gene/transcript annotations.

The cross-source trap is the build: the registered keys join cleanly, but the variant ID and its frequencies do NOT transfer between builds, so a v2 (GRCh37) variant and a v4 (GRCh38) variant for the same locus carry different coordinates. Join on rsID or lift over coordinates; never assume a `chrom-pos-ref-alt` string from one release matches another.

## Access notes

**Low-volume agent queries:** GraphQL API at `https://gnomad.broadinstitute.org/api`, no key. POST a query specifying `variantId`/`gene`/`region` plus a `dataset` argument. It is throttled and explicitly not intended for bulk or programmatic harvesting; treat it as an interactive lookup surface only.

**Large analyses:** bulk distribution as VCF and Hail Tables on public cloud buckets. AWS Open Data at `s3://gnomad-public-us-east-1` (us-east-1) is anonymous, no AWS account, use `aws s3 ... --no-sign-request`. Mirrored on Google Cloud Storage (`gs://gcp-public-data--gnomad`). Hail Tables are the native format for any genome-scale filter or aggregation; VCFs are the lowest-friction option for spot checks and tool interop.

**Build-mismatch trap:** v4.1 is GRCh38; legacy v2.1.1 is GRCh37. Picking the wrong release silently returns coordinates and frequencies for the wrong build. Always pin the build to your variant set (or lift over) before pulling frequencies, and pass the matching `dataset` argument to the API.

Freshness check: confirm the latest release on the homepage downloads page; major releases land roughly annually, so a stale `last_verified` is likely still current.

## MCP / connector notes

No official MCP. High-value: clinical-variant, rare-disease, and target-validation agents are a broad overlapping audience, and the GraphQL surface is clean for single-entity lookups but unusable for bulk. A connector should normalise variant IDs (strip `chr`, map `MT`->`M`, accept rsID or HGVS and resolve to `chrom-pos-ref-alt`), default to the build matching the requested dataset, expose `get_variant`, `get_gene_constraint`, `lookup_by_rsid`, `region_variants`, and `resolve_variant_id`, and hard-route anything region- or genome-scale to the Hail Tables on the cloud buckets rather than the throttled API.

## Review notes

Potential new join key for review: GNOMAD_VARIANT_ID
  Entity type: genetic_variant
  Pattern: `^([0-9]{1,2}|X|Y|M)-[0-9]+-[ACGT]+-[ACGT]+$` (chr-stripped chrom-pos-ref-alt, MT written M)
  Other datasets that would use it: gnomAD only mints it, but a chr-stripped chrom-pos-ref-alt convention is shared in spirit by ClinVar, dbSNP allele records, ENSEMBL VEP, and OpenTargets Genetics. A build-tagged variant-coordinate key would let those join on locus rather than only on rsID.

Build-tagged coordinate identifier (the variant ID is only valid within a stated genome build, GRCh37 for v2 vs GRCh38 for v4) is not representable by any current registry key. Flagging in case a build-qualified coordinate join key is worth adding; for now `RSID` is the safe cross-build join.

License is MIT for the browser/code plus separate gnomAD terms of use on the data (do-not-reidentify, attribution expected). It is NOT CC0. The `license` field carries `MIT`; the non-reidentification obligation is a behavioural term, not an SPDX licence, and is noted here rather than in the YAML.
