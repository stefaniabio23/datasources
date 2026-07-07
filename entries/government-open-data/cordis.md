---
id: cordis
name: CORDIS (EU Research Projects)
domain: government-open-data
entry_kind: knowledge-graph
description: The European Commission's registry of EU-funded research projects (FP1 to Horizon Europe) with participating organisations, results, deliverables, and links to open-access publications.
homepage_url: https://cordis.europa.eu/
docs_url: https://cordis.europa.eu/about/services
type:
  - bulk-download
  - database
  - rest-api
auth_required: none
cost: free
license: CC-BY-4.0
rate_limit: "no published limit on bulk downloads or SPARQL; interactive CORDIS API requires registration"
bulk_available: true
frequency: "portal updated continuously; per-framework-programme bulk snapshots refreshed periodically"
lag: "weeks-to-months for newly signed grants and published results to appear"
geography: [global]
join_keys:
  - DOI
  - ISO_2
primary_keys:
  - CORDIS_PROJECT_ID
  - CORDIS_RCN
  - CORDIS_PIC
join_key_fields:
  - join_key: DOI
    fields: [doi]
  - join_key: ISO_2
    fields: [country]
mcp_status: mcp-needed-low-value
agent_use_cases:
  - EU research-funding lookup
  - grant participant mapping
  - collaboration-network analysis
  - technology-landscape scouting
  - linking projects to open-access publications
access_test:
  command: "curl -sf 'https://cordis.europa.eu/datalab/sparql?query=SELECT%20%3Fp%20WHERE%20%7B%3Fs%20%3Fp%20%3Fo%7D%20LIMIT%201&format=application/sparql-results%2Bjson'"
  expected_status: 200
  expected_fields: [head, results]
last_verified: 2026-07-07
build_priority: medium
---

# CORDIS (EU Research Projects)

## Why this source matters

CORDIS (Community Research and Development Information Service) is the European Commission's primary public record of projects funded by the EU framework programmes for research and innovation, from FP1 through Horizon 2020 and Horizon Europe (2021-2027). Managed by the Publications Office of the EU, it exposes project factsheets (budget, EC contribution, dates, topics, funding scheme), participating organisations (with coordinator flags, activity type, country, city), reported results and deliverables, and links to open-access publications. It is the canonical way to answer "who received EU research money, for what, with whom, and what came out of it." Secondary relevance to `academic` (links projects to publications and researchers) and `corporate-registry` (organisation participation records with PIC and VAT).

## Agent use cases

- EU research-funding lookup
- grant participant mapping
- collaboration-network analysis
- technology-landscape scouting
- linking projects to open-access publications

## Join strategy

CORDIS exposes two registry join keys directly: `DOI` on project publications/results (join to OpenAlex, Crossref, Europe PMC) and a two-letter country code on organisations that maps to `ISO_2` (EU convention deviates from strict ISO 3166-1 alpha-2: `EL` for Greece, `UK` for the United Kingdom, so normalise before joining to `ISO_3` sources).

Source-internal identifiers carry most of the entity structure and are not (yet) in the canonical registry: the project id and RCN identify projects; the PIC (Participant Identification Code) identifies organisations across the entire EU Funding & Tenders ecosystem and is the natural bridge to other EU-funding datasets. Organisation records also carry a `vatNumber`. See Review notes for the PIC candidate.

The EURIO knowledge graph (RDF/SPARQL) is the richest join surface: it models projects, organisations, results, and topics as linked entities. It does not natively mint `ROR` for organisations (identity is PIC-based), so ROR joins require external enrichment rather than a direct field.

## Access notes

Three no-auth paths, no key required:

- **Bulk downloads** at data.europa.eu, one dataset per framework programme (Horizon Europe, H2020, FP7, ...) plus reference tables (countries, programmes, organisation activity types), in CSV, XML, XLS, and JSON. Best for full-corpus analysis. Project and organisation tables join on the project id.
- **SPARQL** endpoint at `https://cordis.europa.eu/datalab/sparql` over the EURIO knowledge graph (ontology at op.europa.eu EU-vocabularies). Best for entity-linked queries; returns standard SPARQL JSON (`head` / `results`).
- **Search export** (XML/CSV/JSON) and RSS feeds off the portal for incremental content.

The interactive CORDIS **API** (saved searches, alerts, data-extraction management) is the one surface that requires a registered account; the bulk and SPARQL paths above cover programmatic reuse without it, which is why `auth_required` is `none`.

## MCP / connector notes

No MCP found (searched modelcontextprotocol, GitHub, npm, PyPI). Audience is moderate (research-funding intelligence, competitive scouting, EU grant analysis), hence low-value tier. A useful connector would wrap the SPARQL endpoint plus the bulk snapshots and expose: `search_projects` (by topic/acronym/programme/date), `get_project` (factsheet + participants + results), `get_organisation` (by PIC or name), `project_publications` (DOIs), and `collaboration_network` (co-participation edges). The MCP must abstract over the SPARQL/EURIO learning curve and over the per-programme fragmentation of the bulk files, and normalise the EU country-code deviations.

## Review notes

- Country codes use EU-style two-letter codes mapped here to `ISO_2`, with known deviations (`EL`=Greece, `UK`=United Kingdom). Flag for consumers normalising to `ISO_3`.
- Potential new join key for review: `PIC`
  - Entity type: eu_funded_organisation
  - Pattern: 9-digit numeric Participant Identification Code (e.g. `999999999`)
  - Other datasets that would use it: EU Funding & Tenders Portal, EU Financial Transparency System, other EU grant/tender datasets. High cross-source utility within the EU-funding domain; consider PR to `schema/join-keys.yaml`.
- Task hint suggested `ROR` as a join key; could not confirm ROR is exposed in the CORDIS bulk CSVs or the EURIO graph (organisation identity is PIC-based). Excluded from `join_keys` to avoid asserting a field that may not exist. Verify against a live SPARQL query or org CSV before adding.
- License is CC-BY-4.0 under Commission Decision 2011/833/EU (Reuse Decision); attribution to the European Union required. Beneficiary-supplied materials and third-party media within project content may carry separate terms.
