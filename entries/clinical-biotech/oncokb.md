---
id: oncokb
name: OncoKB
domain: clinical-biotech
entry_kind: knowledge-graph
description: MSK's precision-oncology knowledge base of the clinical actionability of cancer gene alterations, mapping variants to oncogenic effect and FDA/guideline therapy levels.
homepage_url: https://www.oncokb.org/
docs_url: https://www.oncokb.org/api-access
type:
  - rest-api
  - bulk-download
auth_required: api-key-free
cost: free-non-commercial
license: OncoKB-Terms
rate_limit: "per-token fair-use limits"
bulk_available: true
frequency: "rolling curation updates, versioned releases"
lag: "curation lag behind new approvals and publications"
geography: [global]
join_keys:
  - GENE_SYMBOL
primary_keys:
  - ONCOTREE_CODE
  - HGVS_PROTEIN_CHANGE
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/genomoncology/biomcp
mcp_command:
  - "uvx --from biomcp-python biomcp run"
agent_use_cases:
  - oncogenic-effect annotation of variants
  - therapy actionability and evidence-level lookup
  - tumor-type matching via OncoTree
  - precision-oncology decision support
access_test:
  command: "curl -sf -H \"Authorization: Bearer ${ONCOKB_TOKEN}\" 'https://www.oncokb.org/api/v1/utils/allCuratedGenes' -o /dev/null"
  expected_status: 200
last_verified: 2026-07-02
build_priority: low
notes: "access_test constructed not executed; requires a free ${ONCOKB_TOKEN} (register at oncokb.org). Free for academic/research use; commercial and clinical use require a paid licence. Covered by the biomcp MCP. License is non-SPDX (flagged). OncoKB homepage is JS-heavy and did not render via WebFetch; fields drawn from prior knowledge and should be re-verified."
---

# OncoKB

## Why this source matters

OncoKB, from Memorial Sloan Kettering, is the reference knowledge base for the *clinical* meaning of cancer mutations: for a given gene alteration and tumor type, it states whether the alteration is oncogenic and what therapies are actionable, graded by evidence level (FDA-recognised, standard-of-care, clinical evidence, etc.). It is the layer that turns a raw variant call into a treatment-relevant assertion, widely used in molecular tumor boards and precision-oncology pipelines. Secondary domain overlap with `bio-genomics` (variant annotation).

## Agent use cases

- oncogenic-effect annotation of variants
- therapy actionability and evidence-level lookup
- tumor-type matching via OncoTree
- precision-oncology decision support

## Join strategy

The canonical join key is `GENE_SYMBOL` (HGNC). OncoKB addresses alterations by gene plus protein change (`HGVS_PROTEIN_CHANGE`, e.g. `BRAF V600E`) and tumor type by `ONCOTREE_CODE` (the OncoTree cancer-type ontology); both are native primary keys. Pair with `chembl` / `drugs-at-fda` to link the recommended therapy to drug records, and with `clinicaltrials-gov` for matching trials by gene and tumor type.

## Access notes

REST at `oncokb.org/api/v1/` requires a bearer token from a free registration; the token is free for academic/research use, while commercial and clinical use require a separate licence agreement. Annotated-gene and variant endpoints plus versioned data-file downloads are available. Rate limits are per token. Pin the OncoKB data version for reproducibility, since actionability levels change as approvals land.

## MCP / connector notes

Covered by `biomcp` (`uvx --from biomcp-python biomcp run`) as one of its oncology sources. No dedicated OncoKB MCP; biomcp is the practical route. A connector must carry the token and surface the gene/variant/tumor-type annotate calls.

## Review notes

- License `OncoKB-Terms` is non-SPDX (free academic, licensed commercial/clinical). Confirm the short-name convention.
- Homepage is a JS single-page app that WebFetch could not render; API base, token flow, and endpoint paths were filled from prior knowledge and should be re-verified against `oncokb.org/api-access` before publication.
- `ONCOTREE_CODE` has cross-source utility (cBioPortal, GENIE, trials matching); consider promoting to a canonical join key if a second OncoTree-keyed source is added.
