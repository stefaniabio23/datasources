---
id: drugbank
name: DrugBank
domain: clinical-biotech
entry_kind: registry
description: Curated drug knowledgebase covering chemistry, pharmacology, targets, interactions, and external identifiers for approved, investigational, and experimental small-molecule and biotech drugs.
homepage_url: https://go.drugbank.com/
docs_url: https://docs.drugbank.com/v1/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: account-required
cost: free-non-commercial
license: DrugBank-Custom-License
rate_limit: "no public fixed cap; per-contract quota negotiated separately for free academic and paid commercial API tiers; polite use expected"
bulk_available: true
frequency: "minor releases every few months; major versions ~yearly"
lag: "weeks to months between FDA approval and DrugBank entry"
geography: [global]
join_keys:
  - CHEMBL_ID
  - RXNORM_CUI
  - BNF_CODE
  - GENE_SYMBOL
  - UNIPROT_ACCESSION
  - MESH_TERM
  - WIKIDATA_QID
primary_keys:
  - DRUGBANK_ID
  - DRUGBANK_TARGET_ID
  - DRUGBANK_INTERACTION_ID
  - DRUGBANK_PATHWAY_ID
join_key_fields:
  - join_key: CHEMBL_ID
    fields: [external_identifiers]
  - join_key: RXNORM_CUI
    fields: [external_identifiers]
  - join_key: GENE_SYMBOL
    fields: [targets.polypeptide.gene_name, enzymes.polypeptide.gene_name, transporters.polypeptide.gene_name, carriers.polypeptide.gene_name]
  - join_key: UNIPROT_ACCESSION
    fields: [targets.polypeptide.id, targets.polypeptide.external_identifiers, enzymes.polypeptide.id, transporters.polypeptide.id, carriers.polypeptide.id]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/openpharma-org/drugbank-mcp-server
mcp_notes: >
  One unofficial community MCP (openpharma-org/drugbank-mcp-server, JS, ~10 stars).
  Requires a DrugBank Online API token. Ideal surface: search_drug, get_drug,
  list_targets, list_interactions, resolve_external_id (NDC, RxCUI, ChEMBL to DBID).
agent_use_cases:
  - drug pharmacology lookup
  - drug-drug interaction screening
  - drug-target resolution
  - cross-identifier mapping (NDC, RxCUI, ChEMBL, KEGG to DBID)
  - mechanism-of-action retrieval
access_test:
  command: "curl -sf -H \"Authorization: ${DRUGBANK_API_KEY}\" 'https://api.drugbank.com/v1/drug_names.json?q=lipitor'"
  expected_status: 200
  expected_fields: [drugbank_id, name, synonyms]
last_verified: 2026-06-08
build_priority: medium
notes: "access_test not executed; requires DRUGBANK_API_KEY commercial token. Anonymous request to api.drugbank.com returns 401."
---

# DrugBank

## Why this source matters

DrugBank is the canonical curated drug knowledgebase: ~14K drug entries (FDA-approved small molecules, biologics, nutraceuticals, experimental and investigational compounds), each fused with pharmacology, mechanism of action, targets, enzymes, transporters, carriers, ADME, drug-drug interactions, food interactions, dosage, ATC codes, and a dense web of external identifiers (RxNorm, NDC, ChEMBL, ChEBI, PubChem, KEGG, UniProt, WHO ATC, BNF). Run by the Wishart Lab at the University of Alberta and commercialised through OMx Personal Health Analytics. The free public website at go.drugbank.com is the most-cited drug reference in biomedical literature; programmatic API and dataset downloads sit behind an academic-or-commercial license. Where openFDA tells you what the FDA has on record, DrugBank tells you what the drug actually does and how it crosswalks to every other terminology.

## Agent use cases

- drug pharmacology lookup
- drug-drug interaction screening
- drug-target resolution
- cross-identifier mapping (NDC, RxCUI, ChEMBL, KEGG to DBID)
- mechanism-of-action retrieval

## Join strategy

DrugBank's main value as a join hub is its dense identifier crosswalk. Each drug record carries external links to `RXNORM_CUI`, `CHEMBL_ID`, `BNF_CODE`, plus PubChem CID, ChEBI ID, KEGG Drug, ATC, UNII, NDC, and ICD-10 indications. Targets, enzymes, transporters, and carriers resolve to `UNIPROT_ACCESSION` and `GENE_SYMBOL`. Drug indications and adverse reactions surface as `MESH_TERM` annotations. Each drug entry also has a `WIKIDATA_QID` mapping in the external links file.

DrugBank-internal `DRUGBANK_ID` (DBxxxxx format, e.g. DB00945 for aspirin) is the source's primary key but is intentionally outside the canonical registry; use it for direct DrugBank lookups, not cross-source joins. Same for DrugBank target IDs (BExxxxxxx), drug interaction IDs, and pathway IDs (SMPxxxxxxx).

Common pairings: openFDA (RxCUI and NDC to FAERS adverse events), RxNorm (clinical drug concepts), ChEMBL (bioactivity assays), UniProt (target protein details), ClinicalTrials.gov (indications to active trials), OpenTargets (target-disease associations).

Potential new join keys flagged below: `DRUGBANK_ID`, `ATC_CODE`, `UNII`, `KEGG_DRUG_ID`, `PUBCHEM_CID`, `CHEBI_ID`.

