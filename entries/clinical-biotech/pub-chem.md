---
id: pub-chem
name: PubChem
domain: clinical-biotech
entry_kind: knowledge-graph
description: Open chemistry database from NIH/NLM aggregating compounds, substances, and bioassays with dense cross-references to drug, target, and literature resources.
homepage_url: https://pubchem.ncbi.nlm.nih.gov/
docs_url: https://pubchem.ncbi.nlm.nih.gov/docs/programmatic-access
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: US-Government-Public-Domain
rate_limit: "5 req/sec, 400 req/min; dynamic throttling via response headers"
bulk_available: true
frequency: "compound and substance records updated continuously; FTP snapshots refreshed regularly (weekly for most subsets)"
lag: "hours-to-days for new depositor submissions; weeks-to-months for full cross-reference enrichment"
geography: [global]
join_keys:
  - INCHI_KEY
  - CHEMBL_ID
  - DRUGBANK_ID
  - CHEBI_ID
  - UNII
  - MESH_TERM
  - PMID
  - DOI
  - UNIPROT_ACCESSION
  - GENE_SYMBOL
  - ENTREZ_GENE_ID
  - NCBI_TAXON_ID
  - NDC
  - ATC_CODE
  - RXNORM_CUI
  - WIKIDATA_QID
primary_keys:
  - PUBCHEM_CID
  - PUBCHEM_SID
  - PUBCHEM_AID
join_key_fields:
  - join_key: INCHI_KEY
    fields: [InChIKey, props.urn.label=InChIKey]
  - join_key: CHEMBL_ID
    fields: [xrefs.RegistryID, source.SourceName=ChEMBL]
  - join_key: DRUGBANK_ID
    fields: [xrefs.RegistryID, source.SourceName=DrugBank]
  - join_key: CHEBI_ID
    fields: [xrefs.RegistryID, source.SourceName=ChEBI]
  - join_key: UNII
    fields: [xrefs.RegistryID, source.SourceName=FDA-Global-Substance-Registration-System-GSRS]
  - join_key: MESH_TERM
    fields: [xrefs.MeSH, synonyms]
  - join_key: PMID
    fields: [xrefs.PubMedID, literature.PMID]
  - join_key: DOI
    fields: [xrefs.DOI, reference.DOI]
  - join_key: UNIPROT_ACCESSION
    fields: [target.protein_accession, gene_target.uniprot]
  - join_key: GENE_SYMBOL
    fields: [gene.symbol, target.gene_symbol]
  - join_key: ENTREZ_GENE_ID
    fields: [gene.GeneID, xrefs.GeneID]
  - join_key: NCBI_TAXON_ID
    fields: [taxonomy.TaxID, xrefs.TaxonomyID]
  - join_key: NDC
    fields: [xrefs.RegistryID, source.SourceName=FDA-NDC]
  - join_key: ATC_CODE
    fields: [classification.ATC]
  - join_key: RXNORM_CUI
    fields: [xrefs.RegistryID, source.SourceName=RxNorm]
  - join_key: WIKIDATA_QID
    fields: [xrefs.Wikidata]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/cyanheads/pubchem-mcp-server
  - github.com/augmented-nature/pubchem-mcp-server
  - github.com/JackKuo666/PubChem-MCP-Server
  - github.com/BioContext/PubChem-MCP
  - github.com/PhelanShao/pubchem-mcp-server
mcp_notes: >
  Five community MCP wrappers exist (no official). The cyanheads server is the broadest
  (search, properties, safety, bioactivity, cross-refs, both STDIO and Streamable HTTP).
  Suggested canonical surface: search_compound (by name, SMILES, InChIKey, CID),
  get_compound_properties, get_bioassay, get_substance_xrefs, resolve_identifier,
  get_classification. Connector should trim heavy PUG-View JSON sections by default
  and route bulk pulls to FTP rather than paginating the REST API.
