"""Shared helpers for the group-2 sports e-commerce analytics platform.

The local demo runs on SQLite so it can be reproduced on a clean Windows or
Linux machine without a Hadoop cluster. MySQL/Hive DDL and DataX jobs are
generated from the same schema registry for the lab VM.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ODS_DIR = DATA_DIR / "ods_csv"
DB_PATH = DATA_DIR / "t2_ecommerce.db"
MODEL_DIR = ROOT / "models"
DOC_DIR = ROOT / "doc"
SQL_DIR = ROOT / "sql"
DATAX_IMPORT_DIR = ROOT / "config" / "import"
DATAX_EXPORT_DIR = ROOT / "config" / "export"
DASHBOARD_DIR = ROOT / "dashboard"

GROUP_NO = 2
GROUP_NAME = "运动"
PREFIX = "t2"
SEED = 2

# 180 days are used so that both 618 and Double 11 fall inside the fact period.
# The dashboard and the 90-day ADS trend intentionally show the most recent
# 90 days, which satisfies the "90-day daily GMV" requirement while retaining
# both promotion peaks for event comparison.
START_DATE = "2025-05-16"
END_DATE = "2025-11-11"

ODS_TABLES = [
    "user_info",
    "category",
    "product_info",
    "brand_info",
    "shop_info",
    "order_info",
    "order_detail",
    "payment_info",
    "refund_info",
    "logistics_info",
    "review_info",
    "cart_info",
    "search_log",
]

DIM_TABLES = [
    "user_info",
    "product_info",
    "category",
    "date",
    "region",
    "brand",
]

DWD_TABLES = [
    "order",
    "order_detail",
    "payment",
    "refund",
    "logistics",
    "review",
    "cart",
    "search_log",
    "user_action",
    "inventory",
]

DWS_TABLES = [
    "user_user_1d",
    "user_user_nd",
    "user_user_total",
    "user_rfm",
    "user_retention_1d",
    "traffic_page_1d",
    "traffic_user_1d",
    "user_funnel_1d",
    "trade_product_1d",
    "trade_product_nd",
    "trade_category_1d",
    "trade_category_nd",
    "trade_brand_1d",
    "trade_region_1d",
    "trade_region_nd",
    "user_region_total",
    "traffic_region_1d",
    "promo_activity_1d",
]

ADS_TABLES = [
    "gmv_total",
    "gmv_daily",
    "region_sales",
    "city_sales",
    "category_proportion",
    "brand_rank",
    "user_funnel",
    "user_retention",
    "user_rfm",
    "product_rank",
    "product_stock_warn",
    "core_kpi",
    "kpi_trend",
    "inventory_alarm",
    "sales_forecast",
    "user_churn_predict",
]


def table(layer: str, name: str) -> str:
    return f"{PREFIX}_{layer}_{name}"


def connect(path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def read_sql(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> list[dict]:
    return [dict(row) for row in conn.execute(sql, tuple(params)).fetchall()]


def scalar(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> Any:
    row = conn.execute(sql, tuple(params)).fetchone()
    return None if row is None else row[0]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sqlite_columns(conn: sqlite3.Connection, name: str) -> list[dict]:
    return [dict(r) for r in conn.execute(f"PRAGMA table_info({name})").fetchall()]


def ensure_dirs() -> None:
    for path in (
        DATA_DIR,
        ODS_DIR,
        MODEL_DIR,
        DOC_DIR,
        SQL_DIR,
        DATAX_IMPORT_DIR,
        DATAX_EXPORT_DIR,
        DASHBOARD_DIR / "static",
        ROOT / "dashboard" / "dist",
        ROOT / "flask_app" / "blueprints",
    ):
        path.mkdir(parents=True, exist_ok=True)


def pct(numerator: float, denominator: float, digits: int = 2) -> float:
    if not denominator:
        return 0.0
    return round(numerator / denominator * 100, digits)


def safe_div(numerator: float, denominator: float) -> float:
    return 0.0 if not denominator else numerator / denominator
