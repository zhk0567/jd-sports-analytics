from __future__ import annotations

from flask import Blueprint, request

from ..db import fail, ok, one, query


bp = Blueprint("overview", __name__)


@bp.get("/gmv")
def gmv():
    row = one("SELECT * FROM t2_ads_gmv_total LIMIT 1")
    return ok(row or {})


@bp.get("/core_kpi")
def core_kpi():
    rows = query("SELECT * FROM t2_ads_core_kpi ORDER BY rowid")
    return ok({"items": rows, "dict": {r["metric_key"]: r["metric_value"] for r in rows}})


@bp.get("/kpi_trend")
def kpi_trend():
    kpi = (request.args.get("kpi") or "gmv").strip()
    days = max(1, min(90, int(request.args.get("days", 30))))
    allowed = {"gmv", "orders", "uv", "aov", "pay_rate", "refund_rate", "conversion_rate"}
    if kpi not in allowed:
        return fail(f"kpi must be one of {sorted(allowed)}")
    rows = query(
        f"SELECT stat_date, {kpi} AS value FROM t2_ads_kpi_trend ORDER BY stat_date DESC LIMIT ?",
        (days,),
    )
    return ok({"kpi": kpi, "days": days, "items": list(reversed(rows))})


@bp.get("/dashboard_overview")
def dashboard_overview():
    kpis = query("SELECT * FROM t2_ads_core_kpi ORDER BY rowid")
    kpi_dict = {r["metric_key"]: r for r in kpis}
    payload = {
        "gmv_total": one("SELECT * FROM t2_ads_gmv_total LIMIT 1") or {},
        "kpi": kpi_dict,
        "trend": query("SELECT * FROM t2_ads_gmv_daily ORDER BY stat_date"),
        "category": query("SELECT * FROM t2_ads_category_proportion ORDER BY rank_no LIMIT 8"),
        "brands": query("SELECT * FROM t2_ads_brand_rank ORDER BY rank_no LIMIT 10"),
        "regions": query("SELECT * FROM t2_ads_region_sales ORDER BY rank_no"),
        "funnel": query("SELECT * FROM t2_ads_user_funnel ORDER BY stage_no"),
        "retention": query("SELECT * FROM t2_ads_user_retention"),
        "rfm": query("SELECT * FROM t2_ads_user_rfm"),
        "products": query("SELECT * FROM t2_ads_product_rank ORDER BY rank_no LIMIT 10"),
        "inventory": query("SELECT * FROM t2_ads_inventory_alarm ORDER BY stock_qty LIMIT 10"),
        "promo": query("SELECT promo_id, SUM(order_count) AS order_count, SUM(paid_orders) AS paid_orders, SUM(gmv) AS gmv, AVG(aov) AS aov, AVG(uplift_rate) AS uplift_rate FROM t2_dws_promo_activity_1d GROUP BY promo_id"),
        "forecast": query("SELECT * FROM t2_ads_sales_forecast ORDER BY forecast_date"),
        "churn": query("SELECT * FROM t2_ads_user_churn_predict ORDER BY rank_no LIMIT 10"),
        "health": {
            "ods_tables": 13,
            "dim_tables": 6,
            "dwd_tables": 10,
            "dws_tables": 18,
            "ads_tables": 16,
            "api_prefix": "/api/t2",
        },
    }
    return ok(payload)


@bp.post("/dashboard_refresh")
@bp.get("/dashboard_refresh")
def dashboard_refresh():
    try:
        from scripts.t2_refresh_ads import refresh_ads

        result = refresh_ads()
        return ok(result, "ADS refreshed")
    except Exception as exc:  # pragma: no cover - surfaced to the dashboard
        return fail(f"refresh failed: {exc}", 500)

