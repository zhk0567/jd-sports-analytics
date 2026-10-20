-- t2 运动电商：DWS / ADS 参考实现（Hive SQL）
-- 指标口径以 doc/电商经营指标体系.md 为准；本地演示由 scripts/t2_build_warehouse.py 物化。

-- ============ DWS 用户主题 ============
INSERT OVERWRITE TABLE t2_dws_user_user_1d
SELECT d.stat_date,
       count(DISTINCT CASE WHEN u.register_date = d.stat_date THEN u.user_id END) AS new_users,
       count(DISTINCT a.user_id) AS active_users,
       count(DISTINCT o.user_id) AS order_users,
       count(DISTINCT CASE WHEN o.is_paid = 1 THEN o.user_id END) AS paid_users,
       count(DISTINCT o.order_id) AS orders,
       count(DISTINCT CASE WHEN o.is_paid = 1 THEN o.order_id END) AS paid_orders,
       sum(o.pay_amount) AS gmv,
       sum(o.pay_amount) / greatest(count(DISTINCT CASE WHEN o.is_paid = 1 THEN o.user_id END), 1) AS arpu,
       count(DISTINCT CASE WHEN o.is_paid = 1 THEN o.user_id END) AS repurchase_users
FROM t2_dim_date d
LEFT JOIN t2_dim_user_info u ON u.register_date = d.stat_date
LEFT JOIN t2_dwd_user_action a ON a.action_date = d.stat_date
LEFT JOIN t2_dwd_order o ON o.order_date = d.stat_date
GROUP BY d.stat_date;

INSERT OVERWRITE TABLE t2_dws_user_user_nd
SELECT d.stat_date,
       count(DISTINCT a7.user_id) AS active_users_7d,
       count(DISTINCT a30.user_id) AS active_users_30d,
       count(DISTINCT u7.user_id) AS new_users_7d,
       count(DISTINCT o7.user_id) AS order_users_7d,
       sum(o7.pay_amount) AS gmv_7d,
       sum(o30.pay_amount) AS gmv_30d,
       count(DISTINCT CASE WHEN o30.order_count >= 2 THEN o30.user_id END) / greatest(count(DISTINCT o30.user_id), 1) * 100 AS repeat_rate_30d
FROM t2_dim_date d
LEFT JOIN t2_dwd_user_action a7 ON a7.action_date BETWEEN date_sub(d.stat_date, 6) AND d.stat_date
LEFT JOIN t2_dwd_user_action a30 ON a30.action_date BETWEEN date_sub(d.stat_date, 29) AND d.stat_date
LEFT JOIN t2_dim_user_info u7 ON u7.register_date BETWEEN date_sub(d.stat_date, 6) AND d.stat_date
LEFT JOIN t2_dwd_order o7 ON o7.order_date BETWEEN date_sub(d.stat_date, 6) AND d.stat_date
LEFT JOIN t2_dwd_order o30 ON o30.order_date BETWEEN date_sub(d.stat_date, 29) AND d.stat_date
GROUP BY d.stat_date;

INSERT OVERWRITE TABLE t2_dws_user_user_total
SELECT user_id, min(order_date) AS first_order_date, max(order_date) AS last_order_date,
       count(DISTINCT order_id) AS order_count,
       count(DISTINCT CASE WHEN is_paid = 1 THEN order_id END) AS paid_order_count,
       sum(pay_amount) AS total_gmv,
       sum(pay_amount) / greatest(count(DISTINCT order_id), 1) AS avg_order_amount,
       datediff(to_date('2025-11-11'), max(order_date)) AS days_since_last_order,
       max(member_level_num) AS member_level_num
FROM t2_dwd_order o LEFT JOIN t2_dim_user_info u ON o.user_id = u.user_id
GROUP BY o.user_id;

INSERT OVERWRITE TABLE t2_dws_user_rfm
SELECT user_id, r_score AS rfm_r, f_score AS rfm_f, m_score AS rfm_m,
       round(r_score * 0.4 + f_score * 0.3 + m_score * 0.3, 2) AS rfm_score,
       CASE WHEN r_score * 0.4 + f_score * 0.3 + m_score * 0.3 >= 4.2 THEN '高价值'
            WHEN r_score * 0.4 + f_score * 0.3 + m_score * 0.3 >= 3.5 THEN '潜力'
            WHEN r_score * 0.4 + f_score * 0.3 + m_score * 0.3 >= 2.8 THEN '稳定'
            WHEN r_score * 0.4 + f_score * 0.3 + m_score * 0.3 >= 2.0 THEN '流失预警' ELSE '流失' END AS segment,
       last_order_date, order_count, total_gmv
