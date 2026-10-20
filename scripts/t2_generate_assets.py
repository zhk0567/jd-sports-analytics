"""Generate MySQL/Hive DDL, DataX jobs and one-click pipeline wrappers."""

from __future__ import annotations

import json
from pathlib import Path

from t2_common import (
    ADS_TABLES,
    DATAX_EXPORT_DIR,
    DATAX_IMPORT_DIR,
    DB_PATH,
    DIM_TABLES,
    DWD_TABLES,
    DWS_TABLES,
    ODS_TABLES,
    SQL_DIR,
    connect,
    ensure_dirs,
    sqlite_columns,
    table,
)


ID_COLUMNS = {
    "user_id", "product_id", "category_id", "brand_id", "shop_id", "order_id",
    "detail_id", "payment_id", "refund_id", "logistics_id", "review_id",
    "cart_id", "log_id", "date_key", "region_id",
}


def mysql_type(sqlite_type: str, name: str) -> str:
    t = (sqlite_type or "TEXT").upper()
    if "INT" in t:
        return "BIGINT"
    if any(x in t for x in ("REAL", "FLOA", "DOUB", "NUM")):
        return "DECIMAL(18,4)"
    if any(x in name for x in ("content", "url", "remark", "definition", "path", "name")):
        return "TEXT"
    return "VARCHAR(255)"


def hive_type(sqlite_type: str) -> str:
    t = (sqlite_type or "TEXT").upper()
    if "INT" in t:
        return "BIGINT"
    if any(x in t for x in ("REAL", "FLOA", "DOUB", "NUM")):
        return "DOUBLE"
    return "STRING"


def columns_for(conn, name):
    return sqlite_columns(conn, name)


