-- t2 运动电商：DIM / DWD 参考实现（Hive SQL）
-- 本地演示的权威实现在 scripts/t2_build_warehouse.py，本文件用于实验环境复现与答辩讲解。

-- ============ DIM ============
INSERT OVERWRITE TABLE t2_dim_user_info
SELECT
  user_id,
  concat(substr(username, 1, 1), '**') AS user_name,
  gender, cast(age AS int) AS age,
  CASE WHEN cast(age AS int) <= 24 THEN '18-24'
       WHEN cast(age AS int) <= 29 THEN '25-29'
       WHEN cast(age AS int) <= 34 THEN '30-34'
       WHEN cast(age AS int) <= 39 THEN '35-39' ELSE '40+' END AS age_group,
  concat(substr(phone, 1, 3), '****', substr(phone, 8)) AS phone,
  email, province, city, register_time, substr(register_time, 1, 10) AS register_date,
  user_level,
  CASE user_level WHEN '黑卡' THEN 4 WHEN '金卡' THEN 3 WHEN '银卡' THEN 2 ELSE 1 END AS member_level_num,
  cast(is_member AS int) AS is_member, last_login_time
FROM t2_ods_user_info;

INSERT OVERWRITE TABLE t2_dim_product_info
SELECT p.product_id, p.product_name, p.category_id, p.brand_id, p.shop_id,
       cast(p.price AS double) AS price, cast(p.original_price AS double) AS original_price,
       cast(p.stock_qty AS int) AS stock_qty, cast(p.sales_qty AS int) AS sales_qty,
       p.size, p.color, p.material, p.target_group, p.season, p.listing_date, p.status,
       c1.category_name AS cat1_name, c2.category_name AS cat2_name,
       concat(c1.category_name, '/', c2.category_name) AS category_path,
       CASE WHEN cast(p.price AS double) >= 1000 THEN '高端'
            WHEN cast(p.price AS double) >= 400 THEN '中端' ELSE '入门' END AS product_level,
       b.brand_name, b.brand_level, b.brand_country, s.shop_name, s.shop_type, p.image_url
FROM t2_ods_product_info p
LEFT JOIN t2_ods_category c2 ON p.category_id = c2.category_id
LEFT JOIN t2_ods_category c1 ON c2.parent_id = c1.category_id
LEFT JOIN t2_ods_brand_info b ON p.brand_id = b.brand_id
LEFT JOIN t2_ods_shop_info s ON p.shop_id = s.shop_id;

INSERT OVERWRITE TABLE t2_dim_category
SELECT c.category_id, c.category_name, c.parent_id, cast(c.category_level AS int) AS category_level,
       c.category_path, cast(c.sort_no AS int) AS sort_no, count(p.product_id) AS product_count
FROM t2_ods_category c LEFT JOIN t2_dim_product_info p ON c.category_id = p.category_id
GROUP BY c.category_id, c.category_name, c.parent_id, c.category_level, c.category_path, c.sort_no;

INSERT OVERWRITE TABLE t2_dim_date
SELECT date_format(d, 'yyyyMMdd') AS date_key, date_format(d, 'yyyy-MM-dd') AS stat_date,
       year(d) AS year, month(d) AS month, day(d) AS day, weekofyear(d) AS week,
       quarter(d) AS quarter, dayofweek(d) AS day_of_week,
       CASE dayofweek(d) WHEN 1 THEN '周日' WHEN 2 THEN '周一' WHEN 3 THEN '周二'
            WHEN 4 THEN '周三' WHEN 5 THEN '周四' WHEN 6 THEN '周五' ELSE '周六' END AS day_name,
       CASE WHEN dayofweek(d) IN (1, 7) THEN 1 ELSE 0 END AS is_weekend,
       CASE WHEN d BETWEEN '2025-06-15' AND '2025-06-18' OR d BETWEEN '2025-11-08' AND '2025-11-11' THEN 1 ELSE 0 END AS is_promo,
       CASE WHEN d BETWEEN '2025-06-15' AND '2025-06-18' THEN '618'
            WHEN d BETWEEN '2025-11-08' AND '2025-11-11' THEN '双11' ELSE '' END AS promo_name
FROM (SELECT date_add(to_date('2025-05-16'), pos) AS d
      FROM (SELECT posexplode(sequence(to_date('2025-05-16'), to_date('2025-11-11'), interval 1 day)) AS (pos, dt)) x) y;