FROM (
  SELECT user_id,
         ntile(5) OVER (ORDER BY days_since_last_order DESC) AS r_score,
         ntile(5) OVER (ORDER BY order_count) AS f_score,
         ntile(5) OVER (ORDER BY total_gmv) AS m_score,
         last_order_date, order_count, total_gmv
  FROM t2_dws_user_user_total
) x;

INSERT OVERWRITE TABLE t2_dws_user_retention_1d
SELECT u.register_date AS cohort_date, count(DISTINCT u.user_id) AS cohort_users,
       count(DISTINCT CASE WHEN a1.user_id IS NOT NULL THEN u.user_id END) AS d1_users,
       count(DISTINCT CASE WHEN a1.user_id IS NOT NULL THEN u.user_id END) / count(DISTINCT u.user_id) * 100 AS d1_rate,
       count(DISTINCT CASE WHEN a7.user_id IS NOT NULL THEN u.user_id END) AS d7_users,
       count(DISTINCT CASE WHEN a7.user_id IS NOT NULL THEN u.user_id END) / count(DISTINCT u.user_id) * 100 AS d7_rate,
       count(DISTINCT CASE WHEN a30.user_id IS NOT NULL THEN u.user_id END) AS d30_users,
       count(DISTINCT CASE WHEN a30.user_id IS NOT NULL THEN u.user_id END) / count(DISTINCT u.user_id) * 100 AS d30_rate
FROM t2_dim_user_info u
LEFT JOIN t2_dwd_user_action a1 ON a1.user_id = u.user_id AND a1.action_date = date_add(u.register_date, 1)
LEFT JOIN t2_dwd_user_action a7 ON a7.user_id = u.user_id AND a7.action_date = date_add(u.register_date, 7)
LEFT JOIN t2_dwd_user_action a30 ON a30.user_id = u.user_id AND a30.action_date = date_add(u.register_date, 30)
GROUP BY u.register_date;

-- ============ DWS 流量主题 ============
INSERT OVERWRITE TABLE t2_dws_traffic_page_1d
SELECT action_date AS stat_date, page, count(*) AS pv, count(DISTINCT user_id) AS uv,
       avg(duration_sec) AS avg_duration
FROM t2_dwd_user_action GROUP BY action_date, page;

INSERT OVERWRITE TABLE t2_dws_traffic_user_1d
SELECT action_date AS stat_date, count(*) AS pv, count(DISTINCT user_id) AS uv,
       count(DISTINCT session_id) AS visits, avg(duration_sec) AS avg_duration,
       count(DISTINCT CASE WHEN u.register_date = action_date THEN user_id END) / count(DISTINCT user_id) * 100 AS new_user_ratio,
       0 AS bounce_rate
FROM t2_dwd_user_action a LEFT JOIN t2_dim_user_info u ON a.user_id = u.user_id
GROUP BY action_date;

INSERT OVERWRITE TABLE t2_dws_user_funnel_1d
SELECT s.search_date AS stat_date, count(DISTINCT s.user_id) AS search_users,
       count(DISTINCT c.user_id) AS cart_users, count(DISTINCT o.user_id) AS order_users,
       count(DISTINCT CASE WHEN o.is_paid = 1 THEN o.user_id END) AS pay_users,
       count(DISTINCT c.user_id) / greatest(count(DISTINCT s.user_id), 1) * 100 AS search_to_cart_rate,
       count(DISTINCT o.user_id) / greatest(count(DISTINCT c.user_id), 1) * 100 AS cart_to_order_rate,
       count(DISTINCT CASE WHEN o.is_paid = 1 THEN o.user_id END) / greatest(count(DISTINCT o.user_id), 1) * 100 AS order_to_pay_rate,
       count(DISTINCT CASE WHEN o.is_paid = 1 THEN o.user_id END) / greatest(count(DISTINCT s.user_id), 1) * 100 AS overall_rate
FROM t2_dwd_search_log s
LEFT JOIN t2_dwd_cart c ON c.action_date = s.search_date
LEFT JOIN t2_dwd_order o ON o.order_date = s.search_date
GROUP BY s.search_date;

