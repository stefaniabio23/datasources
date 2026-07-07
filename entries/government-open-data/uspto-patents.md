---
id: uspto-patents
name: USPTO Open Data Portal (Patents)
domain: government-open-data
entry_kind: registry
description: US Patent and Trademark Office's Open Data Portal, the successor to the PatentsView Search API and PEDS, covering all granted US patents and published applications with disambiguated assignee/inventor data, CPC/USPC classification, citations, and full prosecution (Patent File Wrapper) records.
homepage_url: https://data.uspto.gov
docs_url: https://data.uspto.gov/apis/getting-started
type:
  - rest-api
  - bulk-download
  - web-ui
auth_required: api-key-free
cost: free-with-registration
license: US-Government-Public-Domain
rate_limit: "per-key throttling on the ODP APIs; specific quotas published per API in the catalog"
bulk_available: true
frequency: "daily refresh for Patent File Wrapper; granted patents weekly (Tuesday grant cycle)"
lag: "days for prosecution events into PFW; weekly for new grants"
geography: [US]
join_keys:
  - PATENT_PUBLICATION_NUMBER
  - CPC_CODE
primary_keys:
  - US_PATENT_NUMBER
  - US_APPLICATION_NUMBER
  - USPTO_ASSIGNEE_ID
  - USPTO_INVENTOR_ID
mcp_status: mcp-needed-high-value
mcp_maturity: none
mcp_notes: >
  No official MCP. The legacy PatentsView Search API (api.patentsview.org) shut down
  2026-03-20 and now returns HTTP 410 Gone; all access has moved to the ODP APIs at
  data.uspto.gov, which require a free API key (MyODP) plus a USPTO.gov account sign-in
  (account requirement added 2026-06-18). Any connector must be built against the ODP
  surface, not PatentsView. Suggested surface: search_patents, get_patent, search_applications,
  get_file_wrapper, search_by_assignee, get_continuity. Endpoint paths MUST be re-verified
  against the live ODP catalog before coding.
agent_use_cases:
  - patent prior-art and prosecution lookup
  - assignee patent-portfolio diligence
  - inventor career and co-inventor mapping
  - drug-patent identification for Orange Book linkage
  - technology-area scan by CPC classification
notes: "API endpoint paths must be verified before coding: legacy PatentsView Search API shut down 2026-03-20 (api.patentsview.org returns HTTP 410); data now flows through the USPTO Open Data Portal, which requires a free MyODP API key and (from 2026-06-18) a USPTO.gov account sign-in. access_test not yet executed; requires ${USPTO_ODP_API_KEY}."
last_verified: 2026-06-22
build_priority: high
---

# USPTO Open Data Portal (Patents)

## Why this source matters

The USPTO Open Data Portal (ODP) at `data.uspto.gov` is the canonical, free, public-domain source for US patent data, run by the US Patent and Trademark Office. It is the consolidation point that replaced both the PatentsView Search API (which shut down 2026-03-20) and the legacy Patent Examination Data System (PEDS). It covers every granted US patent and every published US application, with USPTO-disambiguated assignee and inventor entities, CPC and USPC classification, patent-to-patent citations back to 1976, and the full Patent File Wrapper (PFW) of prosecution history and continuity relationships. For an agent, this is the system of record for "who owns / invented / cites what" in US patents. Secondary domains: corporate-registry (assignees are companies, so the portfolio view supports company diligence) and clinical-biotech (US patent numbers listed in the FDA Orange Book identify the drug patents protecting an approved product).

## Agent use cases

- patent prior-art and prosecution lookup
- assignee patent-portfolio diligence
- inventor career and co-inventor mapping
- drug-patent identification for Orange Book linkage
- technology-area scan by CPC classification

## Join strategy

None of the patent-specific identifiers ODP mints are in the canonical join-key registry yet, so `join_keys` is empty. The source-native identifiers (in `primary_keys`) are:

- `US_PATENT_NUMBER` — the granted-patent number. This is the highest-value cross-source identifier: the FDA Orange Book lists patents protecting an approved drug by patent number, so a US patent number joins the existing `fda-orange-book` entry to its listed patents. Flagged below for registry review.
- `US_APPLICATION_NUMBER` — the application serial number; the key into the Patent File Wrapper and the link between a publication and its eventual grant.
- `USPTO_ASSIGNEE_ID`, `USPTO_INVENTOR_ID` — USPTO-disambiguated entity identifiers (carried over conceptually from PatentsView's disambiguation work). Source-internal; useful for resolving the same company or person across many filings, but not yet a cross-source canonical key.

There is no native US patent-family identifier. A patent family must be reconstructed from the continuity data in the PFW (parent/child/continuation/divisional links), not read off a single field. Agents needing INPADOC- or DOCDB-style families should layer EPO OPS or a commercial family source on top.

If `US_PATENT_NUMBER` is promoted to a canonical join key, populate `join_keys` and `join_key_fields` on both this entry and `fda-orange-book` in the same change.

## Access notes

**Base:** the ODP APIs are served from `data.uspto.gov` (catalog at `https://data.uspto.gov/apis`). HTTP GET/POST, JSON responses.

**Auth:** a free API key is required. Get it from MyODP (`https://data.uspto.gov/myodp`); from 2026-06-18 obtaining a key also requires a USPTO.gov account sign-in (identity-verified, ID.me-linked). Inject the key at runtime, do not inline it: `curl -H "X-API-KEY: ${USPTO_ODP_API_KEY}" ...`. The exact header name and endpoint paths must be confirmed against the live catalog before any coding (see Review notes).

**Coverage detail:** the Patent File Wrapper (the PEDS successor) holds publicly available application bibliographic/front-page and patent-related fields filed from January 2001 to present, refreshed daily. Granted patents follow the weekly Tuesday grant cycle. Citations are available from 1976.

**Verify freshness:** PFW is refreshed daily; confirm currency by checking the most recent prosecution-event date on a recently active application, or the latest grant date against the current week's grant cycle.

**Migration gotcha:** any code or docs pointing at `api.patentsview.org` is dead. That host now 301-redirects to the ODP transition guide and the old endpoints return HTTP 410 Gone. Treat PatentsView field names as a rough guide only; ODP response shapes differ.

**Bulk:** full datasets are downloadable from the portal (and the legacy bulk-data products at `bulkdata.uspto.gov` for full-text grant/application XML). Use bulk for any large portfolio or full-corpus scan; the API is for targeted lookups.

## MCP / connector notes

No MCP exists. High-value target: patent prior-art, company-IP-diligence, and drug-patent agents are an overlapping audience, and the ODP APIs return verbose nested JSON that is a poor fit for a context window. Suggested surface: `search_patents` (by keyword, assignee, CPC, date), `get_patent` (trimmed bibliographic payload), `search_applications`, `get_file_wrapper` (prosecution + continuity for one application), `search_by_assignee`, `get_continuity` (family reconstruction helper). The connector must hold the API key, paginate behind the scenes (PFW web extraction caps at 3,000 records per pull), and reconstruct families from continuity links since there is no native family field. Critically, the endpoint paths must be pinned against the live ODP catalog at build time because the PatentsView shutdown is recent and the ODP surface is still settling.

## Review notes

- **Potential new join key for review: `US_PATENT_NUMBER`**
  - Entity type: `granted_patent`
  - Pattern: US grant numbers are messy (utility 7-8 digits, plus design `D`, plant `PP`, reissue `RE`, and other prefixes); a strict regex is not advisable, suggest a normalized-string form.
  - Other datasets that would use it: the existing `fda-orange-book` entry lists drug patents by patent number (`Patent_No`); this would create a direct USPTO-patent to FDA-approval bridge. EPO OPS and Google Patents also key on US patent numbers.
  - This is the single highest-value join this entry would unlock. Recommend prioritising it for a `schema/join-keys.yaml` PR.
- `US_APPLICATION_NUMBER` and `USPTO_ASSIGNEE_ID` could also warrant registration if more patent-adjacent sources land in the directory; lower priority for now.
- API endpoint paths and the auth header name were NOT executed against the live API (key + USPTO.gov account required). The PatentsView shutdown and ODP account-sign-in requirement are verified via the 301 redirect from `api.patentsview.org` to the ODP transition guide and USPTO subscription-center announcements; the exact ODP request shape must be verified before any connector is coded.
