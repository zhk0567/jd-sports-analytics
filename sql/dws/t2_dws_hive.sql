CREATE DATABASE IF NOT EXISTS t2_ecommerce;
USE t2_ecommerce;

DROP TABLE IF EXISTS `t2_dws_user_user_1d`;
CREATE TABLE `t2_dws_user_user_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `new_users` DOUBLE COMMENT 'new_users',
  `active_users` BIGINT COMMENT 'active_users',
  `order_users` BIGINT COMMENT 'order_users',
  `paid_users` BIGINT COMMENT 'paid_users',
  `orders` BIGINT COMMENT 'orders',
  `paid_orders` BIGINT COMMENT 'paid_orders',
  `gmv` DOUBLE COMMENT 'gmv',
  `arpu` DOUBLE COMMENT 'arpu',
  `repurchase_users` DOUBLE COMMENT 'repurchase_users'
) COMMENT 't2 运动电商 DWS user_user_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_user_user_nd`;
CREATE TABLE `t2_dws_user_user_nd` (
  `stat_date` STRING COMMENT 'stat_date',
  `active_users_7d` BIGINT COMMENT 'active_users_7d',
  `active_users_30d` BIGINT COMMENT 'active_users_30d',
  `new_users_7d` BIGINT COMMENT 'new_users_7d',
  `order_users_7d` BIGINT COMMENT 'order_users_7d',
  `gmv_7d` DOUBLE COMMENT 'gmv_7d',
  `gmv_30d` DOUBLE COMMENT 'gmv_30d',
  `repeat_rate_30d` DOUBLE COMMENT 'repeat_rate_30d'
) COMMENT 't2 运动电商 DWS user_user_nd'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_user_user_total`;
CREATE TABLE `t2_dws_user_user_total` (
  `user_id` STRING COMMENT 'user_id',
  `first_order_date` STRING COMMENT 'first_order_date',
  `last_order_date` STRING COMMENT 'last_order_date',
  `order_count` BIGINT COMMENT 'order_count',
  `paid_order_count` BIGINT COMMENT 'paid_order_count',
  `total_gmv` DOUBLE COMMENT 'total_gmv',
  `avg_order_amount` DOUBLE COMMENT 'avg_order_amount',
  `days_since_last_order` BIGINT COMMENT 'days_since_last_order',
  `user_level` STRING COMMENT 'user_level',
  `member_level_num` BIGINT COMMENT 'member_level_num',
  `rfm_r` BIGINT COMMENT 'rfm_r',
  `rfm_f` BIGINT COMMENT 'rfm_f',
  `rfm_m` BIGINT COMMENT 'rfm_m'
) COMMENT 't2 运动电商 DWS user_user_total' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_user_rfm`;
CREATE TABLE `t2_dws_user_rfm` (
  `user_id` STRING COMMENT 'user_id',
  `rfm_r` BIGINT COMMENT 'rfm_r',
  `rfm_f` BIGINT COMMENT 'rfm_f',
  `rfm_m` BIGINT COMMENT 'rfm_m',
  `rfm_score` DOUBLE COMMENT 'rfm_score',
  `segment` STRING COMMENT 'segment',
  `last_order_date` STRING COMMENT 'last_order_date',
  `order_count` BIGINT COMMENT 'order_count',
  `total_gmv` DOUBLE COMMENT 'total_gmv'
) COMMENT 't2 运动电商 DWS user_rfm' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_user_retention_1d`;
CREATE TABLE `t2_dws_user_retention_1d` (
  `cohort_date` STRING COMMENT 'cohort_date',
  `cohort_users` BIGINT COMMENT 'cohort_users',
  `d1_users` BIGINT COMMENT 'd1_users',
  `d1_rate` DOUBLE COMMENT 'd1_rate',
  `d7_users` BIGINT COMMENT 'd7_users',
  `d7_rate` DOUBLE COMMENT 'd7_rate',
  `d30_users` BIGINT COMMENT 'd30_users',
  `d30_rate` DOUBLE COMMENT 'd30_rate'
) COMMENT 't2 运动电商 DWS user_retention_1d' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_traffic_page_1d`;
CREATE TABLE `t2_dws_traffic_page_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `page` STRING COMMENT 'page',
  `pv` BIGINT COMMENT 'pv',
  `uv` BIGINT COMMENT 'uv',
  `avg_duration` DOUBLE COMMENT 'avg_duration'
) COMMENT 't2 运动电商 DWS traffic_page_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_traffic_user_1d`;
CREATE TABLE `t2_dws_traffic_user_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `pv` BIGINT COMMENT 'pv',
  `uv` BIGINT COMMENT 'uv',
  `visits` BIGINT COMMENT 'visits',
  `avg_duration` DOUBLE COMMENT 'avg_duration',
  `new_user_ratio` DOUBLE COMMENT 'new_user_ratio',
  `bounce_rate` BIGINT COMMENT 'bounce_rate'
) COMMENT 't2 运动电商 DWS traffic_user_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_user_funnel_1d`;
CREATE TABLE `t2_dws_user_funnel_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `search_users` BIGINT COMMENT 'search_users',
  `cart_users` BIGINT COMMENT 'cart_users',
  `order_users` BIGINT COMMENT 'order_users',
  `pay_users` BIGINT COMMENT 'pay_users',
  `search_to_cart_rate` DOUBLE COMMENT 'search_to_cart_rate',
  `cart_to_order_rate` DOUBLE COMMENT 'cart_to_order_rate',
  `order_to_pay_rate` DOUBLE COMMENT 'order_to_pay_rate',
  `overall_rate` DOUBLE COMMENT 'overall_rate'
) COMMENT 't2 运动电商 DWS user_funnel_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_trade_product_1d`;
CREATE TABLE `t2_dws_trade_product_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `product_id` STRING COMMENT 'product_id',
  `sales_qty` BIGINT COMMENT 'sales_qty',
  `gmv` DOUBLE COMMENT 'gmv',
  `order_count` BIGINT COMMENT 'order_count',
  `product_name` STRING COMMENT 'product_name',
  `category_id` STRING COMMENT 'category_id',
  `brand_id` STRING COMMENT 'brand_id',
  `cat1_name` STRING COMMENT 'cat1_name',
  `cat2_name` STRING COMMENT 'cat2_name',
  `uv` DOUBLE COMMENT 'uv',
  `conversion_rate` DOUBLE COMMENT 'conversion_rate'
) COMMENT 't2 运动电商 DWS trade_product_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_trade_product_nd`;
CREATE TABLE `t2_dws_trade_product_nd` (
  `product_id` STRING COMMENT 'product_id',
  `sales_qty_7d` DOUBLE COMMENT 'sales_qty_7d',
  `gmv_7d` DOUBLE COMMENT 'gmv_7d',
  `sales_qty_30d` BIGINT COMMENT 'sales_qty_30d',
  `gmv_30d` DOUBLE COMMENT 'gmv_30d',
  `stat_date` STRING COMMENT 'stat_date',
  `rank_30d` BIGINT COMMENT 'rank_30d'
) COMMENT 't2 运动电商 DWS trade_product_nd'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_trade_category_1d`;
CREATE TABLE `t2_dws_trade_category_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `category_id` STRING COMMENT 'category_id',
  `sales_qty` BIGINT COMMENT 'sales_qty',
  `gmv` DOUBLE COMMENT 'gmv',
  `order_count` BIGINT COMMENT 'order_count',
  `category_name` STRING COMMENT 'category_name',
  `gmv_share` DOUBLE COMMENT 'gmv_share'
) COMMENT 't2 运动电商 DWS trade_category_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_trade_category_nd`;
CREATE TABLE `t2_dws_trade_category_nd` (
  `category_id` STRING COMMENT 'category_id',
  `gmv_7d` DOUBLE COMMENT 'gmv_7d',
  `gmv_30d` DOUBLE COMMENT 'gmv_30d',
  `gmv_prev_30d` DOUBLE COMMENT 'gmv_prev_30d',
  `growth_rate_30d` DOUBLE COMMENT 'growth_rate_30d',
  `stat_date` STRING COMMENT 'stat_date'
) COMMENT 't2 运动电商 DWS trade_category_nd'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_trade_brand_1d`;
CREATE TABLE `t2_dws_trade_brand_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `brand_id` STRING COMMENT 'brand_id',
  `sales_qty` BIGINT COMMENT 'sales_qty',
  `gmv` DOUBLE COMMENT 'gmv',
  `order_count` BIGINT COMMENT 'order_count',
  `brand_name` STRING COMMENT 'brand_name',
  `gmv_share` DOUBLE COMMENT 'gmv_share'
) COMMENT 't2 运动电商 DWS trade_brand_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_trade_region_1d`;
CREATE TABLE `t2_dws_trade_region_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city',
  `order_count` BIGINT COMMENT 'order_count',
  `gmv` DOUBLE COMMENT 'gmv',
  `paid_users` BIGINT COMMENT 'paid_users',
  `aov` DOUBLE COMMENT 'aov'
) COMMENT 't2 运动电商 DWS trade_region_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_trade_region_nd`;
CREATE TABLE `t2_dws_trade_region_nd` (
  `province` STRING COMMENT 'province',
  `gmv_7d` DOUBLE COMMENT 'gmv_7d',
  `gmv_30d` DOUBLE COMMENT 'gmv_30d',
  `gmv_prev_30d` DOUBLE COMMENT 'gmv_prev_30d',
  `growth_rate_30d` DOUBLE COMMENT 'growth_rate_30d',
  `stat_date` STRING COMMENT 'stat_date'
) COMMENT 't2 运动电商 DWS trade_region_nd'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_user_region_total`;
CREATE TABLE `t2_dws_user_region_total` (
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city',
  `total_users` BIGINT COMMENT 'total_users',
  `order_users` BIGINT COMMENT 'order_users',
  `total_gmv` DOUBLE COMMENT 'total_gmv',
  `avg_gmv_per_user` DOUBLE COMMENT 'avg_gmv_per_user'
) COMMENT 't2 运动电商 DWS user_region_total' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_traffic_region_1d`;
CREATE TABLE `t2_dws_traffic_region_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `province` STRING COMMENT 'province',
  `pv` BIGINT COMMENT 'pv',
  `uv` BIGINT COMMENT 'uv',
  `order_users` DOUBLE COMMENT 'order_users',
  `gmv` DOUBLE COMMENT 'gmv'
) COMMENT 't2 运动电商 DWS traffic_region_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dws_promo_activity_1d`;
CREATE TABLE `t2_dws_promo_activity_1d` (
  `stat_date` STRING COMMENT 'stat_date',
  `promo_id` STRING COMMENT 'promo_id',
  `order_count` BIGINT COMMENT 'order_count',
  `paid_orders` BIGINT COMMENT 'paid_orders',
  `gmv` DOUBLE COMMENT 'gmv',
  `aov` DOUBLE COMMENT 'aov',
  `conversion_rate` DOUBLE COMMENT 'conversion_rate',
  `uplift_rate` DOUBLE COMMENT 'uplift_rate'
) COMMENT 't2 运动电商 DWS promo_activity_1d'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');
