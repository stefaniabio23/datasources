# catalog/

Layered machine-readable metadata for multi-dataset sources.

The canonical pattern, per source:

```
catalog/<source_id>/
  source.yaml                            # provider-level manifest
  datasets/<dataset_id>.yaml             # one per dataset/route/table
  schemas/<dataset_id>.schema.yaml       # field-level schema per dataset
  generated/series-index.csv             # optional series-level index
```

Single-dataset providers (Crossref, ORCID, Companies House) live in `entries/` only and never gain a `catalog/<source>/` directory. The catalog layer exists for sources like EIA, OECD, World Bank, NCBI E-utilities, FRED where a single provider exposes many distinct datasets or routes worth modelling individually.

## File-level validation

| Path | Schema |
|---|---|
| `catalog/<id>/source.yaml` | `schema/source.schema.yaml` |
| `catalog/<id>/datasets/*.yaml` | `schema/dataset.schema.yaml` |
| `catalog/<id>/schemas/*.schema.yaml` | `schema/field-schema.schema.yaml` |

`scripts/validate_entries.py` walks `catalog/` and validates each file.

## Generator outputs

`scripts/generate.py` emits, alongside the entry-level outputs:

- `generated/datasets.csv` — one row per `catalog/<id>/datasets/*.yaml` entry
- `generated/fields.csv` — one row per field across all `catalog/<id>/schemas/*.schema.yaml` files

Both are empty when `catalog/` has no contents.

## Cross-layer wiring

- `catalog/<id>/source.yaml` has `id: <id>` matching the directory name AND matching the `entries/<domain>/<id>.md` entry id. The entry can link to the catalog via `catalog_path: catalog/<id>/source.yaml`.
- `catalog/<id>/datasets/<dataset_id>.yaml` has `source_id: <id>` referencing the source.yaml.
- `catalog/<id>/schemas/<dataset_id>.schema.yaml` has `source_id: <id>` AND `dataset_id: <dataset_id>` matching the dataset manifest.

The validator enforces these references; broken links fail the build.

## When to promote an entry to a catalog source

Add a `catalog/<id>/` directory when the source is `entry_kind: mixed` or `entry_kind: panel` AND either:
- The provider has a self-describing metadata API (EIA v2, OECD SDMX, FRED, World Bank, NCBI E-utils), so dataset enumeration and field schemas can be auto-discovered
- Or you intend to model the top ~5 sub-datasets by hand because they're high-value for downstream quant/backtest agents

For sources that are nominally multi-dataset but where individual datasets aren't worth modelling separately (e.g. newsapi has many endpoints but they're variations of one entity), keep them as entries-only.