agent_use_cases:
  - chemical structure search
  - identifier crosswalk between chemistry databases
  - bioassay screening data retrieval
  - drug compound metadata lookup
  - target-bioactivity mapping
access_test:
  command: "curl -sf 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/MolecularFormula,MolecularWeight,InChIKey/JSON'"
  expected_status: 200
  expected_fields: [PropertyTable.Properties.CID, PropertyTable.Properties.MolecularFormula, PropertyTable.Properties.InChIKey]
last_verified: 2026-06-09
build_priority: high
---

# PubChem

## Why this source matters

PubChem is the reference open chemistry database, run by the National Center for Biotechnology Information (NCBI) at the US National Library of Medicine. It aggregates over 110 million unique compounds (CID), several hundred million substance records (SID) deposited by ~1,000 data sources, and over a million bioassays (AID) with associated activity measurements. Each compound record carries standardised structure (SMILES, InChI, InChIKey), computed physicochemical properties, computed and curated names, classification (ATC, MeSH, GHS hazards), patent and literature links, vendor information, and a dense cross-reference web to ChEMBL, ChEBI, DrugBank, UNII, RxNorm, NDC, CAS, and many others. Where ChEMBL is curated medicinal-chemistry literature and DrugBank is curated drug knowledge, PubChem is the broad aggregator that ties them together. Secondary domain coverage: bio-genomics (gene and protein target annotations) and academic (literature back-references via PMID/DOI).

## Agent use cases

- chemical structure search
- identifier crosswalk between chemistry databases
- bioassay screening data retrieval
- drug compound metadata lookup
- target-bioactivity mapping

## Join strategy

PubChem is the hub for chemistry-side joins. Its CID (compound identifier) is the de-facto pivot used by ChEMBL, DrugBank, ChEBI, openFDA, and dozens of cheminformatics tools to address one canonical structure. Every compound record carries `INCHI_KEY` (canonical chemistry key), and cross-references to `CHEMBL_ID`, `DRUGBANK_ID`, `CHEBI_ID`, `UNII`, `NDC`, `ATC_CODE`, `RXNORM_CUI`, and `WIKIDATA_QID`. Bioassay records link to `UNIPROT_ACCESSION`, `GENE_SYMBOL`, `ENTREZ_GENE_ID`, and `NCBI_TAXON_ID` for the assayed target. Literature back-references attach `PMID` and `DOI`. MeSH headings appear as `MESH_TERM` annotations for synonyms and pharmacological actions.

PubChem mints three source-internal IDs: `PUBCHEM_CID` (canonical compound), `PUBCHEM_SID` (depositor substance, many-to-one to CID), and `PUBCHEM_AID` (bioassay). CID is the most-referenced of the three across the wider chemistry ecosystem and is a strong candidate for the canonical registry; flagged for review.

Common pairings: ChEMBL (deeper bioactivity curation per assay), DrugBank (drug pharmacology and DDI), ChEBI (chemical ontology), openFDA (regulatory side via NDC and UNII), UniProt (target sequence resolution), Reactome (pathway context).

## Access notes

**Programmatic access:** PUG REST at `https://pubchem.ncbi.nlm.nih.gov/rest/pug/`, no auth. Rate-limited to 5 req/sec and 400 req/min globally; the HTTP response headers (`X-Throttling-Control`) surface live throttle state so a polite client can back off before being blocked. PUG-View at `https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/` returns the rich annotated record JSON (hundreds of curated sections per compound), heavier but the right shape for lookup-style agent use. PUG-SOAP is legacy and not recommended for new work.

**Bulk:** FTP at `https://ftp.ncbi.nlm.nih.gov/pubchem/` (also `ftp://`). The full compound corpus sits under `Compound/CURRENT-Full/` as SDF (~340 files, ~300 GB compressed), with parallel directories for substance, bioassay, and the PubChemRDF distribution. Use bulk for any analysis that would otherwise exceed a few hundred thousand REST calls. PubChemRDF and the new `downloads2` v2 portal expose JSON, JSONL, CSV, XML, and Turtle subsets for targeted pulls.

