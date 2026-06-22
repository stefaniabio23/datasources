---
id: interpro
name: InterPro
domain: bio-genomics
entry_kind: registry
description: Integrated database of protein families, domains, and functional sites maintained by EMBL-EBI, unifying signatures from 13 member databases (Pfam, CATH-Gene3D, PANTHER, PROSITE, SMART, and others) into a single resource with REST API and FTP bulk downloads.
homepage_url: https://www.ebi.ac.uk/interpro
docs_url: https://interpro-documentation.readthedocs.io/en/latest/
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: CC0
rate_limit: "unpublished; polite use expected, large pulls should use FTP bulk download"
bulk_available: true
frequency: "approximately every 8 weeks (~2 months); release 109.0 June 2026"
lag: "weeks-to-months for newly published signatures to be integrated and released"
geography: [global]
join_keys:
  - INTERPRO_ID
  - UNIPROT_ACCESSION
  - PDB_ID
  - GO_ID
  - NCBI_TAXON_ID
primary_keys:
  - INTERPRO_ID
join_key_fields:
  - join_key: INTERPRO_ID
    fields: [metadata.accession, accession]
  - join_key: UNIPROT_ACCESSION
    fields: [metadata.accession, accession]
  - join_key: PDB_ID
    fields: [metadata.accession, accession]
  - join_key: GO_ID
    fields: [metadata.go_terms.identifier]
  - join_key: NCBI_TAXON_ID
    fields: [metadata.taxId, metadata.accession]
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  Clean REST API with a regular path grammar (entry / protein / structure / taxonomy / proteome / set),
  but the modifier-chaining query model and the size of protein-match payloads make raw responses a
  poor fit for context windows. Suggested surface: get_entry, search_entries, get_protein_matches,
  resolve_uniprot_to_families, get_entry_proteins, get_member_db_signature.
agent_use_cases:
  - protein family and domain lookup
  - functional annotation from sequence
  - member-database signature resolution
  - domain-architecture comparison
  - GO-term annotation via family membership
access_test:
  command: "curl -sf 'https://www.ebi.ac.uk/interpro/api/entry/interpro/IPR000001/?format=json'"
  expected_status: 200
  expected_fields: [metadata.accession, metadata.name, metadata.type, metadata.member_databases]
last_verified: 2026-06-22
build_priority: high
---

# InterPro

## Why this source matters

InterPro is the reference open resource for protein classification, run by EMBL-EBI as a Global Core Biodata Resource and part of ELIXIR. It integrates protein signatures from 13 member databases (Pfam, CATH-Gene3D, PANTHER, PROSITE, PRINTS, PIRSF, SMART, SUPERFAMILY, CDD, HAMAP, SFLD, NCBIfam, MobiDB Lite) into a single non-redundant set of entries, each tagged with one of five types: family, domain, repeat, site, or homologous superfamily. Release 109.0 (June 2026) covers tens of thousands of entries and matches the bulk of UniProtKB. For any agent asking "what family does this protein belong to, what domains does it contain, what does it do," InterPro is the place to resolve a sequence or accession to functional classification. It is also the canonical access point for Pfam: the standalone Pfam website has been decommissioned and Pfam families are now reachable only through InterPro. Secondary relevance to `clinical-biotech` (target family annotation) and `academic` (each signature traces to source literature in its member database).

## Agent use cases

- protein family and domain lookup
- functional annotation from sequence
- member-database signature resolution
- domain-architecture comparison
- GO-term annotation via family membership

## Join strategy

InterPro is the issuing authority for `INTERPRO_ID` (e.g. `IPR000001`, pattern `^IPR[0-9]{6}$`), its native primary key for each integrated family/domain/site entry. The protein endpoint exposes `UNIPROT_ACCESSION` as the pivot between classification and sequence: every InterPro entry resolves to the set of UniProtKB proteins it matches, and conversely any UniProt accession resolves to its InterPro family/domain assignments. The structure endpoint carries `PDB_ID` for domain-to-structure mapping, entries carry `GO_ID` for ontology annotation transferred through family membership, and the taxonomy/proteome endpoints carry `NCBI_TAXON_ID` for organism-scoped queries.

