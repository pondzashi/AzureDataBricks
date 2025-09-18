#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${DATA_DIR:-data}"
DBFS_TARGET_ROOT="${DBFS_TARGET_ROOT:-dbfs:/FileStore/tables/sales_demo}"

if ! command -v databricks >/dev/null 2>&1; then
  echo "[error] databricks CLI not found in PATH. Activate the virtual environment and install requirements first." >&2
  exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
  echo "[error] DATA_DIR '$DATA_DIR' does not exist." >&2
  exit 1
fi

echo "[info] Ensuring target directory $DBFS_TARGET_ROOT exists"
databricks fs mkdirs "$DBFS_TARGET_ROOT"

echo "[info] Uploading CSV files from $DATA_DIR"
for file in "$DATA_DIR"/*.csv; do
  [ -e "$file" ] || continue
  base_name=$(basename "$file")
  target_path="$DBFS_TARGET_ROOT/$base_name"
  echo "  -> $base_name"
  databricks fs cp "$file" "$target_path" --overwrite
done

databricks fs ls "$DBFS_TARGET_ROOT"
