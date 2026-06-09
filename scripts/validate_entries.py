#!/usr/bin/env python3
"""
Validate every entries/**/*.md against schema/entry.schema.yaml.

Hard errors:
- JSON Schema conformance
- id matches filename slug
- domain matches parent folder
- join_keys reference schema/join-keys.yaml
- mcp-exists requires mcp_maturity and mcp_package
- last_verified is a valid ISO date

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


def main():
    project_root = Path(__file__).resolve().parent.parent
    schema_dir = project_root / "schema"
    entries_root = project_root / "entries"

    entry_schema = yaml.safe_load((schema_dir / "entry.schema.yaml").read_text())
    registry = yaml.safe_load((schema_dir / "join-keys.yaml").read_text())

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

    print(f"\nChecked {len(entry_files)} entries: "
          f"{failed_files} failed, {total_errors} errors, {total_warnings} warnings.")
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
