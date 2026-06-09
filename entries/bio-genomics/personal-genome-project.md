---
id: personal-genome-project
name: Personal Genome Project
domain: bio-genomics
entry_kind: registry
description: Open-consent global network of participant-driven projects publishing whole-genome sequences, genotyping arrays, phenotype surveys, microbiome, and health records under a CC0-equivalent public-domain dedication.
homepage_url: https://www.personalgenomes.org/
docs_url: https://my.pgp-hms.org/public_genetic_data
type:
  - web-ui
  - bulk-download
  - scraper-required
auth_required: none
cost: free
license: CC0-1.0
bulk_available: true
frequency: irregular
lag: "Updated when new participants enrol or upload data; no fixed cadence"
geography: [USA, CAN, GBR, AUT, CHN, global]
join_keys:
  - URL
primary_keys:
  - PGP_HU_ID
  - PGP_LEGACY_ID
join_key_fields:
  - join_key: URL
    fields: ["/profiles/public?hex={PGP_HU_ID}", "/user_file/download/{file_id}"]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  No public API. A connector would have to scrape the participant directory and the
  public_genetic_data table on my.pgp-hms.org, enumerate /user_file/download/{id}
  links, and normalise participant hex IDs across the five member sites. Demand is
  narrow (open-consent genomics researchers, citizen-science tooling) so this is
  low-value but technically tractable.
agent_use_cases:
  - retrieve open-consent whole-genome and genotyping data for benchmarking
  - cross-reference genotype with self-reported phenotype and trait surveys
  - assemble an open-license cohort for variant-calling or imputation pipelines
  - link consumer DTC genotyping formats (23andMe, AncestryDNA) to research-grade VCF
  - identify open-data participants for re-contact-style citizen-science studies
access_test:
  command: "curl -sfI 'https://my.pgp-hms.org/public_genetic_data'"
  expected_status: 200
last_verified: 2026-06-09
build_priority: low
notes: "Five member projects under the Personal Genome Project Global Network umbrella (Harvard, Canada, UK, Austria, China). Each runs its own portal; Harvard PGP at my.pgp-hms.org is the canonical and largest data surface. No machine-readable API; scraping the public_genetic_data table is currently the only programmatic access path."
---

# Personal Genome Project

## Why this source matters

The Personal Genome Project is an open-consent research framework started by George Church's lab at Harvard Medical School in 2005, with sister projects at the University of Toronto + Hospital for Sick Children (PGP Canada, 2012), University College London (PGP UK, 2013), CeMM in Vienna (Genom Austria, 2014), and Fudan University in Shanghai (PGP China, 2017). Governance sits with the Open Humans Foundation, a US 501(c)(3). The network's distinguishing move is the consent model: participants accept identifiability and waive de-identification guarantees, and in return their genome, exome, array data, microbiome, trait surveys, and (in many cases) full medical records are published under a CC0-equivalent public-domain dedication. Harvard PGP alone reports roughly 6,200 participant profiles, 796 whole-genome sequences, and 3,179 other genetic datasets publicly downloadable, plus 4,142 deposited tissue samples. For an agent, the value is open-licensed paired genotype + phenotype data that does not require a DARS or controlled-access application, which is rare in human genomics.

## Agent use cases

- retrieve open-consent whole-genome and genotyping data for benchmarking
- cross-reference genotype with self-reported phenotype and trait surveys
- assemble an open-license cohort for variant-calling or imputation pipelines
- link consumer DTC genotyping formats (23andMe, AncestryDNA) to research-grade VCF
- identify open-data participants for re-contact-style citizen-science studies

## Join strategy

PGP exposes very few canonical join keys. The reliable bridge is `URL`: every participant profile and every data file has a stable web address (`my.pgp-hms.org/profiles/public?hex=hu5D9DE3`, `my.pgp-hms.org/user_file/download/4217`) that can be cited from other notes or registries. The load-bearing identifiers are project-internal and intentionally outside the canonical registry: the hex participant ID (`hu5D9DE3`, `hu375852`) used across Harvard PGP, and the legacy three-to-four-digit PGP number (`PGP148`) still surfaced in the directory for early enrolees. PGP Canada, PGP UK, Genom Austria, and PGP China each mint their own ID-space, with no global cross-walk published. Pair with NCBI SRA / ENA when participants have also deposited raw reads there (some do; not all), and with `bio-genomics` reference sources (Ensembl, ClinVar, gnomAD) to annotate variants called from PGP VCFs. Pair with the `consumer-signal` domain when working with the 23andMe/AncestryDNA raw exports that participants upload alongside research-grade data. See review notes for proposed canonical IDs.

