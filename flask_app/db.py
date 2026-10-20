"""Small SQLite access layer with JSON-safe conversion."""

from __future__ import annotations

import math
import sqlite3
from typing import Any

import numpy as np
import pandas as pd
from flask import jsonify

from .config import DB_PATH


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def query(sql: str, params=()) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def one(sql: str, params=()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def clean(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return round(value, 4)
    if isinstance(value, (pd.Timestamp,)):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


def ok(data: Any = None, msg: str = "ok"):
    return jsonify({"code": 0, "msg": msg, "data": clean(data)})


def fail(msg: str, code: int = 400, http_status: int = 200):
    return jsonify({"code": code, "msg": msg, "data": None}), http_status

