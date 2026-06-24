#!/usr/bin/env bash
# Run locally: bash publish.sh
#
# Reads GOOGLE_SERVICE_ACCOUNT_JSON from macOS Keychain.
# To store the key the first time:
#   security add-generic-password -a "datasources" -s "google-sa-datasets-498814" -w "$(cat ~/Downloads/your-key.json)"
#
# GOOGLE_SHEET_ID is read from .env (gitignored).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: .env not found. Copy .env.example to .env and fill in GOOGLE_SHEET_ID." >&2
  exit 1
fi

source "$ENV_FILE"

if [[ -z "${GOOGLE_SHEET_ID:-}" ]]; then
  echo "Error: GOOGLE_SHEET_ID not set in .env" >&2
  exit 1
fi

export GOOGLE_SHEET_ID

echo "Reading service account key from Keychain..."
GOOGLE_SERVICE_ACCOUNT_JSON="$(security find-generic-password -a "datasources" -s "google-sa-datasets-498814" -w 2>/dev/null | xxd -r -p || true)"

if [[ -z "$GOOGLE_SERVICE_ACCOUNT_JSON" ]]; then
  echo "Error: key not found in Keychain." >&2
  echo "Store it with:" >&2
  echo '  security add-generic-password -a "datasources" -s "google-sa-datasets-498814" -w "$(cat ~/Downloads/your-key.json)"' >&2
  exit 1
fi
export GOOGLE_SERVICE_ACCOUNT_JSON

echo "Validating entries..."
python3 "$SCRIPT_DIR/scripts/validate_entries.py"

echo "Generating outputs..."
python3 "$SCRIPT_DIR/scripts/generate.py"

echo "Publishing to Google Sheet..."
python3 "$SCRIPT_DIR/scripts/publish_to_sheet.py"

echo "Done."
