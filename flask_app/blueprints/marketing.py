from __future__ import annotations

from flask import Blueprint

from ..db import ok, query


bp = Blueprint("marketing", __name__)


@bp.get("/promo_activity")
def promo_activity():
    by_promo = query(
        """
        SELECT promo_id,
               SUM(order_count) AS order_count,
               SUM(paid_orders) AS paid_orders,
               ROUND(SUM(gmv), 2) AS gmv,
               ROUND(AVG(aov), 2) AS aov,
               ROUND(AVG(conversion_rate), 2) AS conversion_rate,
               ROUND(AVG(uplift_rate), 2) AS uplift_rate
        FROM t2_dws_promo_activity_1d
        GROUP BY promo_id
        ORDER BY gmv DESC
        """
    )
    daily = query(
        """
        SELECT stat_date, promo_id, order_count, paid_orders, ROUND(gmv, 2) AS gmv,
               ROUND(aov, 2) AS aov, ROUND(uplift_rate, 2) AS uplift_rate
        FROM t2_dws_promo_activity_1d
        ORDER BY stat_date
        """
    )
    return ok({"summary": by_promo, "daily": daily})

