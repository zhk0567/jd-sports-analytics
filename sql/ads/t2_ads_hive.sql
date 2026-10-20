CREATE DATABASE IF NOT EXISTS t2_ecommerce;
USE t2_ecommerce;

DROP TABLE IF EXISTS `t2_ads_gmv_total`;
CREATE TABLE `t2_ads_gmv_total` (
  `stat_date` STRING COMMENT 'stat_date',
  `today_gmv` DOUBLE COMMENT 'today_gmv',
  `total_gmv` DOUBLE COMMENT 'total_gmv',
  `yesterday_gmv` DOUBLE COMMENT 'yesterday_gmv',
  `mom_rate` DOUBLE COMMENT 'mom_rate',
  `yoy_rate` DOUBLE COMMENT 'yoy_rate',
  `paid_orders` BIGINT COMMENT 'paid_orders',
  `aov` DOUBLE COMMENT 'aov',
  `pay_rate` DOUBLE COMMENT 'pay_rate',
  `updated_at` STRING COMMENT 'updated_at'
) COMMENT 't2 运动电商 ADS gmv_total'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_gmv_daily`;
CREATE TABLE `t2_ads_gmv_daily` (
  `stat_date` STRING COMMENT 'stat_date',
  `gmv` DOUBLE COMMENT 'gmv',
  `orders` BIGINT COMMENT 'orders',
  `paid_orders` BIGINT COMMENT 'paid_orders',
  `pay_rate` DOUBLE COMMENT 'pay_rate',
  `aov` DOUBLE COMMENT 'aov',
  `promo_name` STRING COMMENT 'promo_name'
) COMMENT 't2 运动电商 ADS gmv_daily'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_region_sales`;
CREATE TABLE `t2_ads_region_sales` (
  `province` STRING COMMENT 'province',
  `gmv` DOUBLE COMMENT 'gmv',
  `order_count` BIGINT COMMENT 'order_count',
  `growth_rate` DOUBLE COMMENT 'growth_rate',
  `rank_no` BIGINT COMMENT 'rank_no'
) COMMENT 't2 运动电商 ADS region_sales' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_city_sales`;
CREATE TABLE `t2_ads_city_sales` (
  `city` STRING COMMENT 'city',
  `province` STRING COMMENT 'province',
  `gmv` DOUBLE COMMENT 'gmv',
  `order_count` BIGINT COMMENT 'order_count',
  `rank_no` BIGINT COMMENT 'rank_no'
) COMMENT 't2 运动电商 ADS city_sales' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_category_proportion`;
CREATE TABLE `t2_ads_category_proportion` (
  `category_id` STRING COMMENT 'category_id',
  `category_name` STRING COMMENT 'category_name',
  `gmv` DOUBLE COMMENT 'gmv',
  `gmv_share` DOUBLE COMMENT 'gmv_share',
  `order_count` BIGINT COMMENT 'order_count',
  `rank_no` BIGINT COMMENT 'rank_no'
) COMMENT 't2 运动电商 ADS category_proportion' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_brand_rank`;
CREATE TABLE `t2_ads_brand_rank` (
  `brand_id` STRING COMMENT 'brand_id',
  `brand_name` STRING COMMENT 'brand_name',
  `sales_qty` BIGINT COMMENT 'sales_qty',
  `gmv` DOUBLE COMMENT 'gmv',
  `gmv_share` DOUBLE COMMENT 'gmv_share',
  `rank_no` BIGINT COMMENT 'rank_no'
) COMMENT 't2 运动电商 ADS brand_rank' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_user_funnel`;
CREATE TABLE `t2_ads_user_funnel` (
  `stage_no` BIGINT COMMENT 'stage_no',
  `stage_name` STRING COMMENT 'stage_name',
  `user_count` BIGINT COMMENT 'user_count',
  `conversion_rate` DOUBLE COMMENT 'conversion_rate',
  `overall_rate` DOUBLE COMMENT 'overall_rate'
) COMMENT 't2 运动电商 ADS user_funnel' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_user_retention`;
CREATE TABLE `t2_ads_user_retention` (
  `period` STRING COMMENT 'period',
  `retention_rate` DOUBLE COMMENT 'retention_rate',
  `cohort_users` BIGINT COMMENT 'cohort_users',
  `retained_users` BIGINT COMMENT 'retained_users'
) COMMENT 't2 运动电商 ADS user_retention' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_user_rfm`;
CREATE TABLE `t2_ads_user_rfm` (
  `segment` STRING COMMENT 'segment',
  `user_count` BIGINT COMMENT 'user_count',
  `avg_r` DOUBLE COMMENT 'avg_r',
  `avg_f` DOUBLE COMMENT 'avg_f',
  `avg_m` DOUBLE COMMENT 'avg_m',
  `avg_monetary` DOUBLE COMMENT 'avg_monetary',
  `user_share` DOUBLE COMMENT 'user_share'
) COMMENT 't2 运动电商 ADS user_rfm' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_product_rank`;
CREATE TABLE `t2_ads_product_rank` (
  `product_id` STRING COMMENT 'product_id',
  `product_name` STRING COMMENT 'product_name',
  `brand_name` STRING COMMENT 'brand_name',
  `category_name` STRING COMMENT 'category_name',
  `sales_qty` BIGINT COMMENT 'sales_qty',
  `gmv` DOUBLE COMMENT 'gmv',
  `rank_no` BIGINT COMMENT 'rank_no'
) COMMENT 't2 运动电商 ADS product_rank' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_product_stock_warn`;
CREATE TABLE `t2_ads_product_stock_warn` (
  `product_id` STRING COMMENT 'product_id',
  `product_name` STRING COMMENT 'product_name',
  `stock_qty` BIGINT COMMENT 'stock_qty',
  `sales_qty_30d` DOUBLE COMMENT 'sales_qty_30d',
  `turnover_days` DOUBLE COMMENT 'turnover_days',
  `warn_level` STRING COMMENT 'warn_level'
) COMMENT 't2 运动电商 ADS product_stock_warn' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_core_kpi`;
CREATE TABLE `t2_ads_core_kpi` (
  `metric_key` STRING COMMENT 'metric_key',
  `metric_name` STRING COMMENT 'metric_name',
  `metric_value` DOUBLE COMMENT 'metric_value',
  `metric_unit` STRING COMMENT 'metric_unit',
  `metric_group` STRING COMMENT 'metric_group',
  `definition` STRING COMMENT 'definition'
) COMMENT 't2 运动电商 ADS core_kpi' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_kpi_trend`;
CREATE TABLE `t2_ads_kpi_trend` (
  `stat_date` STRING COMMENT 'stat_date',
  `gmv` DOUBLE COMMENT 'gmv',
  `orders` BIGINT COMMENT 'orders',
  `uv` BIGINT COMMENT 'uv',
  `aov` DOUBLE COMMENT 'aov',
  `pay_rate` DOUBLE COMMENT 'pay_rate',
  `refund_rate` DOUBLE COMMENT 'refund_rate',
  `conversion_rate` DOUBLE COMMENT 'conversion_rate'
) COMMENT 't2 运动电商 ADS kpi_trend'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_inventory_alarm`;
CREATE TABLE `t2_ads_inventory_alarm` (
  `product_id` STRING COMMENT 'product_id',
  `product_name` STRING COMMENT 'product_name',
  `brand_id` STRING COMMENT 'brand_id',
  `stock_qty` BIGINT COMMENT 'stock_qty',
  `safety_stock` BIGINT COMMENT 'safety_stock',
  `shortage` BIGINT COMMENT 'shortage',
  `alarm_level` STRING COMMENT 'alarm_level'
) COMMENT 't2 运动电商 ADS inventory_alarm' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_sales_forecast`;
CREATE TABLE `t2_ads_sales_forecast` (
  `forecast_date` STRING COMMENT 'forecast_date',
  `predicted_gmv` DOUBLE COMMENT 'predicted_gmv',
  `lower_bound` BIGINT COMMENT 'lower_bound',
  `upper_bound` DOUBLE COMMENT 'upper_bound',
  `model_name` STRING COMMENT 'model_name',
  `mae` DOUBLE COMMENT 'mae',
  `rmse` DOUBLE COMMENT 'rmse',
  `r2` DOUBLE COMMENT 'r2',
  `mape` DOUBLE COMMENT 'mape'
) COMMENT 't2 运动电商 ADS sales_forecast' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_ads_user_churn_predict`;
CREATE TABLE `t2_ads_user_churn_predict` (
  `user_id` STRING COMMENT 'user_id',
  `churn_prob` DOUBLE COMMENT 'churn_prob',
  `risk_level` STRING COMMENT 'risk_level',
  `recency_days` BIGINT COMMENT 'recency_days',
  `frequency` BIGINT COMMENT 'frequency',
  `monetary` DOUBLE COMMENT 'monetary',
  `member_level` BIGINT COMMENT 'member_level',
  `rank_no` BIGINT COMMENT 'rank_no'
) COMMENT 't2 运动电商 ADS user_churn_predict' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');
