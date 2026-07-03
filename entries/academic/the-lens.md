---
id: the-lens
name: The Lens
domain: academic
entry_kind: knowledge-graph
description: Integrated scholarly-and-patent knowledge graph linking ~200M scholarly records to global patent documents, biological sequences, and patent-to-paper citations.
homepage_url: https://www.lens.org/
docs_url: https://docs.api.lens.org/
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: account-required
cost: freemium
license: Lens-Terms-of-Use
rate_limit: "plan-dependent; per-minute + per-month request and record quotas; see x-rate-limit-remaining-request-per-minute response header"
bulk_available: true
geography: [global]
join_keys:
  - DOI
  - PMID
  - PMCID
  - MAG_ID
  - ORCID
  - ISSN
primary_keys:
  - LENS_ID
join_key_fields:
  - join_key: DOI
    fields:
      - "external_ids[type=doi].value"
  - join_key: PMID
    fields:
      - "external_ids[type=pmid].value"
  - join_key: PMCID
    fields:
      - "external_ids[type=pmcid].value"
  - join_key: MAG_ID
    fields:
      - "external_ids[type=magid].value"
  - join_key: ORCID
    fields:
      - "authors.ids[type=orcid].value"
  - join_key: ISSN
    fields:
      - "source.issn.value"
mcp_status: mcp-needed-high-value
agent_use_cases:
  - patent search
  - patent-to-paper citation linkage
  - technology-landscape mapping
  - biological sequence lookup in patents
  - scholarly literature search
access_test:
  command: "curl -sf -H \"Authorization: Bearer ${LENS_API_TOKEN}\" 'https://api.lens.org/scholarly/search?query=title:CRISPR&size=1'"
  expected_status: 200
  expected_fields: [total, data, results]
last_verified: 2026-07-02
build_priority: medium
notes: "access_test not yet executed; requires ${LENS_API_TOKEN} bearer token issued per approved API plan."
---

# The Lens

## Why this source matters

The Lens (operated by Cambia, a non-profit) serves an integrated scholarly-and-patent knowledge graph as a public good. It harmonises over 200M scholarly records (from Microsoft Academic, PubMed, Crossref, plus open-access data and ORCID) and the full global patent corpus, then cross-links them: PatCite maps which patents cite which papers, and PatSeq extracts biological sequences disclosed in patents. That patent-to-scholarship bridge is the reason to reach for The Lens over a pure scholarly graph like OpenAlex. It is the cleanest free-tier path to answer "which patents cite this research" or "what does the IP landscape around this technology look like". Secondary relevance to `clinical-biotech` (PatSeq biological-sequence search over patents).

## Agent use cases

- patent search
- patent-to-paper citation linkage
- technology-landscape mapping
- biological sequence lookup in patents
- scholarly literature search

## Join strategy

Scholarly records normalise external identifiers into a typed `external_ids` array exposing `DOI`, `PMID`, `PMCID`, and `MAG_ID`, with `ORCID` on authors and `ISSN` on the source venue. These make The Lens joinable against OpenAlex, Crossref, Europe PMC, and PubMed on the same canonical keys.

The Lens mints its own `LENS_ID` (e.g. `100-004-910-081-14X`) as the stable primary key for every scholarly work AND every patent document; it is source-internal (like OpenAlex's work IDs) and kept out of the canonical registry, so use it for direct Lens lookups rather than cross-source joins.

Patent records carry no registry-canonical join key today. The high-value patent identifiers (patent publication number, and the INPADOC `family_id`) are flagged as new-key candidates in Review notes; until they are registered, patents join to scholarly works only indirectly via NPL (non-patent-literature) citations resolved back to `DOI`/`PMID`.

## Access notes

Hit `[GET] https://api.lens.org/scholarly/search` (or `/patent/search`) with a bearer token, or fetch a single record via `/scholarly/{lens_id}` and `/patent/{lens_id}`. Token goes in the `Authorization: Bearer` header (POST) or a `token=` query param (GET); request it from the Lens user profile. Access tiers: a free 14-day non-commercial trial, a free Institutional User plan for users with an institution email under an active Institutional Toolkit subscription, and paid custom plans for higher volume, automation, or commercial use (individual commercial-use agreement is $1,000 USD/year). Rate limits are plan-dependent, enforced per-minute and per-month on both requests and records; check `x-rate-limit-remaining-request-per-minute` and the `/subscriptions/*/usage` endpoints. Bulk downloads are available on higher tiers. Data reuse follows Lens terms modelled on CC BY-NC-SA, and requires retaining `LENS_ID` values in any redistribution.

## MCP / connector notes

No MCP exists for Lens.org (GitHub/npm "lens-mcp" results are all for the unrelated web3 Lens Protocol). High value: patent-to-scholarship linkage overlaps the audience of several academic and clinical-biotech entries, and no free source replicates PatCite/PatSeq. Suggested surface: `search_scholarly`, `search_patents`, `get_record` (by `lens_id`), `get_patent_citations` (NPL + patent-to-patent), `patseq_sequence_lookup`. The connector must abstract over the typed `external_ids[type=...].value` array (flatten to top-level `doi`/`pmid`), inject the bearer token, and track the per-minute/per-month quota headers so agents can throttle before hitting 429.

## Review notes

- License: `Lens-Terms-of-Use` is a new canonical short name (not yet in SCHEMA.md § License conventions). The Lens describes reuse as "similar to CC BY-NC-SA" but adds custom obligations (retain `LENS_ID` on redistribution) and a separate commercial-use agreement, so it is not literally CC-BY-NC-SA-4.0. Confirm the short name or map to an SPDX code before merge.
- Potential new join key for review: `PATENT_PUBLICATION_NUMBER`
    Entity type: patent_publication
    Pattern: jurisdiction (ISO-2) + doc number + kind code, e.g. `US_10000000_B2` / `EP_1000000_A1` (also expressed as `country` + `doc_number` + `kind`)
    Other datasets that would use it: Google Patents, USPTO PatentsView, EPO OPS, Espacenet, PATSTAT
- Potential new join key for review: `INPADOC_FAMILY_ID`
    Entity type: patent_family
    Pattern: numeric INPADOC/DOCDB simple-family identifier (Lens exposes as `family_id`)
    Other datasets that would use it: EPO OPS, PATSTAT, USPTO PatentsView, Google Patents
- `coreid` (CORE repository identifier) and NPL-citation linkage are additional lower-value candidates; not flagged for registry addition yet.
- `auth_required` set to `account-required` because even the free tiers require an account plus an approved, plan-scoped bearer token (no anonymous API access); revisit if an `api-key-free`-style anonymous key is ever offered.
