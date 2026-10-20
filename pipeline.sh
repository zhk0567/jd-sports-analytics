#!/usr/bin/env bash
set -euo pipefail
PY=${PY:-.venv/bin/python}
python_bin=$PY
[ -x "$python_bin" ] || python_bin=python
"$python_bin" scripts/t2_generate_data.py
"$python_bin" scripts/t2_build_warehouse.py
"$python_bin" scripts/t2_train_models.py
"$python_bin" scripts/t2_generate_assets.py
"$python_bin" scripts/t2_generate_docs.py
"$python_bin" scripts/t2_validate.py
echo "pipeline finished: http://127.0.0.1:5000"
