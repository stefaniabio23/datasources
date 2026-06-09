#!/usr/bin/env python3
"""
Generate shareable outputs from entries/**/*.md and catalog/**/*.yaml.

Outputs:
- generated/index.json         — all entries flattened, machine-readable
- generated/sources.csv        — one row per source (entry + catalog source.yaml)
- generated/datasets.csv       — one row per catalog dataset
- generated/fields.csv         — one row per field across catalog field schemas
- generated/join-keys.csv      — one row per canonical join key from schema/join-keys.yaml
- generated/join-key-index.md  — reverse index: each join_key → datasets that expose it

Run from the project root:
    python3 scripts/generate.py

Dependencies:
    pip install pyyaml
"""

import csv
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


SOURCES_COLUMNS = [
    "id",
    "name",
    "domain",
    "entry_kind",
    "entry_level",
    "description",
    "type",
    "auth_required",
    "cost",
    "license",
    "rate_limit",
    "bulk_available",
    "frequency",
    "lag",
    "geography",
    "mcp_status",
    "mcp_maturity",
    "mcp_package",
    "join_keys",
    "primary_keys",
    "agent_use_cases",
    "homepage_url",
    "docs_url",
    "build_priority",
    "last_verified",
    "catalog_path",
    "parent_source",
]

DATASETS_COLUMNS = [
    "id",
    "source_id",
    "name",
    "entry_level",
    "entry_kind",
    "route",
    "data_endpoint",
    "metadata_endpoint",
    "time_index",
    "time_grain",
    "primary_keys",
    "join_keys",
    "field_schema",
    "agent_use_cases",
]

FIELDS_COLUMNS = [
    "source_id",
    "dataset_id",
    "field_name",
    "type",
    "role",
    "join_key",
    "unit",
    "required",
    "description",
]

JOIN_KEYS_COLUMNS = [
    "join_key",
    "entity_type",
    "pattern",
    "examples",
    "description",
]


def parse_entry(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fm = yaml.safe_load(text[4:end])
    if not isinstance(fm, dict):
        return None
    return fm


def normalize(obj):
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize(v) for v in obj]
    if isinstance(obj, date):
        return obj.isoformat()
    return obj


