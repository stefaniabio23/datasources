#!/usr/bin/env python3
"""
Publish the datasources registry to Airtable as two linked tables.

  JoinKeys  — one row per canonical join key (from generated/join-keys.csv)
  Sources   — one row per source (from generated/index.json), with a
              `join_keys` linked-record field pointing at JoinKeys.

The link makes the many-to-many a real Airtable relation: open a source and
see its keys as chips; open a key and see every source that exposes it.

GitHub stays canonical. Airtable is an overwrite mirror: each run upserts on a
stable key (`join_key` / `id`) and prunes records no longer in the repo.

Required env vars:
  AIRTABLE_TOKEN    — personal access token (pat...). Read from the macOS
                      Keychain at runtime; never written to disk:
                      AIRTABLE_TOKEN=$(security find-generic-password -s AIRTABLE_TOKEN -w)
  AIRTABLE_BASE_ID  — target base id (the "app"-prefixed id from the base URL).

Optional:
  AIRTABLE_SOURCES_TABLE   (default "Sources")
  AIRTABLE_JOINKEYS_TABLE  (default "JoinKeys")

Run locally:
  AIRTABLE_TOKEN=$(security find-generic-password -s AIRTABLE_TOKEN -w) \
  AIRTABLE_BASE_ID=<your-base-id> \
  python3 scripts/publish_to_airtable.py

Dry run (no network; validates data mapping only):
  python3 scripts/publish_to_airtable.py --dry-run

Dependencies:
  pip install pyairtable
"""

import csv
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATED = PROJECT_ROOT / "generated"

SOURCES_TABLE = os.environ.get("AIRTABLE_SOURCES_TABLE", "Sources")
JOINKEYS_TABLE = os.environ.get("AIRTABLE_JOINKEYS_TABLE", "JoinKeys")

# Closed enums from schema/entry.schema.yaml. Used to pre-seed select options
# (nice order + colours). typecast=True on upsert also auto-creates any stragglers.
DOMAINS = [
    "academic", "clinical-biotech", "bio-genomics", "public-health",
    "healthcare-claims", "finance-markets", "corporate-registry", "news-events",
    "consumer-signal", "government-open-data", "geospatial",
]
ENTRY_KINDS = [
    "registry", "time-series", "panel", "event-stream", "knowledge-graph",
    "corpus", "reference-table", "geospatial", "mixed",
]
TYPES = [
    "rest-api", "bulk-download", "dataset-dump", "database", "web-ui",
    "scraper-required", "unofficial-api", "socrata", "odata", "powerbi-export",
]
AUTH = ["none", "api-key-free", "api-key-paid", "account-required", "oauth", "dars-or-equivalent"]
COST = ["free", "freemium", "paid", "free-with-registration", "free-non-commercial"]
MCP_STATUS = [
    "mcp-exists", "mcp-needed-high-value", "mcp-needed-low-value",
    "api-direct-sufficient", "requires-scraping", "fragile-unofficial",
]
MCP_MATURITY = ["official", "community", "experimental", "none"]
PRIORITY = ["high", "medium", "low"]


def _choices(values):
    return {"choices": [{"name": v} for v in values]}


def joinkeys_fields_spec():
    return [
        {"name": "join_key", "type": "singleLineText"},   # primary
        {"name": "entity_type", "type": "singleLineText"},
        {"name": "pattern", "type": "singleLineText"},
        {"name": "examples", "type": "multilineText"},
        {"name": "description", "type": "multilineText"},
    ]


def sources_fields_spec(joinkeys_table_id):
    return [
        {"name": "id", "type": "singleLineText"},          # primary
        {"name": "name", "type": "singleLineText"},
        {"name": "domain", "type": "singleSelect", "options": _choices(DOMAINS)},
        {"name": "entry_kind", "type": "singleSelect", "options": _choices(ENTRY_KINDS)},
        {"name": "description", "type": "multilineText"},
        {"name": "join_keys", "type": "multipleRecordLinks",
         "options": {"linkedTableId": joinkeys_table_id}},
        {"name": "type", "type": "multipleSelects", "options": _choices(TYPES)},
        {"name": "auth_required", "type": "singleSelect", "options": _choices(AUTH)},
        {"name": "cost", "type": "singleSelect", "options": _choices(COST)},
        {"name": "license", "type": "singleLineText"},
        {"name": "mcp_status", "type": "singleSelect", "options": _choices(MCP_STATUS)},
        {"name": "mcp_maturity", "type": "singleSelect", "options": _choices(MCP_MATURITY)},
        {"name": "mcp_package", "type": "multilineText"},
        {"name": "primary_keys", "type": "multilineText"},
        {"name": "agent_use_cases", "type": "multilineText"},
        {"name": "rate_limit", "type": "singleLineText"},
        {"name": "bulk_available", "type": "checkbox",
         "options": {"icon": "check", "color": "greenBright"}},
        {"name": "frequency", "type": "singleLineText"},
        {"name": "lag", "type": "singleLineText"},
        {"name": "geography", "type": "singleLineText"},
        {"name": "homepage_url", "type": "url"},
        {"name": "docs_url", "type": "url"},
        {"name": "build_priority", "type": "singleSelect", "options": _choices(PRIORITY)},
        {"name": "last_verified", "type": "date", "options": {"dateFormat": {"name": "iso"}}},
        {"name": "notes", "type": "multilineText"},
    ]


