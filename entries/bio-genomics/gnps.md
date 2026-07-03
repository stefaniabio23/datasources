---
id: gnps
name: GNPS
domain: bio-genomics
entry_kind: knowledge-graph
description: Open community knowledge base of tandem MS/MS reference spectra, molecular networks, and natural-product annotations, run by the Dorrestein lab / CCMS at UC San Diego.
homepage_url: https://gnps.ucsd.edu/
docs_url: https://ccms-ucsd.github.io/GNPSDocumentation/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC0
bulk_available: true
frequency: continuous (community contributions)
geography: [global]
join_keys:
  - INCHI_KEY
  - PMID
primary_keys:
  - CCMSLIB_SPECTRUM_ID
  - MASSIVE_DATASET_ID
  - GNPS_TASK_ID
join_key_fields:
  - join_key: PMID
    fields: [Pubmed_ID]
  - join_key: INCHI_KEY
    fields: [InChIKey_smiles, InChIKey_inchi]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - MS/MS spectral dereplication
  - compound annotation by structure
  - natural-product library lookup
  - molecular network exploration
  - metabolomics dataset discovery
access_test:
  command: "curl -sf 'https://gnps.ucsd.edu/ProteoSAFe/SpectrumCommentServlet?SpectrumID=CCMSLIB00000072100'"
  expected_status: 200
  expected_fields: [annotations, Compound_Name, SpectrumID, Pubmed_ID, Smiles]
last_verified: 2026-07-02
build_priority: low
---

# GNPS

## Why this source matters

GNPS (Global Natural Products Social Molecular Networking) is an open-access mass-spectrometry knowledge base run by the Dorrestein lab and the Center for Computational Mass Spectrometry (CCMS) at UC San Diego. It hosts community-curated reference MS/MS spectral libraries, runs molecular-networking analyses that link spectra by spectral similarity, and is paired with the MassIVE repository for raw untargeted metabolomics/proteomics datasets. For an agent working in metabolomics or natural-products chemistry, GNPS is the primary place to dereplicate an unknown MS/MS spectrum against reference libraries and to pull structure-annotated compound metadata (name, SMILES, InChI, InChIKey, CAS, PubMed).

## Agent use cases

- MS/MS spectral dereplication
- compound annotation by structure
- natural-product library lookup
- molecular network exploration
- metabolomics dataset discovery

## Join strategy

GNPS spectral-library entries carry two registry-canonical keys usable for cross-source joining: `INCHI_KEY` (in the cleaned library dumps as `InChIKey_smiles` / `InChIKey_inchi`, computed from the entry's SMILES/InChI) and `PMID` (the `Pubmed_ID` field). Pair `INCHI_KEY` with ChEBI, ChEMBL, PubChem, or any structure-indexed chemistry source to move from a spectrum to a molecule; pair `PMID` with PubMed / Europe PMC / OpenAlex for the literature behind a reference spectrum.

Source-native identifiers stay in `primary_keys`, not `join_keys`: the spectral-library accession (`SPECTRUMID`, e.g. `CCMSLIB00000072100`), the MassIVE dataset accession (`MSVxxxxxxxxx`), and the GNPS `task_id` for a workflow run. The library accession is a stable global handle for a reference spectrum and is a candidate canonical join key (flagged below). The source also emits raw `SMILES` and `INCHI` structure strings, which are structure identifiers but have no canonical registry key of their own; `INCHI_KEY` is the hashed, joinable form.

## Access notes

Single library entry as JSON (no auth): `https://gnps.ucsd.edu/ProteoSAFe/SpectrumCommentServlet?SpectrumID=CCMSLIB00000072100` returns `{"annotations":[{...}]}` with `Compound_Name`, `Smiles`, `INCHI`, `CAS_Number`, `Pubmed_ID`, `SpectrumID`, and library membership. Note fields left blank appear as the literal string `N/A`, not null.

USI-based JSON/CSV retrieval of a single spectrum: `https://metabolomics-usi.gnps2.org/json/?usi1=mzspec:GNPS:GNPS-LIBRARY:accession:CCMSLIB00000072100`.

Bulk: whole reference libraries download from `https://gnps.ucsd.edu/ProteoSAFe/libraries.jsp` (per-library MGF/MSP/JSON, plus a combined `ALL_GNPS.json`), which is the cleaned form that carries `InChIKey_smiles`. Browsing/downloading libraries and hitting the read endpoints needs no account; submitting data or running molecular-networking/spectral-search workflows through ProteoSAFe requires a free GNPS account. Rate limits are not documented, so throttle bulk scraping.

## MCP / connector notes

No GNPS-specific MCP found (searched modelcontextprotocol, GitHub, npm, PyPI as of 2026-07-02). Audience is narrow (metabolomics / natural-products MS) relative to the rest of the registry, so this is low-value to build now. A useful connector surface would be: `get_library_spectrum(ccmslib_id)`, `search_by_inchikey(inchikey)`, `search_by_compound_name(name)`, `list_libraries()`, and `get_massive_dataset(msv_id)`. The connector must abstract over the idiosyncratic ProteoSAFe servlet endpoints vs the newer gnps2.org USI endpoints, normalise the `N/A` sentinel strings to null, and compute/expose `INCHI_KEY` from the raw SMILES/InChI where the servlet does not return it directly.

## Review notes

Potential new join key for review: `CCMSLIB_SPECTRUM_ID`
  Entity type: reference_ms_ms_spectrum
  Pattern: `^CCMSLIB[0-9]{11}$`
  Other datasets that would use it: MassIVE, MetaboLights, mzspec USI ecosystem, GNPS2, any tool citing a GNPS reference spectrum. This is the "spectral library id" hint and is currently in `primary_keys` only.

Potential new join key for review: `MASSIVE_DATASET_ID`
  Entity type: mass_spec_dataset
  Pattern: `^MSV[0-9]{9}$`
  Other datasets that would use it: MassIVE, ProteomeXchange, MetabolomicsWorkbench, GNPS. Metabolomics/proteomics repository accession; parked in `primary_keys` for now.

License: MassIVE/GNPS deposited data defaults to CC0 (ProteomeXchange minimum), with a stated intent to move new submissions toward CC-BY over time. Individual contributed library entries could carry contributor-specific terms; confirm per-library if redistribution matters. Set `license: CC0` as the documented default.

Successor platform: a GNPS2 instance (gnps2.org, Wang Bioinformatics Lab) is the actively developed successor; endpoints and accession schemes are shared. Worth a separate entry later, not merged here.
