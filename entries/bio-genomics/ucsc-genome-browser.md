---
id: ucsc-genome-browser
name: UCSC Genome Browser
domain: bio-genomics
entry_kind: mixed
description: UCSC Genomics Institute's reference genome browser with assemblies, annotation tracks, and pairwise/multiple alignments for human, mouse, and thousands of other species, exposed via REST API, public MySQL, FTP, and Table Browser.
homepage_url: https://genome.ucsc.edu/
docs_url: https://genome.ucsc.edu/goldenPath/help/api.html
type:
  - rest-api
  - bulk-download
  - database
  - web-ui
auth_required: none
cost: free
license: MIT
rate_limit: "soft guidance ~1 req/sec to REST API; botDelay enforced server-side under load; MySQL servers throttle heavy queries"
bulk_available: true
frequency: "track-by-track; most reference tracks refresh on a months cadence, MySQL servers sync weekly Monday mornings Pacific"
lag: "weeks-to-months between upstream annotation release and inclusion in a UCSC track"
geography: [global]
join_keys:
  - GENE_SYMBOL
  - ENSEMBL_ID
  - RSID
  - ENTREZ_GENE_ID
  - DOI
primary_keys:
  - UCSC_ASSEMBLY_DB
  - UCSC_TRACK_NAME
  - UCSC_CHROM
join_key_fields:
  - join_key: GENE_SYMBOL
    fields: [knownGene.geneSymbol, refGene.name2, ncbiRefSeq.name2]
  - join_key: ENSEMBL_ID
    fields: [knownGene.name, knownToEnsembl.value, ensGene.name]
  - join_key: RSID
    fields: [snp151.name, dbSnp155.name]
  - join_key: ENTREZ_GENE_ID
    fields: [refGene.name, knownToLocusLink.value]
mcp_status: mcp-exists
mcp_maturity: community
mcp_package:
  - github.com/hlydecker/ucsc-genome-mcp
  - github.com/QuentinCody/ucsc-mcp-server
mcp_notes: >
  Two community MCPs wrap the REST API; neither official. Surface is small (findGenome, list,
  getData, search) so a clean connector is tractable. Track-name discovery and coordinate
  validation are the load-bearing pieces; payload trimming matters because getData responses
  can hit the 1M-item cap on dense tracks.
agent_use_cases:
  - assembly and track discovery
  - sequence retrieval by coordinate
  - annotation-track lookup for a region
  - cross-assembly coordinate liftOver
  - conservation and alignment scoring lookup
access_test:
  command: "curl -sf 'https://api.genome.ucsc.edu/list/ucscGenomes'"
  expected_status: 200
  expected_fields: [downloadTime, ucscGenomes]
last_verified: 2026-06-09
build_priority: medium
---

# UCSC Genome Browser

## Why this source matters

Reference genome browser run by the UCSC Genomics Institute, covering hundreds of vertebrate, invertebrate, viral, and microbial assemblies plus the GenArk hub set of thousands more. UCSC is the canonical home of liftOver chains, the Known Genes track, multi-species conservation scores (phyloP, phastCons), and curated regulatory, variation, and clinical genetics tracks layered over each assembly. Agents working on genomic coordinates, region annotation, cross-assembly mapping, or variant context should treat UCSC as the join point between sequence space and the rest of the annotation universe. Secondary relevance to `clinical-biotech` via ClinVar, DECIPHER, and OMIM tracks layered into the browser.

## Agent use cases

- assembly and track discovery
- sequence retrieval by coordinate
- annotation-track lookup for a region
- cross-assembly coordinate liftOver
- conservation and alignment scoring lookup

## Join strategy

UCSC is a coordinate-first source, so genomic ranges (`chrom`, `start`, `end`) are the natural join axis with any other genomic dataset. For entity-level joins it exposes `GENE_SYMBOL` (knownGene, refGene, ncbiRefSeq tracks), `ENSEMBL_ID` (ensGene track and the knownToEnsembl cross-reference table), `ENTREZ_GENE_ID` via the refGene `name` field and knownToLocusLink, and `RSID` via the dbSnp tracks. The DOI of the publication describing a track is generally referenced in track metadata under `pmid`/`doi` schema fields.

