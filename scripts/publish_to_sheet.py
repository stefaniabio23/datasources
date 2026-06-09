#!/usr/bin/env python3
"""
Publish generated CSVs to a Google Sheet, one tab per CSV.

  generated/sources.csv     → tab "Sources"
  generated/join-keys.csv   → tab "JoinKeys"

Tabs are created if missing. Each run clears the existing tab content and writes
the current CSV. The repo stays canonical; the Sheet is downstream.

Required env vars:
  GOOGLE_SERVICE_ACCOUNT_JSON  — full JSON of a service account with editor
                                 access to the target Sheet
  GOOGLE_SHEET_ID              — the spreadsheet ID

Run locally:
  export GOOGLE_SERVICE_ACCOUNT_JSON="$(cat ~/.config/datasources-sa.json)"
  export GOOGLE_SHEET_ID="..."
  python3 scripts/publish_to_sheet.py

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

TABS = [
    ("Sources", "sources.csv"),
    ("JoinKeys", "join-keys.csv"),
]


def get_or_create_tab(service, sheet_id, title):
    meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    existing = {s["properties"]["title"] for s in meta["sheets"]}
    if title in existing:
        return
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
    ).execute()
    print(f"  created tab '{title}'")


def main():
    project_root = Path(__file__).resolve().parent.parent
    generated_root = project_root / "generated"

    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")

    missing = []
    if not sa_json:
        missing.append("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sheet_id:
        missing.append("GOOGLE_SHEET_ID")
    if missing:
        print(f"Required env vars not set: {', '.join(missing)}", file=sys.stderr)
        return 2

    credentials = service_account.Credentials.from_service_account_info(
        json.loads(sa_json), scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    values = service.spreadsheets().values()

    for title, csv_name in TABS:
        csv_path = generated_root / csv_name
        if not csv_path.exists():
            print(f"  skip {title}: {csv_path.relative_to(project_root)} not found")
            continue

        with csv_path.open() as f:
            rows = list(csv.reader(f))

        get_or_create_tab(service, sheet_id, title)

        values.clear(spreadsheetId=sheet_id, range=title).execute()
        if not rows:
            print(f"  {title}: 0 rows (empty)")
            continue

        result = values.update(
            spreadsheetId=sheet_id,
            range=f"{title}!A1",
            valueInputOption="RAW",
            body={"values": rows},
        ).execute()
        print(
            f"  {title}: wrote {result.get('updatedRows', 0)} rows × "
            f"{result.get('updatedColumns', 0)} cols"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
