from __future__ import annotations

from flask import Blueprint, request

from ..db import ok, query


bp = Blueprint("user", __name__)


@bp.get("/user_funnel")
def user_funnel():
    return ok(query("SELECT * FROM t2_ads_user_funnel ORDER BY stage_no"))


@bp.get("/user_retention")
def user_retention():
    return ok(query("SELECT * FROM t2_ads_user_retention"))


@bp.get("/user_rfm")
def user_rfm():
    return ok(query("SELECT * FROM t2_ads_user_rfm"))


@bp.get("/user_churn")
def user_churn():
    top = max(1, min(100, int(request.args.get("top", 100))))
    return ok(query("SELECT * FROM t2_ads_user_churn_predict ORDER BY rank_no LIMIT ?", (top,)))


@bp.get("/user_list")
def user_list():
    page = max(1, int(request.args.get("page", 1)))
    size = max(1, min(100, int(request.args.get("size", 10))))
    where = ["1=1"]
    params: list = []
    for field in ["province", "gender", "user_level"]:
        value = request.args.get(field)
        if value:
            where.append(f"u.{field} = ?")
            params.append(value)
    keyword = (request.args.get("q") or "").strip()
    if keyword:
        where.append("(u.user_id LIKE ? OR u.user_name LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    clause = " AND ".join(where)
    total = query(f"SELECT COUNT(*) AS n FROM t2_dim_user_info u WHERE {clause}", params)[0]["n"]
    rows = query(
        f"""
        SELECT u.user_id, u.user_name, u.gender, u.age, u.age_group, u.phone, u.province, u.city,
               u.user_level, u.register_date, u.last_login_time,
               COALESCE(o.order_count, 0) AS order_count, COALESCE(o.total_gmv, 0) AS total_gmv
        FROM t2_dim_user_info u
        LEFT JOIN (
          SELECT user_id, COUNT(*) AS order_count, SUM(pay_amount) AS total_gmv
          FROM t2_dwd_order GROUP BY user_id
        ) o ON u.user_id = o.user_id
        WHERE {clause}
        ORDER BY u.user_id LIMIT ? OFFSET ?
        """,
        params + [size, (page - 1) * size],
    )
    return ok({"page": page, "size": size, "total": total, "items": rows})

