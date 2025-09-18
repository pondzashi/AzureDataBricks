#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="${VENV_DIR:-.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[error] Python interpreter '$PYTHON_BIN' was not found. Install Python 3.9+ or set PYTHON_BIN to a valid interpreter." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[info] Creating virtual environment in '$VENV_DIR'"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "[info] Reusing existing virtual environment '$VENV_DIR'"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip

if [ -f requirements.txt ]; then
  python -m pip install -r requirements.txt
else
  echo "[warn] requirements.txt not found. No Python packages were installed." >&2
fi

echo
cat <<'MSG'
The virtual environment is ready.
Run 'source ${VENV_DIR}/bin/activate' to start using it in your current shell.
After activation you can configure the Databricks CLI with:

  databricks configure --token

Refer to README.md for the remaining setup steps.
MSG