-- ============ DWS 商品 / 地区 / 营销主题 ============
INSERT OVERWRITE TABLE t2_dws_trade_product_1d
SELECT order_date AS stat_date, product_id, product_name, category_id, brand_id,
       sum(quantity) AS sales_qty, sum(line_gmv) AS gmv, count(DISTINCT order_id) AS order_count,
       0 AS uv, 0 AS conversion_rate
FROM t2_dwd_order_detail GROUP BY order_date, product_id, product_name, category_id, brand_id;

INSERT OVERWRITE TABLE t2_dws_trade_product_nd
SELECT order_date AS stat_date, product_id,
       sum(CASE WHEN order_date >= date_sub(stat_date, 6) THEN quantity ELSE 0 END) AS sales_qty_7d,
       sum(CASE WHEN order_date >= date_sub(stat_date, 6) THEN line_gmv ELSE 0 END) AS gmv_7d,
       sum(quantity) AS sales_qty_30d, sum(line_gmv) AS gmv_30d,
       row_number() OVER (PARTITION BY order_date ORDER BY sum(line_gmv) DESC) AS rank_30d
FROM t2_dwd_order_detail
WHERE order_date >= date_sub(stat_date, 29)
GROUP BY order_date, product_id;

INSERT OVERWRITE TABLE t2_dws_trade_category_1d
SELECT order_date AS stat_date, category_id, max(p.category_name) AS category_name,
       sum(quantity) AS sales_qty, sum(line_gmv) AS gmv, count(DISTINCT order_id) AS order_count,
       sum(line_gmv) / sum(sum(line_gmv)) OVER (PARTITION BY order_date) * 100 AS gmv_share
FROM t2_dwd_order_detail d JOIN t2_dim_category p ON d.category_id = p.category_id
GROUP BY order_date, category_id;

INSERT OVERWRITE TABLE t2_dws_trade_category_nd
SELECT order_date AS stat_date, category_id, sum(line_gmv) AS gmv_30d,
       sum(line_gmv) AS gmv_7d, 0 AS growth_rate_30d
FROM t2_dwd_order_detail
WHERE order_date >= date_sub(stat_date, 29)
GROUP BY order_date, category_id;

INSERT OVERWRITE TABLE t2_dws_trade_brand_1d
SELECT order_date AS stat_date, brand_id, max(brand_name) AS brand_name,
       sum(quantity) AS sales_qty, sum(line_gmv) AS gmv, count(DISTINCT order_id) AS order_count,
       sum(line_gmv) / sum(sum(line_gmv)) OVER (PARTITION BY order_date) * 100 AS gmv_share
FROM t2_dwd_order_detail d JOIN t2_dim_product_info p ON d.product_id = p.product_id
GROUP BY order_date, brand_id;

INSERT OVERWRITE TABLE t2_dws_trade_region_1d
SELECT order_date AS stat_date, province, city, count(DISTINCT order_id) AS order_count,
       sum(pay_amount) AS gmv, count(DISTINCT user_id) AS paid_users,
       sum(pay_amount) / greatest(count(DISTINCT order_id), 1) AS aov
FROM t2_dwd_order GROUP BY order_date, province, city;

INSERT OVERWRITE TABLE t2_dws_trade_region_nd
SELECT order_date AS stat_date, province, sum(pay_amount) AS gmv_7d,
       sum(pay_amount) AS gmv_30d, 0 AS growth_rate_30d
FROM t2_dwd_order
WHERE order_date >= date_sub(stat_date, 29)
GROUP BY order_date, province;

INSERT OVERWRITE TABLE t2_dws_user_region_total
SELECT u.province, u.city, count(DISTINCT u.user_id) AS total_users,
       count(DISTINCT o.user_id) AS order_users, sum(o.pay_amount) AS total_gmv,
       sum(o.pay_amount) / greatest(count(DISTINCT u.user_id), 1) AS avg_gmv_per_user
FROM t2_dim_user_info u LEFT JOIN t2_dwd_order o ON u.user_id = o.user_id
GROUP BY u.province, u.city;

INSERT OVERWRITE TABLE t2_dws_traffic_region_1d
SELECT a.action_date AS stat_date, u.province, count(*) AS pv, count(DISTINCT a.user_id) AS uv,
       count(DISTINCT o.user_id) AS order_users, sum(o.pay_amount) AS gmv
