---
id: who-flunet
name: WHO FluNet
domain: public-health
entry_kind: time-series
description: WHO global influenza surveillance combining weekly reports from ~150 National Influenza Centres into a unified view of virological detections, subtype distribution, and positivity rates.
homepage_url: https://www.who.int/tools/flunet
docs_url: https://www.who.int/tools/flunet
type:
  - powerbi-export
  - web-ui
  - bulk-download
auth_required: none
cost: free
license: CC-BY-NC-SA-3.0-IGO
rate_limit: "not published; dashboard is public, CSV exports are direct download"
bulk_available: true
frequency: weekly
lag: "~1-2 weeks behind reporting week"
geography: [global]
join_keys:
  - ISO_3
  - DATE
primary_keys:
  - WHO_REGION_CODE
  - WHO_HEMISPHERE
  - INFLUENZA_TYPE_SUBTYPE
join_key_fields:
  - join_key: ISO_3
    fields: [Country_code_iso3, ISO3]
  - join_key: DATE
    fields: [ISO_WEEKSTARTDATE, ISO_YEAR, ISO_WEEK]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Narrow audience (public-health analysts, virology researchers, infectious-disease forecasters).
  Power BI dashboard is not directly REST-callable; an MCP would wrap the CSV export workflow
  or sit on top of the underlying GISRS data feed. Suggested surface: get_country_week,
  get_subtype_distribution, get_hemisphere_trend, get_country_peak_weeks.
agent_use_cases:
  - global flu surveillance tracking
  - flu strain mix monitoring
  - hemisphere-level seasonality analysis
  - public-health early warning
  - pandemic readiness intelligence
last_verified: 2026-06-08
build_priority: low
notes: "Power BI dashboard URL is the canonical public view; underlying programmatic access is via the WHO Surveillance and Monitoring System (GISRS) portal. WHO migrates these properties periodically; verify the URL before automating."
---

# WHO FluNet

## Why this source matters

The only consolidated global view of influenza activity. Aggregates weekly reports from ~150 WHO-recognised National Influenza Centres into a single dashboard with country-level virological detections, type and subtype breakdown (A/H1N1pdm09, A/H3N2, B/Victoria, B/Yamagata, not-determined), specimens processed, and positivity rate. Coverage extends back to ~1995. For agents doing global respiratory-virus surveillance, FluNet is the cross-country anchor that makes hemisphere comparisons, strain-dominance tracking, and peak-week forecasting possible. Pair with CDC FluView for US detail and UKHSA respiratory surveillance for UK detail.

## Agent use cases

- global flu surveillance tracking
- flu strain mix monitoring
- hemisphere-level seasonality analysis
- public-health early warning
- pandemic readiness intelligence

## Join strategy

`ISO_3` (country) and `DATE` (ISO week-start) are the registry-backed keys. The CSV export typically labels them `Country_code_iso3` and `ISO_WEEKSTARTDATE` (alongside `ISO_YEAR`, `ISO_WEEK`); confirm the current column names before joining.

WHO-internal keys (`WHO_REGION_CODE`, `WHO_HEMISPHERE`, `INFLUENZA_TYPE_SUBTYPE`) are not in the canonical registry. They are useful within FluNet but not for cross-source joins.

Common pairings: CDC FluView for US weekly detail (MMWR-week-based), UKHSA respiratory surveillance for UK detail, ECDC ERVISS for EU, OpenAlex for the flu-research literature side.

## Access notes

Canonical entry point: the Power BI dashboard at `https://app.powerbi.com/view?r=eyJrIjoiNjViM2Y4NjktMjJmMC00Y2NjLWFmOWQtODQ0NjZkNWM1YzNmIiwidCI6ImY2MTBjMGI3LWJkMjQtNGIzOS04MTBiLTNkYzI4MGFmYjU5MCIsImMiOjh9`. The Power BI "Download / Export data" option yields a CSV of the underlying weekly counts. No auth.

For programmatic access without scraping the Power BI viewer, the underlying GISRS data feed is published via the WHO Surveillance and Monitoring System portal with bulk CSV exports.

Gotchas:

- The dashboard CSV export reflects the current filter state, not the full dataset. Clear filters before exporting if you want everything.
- Country reporting is voluntary; gaps in low-resource regions can be large.
- Subtype labels evolve as new strains emerge; expect schema drift over multi-year analyses.
- Power BI viewer endpoints are not stable for direct scraping; the JS-rendered DOM can change without notice.

## MCP / connector notes

No MCP. Narrow audience but a real one. A connector would need to either wrap the CSV-export workflow on the Power BI dashboard or sit on the GISRS data feed. Suggested surface: `get_country_week(iso3, year, week)`, `get_subtype_distribution(year, hemisphere)`, `get_hemisphere_trend(season, hemisphere)`, `get_country_peak_weeks(iso3, season)`.

## Review notes

None.
