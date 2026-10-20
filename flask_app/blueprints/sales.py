from __future__ import annotations

from flask import Blueprint, request

from ..db import ok, query


bp = Blueprint("sales", __name__)


@bp.get("/sales_trend")
def sales_trend():
    days = max(1, min(90, int(request.args.get("days", 90))))
    rows = query("SELECT * FROM t2_ads_gmv_daily ORDER BY stat_date DESC LIMIT ?", (days,))
    return ok({"days": days, "items": list(reversed(rows))})


@bp.get("/region_sales")
def region_sales():
    return ok(query("SELECT * FROM t2_ads_region_sales ORDER BY rank_no"))


@bp.get("/city_sales")
def city_sales():
    top = max(1, min(30, int(request.args.get("top", 30))))
    return ok(query("SELECT * FROM t2_ads_city_sales ORDER BY rank_no LIMIT ?", (top,)))


@bp.get("/category_proportion")
def category_proportion():
    return ok(query("SELECT * FROM t2_ads_category_proportion ORDER BY rank_no"))


@bp.get("/brand_rank")
def brand_rank():
    return ok(query("SELECT * FROM t2_ads_brand_rank ORDER BY rank_no LIMIT 10"))

