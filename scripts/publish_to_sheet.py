#!/usr/bin/env python3
"""
Publish generated/dataset-table.csv to a Google Sheet.

The Sheet is a downstream render target, not a source of truth. Each run clears
the configured range and overwrites it with the current CSV contents.

Required env vars:
  GOOGLE_SERVICE_ACCOUNT_JSON  — full JSON of a service account with editor
                                 access to the target Sheet
  GOOGLE_SHEET_ID              — the spreadsheet ID (the long token in the URL)
Optional env vars:
  GOOGLE_SHEET_RANGE           — A1 range to clear and write (default: "Sheet1")

Run locally:
  export GOOGLE_SERVICE_ACCOUNT_JSON="$(cat ~/.config/datasources-sa.json)"
  export GOOGLE_SHEET_ID="..."
  python3 scripts/publish_to_sheet.py

In GitHub Actions: store GOOGLE_SERVICE_ACCOUNT_JSON and GOOGLE_SHEET_ID as
repo secrets (Settings → Secrets and variables → Actions) and reference via
${{ secrets.NAME }} in the workflow.

Dependencies:
  pip install google-api-python-client google-auth
"""

import csv
import json
import os
import sys
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print(
        "Missing dependency. Install with: pip install google-api-python-client google-auth",
        file=sys.stderr,
    )
    sys.exit(2)


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "generated" / "dataset-table.csv"

    if not csv_path.exists():
        print(
            f"Missing {csv_path.relative_to(project_root)}. Run scripts/generate.py first.",
            file=sys.stderr,
        )
        return 2

    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    sheet_range = os.environ.get("GOOGLE_SHEET_RANGE", "Sheet1")

    missing = []
    if not sa_json:
        missing.append("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sheet_id:
        missing.append("GOOGLE_SHEET_ID")
    if missing:
        print(f"Required env vars not set: {', '.join(missing)}", file=sys.stderr)
        return 2

    with csv_path.open() as f:
        rows = list(csv.reader(f))
    print(f"Loaded {len(rows)} rows from {csv_path.relative_to(project_root)}")

    credentials = service_account.Credentials.from_service_account_info(
        json.loads(sa_json), scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    sheets = service.spreadsheets().values()

    sheets.clear(spreadsheetId=sheet_id, range=sheet_range).execute()
    print(f"Cleared range '{sheet_range}'")

    result = sheets.update(
        spreadsheetId=sheet_id,
        range=sheet_range,
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    updated_rows = result.get("updatedRows", 0)
    updated_cols = result.get("updatedColumns", 0)
    print(f"Wrote {updated_rows} rows × {updated_cols} cols to '{sheet_range}'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
