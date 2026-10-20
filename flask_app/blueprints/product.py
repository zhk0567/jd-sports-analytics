from __future__ import annotations

from flask import Blueprint, request

from ..db import ok, query


bp = Blueprint("product", __name__)


@bp.get("/product_rank")
def product_rank():
    top = max(1, min(50, int(request.args.get("top", 20))))
    return ok(query("SELECT * FROM t2_ads_product_rank ORDER BY rank_no LIMIT ?", (top,)))


@bp.get("/inventory_alarm")
def inventory_alarm():
    return ok({
        "items": query("SELECT * FROM t2_ads_inventory_alarm ORDER BY stock_qty"),
        "slow_moving": query("SELECT * FROM t2_ads_product_stock_warn ORDER BY turnover_days DESC LIMIT 20"),
    })

