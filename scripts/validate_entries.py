#!/usr/bin/env python3
"""
Validate every entries/**/*.md and catalog/**/*.yaml against the relevant schemas.

Entry checks (hard errors):
- JSON Schema conformance
- id matches filename slug
- domain matches parent folder
- join_keys reference schema/join-keys.yaml
- mcp-exists requires mcp_maturity and mcp_package
- last_verified is a valid ISO date

Catalog checks (hard errors):
- catalog/<id>/source.yaml validates against schema/source.schema.yaml AND id matches dir name
- catalog/<id>/datasets/*.yaml validates against schema/dataset.schema.yaml AND source_id matches an existing source
- catalog/<id>/schemas/*.schema.yaml validates against schema/field-schema.schema.yaml AND source_id matches an existing source

Soft checks (warnings):
- Required body H2 headings (Why this source matters, Agent use cases, Join strategy,
  Access notes, MCP / connector notes, Review notes)
- notes field under 500 chars

Exit non-zero on any hard error; warnings do not fail.

Run from the project root:
    python3 scripts/validate_entries.py

Dependencies:
    pip install jsonschema pyyaml
"""

import re
import sys
from datetime import date
from pathlib import Path

try:
    import jsonschema
    import yaml
except ImportError:
    print("Missing dependency. Install with: pip install jsonschema pyyaml", file=sys.stderr)
    sys.exit(2)


REQUIRED_BODY_HEADINGS = [
    "Why this source matters",
    "Agent use cases",
    "Join strategy",
    "Access notes",
    "MCP / connector notes",
    "Review notes",
]


def parse_entry(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter (file must start with ---)")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("YAML frontmatter not closed (expected closing ---)")
    fm = yaml.safe_load(text[4:end])
    body = text[end + 5:]
    if not isinstance(fm, dict):
        raise ValueError("YAML frontmatter must be a mapping")
    return fm, body


def normalize(obj):
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize(v) for v in obj]
    if isinstance(obj, date):
        return obj.isoformat()
    return obj


def check_entry(path, schema, registry):
    errors, warnings = [], []
    try:
        fm, body = parse_entry(path)
    except (yaml.YAMLError, ValueError) as e:
        return [f"YAML parse error: {e}"], []

    fm_norm = normalize(fm)
    for err in sorted(jsonschema.Draft202012Validator(schema).iter_errors(fm_norm), key=str):
        loc = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"schema {loc}: {err.message}")

    expected_id = path.stem
    if fm.get("id") != expected_id:
        errors.append(f"id '{fm.get('id')}' does not match filename slug '{expected_id}'")

    expected_domain = path.parent.name
    if fm.get("domain") != expected_domain:
        errors.append(f"domain '{fm.get('domain')}' does not match parent folder '{expected_domain}'")

    for key in fm.get("join_keys") or []:
        if key not in registry:
            errors.append(f"join_key '{key}' not in schema/join-keys.yaml")

    if fm.get("mcp_status") == "mcp-exists":
        if not fm.get("mcp_maturity"):
            errors.append("mcp_status is mcp-exists but mcp_maturity is missing")
        if not fm.get("mcp_package"):
            errors.append("mcp_status is mcp-exists but mcp_package is missing or empty")

    lv = fm.get("last_verified")
    if isinstance(lv, str):
        try:
            date.fromisoformat(lv)
        except ValueError:
            errors.append(f"last_verified '{lv}' is not a valid ISO date")
    elif isinstance(lv, date):
        pass
    elif lv is not None:
        errors.append(f"last_verified has wrong type: {type(lv).__name__}")

    at = fm.get("access_test") or {}
    if at and not (at.get("command") or "").strip():
        errors.append("access_test is present but access_test.command is empty")

    found_headings = re.findall(r"^## (.+?)\s*$", body, re.MULTILINE)
    missing = [h for h in REQUIRED_BODY_HEADINGS if h not in found_headings]
    if missing:
        warnings.append(f"missing body headings: {missing}")
    else:
        indices = [found_headings.index(h) for h in REQUIRED_BODY_HEADINGS]
        if indices != sorted(indices):
            warnings.append("required body headings present but not in canonical order")

    notes = fm.get("notes")
    if isinstance(notes, str) and len(notes) > 500:
        warnings.append(f"notes is {len(notes)} chars; recommend under 500")

    return errors, warnings