INSERT OVERWRITE TABLE t2_dim_region
SELECT concat('R', lpad(row_number() OVER (ORDER BY province, city), 4, '0')) AS region_id,
       province, city,
       CASE WHEN city IN ('北京','上海','广州','深圳') THEN '一线'
            WHEN city IN ('杭州','成都','武汉','西安','南京','长沙','重庆','苏州') THEN '新一线'
            ELSE '二线' END AS city_level
FROM (SELECT province, city FROM t2_ods_user_info
      UNION SELECT province, city FROM t2_ods_order_info
      UNION SELECT province, city FROM t2_ods_logistics_info) r;

INSERT OVERWRITE TABLE t2_dim_brand
SELECT b.brand_id, b.brand_name, b.brand_country, b.brand_level, b.main_category,
       cast(b.establish_year AS int) AS establish_year, count(p.product_id) AS product_count
FROM t2_ods_brand_info b LEFT JOIN t2_dim_product_info p ON b.brand_id = p.brand_id
GROUP BY b.brand_id, b.brand_name, b.brand_country, b.brand_level, b.main_category, b.establish_year;

-- ============ DWD ============
INSERT OVERWRITE TABLE t2_dwd_order
SELECT order_id, user_id, order_time, substr(order_time, 1, 10) AS order_date,
       order_status, cast(total_amount AS double) AS total_amount,
       cast(discount_amount AS double) AS discount_amount, cast(shipping_fee AS double) AS shipping_fee,
       cast(coupon_amount AS double) AS coupon_amount, cast(pay_amount AS double) AS pay_amount,
       province, city, channel, nvl(promo_id, '日常') AS promo_id,
       CASE WHEN cast(pay_amount AS double) > 0 AND order_status IN ('已完成','已发货','已支付','已退款') THEN 1 ELSE 0 END AS is_paid
FROM (SELECT *, row_number() OVER (PARTITION BY order_id ORDER BY order_time DESC) rn
      FROM t2_ods_order_info
      WHERE order_id IS NOT NULL AND user_id IN (SELECT user_id FROM t2_dim_user_info)
        AND cast(total_amount AS double) > 0 AND cast(pay_amount AS double) >= 0
        AND substr(order_time, 1, 10) BETWEEN '2025-05-16' AND '2025-11-11') x
WHERE rn = 1;

INSERT OVERWRITE TABLE t2_dwd_order_detail
SELECT d.detail_id, d.order_id, d.product_id, cast(d.quantity AS int) AS quantity,
       cast(d.unit_price AS double) AS unit_price, cast(d.discount_amount AS double) AS discount_amount,
       cast(d.line_amount AS double) AS line_amount,
       cast(d.line_amount AS double) / sum(cast(d.line_amount AS double)) OVER (PARTITION BY d.order_id) * o.pay_amount AS line_gmv,
       p.product_name, p.category_id, p.brand_id, p.shop_id, o.order_date
FROM t2_ods_order_detail d
JOIN t2_dwd_order o ON d.order_id = o.order_id
JOIN t2_dim_product_info p ON d.product_id = p.product_id
WHERE d.detail_id IS NOT NULL AND cast(d.quantity AS int) > 0
  AND cast(d.unit_price AS double) > 0 AND cast(d.line_amount AS double) > 0;

INSERT OVERWRITE TABLE t2_dwd_payment
SELECT payment_id, order_id, pay_time, substr(pay_time, 1, 10) AS pay_date,
       cast(pay_amount AS double) AS pay_amount, pay_method, pay_status, transaction_no
FROM (SELECT *, row_number() OVER (PARTITION BY order_id ORDER BY pay_time DESC) rn
      FROM t2_ods_payment_info
      WHERE pay_status = '成功' AND cast(pay_amount AS double) > 0
        AND order_id IN (SELECT order_id FROM t2_dwd_order)) x
WHERE rn = 1;

INSERT OVERWRITE TABLE t2_dwd_refund
SELECT refund_id, order_id, refund_time, substr(refund_time, 1, 10) AS refund_date,
       cast(refund_amount AS double) AS refund_amount, refund_reason, refund_status, refund_type
FROM t2_ods_refund_info
WHERE refund_id IS NOT NULL AND cast(refund_amount AS double) > 0
  AND order_id IN (SELECT order_id FROM t2_dwd_order);

INSERT OVERWRITE TABLE t2_dwd_logistics
SELECT logistics_id, order_id, ship_time, deliver_time, sign_time, logistics_company,
       tracking_no, logistics_status, province, city