UCSC also mints source-internal identifiers worth tracking: the assembly database name (`hg38`, `mm39`, `hs1`), the track name within that assembly (`knownGene`, `dbSnp155`, `gencodeV44`), and the UCSC chromosome naming convention (`chr1` not `1`, `chrM` not `MT`). These travel together as a 3-tuple to uniquely identify a row in a UCSC track. The chr-vs-no-chr mismatch is the single most common cause of failed joins with Ensembl, GENCODE, and most VCF-based sources, plan for the rename.

Pair with Ensembl for richer gene model metadata, dbSNP / gnomAD for variant frequency, GENCODE for transcript-level Ensembl IDs, and GTEx for tissue expression at the same coordinates.

## Access notes

**Programmatic queries:** REST API at `https://api.genome.ucsc.edu/`. No auth, no api key. Start with `/list/ucscGenomes` to enumerate assemblies, then `/list/tracks?genome=hg38` for the track catalog, then `/getData/sequence` or `/getData/track` for the payload. Guidance is one request per second; the server enforces a botDelay under load and may temporarily block IPs that ignore it. Single requests cap at 1,000,000 items returned, segment by chromosome or coordinate window for dense tracks.

**Bulk and SQL:** Public MySQL at `genome-mysql.gi.ucsc.edu` (US) and `genome-euro-mysql.soe.ucsc.edu` (EU), port 3306, user `genome`, no password. Same data as the web browser, refreshed weekly on Monday mornings Pacific. FTP and HTTPS bulk downloads under `https://hgdownload.soe.ucsc.edu/goldenPath/<db>/` ship 2bit/FASTA sequences, BigBed, BigWig, MAF alignments, liftOver chain files, and per-track SQL dumps. The Table Browser at `https://genome.ucsc.edu/cgi-bin/hgTables` is the GUI on top of the same SQL backend, handy for ad-hoc filtered exports.

**License:** Data files and database tables are freely usable for any purpose, academic or commercial, with attribution to the original data contributors. Source-code license is MIT for most of the kent codebase; BLAT, isPCR, and the graphical browser CGIs (`kent/src/hg/*`) require a commercial licence from the Genome Browser Store for non-academic installation. Note that the LiftOver chain files themselves are restricted to non-commercial use, and some clinical-genetics tracks (HGMD, LOVD, OMIM) carry upstream licence terms that require obtaining the data directly from the original source.

## MCP / connector notes

Two community MCPs exist: `hlydecker/ucsc-genome-mcp` (Python, wraps the REST API, the more developed of the two) and `QuentinCody/ucsc-mcp-server` (TypeScript, earlier-stage). Neither is official from UCSC.

A purpose-built MCP should expose `list_assemblies()`, `list_tracks(assembly)`, `get_sequence(assembly, chrom, start, end)`, `get_track(assembly, track, chrom, start, end)`, and `liftover(from_assembly, to_assembly, chrom, start, end)`. The connector must abstract over the `chr`-prefixed UCSC chromosome convention vs the bare-numeric Ensembl/GENCODE convention, validate coordinates against assembly chrom sizes before issuing the request, page over the 1M-item cap for dense tracks, and route bulk queries away from the REST API toward MySQL or FTP when the result set will be large.

## Review notes

Potential new join key for review: `UCSC_ASSEMBLY_DB`
  Entity type: genome_assembly
  Pattern: `^[a-zA-Z]+[0-9]+$` (e.g. `hg38`, `mm39`, `hs1`, `sacCer3`)
  Other datasets that would use it: any genomics source that pins coordinates to a UCSC assembly name (GENCODE release notes, ENCODE, GTEx, gnomAD documentation, many published BED/BigBed tracks). It is genuinely cross-source: assembly identity is the implicit join key for every genomic coordinate row in the registry, and right now there is no canonical key for it.

Potential new join key for review: `UCSC_TRACK_NAME`
  Entity type: annotation_track
  Pattern: free-form lowercase identifier (e.g. `knownGene`, `dbSnp155`, `gencodeV44`)
  Other datasets that would use it: lower priority, mostly UCSC-internal. Worth flagging only because it travels with `UCSC_ASSEMBLY_DB` as a 2-tuple for track-row identity.

Genomic-coordinate triples (`chrom`, `start`, `end`) function as a join key across every coordinate-based source in `bio-genomics` but do not fit the single-column UPPER_SNAKE_CASE registry shape. May be worth a separate discussion about whether the registry should model composite or range-based keys, or whether coordinate joins stay implicit and out of scope.