FROM t2_dwd_user_action a
JOIN t2_dim_user_info u ON a.user_id = u.user_id
LEFT JOIN t2_dwd_order o ON o.user_id = a.user_id AND o.order_date = a.action_date
GROUP BY a.action_date, u.province;

INSERT OVERWRITE TABLE t2_dws_promo_activity_1d
SELECT order_date AS stat_date, promo_id, count(DISTINCT order_id) AS order_count,
       count(DISTINCT CASE WHEN is_paid = 1 THEN order_id END) AS paid_orders,
       sum(pay_amount) AS gmv, sum(pay_amount) / greatest(count(DISTINCT order_id), 1) AS aov,
       0 AS conversion_rate, 0 AS uplift_rate
FROM t2_dwd_order GROUP BY order_date, promo_id;

-- ============ ADS ============
INSERT OVERWRITE TABLE t2_ads_gmv_total
SELECT to_date('2025-11-11') AS stat_date,
       sum(CASE WHEN order_date = '2025-11-11' THEN pay_amount ELSE 0 END) AS today_gmv,
       sum(pay_amount) AS total_gmv,
       sum(CASE WHEN order_date = '2025-11-10' THEN pay_amount ELSE 0 END) AS yesterday_gmv,
       0 AS mom_rate, -7.8 AS yoy_rate,
       count(DISTINCT CASE WHEN is_paid = 1 THEN order_id END) AS paid_orders,
       sum(pay_amount) / greatest(count(DISTINCT CASE WHEN is_paid = 1 THEN order_id END), 1) AS aov,
       count(DISTINCT CASE WHEN is_paid = 1 THEN order_id END) / greatest(count(DISTINCT order_id), 1) * 100 AS pay_rate,
       current_timestamp() AS updated_at
FROM t2_dwd_order;

INSERT OVERWRITE TABLE t2_ads_gmv_daily
SELECT stat_date, sum(gmv) AS gmv, sum(orders) AS orders, sum(paid_orders) AS paid_orders,
       sum(paid_orders) / greatest(sum(orders), 1) * 100 AS pay_rate,
       sum(gmv) / greatest(sum(paid_orders), 1) AS aov, max(promo_name) AS promo_name
FROM (
  SELECT o.order_date AS stat_date, o.order_date, sum(o.pay_amount) AS gmv,
         count(DISTINCT o.order_id) AS orders,
         count(DISTINCT CASE WHEN o.is_paid = 1 THEN o.order_id END) AS paid_orders,
         max(d.promo_name) AS promo_name
  FROM t2_dwd_order o LEFT JOIN t2_dim_date d ON o.order_date = d.stat_date
  GROUP BY o.order_date
) x
WHERE stat_date >= date_sub(to_date('2025-11-11'), 89)
GROUP BY stat_date;

INSERT OVERWRITE TABLE t2_ads_region_sales
SELECT province, sum(pay_amount) AS gmv, count(DISTINCT order_id) AS order_count,
       0 AS growth_rate, row_number() OVER (ORDER BY sum(pay_amount) DESC) AS rank_no
FROM t2_dwd_order GROUP BY province;

INSERT OVERWRITE TABLE t2_ads_city_sales
SELECT city, province, sum(pay_amount) AS gmv, count(DISTINCT order_id) AS order_count,
       row_number() OVER (ORDER BY sum(pay_amount) DESC) AS rank_no
FROM t2_dwd_order GROUP BY city, province;

INSERT OVERWRITE TABLE t2_ads_category_proportion
SELECT category_id, max(category_name) AS category_name, sum(gmv) AS gmv,
       sum(gmv) / sum(sum(gmv)) OVER () * 100 AS gmv_share,
       sum(order_count) AS order_count, row_number() OVER (ORDER BY sum(gmv) DESC) AS rank_no
FROM t2_dws_trade_category_1d GROUP BY category_id;

INSERT OVERWRITE TABLE t2_ads_brand_rank
SELECT brand_id, max(brand_name) AS brand_name, sum(sales_qty) AS sales_qty,
       sum(gmv) AS gmv, sum(gmv) / sum(sum(gmv)) OVER () * 100 AS gmv_share,
       row_number() OVER (ORDER BY sum(sales_qty) DESC) AS rank_no
FROM t2_dws_trade_brand_1d GROUP BY brand_id;

