#!/usr/bin/env python3
"""
Discover EIA Open Data sub-datasets by walking the EIA v2 API metadata tree.

For each leaf route that exposes facets + data columns, writes:
  catalog/eia-open-data/datasets/<slug>.yaml
  catalog/eia-open-data/schemas/<slug>.schema.yaml

Hand-curated files (existing in those directories) are never overwritten;
the discovery output is additive.

Requires EIA_API_KEY env var. Free registration at:
  https://www.eia.gov/opendata/register.php

Usage:
    export EIA_API_KEY=...
    python3 scripts/discover_eia.py [--dry-run] [--limit N] [--root /path]

After it finishes, run validate + generate to fold the new files in:
    python3 scripts/validate_entries.py
    python3 scripts/generate.py

Dependencies:
    pip install requests pyyaml
"""

import argparse
import os
import sys
import time
from pathlib import Path

try:
    import requests
    import yaml
except ImportError:
    print(
        "Missing dependency. Install with: pip install requests pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)


SOURCE_ID = "eia-open-data"
API_BASE = "https://api.eia.gov/v2"
SLEEP_SECONDS = 0.4  # be polite to the API

# EIA facet id -> canonical join_key from schema/join-keys.yaml.
# Add to this map as more registry-resolvable facets are identified.
FACET_JOIN_KEYS = {
    "stateid": "US_STATE_CODE",
    "countryRegionId": "ISO_3",
}

# EIA frequency id -> our entry.schema.yaml time_grain enum value.
FREQ_MAP = {
    "annual": "annual",
    "quarterly": "quarterly",
    "monthly": "monthly",
    "weekly": "weekly",
    "daily": "daily",
    "hourly": "hourly",
    "minute": "minutely",
}


def fetch_route(api_key: str, route: str) -> dict:
    url = f"{API_BASE}{route}"
    r = requests.get(url, params={"api_key": api_key}, timeout=20)
    r.raise_for_status()
    return r.json().get("response", {})


def route_to_slug(route: str) -> str:
    return route.strip("/").replace("/", "-") or SOURCE_ID


def dataset_id_for(route: str) -> str:
    return f"eia-{route_to_slug(route)}"


def is_leaf(response: dict) -> bool:
    return bool(response.get("data")) and bool(response.get("facets"))


def normalize_frequencies(freqs) -> list[str]:
    out = []
    for f in freqs or []:
        fid = f.get("id") or f.get("frequency")
        if fid in FREQ_MAP:
            out.append(FREQ_MAP[fid])
    return out


def build_dataset_yaml(route: str, response: dict, schema_rel: str) -> dict:
    facets = response.get("facets") or []
    data_cols = response.get("data") or []
    freqs = normalize_frequencies(response.get("frequency"))

    join_keys = ["DATE"]
    for f in facets:
        jk = FACET_JOIN_KEYS.get(f.get("id"))
        if jk and jk not in join_keys:
            join_keys.append(jk)

    entry_kind = "panel" if len(facets) >= 2 else "time-series"

    primary_key_tag = "_".join(
        (f.get("id") or "").upper() for f in facets if f.get("id")
    )[:60] or "SERIES"

    facet_entries = []
    for f in facets:
        fid = f.get("id")
        entry = {
            "name": fid,
            "description": (f.get("description") or "").strip(),
        }
        if fid in FACET_JOIN_KEYS:
            entry["join_key"] = FACET_JOIN_KEYS[fid]
        facet_entries.append(entry)

    measure_entries = []
    for c in data_cols:
        measure_entries.append({
            "name": c.get("id") or c.get("alias"),
            "unit": c.get("units") or "",
            "description": (c.get("description") or "").strip(),
        })

    name = response.get("name") or response.get("description") or route_to_slug(route)
    description = (response.get("description") or "").strip()

    out = {
        "id": dataset_id_for(route),
        "source_id": SOURCE_ID,
        "name": f"EIA {name}" if not str(name).lower().startswith("eia") else name,
        "entry_level": "dataset",
        "entry_kind": entry_kind,
        "api": {
            "route": route,
            "data_endpoint": f"{route}/data",
            "metadata_endpoint": route,
        },
        "time_index": "period",
        "time_grain": freqs or ["unknown"],
        "primary_keys": [f"EIA_ROUTE_PERIOD_{primary_key_tag}"],
        "join_keys": join_keys,
        "field_schema": schema_rel,
        "facets": facet_entries,
        "measures": measure_entries,
    }
    if description and description != name:
        out["notes"] = description
    return out


def build_schema_yaml(route: str, response: dict) -> dict:
    facets = response.get("facets") or []
    data_cols = response.get("data") or []

    fields = [{
        "name": "period",
        "type": "string",
        "description": "Observation period.",
        "role": "time_index",
        "join_key": "DATE",
        "required": True,
    }]

    for f in facets:
        fid = f.get("id")
        field = {
            "name": fid,
            "type": "string",
            "description": (f.get("description") or "").strip(),
            "role": "dimension",
            "required": True,
        }
        if fid in FACET_JOIN_KEYS:
            field["join_key"] = FACET_JOIN_KEYS[fid]
        fields.append(field)

    for c in data_cols:
        fields.append({
            "name": c.get("id") or c.get("alias"),
            "type": "number",
            "description": (c.get("description") or "").strip(),
            "role": "measure",
            "unit": c.get("units") or "",
            "required": False,
        })

    fields.append({
        "name": "units",
        "type": "string",
        "description": "Unit string returned by the API for this row.",
        "role": "metadata",
        "required": False,
    })

    return {
        "dataset_id": dataset_id_for(route),
        "source_id": SOURCE_ID,
        "fields": fields,
    }


def walk(api_key: str, route: str, leaves: list[tuple[str, dict]]) -> None:
    time.sleep(SLEEP_SECONDS)
    try:
        response = fetch_route(api_key, route)
    except Exception as e:
        print(f"  fetch failed at {route!r}: {e}", file=sys.stderr)
        return

    if is_leaf(response):
        leaves.append((route, response))
        # A route can have both data AND child routes; keep walking the children too.

    for child in response.get("routes") or []:
        cid = child.get("id")
        if not cid:
            continue
        next_route = f"{route}/{cid}" if route else f"/{cid}"
        walk(api_key, next_route, leaves)


def main():
    parser = argparse.ArgumentParser(
        description="Walk the EIA v2 API metadata tree and write dataset + schema manifests."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Walk the tree, print what would be written, but write nothing.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Stop after this many leaves (0 = no limit). Useful for testing.",
    )
    parser.add_argument(
        "--root",
        type=str,
        default="",
        help="Start route (e.g. /electricity). Defaults to the API root.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("EIA_API_KEY")
    if not api_key:
        print(
            "Set EIA_API_KEY. Register free at https://www.eia.gov/opendata/register.php",
            file=sys.stderr,
        )
        return 2

    project_root = Path(__file__).resolve().parent.parent
    catalog_root = project_root / "catalog" / SOURCE_ID
    datasets_dir = catalog_root / "datasets"
    schemas_dir = catalog_root / "schemas"
    datasets_dir.mkdir(parents=True, exist_ok=True)
    schemas_dir.mkdir(parents=True, exist_ok=True)

    existing = {p.stem for p in datasets_dir.glob("*.yaml")}
    print(f"existing datasets (will skip): {len(existing)}")

    leaves: list[tuple[str, dict]] = []
    walk(api_key, args.root, leaves)
    print(f"discovered {len(leaves)} leaf routes")

    if args.limit:
        leaves = leaves[: args.limit]
        print(f"limited to first {len(leaves)}")

    written = 0
    skipped = 0
    for route, response in leaves:
        slug = route_to_slug(route)
        if slug in existing:
            skipped += 1
            continue

        ds_path = datasets_dir / f"{slug}.yaml"
        sc_path = schemas_dir / f"{slug}.schema.yaml"
        schema_rel = f"catalog/{SOURCE_ID}/schemas/{slug}.schema.yaml"

        dataset_yaml = build_dataset_yaml(route, response, schema_rel)
        schema_yaml = build_schema_yaml(route, response)

        if args.dry_run:
            print(f"  would write {ds_path.relative_to(project_root)}")
            continue

        ds_path.write_text(yaml.safe_dump(dataset_yaml, sort_keys=False, allow_unicode=True))
        sc_path.write_text(yaml.safe_dump(schema_yaml, sort_keys=False, allow_unicode=True))
        written += 1
        print(f"  wrote {slug}")

    print(f"\nDone. {written} datasets written, {skipped} skipped (already hand-curated).")
    print("Next: python3 scripts/validate_entries.py && python3 scripts/generate.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
