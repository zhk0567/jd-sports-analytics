"""Final acceptance checks for the t2 sports analytics deliverable."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from t2_common import (
    ADS_TABLES,
    DB_PATH,
    DIM_TABLES,
    DOC_DIR,
    DWD_TABLES,
    DWS_TABLES,
    ODS_TABLES,
    ROOT,
    SQL_DIR,
    connect,
    scalar,
)


def main():
    checks = []
    ok = True

    def check(name, passed, detail=""):
        nonlocal ok
        ok = ok and bool(passed)
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    conn = connect()
    for layer, names in [("ods", ODS_TABLES), ("dim", DIM_TABLES), ("dwd", DWD_TABLES), ("dws", DWS_TABLES), ("ads", ADS_TABLES)]:
        counts = [int(scalar(conn, f'SELECT COUNT(*) FROM "t2_{layer}_{name}"')) for name in names]
        check(f"{layer.upper()} tables", len(counts) == len(names) and min(counts) >= 0, f"{len(names)} tables, rows={sum(counts)}")
    kpi_count = int(scalar(conn, "SELECT COUNT(*) FROM t2_ads_core_kpi"))
    check("30 KPIs", kpi_count == 30, f"{kpi_count} rows")
    gmv = float(scalar(conn, "SELECT metric_value FROM t2_ads_core_kpi WHERE metric_key='gmv'"))
    total = float(scalar(conn, "SELECT total_gmv FROM t2_ads_gmv_total"))
    check("GMV reconciliation", abs(gmv - total) < 0.01, f"kpi={gmv:.2f}, ads={total:.2f}")
    fk = json.loads((DB_PATH.parent / "t2_quality_report.json").read_text(encoding="utf-8")).get("fk", {})
    check("foreign keys", all(int(v) == 0 for v in fk.values() if isinstance(v, int)), str(fk))
    cv = json.loads((DB_PATH.parent / "t2_quality_report.json").read_text(encoding="utf-8")).get("cross_validation", [])
    check("cross validation", all(c.get("passed") for c in cv), f"{len(cv)} checks")
    conn.close()

    sql_files = list(SQL_DIR.rglob("*.sql"))
    check("SQL DDL", len(sql_files) >= 10, f"{len(sql_files)} files")
    import_jobs = list((ROOT / "config" / "import").glob("*.json"))
    export_jobs = list((ROOT / "config" / "export").glob("*.json"))
    check("DataX jobs", len(import_jobs) == 26 and len(export_jobs) == 16, f"import={len(import_jobs)}, export={len(export_jobs)}")

    from flask_app.app import create_app

    app = create_app()
    client = app.test_client()
    routes = [str(r) for r in app.url_map.iter_rules() if str(r).startswith("/api/t2")]
    check("20 API routes", len(set(routes)) == 20, f"{len(set(routes))} unique paths / {len(routes)} rules")
    endpoint_results = []
    endpoints = [
        "/api/t2/gmv", "/api/t2/sales_trend?days=90", "/api/t2/region_sales",
        "/api/t2/city_sales?top=30", "/api/t2/product_rank?top=20", "/api/t2/brand_rank",
        "/api/t2/category_proportion", "/api/t2/core_kpi", "/api/t2/kpi_trend?kpi=gmv&days=30",
        "/api/t2/inventory_alarm", "/api/t2/user_funnel", "/api/t2/user_retention",
        "/api/t2/user_rfm", "/api/t2/user_churn?top=100", "/api/t2/user_list?page=1&size=10",
        "/api/t2/promo_activity", "/api/t2/sales_forecast", "/api/t2/sales_forecast_compare",
        "/api/t2/dashboard_overview",
    ]
    for ep in endpoints:
        response = client.get(ep)
        payload = response.get_json() or {}
        endpoint_results.append({"endpoint": ep, "status": response.status_code, "code": payload.get("code")})
    refresh = client.post("/api/t2/dashboard_refresh")
    refresh_json = refresh.get_json() or {}
    endpoint_results.append({"endpoint": "/api/t2/dashboard_refresh", "status": refresh.status_code, "code": refresh_json.get("code")})
    check("API smoke", all(r["status"] == 200 and r["code"] == 0 for r in endpoint_results), f"{len(endpoint_results)} endpoints")

    dashboard = (ROOT / "dashboard" / "dashboard_t2.html").read_text(encoding="utf-8")
    check("12 dashboard charts", dashboard.count('class="chart"') + dashboard.count('class="list"') == 12, f"charts/lists={dashboard.count('class=\"chart\"') + dashboard.count('class=\"list\"')}")
    check("dashboard assets", (ROOT / "dashboard" / "static" / "echarts.min.js").exists() and (ROOT / "dashboard" / "static" / "china.json").exists(), "echarts + china map")

    docs = list(DOC_DIR.glob("*.md")) + list((DOC_DIR / "process").glob("*.md"))
    check("documents", len(docs) >= 20, f"{len(docs)} markdown files")
    shot = DOC_DIR / "screenshots" / "dashboard_t2.png"
    check("dashboard screenshot", shot.exists() and shot.stat().st_size > 100_000, f"{shot.stat().st_size if shot.exists() else 0} bytes")
    ppt = DOC_DIR / "答辩PPT.pptx"
    slides = 0
    if ppt.exists():
        with zipfile.ZipFile(ppt) as zf:
            slides = len([n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")])
    check("10-slide PPT", slides == 10, f"{slides} slides")

    result = {"ok": ok, "checks": checks, "api": endpoint_results}
    out = DOC_DIR / "验收结果.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": ok, "passed": sum(1 for c in checks if c["passed"]), "total": len(checks), "failed": [c for c in checks if not c["passed"]]}, ensure_ascii=False, indent=2))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
