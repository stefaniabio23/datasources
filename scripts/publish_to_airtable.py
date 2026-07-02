#!/usr/bin/env python3
"""
Publish the datasources registry to Airtable as ONE flat table.

  Sources — one row per dataset, all source fields plus `join_keys` inline as a
            multiple-select (colored chips in the same row). Self-contained: no
            second table, no linked relation.

GitHub stays canonical. Airtable is an overwrite mirror: each run upserts on
`id` and prunes rows no longer in the repo.

Required env vars:
  AIRTABLE_TOKEN    — personal access token (pat...). Read from the macOS
                      Keychain at runtime; never written to disk:
                      AIRTABLE_TOKEN=$(security find-generic-password -s AIRTABLE_TOKEN -w)
  AIRTABLE_BASE_ID  — target base id (the "app"-prefixed id from the base URL).

Optional:
  AIRTABLE_SOURCES_TABLE  (default "Sources")

Run locally:
  AIRTABLE_TOKEN=$(security find-generic-password -s AIRTABLE_TOKEN -w) \
  AIRTABLE_BASE_ID=<your-base-id> \
  python3 scripts/publish_to_airtable.py

Dry run (no network; validates data mapping only):
  python3 scripts/publish_to_airtable.py --dry-run

Note: Airtable's API cannot delete tables or change a field's type. If a
`Sources` table already exists with `join_keys` as a linked-record field (from
an earlier two-table layout), delete that table (and the old `JoinKeys` table)
in the Airtable UI first; this script then recreates a single flat table.

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

# Closed enums from schema/entry.schema.yaml. Used to pre-seed select options
# (nice order + colours). typecast=True on upsert also auto-creates stragglers.
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


def canonical_join_keys():
    """The full canonical key vocabulary, for the join_keys multi-select options."""
    path = GENERATED / "join-keys.csv"
    with path.open() as f:
        return [row["join_key"] for row in csv.DictReader(f)]


def sources_fields_spec(join_key_options):
    return [
        {"name": "id", "type": "singleLineText"},          # primary
        {"name": "name", "type": "singleLineText"},
        {"name": "domain", "type": "singleSelect", "options": _choices(DOMAINS)},
        {"name": "entry_kind", "type": "singleSelect", "options": _choices(ENTRY_KINDS)},
        {"name": "description", "type": "multilineText"},
        {"name": "join_keys", "type": "multipleSelects", "options": _choices(join_key_options)},
        {"name": "type", "type": "multipleSelects", "options": _choices(TYPES)},
        {"name": "auth_required", "type": "singleSelect", "options": _choices(AUTH)},
        {"name": "cost", "type": "singleSelect", "options": _choices(COST)},
        {"name": "license", "type": "singleLineText"},
        {"name": "mcp_status", "type": "singleSelect", "options": _choices(MCP_STATUS)},
        {"name": "mcp_maturity", "type": "singleSelect", "options": _choices(MCP_MATURITY)},
        {"name": "mcp_package", "type": "multilineText"},
        {"name": "mcp_command", "type": "multilineText"},
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


def load_sources():
    return json.loads((GENERATED / "index.json").read_text())


def _joined(value, sep="\n"):
    if isinstance(value, list):
        return sep.join(str(v) for v in value)
    return value


def source_fields(entry):
    """Map one index.json entry to Airtable field values. Omits empty fields."""
    raw = {
        "id": entry.get("id"),
        "name": entry.get("name"),
        "domain": entry.get("domain"),
        "entry_kind": entry.get("entry_kind"),
        "description": entry.get("description"),
        "join_keys": entry.get("join_keys") or [],
        "type": entry.get("type") or [],
        "auth_required": entry.get("auth_required"),
        "cost": entry.get("cost"),
        "license": entry.get("license"),
        "mcp_status": entry.get("mcp_status"),
        "mcp_maturity": entry.get("mcp_maturity"),
        "mcp_package": _joined(entry.get("mcp_package")),
        "mcp_command": _joined(entry.get("mcp_command")),
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


# --------------------------------------------------------------------------- Airtable

def ensure_table(base, name, fields_spec):
    """Return the Table, creating it (or any missing fields) as needed.

    Aborts if the existing table has `join_keys` as a linked-record field: that
    is the old two-table layout, which the API cannot convert in place.
    """
    schema = base.schema()
    match = next((t for t in schema.tables if t.name == name), None)
    if match is None:
        print(f"  creating table '{name}'")
        return base.create_table(name, fields=fields_spec)

    table = base.table(match.id)
    fields = {f.name: f for f in table.schema().fields}
    jk = fields.get("join_keys")
    if jk is not None and jk.type == "multipleRecordLinks":
        sys.exit(
            f"ERROR: table '{name}' has a linked-record 'join_keys' field (old "
            f"two-table layout). Airtable's API cannot convert it. Delete the "
            f"'{name}' and 'JoinKeys' tables in the Airtable UI, then re-run."
        )
    for spec in fields_spec:
        if spec["name"] not in fields:
            print(f"  adding field '{name}.{spec['name']}'")
            table.create_field(spec["name"], spec["type"], options=spec.get("options"))
    return table


def upsert(table, records, key_field):
    """Upsert on key_field, then prune rows whose key is not in `records`."""
    payload = [{"fields": r} for r in records]
    table.batch_upsert(payload, key_fields=[key_field], typecast=True)

    wanted = {r[key_field] for r in records}
    stale = [r["id"] for r in table.all() if r["fields"].get(key_field) not in wanted]
    if stale:
        print(f"  pruning {len(stale)} stale row(s) from '{table.name}'")
        table.batch_delete(stale)


def main():
    dry_run = "--dry-run" in sys.argv

    sources = load_sources()
    key_options = canonical_join_keys()
    records = [source_fields(s) for s in sources]
    print(f"Loaded {len(records)} datasets, {len(key_options)} join-key options.")

    if dry_run:
        known = set(key_options)
        unresolved = sorted({k for r in records for k in r.get("join_keys", []) if k not in known})
        print(f"[dry-run] mapped {len(records)} rows into one flat table")
        print(f"[dry-run] join keys outside the vocabulary: {unresolved or 'none'}")
        return 0 if not unresolved else 1

    token = os.environ.get("AIRTABLE_TOKEN")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    missing = [n for n, v in [("AIRTABLE_TOKEN", token), ("AIRTABLE_BASE_ID", base_id)] if not v]
    if missing:
        print(f"Required env vars not set: {', '.join(missing)}", file=sys.stderr)
        return 2

    from pyairtable import Api

    base = Api(token).base(base_id)
    table = ensure_table(base, SOURCES_TABLE, sources_fields_spec(key_options))

    print("Upserting datasets...")
    upsert(table, records, "id")
    print(f"Done. {len(records)} datasets in one flat '{SOURCES_TABLE}' table.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