License: PubChem is a US Government work and the core data is public domain (17 USC 105). However, individual depositor records may carry their own licence (e.g. ChEMBL contributions inherit CC BY-SA 3.0; some commercial vendors restrict redistribution). For downstream products redistributing PubChem content, check the `source.SourceName` on each record and consult the per-source page at `https://pubchem.ncbi.nlm.nih.gov/source/<source-id>`.

Known gotchas:

- PUG REST property responses use abbreviated keys (e.g. `ConnectivitySMILES`, not the legacy `CanonicalSMILES`). Code written against older endpoints may break silently after server-side renames.
- A single CID can be referenced by many SIDs (one canonical structure with multiple depositor submissions). Joining on SID without rolling up to CID double-counts.
- Bioassay AIDs cover screens of widely varying quality: HTS primary screens, confirmatory dose-response, and literature-mined single measurements all share the same identifier space. The `activity_outcome` and `confirmation_status` fields are essential filters.
- Throttling is dynamic and partly invisible. Hitting 5 req/sec from a single IP routinely triggers transient 503s during peak NCBI load.

## MCP / connector notes

Five community MCP servers exist; no official MCP. The `cyanheads/pubchem-mcp-server` (TypeScript, STDIO + Streamable HTTP) covers the broadest surface (search, properties, safety data, bioactivity, cross-references, entity summaries) and ships a hosted public instance. `augmented-nature/pubchem-mcp-server` advertises coverage of the full ~110M compound corpus with property and bioassay tools. `JackKuo666/PubChem-MCP-Server` and `BioContext/PubChem-MCP` target compound, substance, and bioassay lookups. `PhelanShao/pubchem-mcp-server` focuses on structure-file generation for LLM-driven molecular workflows. None require API keys; all wrap the public PUG REST API.

An ideal canonical surface would expose `search_compound` (name, SMILES, InChIKey, CID), `get_compound_properties` (trimmed, with explicit property list), `get_bioassay` (with activity-outcome filter), `get_substance_xrefs`, `resolve_identifier` (any input identifier to CID), and `get_classification` (MeSH, ATC, GHS). Hard parts: aggressive trimming of PUG-View payloads (full annotated records run to megabytes per compound), respecting the dynamic throttle headers, and routing high-volume requests to FTP snapshots rather than the REST API.

## Review notes

Potential new join key for review: PUBCHEM_CID
  Entity type: chemical_compound
  Pattern: ^[0-9]+$
  Other datasets that would use it: PubChem (mints it), ChEMBL (xrefs), DrugBank (xrefs), ChEBI (xrefs), UniChem, openFDA (some SPL enrichments), DailyMed, Inxight Drugs, KEGG, every cheminformatics tool. Already flagged in the ChEMBL and DrugBank entries' Review notes; this is the third independent flag. Strong candidate for promotion.

Potential new join key for review: CAS_RN
  Entity type: chemical_substance
  Pattern: ^[0-9]{2,7}-[0-9]{2}-[0-9]$
  Other datasets that would use it: PubChem (synonym field), ChemSpider, EPA CompTox, ECHA, USDA FoodData Central, every regulatory chemistry source. CAS Registry Numbers remain the dominant industrial chemical identifier; absence is a real gap for any agent crosswalking to regulatory or industrial-chemistry sources.

License is `US-Government-Public-Domain` for the core NLM data, but contributed depositor records can carry their own terms (ChEMBL records inherit CC BY-SA 3.0; some vendor records are commercial-restricted). Flagging because the YAML's single license field is a simplification; downstream redistribution should be source-checked per record.

`entry_kind: knowledge-graph` chosen over `mixed` because PubChem is fundamentally one linked entity graph (compounds, substances, bioassays, targets, literature) rather than several independent datasets. Open to `mixed` if the registry intent is "any source covering multiple sub-databases".
