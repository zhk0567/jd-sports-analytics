@echo off
setlocal
set PY=.venv\Scripts\python.exe
%PY% scripts\t2_generate_data.py || exit /b 1
%PY% scripts\t2_build_warehouse.py || exit /b 1
%PY% scripts\t2_train_models.py || exit /b 1
%PY% scripts\t2_generate_assets.py || exit /b 1
%PY% scripts\t2_generate_docs.py || exit /b 1
%PY% scripts\t2_validate.py || exit /b 1
echo pipeline finished: http://127.0.0.1:5000
