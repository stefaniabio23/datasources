---
id: wiki-data-query-service
name: Wikidata Query Service
domain: government-open-data
entry_kind: knowledge-graph
description: Public SPARQL endpoint over Wikidata's CC0 knowledge graph of 120M+ items, hubbing identifiers from DOI and ORCID to ISBN, NCT_ID, CHEMBL_ID, OSM_ID and most other cross-domain keys.
homepage_url: https://query.wikidata.org/
docs_url: https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: none
cost: free
license: CC0
rate_limit: "60s hard query timeout; soft per-IP throttling; descriptive User-Agent with contact required"
bulk_available: true
frequency: "live mirror of Wikidata edits; full RDF dumps weekly"
lag: "minutes for live SPARQL; up to a week for RDF dumps"
geography: [global]
join_keys:
  - WIKIDATA_QID
  - WIKIPEDIA_ARTICLE
  - DOI
  - PMID
  - PMCID
  - ARXIV_ID
  - ORCID
  - ISNI
  - ROR
  - ISSN
  - ISBN
  - NCT_ID
  - CHEMBL_ID
  - DRUGBANK_ID
  - UNII
  - ATC_CODE
  - UNIPROT_ACCESSION
  - ENSEMBL_ID
  - ENTREZ_GENE_ID
  - NCBI_TAXON_ID
  - CIK
  - LEI
  - ISO_3
  - ISO_2
  - OSM_ID
  - MESH_TERM
primary_keys:
  - WIKIDATA_QID
  - WIKIDATA_PROPERTY_ID
  - WIKIDATA_LEXEME_ID
join_key_fields:
  - join_key: WIKIDATA_QID
    fields: [item, "?item (entity URI under http://www.wikidata.org/entity/Q...)"]
  - join_key: WIKIPEDIA_ARTICLE
    fields: ["?sitelink (schema:about ?item; schema:isPartOf <https://en.wikipedia.org/>)"]
  - join_key: DOI
    fields: ["wdt:P356"]
  - join_key: PMID
    fields: ["wdt:P698"]
  - join_key: PMCID
    fields: ["wdt:P932"]
  - join_key: ARXIV_ID
    fields: ["wdt:P818"]
  - join_key: ORCID
    fields: ["wdt:P496"]
  - join_key: ISNI
    fields: ["wdt:P213"]
  - join_key: ROR
    fields: ["wdt:P6782"]
  - join_key: ISSN
    fields: ["wdt:P236"]
  - join_key: ISBN
    fields: ["wdt:P212", "wdt:P957"]
  - join_key: NCT_ID
    fields: ["wdt:P3098"]
  - join_key: CHEMBL_ID
    fields: ["wdt:P592"]
  - join_key: DRUGBANK_ID
    fields: ["wdt:P715"]
  - join_key: UNII
    fields: ["wdt:P652"]
  - join_key: ATC_CODE
    fields: ["wdt:P267"]
  - join_key: UNIPROT_ACCESSION
    fields: ["wdt:P352"]
  - join_key: ENSEMBL_ID
    fields: ["wdt:P594", "wdt:P704", "wdt:P705"]
  - join_key: ENTREZ_GENE_ID
    fields: ["wdt:P351"]
  - join_key: NCBI_TAXON_ID
    fields: ["wdt:P685"]
  - join_key: CIK
    fields: ["wdt:P5531"]
  - join_key: LEI
    fields: ["wdt:P1278"]
  - join_key: ISO_3
    fields: ["wdt:P298"]
  - join_key: ISO_2
    fields: ["wdt:P297"]
  - join_key: OSM_ID
    fields: ["wdt:P11693", "wdt:P10689", "wdt:P402"]
  - join_key: MESH_TERM
    fields: ["wdt:P486"]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/wmde/WikidataMCP
  - github.com/cyanheads/wikidata-mcp-server
  - github.com/ebaenamar/wikidata-mcp
mcp_notes: >
  Wikimedia Deutschland (wmde) maintains a read-only Python MCP that wraps SPARQL, entity
  fetch, and external-identifier resolution. cyanheads/wikidata-mcp-server is a more
  feature-rich TypeScript alternative (STDIO and Streamable HTTP) covering search, entity
  fetch, SPARQL execution, and identifier mapping. Connector job is to package SPARQL
  prefixes, inject a contact User-Agent, chunk over the 60s timeout, and translate Q-IDs
  to labels in the requested language.
agent_use_cases:
  - cross-source identifier resolution
  - entity disambiguation by Wikidata Q-ID
  - structured fact lookup on people, places, works, drugs, genes
  - building seed lists for downstream domain-specific pulls
  - federated SPARQL across Wikidata, Commons, and external life-science endpoints
