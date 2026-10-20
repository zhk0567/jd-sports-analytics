from __future__ import annotations

import csv
from pathlib import Path

from flask import Blueprint

from ..config import ROOT
from ..db import ok, query


bp = Blueprint("ml", __name__)


@bp.get("/sales_forecast")
def sales_forecast():
    return ok(query("SELECT * FROM t2_ads_sales_forecast ORDER BY forecast_date"))


@bp.get("/sales_forecast_compare")
def sales_forecast_compare():
    path = ROOT / "models" / "t2_sales_forecast_holdout.csv"
    rows = []
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
    return ok({
        "holdout": rows,
        "forecast": query("SELECT * FROM t2_ads_sales_forecast ORDER BY forecast_date"),
    })

