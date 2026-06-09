---
id: american-gut-project
name: American Gut Project
domain: bio-genomics
entry_kind: corpus
description: Crowdfunded citizen-science microbiome dataset of stool, skin, and oral 16S rRNA samples paired with dietary and lifestyle questionnaires, run by the Knight Lab at UC San Diego.
homepage_url: https://github.com/biocore/American-Gut
docs_url: https://github.com/biocore/American-Gut/blob/master/README.md
type:
  - bulk-download
  - dataset-dump
auth_required: none
cost: free
license: BSD-3-Clause
bulk_available: true
frequency: irregular
lag: "GitHub snapshot frozen at May 2015; FTP mirror periodically refreshed; ENA accession ERP012803 updated when new submissions are deposited"
geography: [global]
join_keys:
  - DOI
  - PMID
primary_keys:
  - AMERICAN_GUT_BARCODE
  - QIITA_STUDY_ID
  - ENA_RUN_ACCESSION
join_key_fields:
  - join_key: DOI
    fields: [README.md]
  - join_key: PMID
    fields: [README.md]
mcp_status: mcp-needed-low-value
mcp_maturity: none
mcp_notes: >
  Static snapshot plus FTP mirror; no live API. A connector would mostly wrap
  FTP listing, OTU/BIOM table fetch, and metadata join against the GitHub
  mapping files. Limited cross-source value beyond microbiome-specific work.
agent_use_cases:
  - retrieve baseline gut microbiome composition for a Western cohort
  - cross-reference diet and lifestyle metadata with 16S taxonomy
  - benchmark new microbiome methods against an open reference dataset
  - replicate published American Gut analyses
access_test:
  command: "curl -sfI 'https://raw.githubusercontent.com/biocore/American-Gut/master/README.md'"
  expected_status: 200
last_verified: 2026-06-09
build_priority: low
notes: "Repository last pushed 2017-03-17; superseded operationally by the Microsetta Initiative, but the deposited data remains the canonical open American Gut release. Access test built against raw GitHub; FTP mirror at ftp.microbio.me/AmericanGut not tested via curl."
---

# American Gut Project

## Why this source matters

The American Gut Project is a crowdfunded citizen-science microbiome study run by Rob Knight's lab at UC San Diego, with collaborators across UCSD, the Earth Microbiome Project, and (in its UK arm) the British Gut. Participants paid a small fee, received a sample kit, returned stool, skin, oral, or environmental swabs, and completed dietary and lifestyle questionnaires. The biocore/American-Gut GitHub repository is the open-data anchor: it holds OTU tables, sample mapping files, and the IPython notebooks used to produce the published analyses. Raw 16S sequences and full metadata are deposited at the European Nucleotide Archive under study accession ERP012803. The headline publication is McDonald et al. 2018 ("American Gut: an Open Platform for Citizen Science Microbiome Research", mSystems, DOI 10.1128/mSystems.00031-18, PMID 29795809), which covers ~15,000 samples across the first cohort. Secondary relevance to `public-health` for diet/lifestyle correlates and to `consumer-signal` for self-reported behavioural metadata.

## Agent use cases

- retrieve baseline gut microbiome composition for a Western cohort
- cross-reference diet and lifestyle metadata with 16S taxonomy
- benchmark new microbiome methods against an open reference dataset
- replicate published American Gut analyses

## Join strategy

Few canonical join keys are exposed directly. The reliable bridges are `DOI` and `PMID` for the McDonald 2018 paper and follow-up publications, which let an agent pivot to OpenAlex, Europe PMC, and PubMed for the methods and downstream citations. The load-bearing identifiers are project-internal and intentionally outside the canonical registry: American Gut sample barcodes (e.g. `000007108`), Qiita study IDs (10317 for the main 16S V4 study, plus a handful of supplementary studies), and ENA run accessions in the `ERR`/`ERX`/`ERS`/`ERP` namespace under ERP012803. Pair with NCBI SRA / ENA for the raw FASTQ, with Qiita for processed BIOM tables and pre-computed diversity metrics, and with the Earth Microbiome Project for cross-cohort comparisons using the same V4 primers.