access_test:
  command: "curl -sf -H 'Accept: application/sparql-results+json' -A 'datasources-directory (contact@example.org)' 'https://query.wikidata.org/sparql?query=SELECT%20%3Fitem%20WHERE%20%7B%20%3Fitem%20wdt%3AP31%20wd%3AQ146.%20%7D%20LIMIT%202'"
  expected_status: 200
  expected_fields: [head.vars, results.bindings]
last_verified: 2026-06-09
build_priority: high
---

# Wikidata Query Service

## Why this source matters

Wikidata is the Wikimedia Foundation's structured knowledge graph: 120M+ items covering people, places, organisations, scholarly works, drugs, genes, proteins, taxa, public companies, geographic features, and almost every named entity that has a Wikipedia article. The Query Service (WDQS) at `query.wikidata.org` exposes the full graph as a SPARQL 1.1 endpoint over a Blazegraph backend, with results in XML, JSON, CSV, TSV, GeoJSON, GPX, and KML. Everything is CC0, no key required. For an agent stitching sources, Wikidata is the canonical mapping table from one identifier scheme to another: a single SPARQL query resolves a CHEMBL_ID to a DOI to an OSM_ID to an ORCID to a Wikipedia article slug in any of 300+ languages. Sits in `government-open-data` as a public open-data resource but functions as a cross-domain bridge across academic, clinical-biotech, bio-genomics, corporate-registry, geospatial, and consumer-signal.

## Agent use cases

- cross-source identifier resolution
- entity disambiguation by Wikidata Q-ID
- structured fact lookup on people, places, works, drugs, genes
- building seed lists for downstream domain-specific pulls
- federated SPARQL across Wikidata, Commons, and external life-science endpoints

## Join strategy

Every Wikidata item is identified by a `WIKIDATA_QID` (`Q42`, `Q146`). Statements use property IDs (`P31` instance-of, `P356` DOI, `P496` ORCID, `P698` PMID, `P352` UniProt, `P351` Entrez Gene, `P685` NCBI taxon, `P5531` SEC CIK, `P1278` LEI, `P11693` OSM relation, `P298` ISO 3166-1 alpha-3). Almost every canonical join key in `schema/join-keys.yaml` has a corresponding Wikidata property; the `join_key_fields` block above lists the major ones as `wdt:Pxxx` triples. Run a single SPARQL query to translate any registered identifier into a Q-ID, then pivot from the Q-ID to any other identifier the item carries.

`WIKIPEDIA_ARTICLE` slugs are exposed as `schema:about` sitelinks against the item, with language scoped by `schema:isPartOf <https://en.wikipedia.org/>` (or any other Wikipedia edition). Pair with OpenAlex (DOIs, ORCIDs, RORs) for scholarly joins, Wikipedia Pageviews for attention overlays, OpenStreetMap for geospatial joins, ClinicalTrials.gov / DailyMed / DrugBank for clinical and pharma joins, and Companies House / SEC EDGAR for corporate joins via LEI and CIK.

Federated queries are first-class: `SERVICE <endpoint>` can call out to the Wikimedia Commons Query Service, IDsMatch, OrthoDB, MeSH SPARQL, and a maintained list of external endpoints. This is what makes WDQS more than a static graph: agents can run a single SPARQL query that joins Wikidata facts against external SPARQL surfaces in one round trip.

## Access notes

**Endpoint:** `https://query.wikidata.org/sparql`. GET with `?query=<SPARQL>` and `Accept: application/sparql-results+json` (or pass `&format=json`). The web UI at `https://query.wikidata.org/` is a query playground over the same endpoint and exposes saved query templates.

**Scholarly subgraph:** `https://query-scholarly.wikidata.org/sparql` carves out the scholarly-works portion (papers, authors, citations) for faster queries against academic data. Use this instead of the main endpoint when your query only touches scholarly items, otherwise you compete with the rest of the graph for the 60s timeout.

**Timeouts and throttling:** hard 60-second query deadline. Long queries time out with a Blazegraph exception, not a 5xx. Public endpoint applies soft per-IP throttling; sustained queries above a few per second get progressively rate-limited. The Wikimedia User-Agent policy requires a descriptive `User-Agent` header naming the tool and a contact email; anonymous and generic UAs get blocked first when load spikes.