def load_join_keys():
    path = GENERATED / "join-keys.csv"
    with path.open() as f:
        return list(csv.DictReader(f))


def load_sources():
    return json.loads((GENERATED / "index.json").read_text())


def _joined(value, sep="\n"):
    if isinstance(value, list):
        return sep.join(str(v) for v in value)
    return value


def source_fields(entry, jk_id_map):
    """Map one index.json entry to Airtable field values. Omits empty fields."""
    links = [jk_id_map[k] for k in entry.get("join_keys", []) or [] if k in jk_id_map]
    raw = {
        "id": entry.get("id"),
        "name": entry.get("name"),
        "domain": entry.get("domain"),
        "entry_kind": entry.get("entry_kind"),
        "description": entry.get("description"),
        "join_keys": links,
        "type": entry.get("type") or [],
        "auth_required": entry.get("auth_required"),
        "cost": entry.get("cost"),
        "license": entry.get("license"),
        "mcp_status": entry.get("mcp_status"),
        "mcp_maturity": entry.get("mcp_maturity"),
        "mcp_package": _joined(entry.get("mcp_package")),
        "primary_keys": _joined(entry.get("primary_keys")),
        "agent_use_cases": _joined(entry.get("agent_use_cases")),
        "rate_limit": entry.get("rate_limit"),
        "bulk_available": bool(entry.get("bulk_available", False)),
        "frequency": entry.get("frequency"),
        "lag": entry.get("lag"),
        "geography": _joined(entry.get("geography"), ", "),
        "homepage_url": entry.get("homepage_url"),
        "docs_url": entry.get("docs_url"),
        "build_priority": entry.get("build_priority"),
        "last_verified": entry.get("last_verified"),
        "notes": entry.get("notes"),
    }
    # Drop None and empty strings; keep booleans and non-empty lists.
    return {k: v for k, v in raw.items() if v not in (None, "", [])}


def joinkey_fields(row):
    raw = {
        "join_key": row.get("join_key"),
        "entity_type": row.get("entity_type"),
        "pattern": row.get("pattern"),
        "examples": row.get("examples"),
        "description": row.get("description"),
    }
    return {k: v for k, v in raw.items() if v not in (None, "")}


# --------------------------------------------------------------------------- Airtable

def ensure_table(base, name, fields_spec):
    """Return the Table, creating it (or any missing fields) as needed."""
    schema = base.schema()
    match = next((t for t in schema.tables if t.name == name), None)
    if match is None:
        print(f"  creating table '{name}'")
        return base.create_table(name, fields=fields_spec)

    table = base.table(match.id)
    existing = {f.name for f in table.schema().fields}
    for spec in fields_spec:
        if spec["name"] not in existing:
            print(f"  adding field '{name}.{spec['name']}'")
            table.create_field(spec["name"], spec["type"], options=spec.get("options"))
    return table


def upsert(table, records, key_field):
    """Upsert on key_field, then prune records whose key is not in `records`."""
    payload = [{"fields": r} for r in records]
    table.batch_upsert(payload, key_fields=[key_field], typecast=True)

    wanted = {r[key_field] for r in records}
    stale = [r["id"] for r in table.all() if r["fields"].get(key_field) not in wanted]
    if stale:
        print(f"  pruning {len(stale)} stale record(s) from '{table.name}'")
        table.batch_delete(stale)


def main():
    dry_run = "--dry-run" in sys.argv

    join_key_rows = load_join_keys()
    sources = load_sources()
    jk_records = [joinkey_fields(r) for r in join_key_rows]

    print(f"Loaded {len(jk_records)} join keys, {len(sources)} sources.")

    if dry_run:
        # Validate mapping offline: every source's join_keys must resolve.
        known = {r["join_key"] for r in jk_records}
        unresolved = {
            k for s in sources for k in (s.get("join_keys") or []) if k not in known
        }
        src_records = [source_fields(s, {k: k for k in known}) for s in sources]
        print(f"[dry-run] mapped {len(src_records)} source rows")
        print(f"[dry-run] unresolved join keys: {sorted(unresolved) or 'none'}")
        return 0 if not unresolved else 1

    token = os.environ.get("AIRTABLE_TOKEN")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    missing = [n for n, v in [("AIRTABLE_TOKEN", token), ("AIRTABLE_BASE_ID", base_id)] if not v]
    if missing:
        print(f"Required env vars not set: {', '.join(missing)}", file=sys.stderr)
        return 2

    from pyairtable import Api

    api = Api(token)
    base = api.base(base_id)

    jk_table = ensure_table(base, JOINKEYS_TABLE, joinkeys_fields_spec())
    sources_table = ensure_table(base, SOURCES_TABLE, sources_fields_spec(jk_table.id))

    print("Upserting join keys...")
    upsert(jk_table, jk_records, "join_key")

    # Build join_key -> record id map from live table state (reliable post-upsert).
    jk_id_map = {r["fields"]["join_key"]: r["id"]
                 for r in jk_table.all() if r["fields"].get("join_key")}

    print("Upserting sources...")
    src_records = [source_fields(s, jk_id_map) for s in sources]
    upsert(sources_table, src_records, "id")

    print(f"Done. {len(jk_records)} join keys, {len(src_records)} sources, relation wired.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