def check_catalog_yaml(path, schema, dir_name=None, source_ids=None):
    errors = []
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]
    if not isinstance(data, dict):
        return ["root must be a mapping"]

    for err in sorted(jsonschema.Draft202012Validator(schema).iter_errors(normalize(data)), key=str):
        loc = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"schema {loc}: {err.message}")

    if dir_name is not None and data.get("id") != dir_name:
        errors.append(f"id '{data.get('id')}' does not match directory name '{dir_name}'")

    if source_ids is not None and data.get("source_id") not in source_ids:
        errors.append(f"source_id '{data.get('source_id')}' not found in catalog/")

    return errors


def main():
    project_root = Path(__file__).resolve().parent.parent
    schema_dir = project_root / "schema"
    entries_root = project_root / "entries"
    catalog_root = project_root / "catalog"

    entry_schema = yaml.safe_load((schema_dir / "entry.schema.yaml").read_text())
    registry = yaml.safe_load((schema_dir / "join-keys.yaml").read_text())
    source_schema = yaml.safe_load((schema_dir / "source.schema.yaml").read_text())
    dataset_schema = yaml.safe_load((schema_dir / "dataset.schema.yaml").read_text())
    field_schema_schema = yaml.safe_load((schema_dir / "field-schema.schema.yaml").read_text())

    # ---- entries -----------------------------------------------------------
    entry_files = sorted(entries_root.rglob("*.md"))
    total_errors = 0
    total_warnings = 0
    failed_files = 0

    for path in entry_files:
        rel = path.relative_to(project_root)
        errors, warnings = check_entry(path, entry_schema, registry)
        if errors:
            failed_files += 1
            total_errors += len(errors)
            print(f"\n[FAIL] {rel}")
            for e in errors:
                print(f"  ERROR: {e}")
            for w in warnings:
                print(f"  warn:  {w}")
        elif warnings:
            total_warnings += len(warnings)
            print(f"[WARN] {rel}")
            for w in warnings:
                print(f"  warn: {w}")
        else:
            print(f"[OK]   {rel}")

    # ---- catalog -----------------------------------------------------------
    catalog_sources = {}
    catalog_files_count = 0
    if catalog_root.exists():
        for src_dir in sorted(catalog_root.iterdir()):
            if not src_dir.is_dir():
                continue
            source_yaml = src_dir / "source.yaml"
            if not source_yaml.exists():
                continue
            catalog_files_count += 1
            errs = check_catalog_yaml(source_yaml, source_schema, dir_name=src_dir.name)
            rel = source_yaml.relative_to(project_root)
            if errs:
                failed_files += 1
                total_errors += len(errs)
                print(f"\n[FAIL] {rel}")
                for e in errs:
                    print(f"  ERROR: {e}")
            else:
                print(f"[OK]   {rel}")
            try:
                catalog_sources[src_dir.name] = yaml.safe_load(source_yaml.read_text())
            except yaml.YAMLError:
                pass

        for src_dir in sorted(catalog_root.iterdir()):
            if not src_dir.is_dir():
                continue
            datasets_dir = src_dir / "datasets"
            if datasets_dir.exists():
                for path in sorted(datasets_dir.glob("*.yaml")):
                    catalog_files_count += 1
                    rel = path.relative_to(project_root)
                    errs = check_catalog_yaml(path, dataset_schema, source_ids=set(catalog_sources.keys()))
                    if errs:
                        failed_files += 1
                        total_errors += len(errs)
                        print(f"\n[FAIL] {rel}")
                        for e in errs:
                            print(f"  ERROR: {e}")
                    else:
                        print(f"[OK]   {rel}")

            schemas_dir = src_dir / "schemas"
            if schemas_dir.exists():
                for path in sorted(schemas_dir.glob("*.schema.yaml")):
                    catalog_files_count += 1
                    rel = path.relative_to(project_root)
                    errs = check_catalog_yaml(path, field_schema_schema, source_ids=set(catalog_sources.keys()))
                    if errs:
                        failed_files += 1
                        total_errors += len(errs)
                        print(f"\n[FAIL] {rel}")
                        for e in errs:
                            print(f"  ERROR: {e}")
                    else:
                        print(f"[OK]   {rel}")

    total_files = len(entry_files) + catalog_files_count
    print(f"\nChecked {total_files} files ({len(entry_files)} entries, {catalog_files_count} catalog): "
          f"{failed_files} failed, {total_errors} errors, {total_warnings} warnings.")
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