**Bulk:** full RDF dumps at `https://dumps.wikimedia.org/wikidatawiki/entities/` (Turtle and N-Triples, weekly, ~150 GB compressed) and JSON dumps in the same tree. For local SPARQL at scale, load the RDF dump into a private Blazegraph or Qlever instance rather than hammering WDQS. Wikimedia has signalled long-term plans to deprecate Blazegraph for WDQS in favour of Qlever or a successor; SPARQL surface and prefixes are expected to remain stable but client code that depends on Blazegraph-specific extensions (`bd:serviceParam`, label-service hints) should plan to migrate.

**Other access modes against the same data:** MediaWiki Action API (`wbgetentities` for up to 50 items per call), the Linked Data interface (content-negotiated entity URIs at `http://www.wikidata.org/entity/Q42`), the Wikibase REST API, and an emerging Wikibase GraphQL surface. WDQS is the right access mode when the query shape is structured (joins, filters, aggregations); fall back to the Action API for high-throughput single-entity fetches.

**Gotchas:**

- The `label-service` (`wikibase:label`) must be the last pattern in a query block, otherwise it silently returns no labels.
- Property paths over large fan-outs (`wdt:P31/wdt:P279*`) blow the 60s budget fast; constrain with selective triples first.
- Statement-level qualifiers and references live under `p:` / `ps:` / `pq:` / `pr:` prefixes, not `wdt:`. Truthy statements via `wdt:` skip deprecated and non-preferred ranks.
- Coordinates use `wdt:P625` and resolve to `geo:wktLiteral`; pair with `wikibase:geoSPARQL` extensions for spatial filtering.
- License is CC0 for the structured data; the Foundation asks attribution as a courtesy.

## MCP / connector notes

MCP coverage is community, not official from Wikimedia.

- `wmde/WikidataMCP` (Python, 25 stars, Wikimedia Deutschland) is the closest to an official-leaning MCP: read-only, wraps SPARQL execution, entity fetch, and external-identifier resolution. Lightweight surface, easy to deploy.
- `cyanheads/wikidata-mcp-server` (TypeScript, STDIO and Streamable HTTP) is the most feature-complete community option, with search, entity fetch, SPARQL execution, label resolution, identifier mapping, and dump-aware fallbacks. Useful when running outside Python.
- `ebaenamar/wikidata-mcp` and several smaller forks exist; lower maturity, narrower coverage.

A good MCP surface for this source: `sparql_query(query, language)`, `get_entity(qid, languages)`, `resolve_identifier(scheme, value)` (DOI to QID, ORCID to QID, NCT to QID, etc.), `get_external_ids(qid)`, `search_entities(text, type)`, `federated_sparql(query)` with allow-list of approved federation endpoints. The connector should pre-inject standard prefixes (`wd`, `wdt`, `p`, `ps`, `pq`, `wikibase`, `bd`, `schema`), set a configurable User-Agent, route scholarly-only queries to `query-scholarly.wikidata.org`, chunk over the 60s timeout via `LIMIT` + `OFFSET`, and fall back to RDF-dump-backed local indexes for queries that consistently time out.

## Review notes

`domain: government-open-data` is a workable fit but not a precise one. Wikidata is a community-curated CC0 knowledge graph, not government data, and functions as a cross-domain identifier hub touching academic, clinical-biotech, bio-genomics, corporate-registry, consumer-signal, geospatial, and news-events. SCHEMA.md and SKILL.md mention a `source-discovery` domain but the schema enum and `entries/` folders do not contain it; if `source-discovery` lands as a real domain, Wikidata is a natural reclassification target. Alternative reasonable placements: `consumer-signal` (alongside `wikipedia-pageviews`) or a new `cross-domain` / `knowledge-graph` domain. Flagging for human review rather than picking silently.

Potential new join keys for review:

- `WIKIDATA_PROPERTY_ID` (entity type `wikidata_property`, pattern `^P[0-9]+$`). Cross-source utility low today, but if more sources start emitting Wikidata property URIs as their own canonical metadata (some catalogues already do), worth registering.
- `WIKIDATA_LEXEME_ID` (entity type `lexeme`, pattern `^L[0-9]+$`). Useful for lexicographic and NLP sources; skip unless a second source lands.

Access test executed: `curl` against `query.wikidata.org/sparql` with a small SPARQL query returned HTTP 200 and the expected `head.vars` + `results.bindings` shape.

OSM_ID properties on Wikidata are split by object type (`P11693` OSM relation, `P10689` OSM way, `P402` OSM relation for territorial entities); the OSM_ID join-key registry entry recommends storing the type prefix (`relation/146268`), so the connector should reassemble `relation/<id>` from the property used rather than emitting bare numeric IDs.
