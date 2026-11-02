#!/usr/bin/env sh
set -eu
FROM_LANG="${1:-en}"
TO_LANG="${2:-zh}"
REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 -m venv "$REPO_ROOT/.venv"
"$REPO_ROOT/.venv/bin/python" -m pip install --upgrade pip
"$REPO_ROOT/.venv/bin/python" -m pip install -r "$REPO_ROOT/requirements.txt"
"$REPO_ROOT/.venv/bin/python" "$REPO_ROOT/local-text-translation/scripts/install_model.py" --from "$FROM_LANG" --to "$TO_LANG"
printf '%s\n' "Ready. Translation runs locally with:"
printf '  %s\n' ".venv/bin/python local-text-translation/scripts/local_translate.py INPUT -o OUTPUT --from $FROM_LANG --to $TO_LANG"