FROM t2_ods_logistics_info l
WHERE logistics_id IS NOT NULL AND order_id IN (SELECT order_id FROM t2_dwd_order)
  AND (ship_time = '' OR deliver_time = '' OR deliver_time >= ship_time)
  AND (deliver_time = '' OR sign_time = '' OR sign_time >= deliver_time);

INSERT OVERWRITE TABLE t2_dwd_review
SELECT review_id, order_id, product_id, user_id, review_time, substr(review_time, 1, 10) AS review_date,
       cast(rating AS int) AS rating, review_content, cast(is_anonymous AS int) AS is_anonymous,
       cast(images_count AS int) AS images_count,
       CASE WHEN cast(rating AS int) >= 4 THEN '好评' WHEN cast(rating AS int) = 3 THEN '中评' ELSE '差评' END AS sentiment
FROM t2_ods_review_info
WHERE review_id IS NOT NULL AND trim(review_content) <> ''
  AND cast(rating AS int) BETWEEN 1 AND 5
  AND order_id IN (SELECT order_id FROM t2_dwd_order)
  AND product_id IN (SELECT product_id FROM t2_dim_product_info);

INSERT OVERWRITE TABLE t2_dwd_cart
SELECT cart_id, user_id, product_id, add_time, substr(add_time, 1, 10) AS action_date,
       cast(quantity AS int) AS quantity, cart_status, source_page
FROM t2_ods_cart_info
WHERE cart_id IS NOT NULL AND cast(quantity AS int) > 0
  AND user_id IN (SELECT user_id FROM t2_dim_user_info)
  AND product_id IN (SELECT product_id FROM t2_dim_product_info);

INSERT OVERWRITE TABLE t2_dwd_search_log
SELECT log_id, user_id, search_time, substr(search_time, 1, 10) AS search_date, keyword, scene,
       cast(result_count AS int) AS result_count, cast(click_count AS int) AS click_count,
       cast(duration_sec AS int) AS duration_sec, device, session_id
FROM t2_ods_search_log
WHERE log_id IS NOT NULL AND trim(keyword) <> '' AND cast(duration_sec AS int) > 0
  AND user_id IN (SELECT user_id FROM t2_dim_user_info);

INSERT OVERWRITE TABLE t2_dwd_user_action
SELECT action_id, user_id, action_time, action_date, action_type, page, keyword, product_id,
       order_id, quantity, click_count, duration_sec, device, province, city
FROM (
  SELECT log_id AS action_id, user_id, search_time AS action_time, search_date AS action_date,
         '搜索' AS action_type, '搜索页' AS page, keyword, '' AS product_id, '' AS order_id,
         0 AS quantity, click_count, duration_sec, device, '' AS province, '' AS city
  FROM t2_dwd_search_log
  UNION ALL
  SELECT cart_id, user_id, add_time, action_date, '加购', '购物车', '', product_id, '',
         quantity, 0, 0, '', '', ''
  FROM t2_dwd_cart
  UNION ALL
  SELECT order_id, user_id, order_time, order_date, '下单', '订单页', '', '', order_id,
         0, 0, 0, '', province, city
  FROM t2_dwd_order
  UNION ALL
  SELECT review_id, user_id, review_time, review_date, '评价', '评价页', '', product_id, order_id,
         0, 0, 0, '', '', ''
  FROM t2_dwd_review
) a;

INSERT OVERWRITE TABLE t2_dwd_inventory
SELECT p.product_id, p.product_name, p.brand_id, p.shop_id, p.stock_qty, p.sales_qty, p.price,
       nvl(s.sales_qty_30d, 0) AS sales_qty_30d,
       nvl(s.sales_qty_30d, 0) / 30.0 AS avg_daily_sales,
       CASE WHEN nvl(s.sales_qty_30d, 0) > 0 THEN p.stock_qty / (s.sales_qty_30d / 30.0) ELSE 999 END AS turnover_days,
       CASE WHEN p.stock_qty = 0 THEN '断货' WHEN p.stock_qty < 20 THEN '低库存'
            WHEN nvl(s.sales_qty_30d, 0) = 0 OR p.stock_qty / (s.sales_qty_30d / 30.0) > 180 THEN '滞销'
            ELSE '健康' END AS stock_status
FROM t2_dim_product_info p
LEFT JOIN (
  SELECT product_id, sum(quantity) AS sales_qty_30d
  FROM t2_dwd_order_detail
  WHERE order_date >= date_sub(to_date('2025-11-11'), 29)
  GROUP BY product_id
) s ON p.product_id = s.product_id;