INSERT OVERWRITE TABLE t2_ads_user_funnel
SELECT 1 AS stage_no, '搜索触达' AS stage_name, sum(click_count) AS user_count, 100.0 AS conversion_rate, 100.0 AS overall_rate FROM t2_dwd_search_log
UNION ALL SELECT 2, '加入购物车', count(*), 0, 0 FROM t2_dwd_cart
UNION ALL SELECT 3, '提交订单', count(DISTINCT order_id), 0, 0 FROM t2_dwd_order
UNION ALL SELECT 4, '支付成功', count(DISTINCT order_id), 0, 0 FROM t2_dwd_order WHERE is_paid = 1;

INSERT OVERWRITE TABLE t2_ads_user_retention
SELECT '次日留存' AS period, avg(d1_rate) AS retention_rate, sum(cohort_users) AS cohort_users, sum(d1_users) AS retained_users FROM t2_dws_user_retention_1d
UNION ALL SELECT '7日留存', avg(d7_rate), sum(cohort_users), sum(d7_users) FROM t2_dws_user_retention_1d
UNION ALL SELECT '30日留存', avg(d30_rate), sum(cohort_users), sum(d30_users) FROM t2_dws_user_retention_1d;

INSERT OVERWRITE TABLE t2_ads_user_rfm
SELECT segment, count(DISTINCT user_id) AS user_count,
       count(DISTINCT user_id) / sum(count(DISTINCT user_id)) OVER () * 100 AS user_share,
       avg(rfm_r) AS avg_r, avg(rfm_f) AS avg_f, avg(rfm_m) AS avg_m, avg(total_gmv) AS avg_monetary
FROM t2_dws_user_rfm GROUP BY segment;

INSERT OVERWRITE TABLE t2_ads_product_rank
SELECT product_id, max(product_name) AS product_name, max(brand_name) AS brand_name,
       max(category_name) AS category_name, sum(sales_qty) AS sales_qty, sum(gmv) AS gmv,
       row_number() OVER (ORDER BY sum(sales_qty) DESC) AS rank_no
FROM t2_dws_trade_product_1d d JOIN t2_dim_product_info p USING (product_id)
GROUP BY product_id;

INSERT OVERWRITE TABLE t2_ads_product_stock_warn
SELECT product_id, product_name, stock_qty, sales_qty_30d, turnover_days,
       CASE WHEN sales_qty_30d = 0 THEN '严重滞销' ELSE '滞销预警' END AS warn_level
FROM t2_dwd_inventory WHERE stock_qty > 0 AND sales_qty_30d = 0;

INSERT OVERWRITE TABLE t2_ads_inventory_alarm
SELECT product_id, product_name, brand_id, stock_qty, 30 AS safety_stock,
       greatest(30 - stock_qty, 0) AS shortage,
       CASE WHEN stock_qty = 0 THEN '断货' WHEN stock_qty < 10 THEN '严重'
            WHEN turnover_days > 180 THEN '滞销' ELSE '关注' END AS alarm_level
FROM t2_dwd_inventory WHERE stock_qty < 20 OR turnover_days > 180;

INSERT OVERWRITE TABLE t2_ads_kpi_trend
SELECT stat_date, gmv, orders, 0 AS uv, aov, pay_rate, 0 AS refund_rate, 0 AS conversion_rate
FROM t2_ads_gmv_daily;

INSERT OVERWRITE TABLE t2_ads_core_kpi
SELECT 'gmv' AS metric_key, 'GMV' AS metric_name, sum(pay_amount) AS metric_value,
       '元' AS metric_unit, '交易' AS metric_group, '支付订单金额合计' AS definition
FROM t2_dwd_order
UNION ALL SELECT 'paid_order_count', '支付订单数', count(DISTINCT order_id), '单', '交易', '支付成功订单数'
FROM t2_dwd_order WHERE is_paid = 1
UNION ALL SELECT 'order_count', '订单数', count(DISTINCT order_id), '单', '交易', '提交订单数' FROM t2_dwd_order
UNION ALL SELECT 'aov', '客单价', sum(pay_amount) / greatest(count(DISTINCT CASE WHEN is_paid=1 THEN order_id END),1), '元', '交易', 'GMV/支付订单数' FROM t2_dwd_order
UNION ALL SELECT 'refund_rate', '退货率', count(DISTINCT CASE WHEN refund_status='已退款' THEN order_id END) / greatest(count(DISTINCT CASE WHEN is_paid=1 THEN order_id END),1) * 100, '%', '交易', '已退款订单/支付订单' FROM t2_dwd_refund;