## Access notes

**Primary surface (Harvard PGP):** `https://my.pgp-hms.org/public_genetic_data` lists every public file with type, size, and a `/user_file/download/{id}` link. File IDs are dense integers, file sizes range from a few KB (23andMe/Ancestry text dumps) up to ~112 GB (uncompressed WGS BAM). Formats include VCF, BAM, CRAM/CRAI, FASTQ, 23andMe raw text, AncestryDNA raw text, Complete Genomics TSV, Illumina, biometric CSV, medical records (PDF/XML), and DICOM imaging.

**Participant directory:** `https://my.pgp-hms.org/users` is a paginated HTML table; each row links to `/profiles/public?hex=huXXXXXX` with sample-type tags, enrolment date, dataset counts.

**Genome reports:** `https://evidence.personalgenomes.org/genomes` (GET-Evidence) holds curated variant interpretations layered over the same participant set.

**Other member projects:** PGP Canada (`personalgenomes.ca`), PGP UK (`personalgenomes.org.uk`), Genom Austria (`genomaustria.at`), PGP China (`pgpchina.org`). Each runs an independent portal; data volumes are materially smaller than Harvard PGP.

**No API.** No documented REST endpoint, no JSON dump, no robots-respected sitemap of the public_genetic_data table. Bulk access today means HTML scraping the table and then issuing direct `/user_file/download/{id}` GETs. Be polite; the site is run by a non-profit.

**License nuance.** The network policy is "Public Data shared via CC0 waiver or equivalent". Recorded as `CC0-1.0` in YAML because that is the operative public-domain dedication; downstream re-publication should still credit PGP and respect the original consent framing (participants accepted identifiability; researchers should not strip that context).

## MCP / connector notes

No MCP exists. A useful connector surface would be small and scrape-backed: `list_participants(site, page)`, `get_participant(hex_id)` returning the profile JSON plus an enumeration of public files, `list_public_files(data_type, format)`, `download_file(file_id)` for the `/user_file/download/{id}` URLs, and a `resolve_pgp_id(hex_or_legacy)` helper that handles the `hu5D9DE3` and `PGP148` forms. The hardest abstraction is cross-site identity: the five member portals run independent ID-spaces, so any cross-network connector either treats them as five distinct sources or maintains a hand-curated mapping. Marked `mcp-needed-low-value` because the audience is narrow (open-consent genomics, citizen-science), but the connector would be straightforward.

## Review notes

Potential new join keys for review (would be reusable across PGP, Open Humans, and any future open-consent participant-driven cohort):

```
Potential new join key for review: PGP_HU_ID
  Entity type: open_consent_participant
  Pattern: ^hu[0-9A-F]{6}$
  Other datasets that would use it: Harvard PGP, Open Humans Foundation member projects, downstream papers re-using PGP data
```

Other items for human attention before merge:

- `geography` includes `global` plus member-project country codes; the network is global but each member project is country-scoped. Left both forms so an agent can filter either way.
- `access_test` exercises only Harvard PGP's `/public_genetic_data` HEAD; the four sister portals are not pinged. Adding per-site tests would inflate the entry without changing the freshness signal materially.
- License recorded as `CC0-1.0` based on the network's published "CC0 waiver or equivalent" policy. The per-file metadata on `my.pgp-hms.org` does not surface a machine-readable license tag, so a strict validator may want to downgrade this to `unknown` until the portal exposes per-file licensing.
- Secondary relevance to `consumer-signal` for the 23andMe / AncestryDNA raw uploads, and to `healthcare-claims` / `public-health` for the medical-record PDFs participants attach. Filed under `bio-genomics` because the genome data is the primary draw.
- No entry yet for Open Humans Foundation (the governance body and a separate participant-data platform); a sibling entry would make sense once PGP is in.
