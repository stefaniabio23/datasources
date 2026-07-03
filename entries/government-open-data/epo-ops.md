---
id: epo-ops
name: EPO Open Patent Services (OPS)
domain: government-open-data
entry_kind: registry
description: European Patent Office REST API for worldwide patent bibliographic, legal-status, full-text, image, family, and classification data.
homepage_url: https://www.epo.org/en/searching-for-patents/data/web-services/ops
docs_url: https://developers.epo.org/
type:
  - rest-api
auth_required: oauth
cost: free-with-registration
license: EPO-OPS-Fair-Use
rate_limit: "non-paying tier: ~3.5 GB traffic/week; per-request throttling enforced via Fair Use charter (X-Throttling-Control header)"
bulk_available: false
frequency: weekly
lag: "days-to-weeks for newly published patents; DOCDB/INPADOC refreshed weekly"
geography: [global]
join_keys: []
primary_keys:
  - EPODOC_PUBLICATION_NUMBER
  - DOCDB_PUBLICATION_NUMBER
  - EPO_APPLICATION_NUMBER
  - INPADOC_FAMILY_ID
  - PRIORITY_NUMBER
  - CPC_CODE
  - IPC_CODE
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - "github.com/JIBSN/epo-ops-mcp-server"
  - "patent-connector (patent.dev, beta)"
mcp_notes: >
  Community MCP servers wrap the published-data and search endpoints. Connector must
  own the OAuth2 client-credentials flow (token refresh + expiry), CQL query building
  for search, XML-to-structured parsing, and Fair Use quota accounting.
agent_use_cases:
  - prior-art search
  - patent family lookup
  - legal-status monitoring
  - CPC/IPC classification retrieval
  - patent full-text and citation extraction
access_test:
  command: "curl -sf -X POST 'https://ops.epo.org/3.2/auth/accesstoken' -H 'Authorization: Basic ${OPS_BASIC_AUTH}' -H 'Content-Type: application/x-www-form-urlencoded' -d 'grant_type=client_credentials'"
  expected_status: 200
  expected_fields: [access_token, token_type, expires_in]
last_verified: 2026-07-02
build_priority: medium
notes: "access_test not executed; requires ${OPS_BASIC_AUTH} = base64(consumer_key:consumer_secret) from a free EPO developer-portal registration."
---

# EPO Open Patent Services (OPS)

## Why this source matters

OPS is the European Patent Office's REST API over its worldwide patent databases: DOCDB bibliographic data (100+ patent authorities), INPADOC legal-status and extended patent families, EP full-text, and patent images. It is the canonical programmatic route to official patent data, the same corpus behind Espacenet. For an agent, one credential set covers prior-art search, family resolution, legal-status tracking, and CPC/IPC classification lookups across global patents. Secondary domain: academic (patents are a prior-art and innovation-research corpus that joins to scholarly literature via applicant/inventor and citation graphs). Run by the EPO, an intergovernmental organisation of 39 member states.

## Agent use cases

- prior-art search
- patent family lookup
- legal-status monitoring
- CPC/IPC classification retrieval
- patent full-text and citation extraction

## Join strategy

OPS exposes no identifier that is currently in the canonical registry, so `join_keys` is empty. Its entire identifier surface is patent-native and lives in `primary_keys`: publication numbers in EPODOC (`EP1000000A1`) and DOCDB (`EP.1000000.A1`) formats, application numbers, priority numbers, the INPADOC family id (the load-bearing cross-patent join, groups all publications of one invention worldwide), and CPC/IPC classification symbols. These are strong cross-source join candidates for any patent-aware registry but are not yet canonical here, so all are flagged below rather than invented into `join_keys`. Applicant and inventor names are free-text (no ORCID/ROR/LEI normalisation), so entity linking to corporate-registry or academic sources is fuzzy-match only until the EPO adds standardised applicant IDs.

## Access notes

Register a free account on the EPO developer portal (developers.epo.org), create an app under the Non-paying access method, and collect the OAuth2 consumer key + secret. Mint a bearer token by POSTing `grant_type=client_credentials` to `https://ops.epo.org/3.2/auth/accesstoken` with HTTP Basic auth `base64(key:secret)`; tokens expire in ~20 minutes and must be refreshed. Data endpoints hang off `https://ops.epo.org/3.2/rest-services/`, e.g. `published-data/publication/epodoc/EP1000000/biblio`, `family/publication/docdb/<num>`, `legal/...`, `classification/cpc/...`, and `published-data/search` (CQL query syntax). Responses are XML by default (`Accept: application/json` is supported on many resources). Free tier allows roughly 3.5 GB of traffic per week; the `X-Throttling-Control` response header signals per-service throttle state (green/yellow/red), respect it and the Fair Use charter. OPS itself is API-only; the EPO ships separate bulk data products (DOCDB, INPADOC, CPC master files) outside OPS.

## MCP / connector notes

Community MCP servers exist (`github.com/JIBSN/epo-ops-mcp-server` exposing `get_published_data` / `search_published_data`; the Patent Connector beta at patent.dev). None official. A robust connector must abstract: the OAuth2 client-credentials token lifecycle (fetch, cache, refresh on 401), CQL query construction for `published-data/search`, EPODOC-vs-DOCDB number normalisation, XML parsing into structured records, family and legal-status graph traversal, and Fair Use quota accounting from `X-Throttling-Control`. Suggested surface: `search_patents`, `get_biblio`, `get_family`, `get_legal_status`, `get_classification`, `get_fulltext`.

## Review notes

None of the join-key hints supplied (patent publication number, INPADOC family, CPC) exist in `schema/join-keys.yaml`. Flagging all as new canonical-key candidates; none invented into `join_keys`.

Potential new join keys for review:

- PATENT_PUBLICATION_NUMBER
  - Entity type: patent_publication
  - Pattern: EPODOC/DOCDB, e.g. `^[A-Z]{2}[0-9]+[A-Z0-9]*$` (country prefix + serial + kind code); note EPODOC (`EP1000000A1`) vs DOCDB (`EP.1000000.A1`) formatting split
  - Other datasets that would use it: Espacenet, USPTO PatentsView, Google Patents Public Data, Lens.org, PATSTAT
- PATENT_APPLICATION_NUMBER
  - Entity type: patent_application
  - Pattern: authority-specific; EPODOC/DOCDB application-number formats
  - Other datasets that would use it: USPTO, WIPO PATENTSCOPE, PATSTAT
- INPADOC_FAMILY_ID
  - Entity type: patent_family
  - Pattern: numeric INPADOC extended-family id
  - Other datasets that would use it: Espacenet, PATSTAT, Google Patents, Lens.org
- CPC_CODE
  - Entity type: patent_classification
  - Pattern: `^[A-H|Y][0-9]{2}[A-Z][0-9]{1,4}/[0-9]{2,6}$` (Cooperative Patent Classification symbol)
  - Other datasets that would use it: USPTO, Google Patents, Lens.org, WIPO
- IPC_CODE
  - Entity type: patent_classification
  - Pattern: `^[A-H][0-9]{2}[A-Z][0-9]{1,4}/[0-9]{2,6}$` (International Patent Classification)
  - Other datasets that would use it: WIPO, USPTO, PATSTAT

License flag: EPO OPS data has no SPDX identifier. Used a proposed canonical short name `EPO-OPS-Fair-Use` (free reuse of patent data subject to the EPO Fair Use charter and OPS terms of use, attribution expected). Confirm/rename before merge.