Member-database signature accessions (Pfam `PF#####`, PANTHER `PTHR#####`, PROSITE `PS#####`, SMART `SM#####`, CATH-Gene3D `G3DSA:`, etc.) are source-native identifiers, not canonical join keys. They are listed in `primary_keys` and surfaced in the `metadata.member_databases` block of each entry. Of these, Pfam IDs have broad cross-source utility (UniProt, Pfam-derived tools, AlphaFold) and are flagged for review below.

InterPro pairs naturally with UniProt: resolve any protein to `UNIPROT_ACCESSION`, fan out to InterPro for family/domain classification, then to PDB or AlphaFold for structure.

## Access notes

**Low-volume queries:** REST API at `https://www.ebi.ac.uk/interpro/api/`, no auth. Seven top-level endpoints: `entry`, `protein`, `structure`, `taxonomy`, `proteome`, `set`, `utils`. Append `?format=json` (default) or `?format=tsv`. First call for a single entry: `/api/entry/interpro/{IPR_ID}/`. For protein classification: `/api/entry/interpro/protein/uniprot/{accession}/`. The query model chains modifiers across endpoints (e.g. entries-of-a-given-type matching proteins-in-a-given-taxon), which is powerful but easy to misconstruct.

InterPro classifies at the **family/domain layer**, not at residue coordinates by default. The `entry-protein` match payloads do carry residue **position fields** (`entry_protein_locations` with `fragments` giving start/end coordinates on the sequence), so domain boundaries are retrievable, but they require the protein-match endpoint rather than the entry metadata endpoint.

Coverage skews toward reviewed sequences: per the brief, InterPro matches roughly 81.8% of all UniProtKB but 96.8% of reviewed (Swiss-Prot) entries, so recall is far higher on curated proteins than on the bulk TrEMBL set. Agents should not assume an unmatched TrEMBL protein has no domains.

**Large analyses:** FTP bulk at `https://ftp.ebi.ac.uk/pub/databases/interpro/` ships the full entry list, protein-match tables, and member-database mappings per release. Check the latest release folder date there to confirm freshness. All InterPro data is freely available for any use. The companion InterProScan software (run signatures against your own sequences locally) is open source under Apache-2.0.

## MCP / connector notes

No official or community MCP found. High-value target: protein-classification queries are a common need across bio-genomics, clinical-biotech, and academic agents (three-plus overlapping audiences), the REST API is stable, and the chained-modifier query grammar plus large protein-match payloads make raw responses a poor context-window fit. Suggested surface: `get_entry` (trimmed metadata + member-DB signatures), `search_entries` (by type, member DB, GO term), `get_protein_matches` (domain architecture with residue positions for one accession), `resolve_uniprot_to_families`, `get_entry_proteins` (paginated), `get_member_db_signature` (Pfam/PANTHER/etc. lookup). The connector should default to trimming match-location arrays, paginate protein lists behind the scenes, and offer a bulk-vs-API switch for proteome-wide pulls.

## Review notes

Potential new join key for review: PFAM_ID
  Entity type: protein_family_signature
  Pattern: ^PF[0-9]{5}$
  Other datasets that would use it: InterPro, UniProt, AlphaFold, Pfam-derived annotation tools. Pfam's standalone site is decommissioned and Pfam is now reachable only through InterPro, which raises the cross-source value of a canonical Pfam key. Currently held in `primary_keys` only. Stephanie reviews and decides whether to PR into `schema/join-keys.yaml`.

Release version note: the brief cited v101.0 (~45,899 entries); the live API root reports release 109.0 (11 June 2026) as current. Coverage figures (81.8% UniProtKB / 96.8% Swiss-Prot) are carried from the brief and were not independently re-confirmed against 109.0; treat as approximate.

License recorded as CC0 (EBI default for InterPro's own integrated data, "freely available for any use"). Individual member databases (e.g. some PROSITE/SMART signatures) may carry their own upstream terms; downstream redistributors mixing member-DB-specific content should check per-member licensing.