def mysql_ddl(conn, layer: str, names: list[str], database: str) -> str:
    lines = [f"CREATE DATABASE IF NOT EXISTS `{database}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;", f"USE `{database}`;", ""]
    for name in names:
        tname = table(layer, name)
        cols = columns_for(conn, tname)
        defs = []
        for col in cols:
            col_def = f"  `{col['name']}` {mysql_type(col['type'], col['name'])}"
            if col["name"] == "stat_date":
                col_def += " NOT NULL"
            defs.append(col_def)
        pk = [c["name"] for c in cols if c["name"] in ID_COLUMNS]
        has_pk = bool(pk) and layer in {"dim", "dwd"}
        if has_pk:
            defs.append(f"  PRIMARY KEY (`{pk[0]}`)")
        for c in cols:
            if c["name"] in ID_COLUMNS and not (has_pk and c["name"] == pk[0]):
                defs.append(f"  KEY `idx_{tname}_{c['name']}` (`{c['name']}`)")
        lines.append(f"DROP TABLE IF EXISTS `{tname}`;")
        lines.append(f"CREATE TABLE `{tname}` (\n" + ",\n".join(defs) + f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 {layer.upper()} {name}';")
        lines.append("")
    return "\n".join(lines)


def hive_ddl(conn, layer: str, names: list[str]) -> str:
    lines = ["CREATE DATABASE IF NOT EXISTS t2_ecommerce;", "USE t2_ecommerce;", ""]
    for name in names:
        tname = table(layer, name)
        cols = columns_for(conn, tname)
        if layer == "ods":
            defs = [f"  `{c['name']}` STRING COMMENT '{c['name']}'" for c in cols]
            lines.append(
                f"DROP TABLE IF EXISTS `{tname}`;\n"
                f"CREATE EXTERNAL TABLE `{tname}` (\n" + ",\n".join(defs) + "\n)"
                f" COMMENT 't2 运动电商 ODS {name}' ROW FORMAT DELIMITED FIELDS TERMINATED BY ','"
                f" STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/{tname}';"
            )
        else:
            defs = [f"  `{c['name']}` {hive_type(c['type'])} COMMENT '{c['name']}'" for c in cols]
            partition = ""
            if any(c["name"] == "stat_date" for c in cols):
                partition = "\nPARTITIONED BY (`dt` STRING COMMENT '分区日期')"
            lines.append(
                f"DROP TABLE IF EXISTS `{tname}`;\n"
                f"CREATE TABLE `{tname}` (\n" + ",\n".join(defs) + "\n)"
                f" COMMENT 't2 运动电商 {layer.upper()} {name}'{partition}"
                f" STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');"
            )
        lines.append("")
    return "\n".join(lines)


def datax_columns(conn, name):
    return [c["name"] for c in columns_for(conn, name)]


def write_import_jobs(conn):
    DATAX_IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    for name in ODS_TABLES:
        cols = datax_columns(conn, table("ods", name))
        mysql_job = {
            "job": {
                "setting": {"speed": {"channel": 3}},
                "content": [{
                    "reader": {"name": "txtfilereader", "parameter": {
                        "path": [f"./data/ods_csv/{name}.csv"], "encoding": "UTF-8",
                        "column": cols, "fieldDelimiter": ",", "skipHeader": True,
                    }},
                    "writer": {"name": "mysqlwriter", "parameter": {
                        "writeMode": "replace", "username": "root", "password": "root",
                        "column": cols,
                        "connection": [{"jdbcUrl": "jdbc:mysql://127.0.0.1:3306/t2_ecommerce_ods?useUnicode=true&characterEncoding=utf8", "table": [table("ods", name)]}],
                    }},
                }],
            }
        }
        (DATAX_IMPORT_DIR / f"mysql_{name}.json").write_text(json.dumps(mysql_job, ensure_ascii=False, indent=2), encoding="utf-8")
        hive_job = {
            "job": {
                "setting": {"speed": {"channel": 3}},
                "content": [{
                    "reader": {"name": "txtfilereader", "parameter": {
                        "path": [f"./data/ods_csv/{name}.csv"], "encoding": "UTF-8",
                        "column": cols, "fieldDelimiter": ",", "skipHeader": True,
                    }},
                    "writer": {"name": "hdfswriter", "parameter": {
                        "defaultFS": "hdfs://localhost:9000", "fileType": "text",
                        "path": f"/user/hive/warehouse/t2_ecommerce.db/{table('ods', name)}",
                        "fileName": f"{name}.csv", "writeMode": "append",
                        "fieldDelimiter": ",", "column": [{"name": c, "type": "string"} for c in cols],
                    }},
                }],
            }
        }
        (DATAX_IMPORT_DIR / f"hive_{name}.json").write_text(json.dumps(hive_job, ensure_ascii=False, indent=2), encoding="utf-8")


def write_export_jobs(conn):
    DATAX_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    for name in ADS_TABLES:
        tname = table("ads", name)
        cols = datax_columns(conn, tname)
        job = {
            "job": {
                "setting": {"speed": {"channel": 2}},
                "content": [{
                    "reader": {"name": "hdfsreader", "parameter": {
                        "defaultFS": "hdfs://localhost:9000", "fileType": "orc",
                        "path": f"/user/hive/warehouse/t2_ecommerce.db/{tname}",
                        "column": ["*"], "encoding": "UTF-8",
                    }},
                    "writer": {"name": "mysqlwriter", "parameter": {
                        "writeMode": "replace", "username": "root", "password": "root",
                        "column": cols,
                        "connection": [{"jdbcUrl": "jdbc:mysql://127.0.0.1:3306/t2_ecommerce_ads?useUnicode=true&characterEncoding=utf8", "table": [tname]}],
                    }},
                }],
            }
        }
        (DATAX_EXPORT_DIR / f"{name}.json").write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")


def write_scripts():
    import_sh = """#!/usr/bin/env bash
set -euo pipefail
DATAX_BIN=${DATAX_BIN:-datax.py}
for f in config/import/*.json; do
  echo "[DataX] $f"
  python "$DATAX_BIN" "$f"
done
"""
    export_sh = """#!/usr/bin/env bash
set -euo pipefail
DATAX_BIN=${DATAX_BIN:-datax.py}
for f in config/export/*.json; do
  echo "[DataX] $f"
  python "$DATAX_BIN" "$f"
done
"""
    import_ps1 = """param([string]$Datax = "datax.py")
$ErrorActionPreference = "Stop"
Get-ChildItem config/import/*.json | ForEach-Object {
  Write-Host "[DataX] $($_.FullName)"
  python $Datax $_.FullName
}
"""
    export_ps1 = """param([string]$Datax = "datax.py")
$ErrorActionPreference = "Stop"
Get-ChildItem config/export/*.json | ForEach-Object {
  Write-Host "[DataX] $($_.FullName)"
  python $Datax $_.FullName
}
"""
    (SQL_DIR.parent / "scripts" / "import_all.sh").write_text(import_sh, encoding="utf-8")
    (SQL_DIR.parent / "scripts" / "export_all.sh").write_text(export_sh, encoding="utf-8")
    (SQL_DIR.parent / "scripts" / "import_all.ps1").write_text(import_ps1, encoding="utf-8")
    (SQL_DIR.parent / "scripts" / "export_all.ps1").write_text(export_ps1, encoding="utf-8")

    pipeline_ps1 = """param([string]$Python = ".venv\\Scripts\\python.exe")
$ErrorActionPreference = "Stop"
$steps = @(
  "scripts/t2_generate_data.py",
  "scripts/t2_build_warehouse.py",
  "scripts/t2_train_models.py",
  "scripts/t2_generate_assets.py",
  "scripts/t2_generate_docs.py",
  "scripts/t2_validate.py"
)
foreach ($step in $steps) {
  Write-Host "==> $step"
  & $Python $step
  if ($LASTEXITCODE -ne 0) { throw "step failed: $step" }
}
Write-Host "pipeline finished: http://127.0.0.1:5000"
"""
    pipeline_bat = """@echo off
setlocal
set PY=.venv\\Scripts\\python.exe
%PY% scripts\\t2_generate_data.py || exit /b 1
%PY% scripts\\t2_build_warehouse.py || exit /b 1
%PY% scripts\\t2_train_models.py || exit /b 1
%PY% scripts\\t2_generate_assets.py || exit /b 1
%PY% scripts\\t2_generate_docs.py || exit /b 1
%PY% scripts\\t2_validate.py || exit /b 1
echo pipeline finished: http://127.0.0.1:5000
"""
    pipeline_sh = """#!/usr/bin/env bash
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
"""
    root = SQL_DIR.parent
    (root / "pipeline.ps1").write_text(pipeline_ps1, encoding="utf-8")
    (root / "pipeline.bat").write_text(pipeline_bat, encoding="utf-8")
    (root / "pipeline.sh").write_text(pipeline_sh, encoding="utf-8")


def write_docs_placeholder():
    pipeline_doc = """# 数据管道运行说明

## 本地演示（SQLite）

```powershell
.\\pipeline.ps1
.venv\\Scripts\\python.exe -m flask --app flask_app.app run --port 5000
```

打开 <http://127.0.0.1:5000>。本地演示引擎使用 SQLite，保证没有 Hadoop 环境也能完整跑通。

## 实验环境（MySQL + Hive + DataX）

1. 执行 `sql/init_databases.sql` 建库；
2. 执行 `sql/ods/*_mysql.sql`、`sql/ods/*_hive.sql` 等建表脚本；
3. 执行 `scripts/import_all.ps1`（或 `.sh`）导入 13 张 ODS 表；
4. 在 Hive 中执行 `sql/etl/*.sql` 完成 DIM/DWD/DWS/ADS 计算；
5. 执行 `scripts/export_all.ps1` 将 ADS 导出到 MySQL；
6. 启动 Flask API 和大屏。

> DataX 任务中的 `root/root`、`hdfs://localhost:9000` 为演示默认值，按虚拟机实际环境修改 `config/import` 与 `config/export`。
"""
    (SQL_DIR.parent / "doc" / "数据管道运行说明.md").write_text(pipeline_doc, encoding="utf-8")


def main():
    ensure_dirs()
    if not DB_PATH.exists():
        raise SystemExit("warehouse db missing; run t2_build_warehouse.py first")
    conn = connect()
    layer_specs = [
        ("ods", ODS_TABLES, "t2_ecommerce_ods"),
        ("dim", DIM_TABLES, "t2_ecommerce_ads"),
        ("dwd", DWD_TABLES, "t2_ecommerce_ads"),
        ("dws", DWS_TABLES, "t2_ecommerce_ads"),
        ("ads", ADS_TABLES, "t2_ecommerce_ads"),
    ]
    for layer, names, db in layer_specs:
        folder = SQL_DIR / layer
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"t2_{layer}_mysql.sql").write_text(mysql_ddl(conn, layer, names, db), encoding="utf-8")
        (folder / f"t2_{layer}_hive.sql").write_text(hive_ddl(conn, layer, names), encoding="utf-8")
    (SQL_DIR / "init_databases.sql").write_text(
        "CREATE DATABASE IF NOT EXISTS t2_ecommerce_ods DEFAULT CHARACTER SET utf8mb4;\n"
        "CREATE DATABASE IF NOT EXISTS t2_ecommerce_ads DEFAULT CHARACTER SET utf8mb4;\n"
        "CREATE DATABASE IF NOT EXISTS t2_ecommerce DEFAULT CHARACTER SET utf8mb4;\n",
        encoding="utf-8",
    )
    write_import_jobs(conn)
    write_export_jobs(conn)
    write_scripts()
    write_docs_placeholder()
    conn.close()
    print(json.dumps({
        "sql_files": [str(p.relative_to(SQL_DIR.parent)) for p in SQL_DIR.rglob("*.sql")],
        "import_jobs": len(list(DATAX_IMPORT_DIR.glob("*.json"))),
        "export_jobs": len(list(DATAX_EXPORT_DIR.glob("*.json"))),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
