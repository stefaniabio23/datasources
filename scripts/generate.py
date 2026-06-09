#!/usr/bin/env python3
"""
Generate shareable outputs from entries/**/*.md.

Outputs:
- generated/index.json         — all entries flattened, machine-readable
- generated/sources.csv        — one row per entry, single flat sheet
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

    print(f"Loaded {len(entries)} entries.")

    write_index_json(entries, generated_root / "index.json")
    print("  wrote generated/index.json")

    write_csv(generated_root / "sources.csv", SOURCES_COLUMNS, entries)
    print(f"  wrote generated/sources.csv ({len(entries)} rows)")

    registry_path = project_root / "schema" / "join-keys.yaml"
    registry = yaml.safe_load(registry_path.read_text()) if registry_path.exists() else {}
    write_join_keys_csv(registry, generated_root / "join-keys.csv")
    print(f"  wrote generated/join-keys.csv ({sum(1 for v in registry.values() if isinstance(v, dict))} rows)")

    write_join_key_index(entries, generated_root / "join-key-index.md")
    print("  wrote generated/join-key-index.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
