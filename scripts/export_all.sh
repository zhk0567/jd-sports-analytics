#!/usr/bin/env bash
set -euo pipefail
DATAX_BIN=${DATAX_BIN:-datax.py}
for f in config/export/*.json; do
  echo "[DataX] $f"
  python "$DATAX_BIN" "$f"
done