def render_cell(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return "; ".join(str(x) for x in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)


def write_index_json(entries, out_path):
    out_path.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n")


def write_csv(out_path, columns, rows_dict_iter):
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(columns)
        for row in rows_dict_iter:
            writer.writerow([render_cell(row.get(c)) for c in columns])


def load_catalog(project_root):
    catalog_root = project_root / "catalog"
    sources, datasets, fields = [], [], []
    if not catalog_root.exists():
        return sources, datasets, fields

    for source_dir in sorted(catalog_root.iterdir()):
        if not source_dir.is_dir():
            continue
        source_yaml = source_dir / "source.yaml"
        if source_yaml.exists():
            sources.append(normalize(yaml.safe_load(source_yaml.read_text())))

        datasets_dir = source_dir / "datasets"
        if datasets_dir.exists():
            for ds_path in sorted(datasets_dir.glob("*.yaml")):
                ds = normalize(yaml.safe_load(ds_path.read_text()))
                if isinstance(ds, dict):
                    api = ds.get("api") or {}
                    ds["route"] = api.get("route")
                    ds["data_endpoint"] = api.get("data_endpoint")
                    ds["metadata_endpoint"] = api.get("metadata_endpoint")
                    datasets.append(ds)

        schemas_dir = source_dir / "schemas"
        if schemas_dir.exists():
            for sc_path in sorted(schemas_dir.glob("*.schema.yaml")):
                sc = normalize(yaml.safe_load(sc_path.read_text()))
                if not isinstance(sc, dict):
                    continue
                for f in (sc.get("fields") or []):
                    fields.append({
                        "source_id": sc.get("source_id"),
                        "dataset_id": sc.get("dataset_id"),
                        "field_name": f.get("name"),
                        "type": f.get("type"),
                        "role": f.get("role"),
                        "join_key": f.get("join_key"),
                        "unit": f.get("unit"),
                        "required": f.get("required"),
                        "description": f.get("description"),
                    })

    return sources, datasets, fields


def write_join_key_index(entries, out_path):
    by_key = defaultdict(list)
    for entry in entries:
        for key in entry.get("join_keys") or []:
            by_key[key].append(entry)

    lines = [
        "# Join-Key Index",
        "",
        "Reverse index of canonical join keys mapped to the datasets that expose them.",
        "Generated from `entries/**/*.md`. Do not hand-edit.",
        "",
        f"**{len(entries)} datasets, {len(by_key)} distinct canonical keys, "
        f"{sum(len(v) for v in by_key.values())} key→source links.**",
        "",
    ]

    for key in sorted(by_key.keys()):
        sources = sorted(by_key[key], key=lambda e: e["name"])
        lines.append(f"## {key}")
        lines.append("")
        lines.append(f"_{len(sources)} dataset(s)._")
        lines.append("")
        for src in sources:
            lines.append(f"- [{src['name']}](../{src['_path']}) — `{src['domain']}`")
        lines.append("")

    out_path.write_text("\n".join(lines))


def write_join_keys_csv(registry, out_path):
    rows = []
    for key, meta in sorted(registry.items()):
        if not isinstance(meta, dict):
            continue
        examples = meta.get("examples") or []
        rows.append({
            "join_key": key,
            "entity_type": meta.get("entity_type", ""),
            "pattern": meta.get("pattern", ""),
            "examples": examples,
            "description": meta.get("description", ""),
        })
    write_csv(out_path, JOIN_KEYS_COLUMNS, rows)


def main():
    project_root = Path(__file__).resolve().parent.parent
    entries_root = project_root / "entries"
    generated_root = project_root / "generated"
    generated_root.mkdir(exist_ok=True)

    entries = []
    for path in sorted(entries_root.rglob("*.md")):
        fm = parse_entry(path)
        if fm is None:
            print(f"  skipped (no parseable frontmatter): {path.relative_to(project_root)}",
                  file=sys.stderr)
            continue
        fm["_path"] = str(path.relative_to(project_root))
        entries.append(normalize(fm))

    if not entries:
        print("No entries found.")
        return 0

    catalog_sources, catalog_datasets, catalog_fields = load_catalog(project_root)

    # Sources tab = entries/ rows + catalog/<src>/source.yaml rows.
    # If an id appears in both, the catalog/source.yaml row takes precedence at
    # the listed columns and the entry contributes anything the catalog source
    # didn't specify.
    by_id = {e["id"]: dict(e) for e in entries}
    for src in catalog_sources:
        sid = src.get("id")
        if sid in by_id:
            merged = {**by_id[sid], **{k: v for k, v in src.items() if v is not None}}
            by_id[sid] = merged
        else:
            by_id[sid] = src
    sources_rows = [by_id[k] for k in sorted(by_id.keys())]

    print(f"Loaded {len(entries)} entries, {len(catalog_sources)} catalog sources, "
          f"{len(catalog_datasets)} catalog datasets, {len(catalog_fields)} catalog fields.")

    write_index_json(entries, generated_root / "index.json")
    print("  wrote generated/index.json")

    write_csv(generated_root / "sources.csv", SOURCES_COLUMNS, sources_rows)
    print(f"  wrote generated/sources.csv ({len(sources_rows)} rows)")

    write_csv(generated_root / "datasets.csv", DATASETS_COLUMNS, catalog_datasets)
    print(f"  wrote generated/datasets.csv ({len(catalog_datasets)} rows)")

    write_csv(generated_root / "fields.csv", FIELDS_COLUMNS, catalog_fields)
    print(f"  wrote generated/fields.csv ({len(catalog_fields)} rows)")

    registry_path = project_root / "schema" / "join-keys.yaml"
    registry = yaml.safe_load(registry_path.read_text()) if registry_path.exists() else {}
    write_join_keys_csv(registry, generated_root / "join-keys.csv")
    print(f"  wrote generated/join-keys.csv ({sum(1 for v in registry.values() if isinstance(v, dict))} rows)")

    write_join_key_index(entries, generated_root / "join-key-index.md")
    print("  wrote generated/join-key-index.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