## Access notes

**Static snapshot:** Clone or browse `github.com/biocore/American-Gut`. The `data/` directory holds OTU tables and sample mapping files frozen at May 2015, scrubbed for PHI. Notebooks in `ipynb/` reproduce the analyses against that snapshot.

**Latest processed data:** FTP at `ftp://ftp.microbio.me/AmericanGut/` (with `latest/` containing the most recent OTU tables and pre-computed diversity comparisons). FTP listing is the canonical freshness check; no programmatic API.

**Raw sequences:** ENA study `ERP012803` at `https://www.ebi.ac.uk/ena/browser/view/ERP012803`. Fetch FASTQ via ENA's portal API or the Aspera/FTP mirrors. Use `https://www.ebi.ac.uk/ena/portal/api/filereport?accession=ERP012803&result=read_run&fields=run_accession,sample_accession,fastq_ftp` to enumerate run-level FASTQ URLs.

**Survey instrument:** GitHub repo includes the dietary and lifestyle questionnaire used during the first cohort; later cohorts under the Microsetta Initiative use a revised survey not reflected in this snapshot.

Known gotchas:

- The biocore repository is effectively archived (last push 2017-03-17). Active enrollment and newer data have moved to the Microsetta Initiative under separate ENA accessions.
- 16S V4 amplicon only in the canonical release; shotgun data is in separate sub-studies and not exhaustively cross-referenced here.
- The May-2015 GitHub snapshot uses an older survey version, do not merge survey columns across snapshot and FTP `latest/` without checking the field dictionary.
- All human-readable PHI has been scrubbed, but linkage attacks across sample barcode + ZIP + age are theoretically possible; downstream re-publication should respect the original consent.

## MCP / connector notes

No MCP exists. Demand is narrow (microbiome researchers and benchmark builders), so this lands as `mcp-needed-low-value`. A useful connector surface would be small: `list_otu_tables(snapshot)`, `fetch_mapping_file(snapshot)`, `list_ena_runs(study=ERP012803)`, `get_qiita_study(study_id)`, and a `resolve_publication_to_data(DOI|PMID)` helper that maps the McDonald 2018 paper and follow-ups to their respective OTU table and FASTQ slice. The connector must abstract over three different access surfaces (GitHub raw, microbio.me FTP, ENA Portal API) and over the snapshot-versus-latest distinction in the FTP mirror.

## Review notes

Potential new join keys for review (all microbiome / nucleotide-archive identifiers; would be reusable across American Gut, Microsetta, Qiita, ENA, and the Earth Microbiome Project):

```
Potential new join key for review: QIITA_STUDY_ID
  Entity type: microbiome_study
  Pattern: ^[0-9]+$
  Other datasets that would use it: Qiita platform studies, Earth Microbiome Project, Microsetta Initiative

Potential new join key for review: ENA_STUDY_ACCESSION
  Entity type: nucleotide_study
  Pattern: ^(ERP|SRP|DRP)[0-9]+$
  Other datasets that would use it: ENA, NCBI SRA (mirror), DDBJ, any project depositing to INSDC
```

License: the biocore/American-Gut repository carries a Modified BSD (BSD-3-Clause) licence on code and notebooks. The deposited sequence data at ENA is governed by INSDC public-data terms separately, and the survey/questionnaire metadata carries participant-consent constraints documented in the McDonald 2018 paper. Recorded as `BSD-3-Clause` here because that is the licence the GitHub source actually publishes; downstream redistribution of sample-level metadata should respect the original IRB scope.

GitHub's licence detector reports `NOASSERTION` despite the LICENSE file containing a Modified BSD text, worth a human eyeball before publication. Flag also: this entry covers the legacy biocore release, not the active Microsetta Initiative; a separate entry for Microsetta may be warranted once it stabilises a public data surface.