## Access notes

**Public website** (go.drugbank.com): free, browsable, attribution required. Good for spot lookups, useless for agent workflows.

**DrugBank Online API** (api.drugbank.com, docs at docs.drugbank.com/v1): REST, token-auth via `Authorization` header. Requires a commercial license or a separate academic license application; rate limits and quotas negotiated per contract. Endpoints cover drug search, drug details (including targets, interactions, ADME), product lookup, indication search, and identifier resolution. There is no anonymous free tier; anonymous requests return 401.

**Withdrawn-drug analysis.** DrugBank tags a withdrawn category (~900+ drugs) with the withdrawal reason and affected groups; filter on the withdrawn group and join via `DRUGBANK_ID` / `INCHI_KEY` to targets, ATC classes, and toxicity. Pair with the dedicated `withdrawn-database` entry for a fuller drug-attrition picture.

**Academic dataset downloads** (`go.drugbank.com/releases/latest`): full XML (~200 MB compressed), CSV crosswalk files (external drug links, target/enzyme/carrier/transporter identifiers, UniProt mappings), SDF structures (2D/3D for drugs and metabolites), FASTA sequences. Free for academic non-commercial research with a free account; commercial use requires a paid license. **As of mid-2026 the academic download program is temporarily paused** with a sign-up list for resumption notifications — verify status before relying on a fresh download.

License nuance: the website is publicly viewable but redistribution of content (including derivative datasets) requires a license. Academic license is free but gated by institutional verification; commercial license is per-seat or per-product, contact sales. This makes DrugBank a non-trivial dependency for any agent product that needs to redistribute or embed drug content.

## MCP / connector notes

One unofficial community MCP exists: `openpharma-org/drugbank-mcp-server` (JavaScript, ~10 stars, created 2025-12). Wraps a subset of the DrugBank Online API; requires the user to supply their own DrugBank API token. No official MCP from DrugBank or Anthropic.

An ideal connector surface would expose `search_drug` (by name, synonym, brand), `get_drug` (full record by DBID), `list_targets`, `list_interactions`, `resolve_external_id` (NDC, RxCUI, ChEMBL, ATC to DBID), and `get_indication`. Hard parts: enforcing the user's per-license rate limits (DrugBank contracts vary widely), normalising the very wide `drug` response (~50 nested fields), and handling the academic-vs-commercial token routing. The bulk XML route is a viable fallback for licensed users with high-volume needs; the connector should not auto-bulk-download given the redistribution restrictions.

## Review notes

- License is custom proprietary. No SPDX code. Used `DrugBank-Custom-License` as a canonical kebab-case short name; flag for promotion to SCHEMA.md's known-licenses list. Real terms vary across academic-free, academic-paid (some tiers), and commercial; the body documents the gating.
- Potential new join key for review: `DRUGBANK_ID`. Entity type: `drug_product`. Pattern: `^DB[0-9]{5}$`. Other datasets that would use it: openFDA (in `openfda.spl_set_id` enrichments inconsistently), Wikidata (P715), KEGG Drug crosswalks, OpenTargets (drug entity), Inxight Drugs, ChEMBL (in cross-references). Strong candidate, very widely referenced across drug-data sources.
- Potential new join key for review: `ATC_CODE`. Entity type: `drug_classification`. Pattern: `^[A-V][0-9]{2}[A-Z]{2}[0-9]{2}$` (5-level WHO Anatomical Therapeutic Chemical code). Other datasets that would use it: WHO ATC/DDD index, BNF, openFDA (pharm_class_epc), every European drug formulary, IQVIA. Critical for cross-country drug classification joins.
- Potential new join key for review: `UNII`. Entity type: `chemical_substance`. Pattern: `^[A-Z0-9]{10}$`. Other datasets that would use it: openFDA, DailyMed, GSRS, USDA FoodData Central. Same key flagged in the openFDA entry; consolidate when promoting.
- Potential new join key for review: `KEGG_DRUG_ID`. Entity type: `drug_product`. Pattern: `^D[0-9]{5}$`. Other datasets that would use it: KEGG Drug, KEGG Pathway, KEGG MEDICUS, Reactome crosswalks.
- Potential new join key for review: `PUBCHEM_CID`. Entity type: `chemical_compound`. Pattern: `^[0-9]+$`. Other datasets that would use it: PubChem, ChEMBL, ChEBI, every cheminformatics source.
- Potential new join key for review: `CHEBI_ID`. Entity type: `chemical_entity`. Pattern: `^CHEBI:[0-9]+$`. Other datasets that would use it: ChEBI, Reactome, Rhea, MetaCyc, ChEMBL crosswalks.
- `auth_required: account-required` reflects the dataset-download path (free account, license click-through). The API path is closer to `api-key-paid` (commercial) or `api-key-free` (academic) depending on contract. Picked the broader gating value; document the nuance in body.
- `cost: free-non-commercial` reflects the academic path. Commercial use is paid. No single enum captures both; flagged.
- `access_test` constructed but not executed (returns 401 without DRUGBANK_API_KEY). Anonymous endpoint probe confirmed the 401 wall.
- As of 2026-06, the academic dataset download program is paused. If still paused at next verification, consider downgrading `bulk_available` or adding a `notes` warning.
