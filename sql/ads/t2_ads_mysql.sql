CREATE DATABASE IF NOT EXISTS `t2_ecommerce_ads` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `t2_ecommerce_ads`;

DROP TABLE IF EXISTS `t2_ads_gmv_total`;
CREATE TABLE `t2_ads_gmv_total` (
  `stat_date` VARCHAR(255) NOT NULL,
  `today_gmv` DECIMAL(18,4),
  `total_gmv` DECIMAL(18,4),
  `yesterday_gmv` DECIMAL(18,4),
  `mom_rate` DECIMAL(18,4),
  `yoy_rate` DECIMAL(18,4),
  `paid_orders` BIGINT,
  `aov` DECIMAL(18,4),
  `pay_rate` DECIMAL(18,4),
  `updated_at` VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS gmv_total';

DROP TABLE IF EXISTS `t2_ads_gmv_daily`;
CREATE TABLE `t2_ads_gmv_daily` (
  `stat_date` VARCHAR(255) NOT NULL,
  `gmv` DECIMAL(18,4),
  `orders` BIGINT,
  `paid_orders` BIGINT,
  `pay_rate` DECIMAL(18,4),
  `aov` DECIMAL(18,4),
  `promo_name` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS gmv_daily';

DROP TABLE IF EXISTS `t2_ads_region_sales`;
CREATE TABLE `t2_ads_region_sales` (
  `province` VARCHAR(255),
  `gmv` DECIMAL(18,4),
  `order_count` BIGINT,
  `growth_rate` DECIMAL(18,4),
  `rank_no` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS region_sales';

DROP TABLE IF EXISTS `t2_ads_city_sales`;
CREATE TABLE `t2_ads_city_sales` (
  `city` VARCHAR(255),
  `province` VARCHAR(255),
  `gmv` DECIMAL(18,4),
  `order_count` BIGINT,
  `rank_no` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS city_sales';

DROP TABLE IF EXISTS `t2_ads_category_proportion`;
CREATE TABLE `t2_ads_category_proportion` (
  `category_id` VARCHAR(255),
  `category_name` TEXT,
  `gmv` DECIMAL(18,4),
  `gmv_share` DECIMAL(18,4),
  `order_count` BIGINT,
  `rank_no` BIGINT,
  KEY `idx_t2_ads_category_proportion_category_id` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS category_proportion';

DROP TABLE IF EXISTS `t2_ads_brand_rank`;
CREATE TABLE `t2_ads_brand_rank` (
  `brand_id` VARCHAR(255),
  `brand_name` TEXT,
  `sales_qty` BIGINT,
  `gmv` DECIMAL(18,4),
  `gmv_share` DECIMAL(18,4),
  `rank_no` BIGINT,
  KEY `idx_t2_ads_brand_rank_brand_id` (`brand_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS brand_rank';

DROP TABLE IF EXISTS `t2_ads_user_funnel`;
CREATE TABLE `t2_ads_user_funnel` (
  `stage_no` BIGINT,
  `stage_name` TEXT,
  `user_count` BIGINT,
  `conversion_rate` DECIMAL(18,4),
  `overall_rate` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS user_funnel';

DROP TABLE IF EXISTS `t2_ads_user_retention`;
CREATE TABLE `t2_ads_user_retention` (
  `period` VARCHAR(255),
  `retention_rate` DECIMAL(18,4),
  `cohort_users` BIGINT,
  `retained_users` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS user_retention';

DROP TABLE IF EXISTS `t2_ads_user_rfm`;
CREATE TABLE `t2_ads_user_rfm` (
  `segment` VARCHAR(255),
  `user_count` BIGINT,
  `avg_r` DECIMAL(18,4),
  `avg_f` DECIMAL(18,4),
  `avg_m` DECIMAL(18,4),
  `avg_monetary` DECIMAL(18,4),
  `user_share` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS user_rfm';

DROP TABLE IF EXISTS `t2_ads_product_rank`;
CREATE TABLE `t2_ads_product_rank` (
  `product_id` VARCHAR(255),
  `product_name` TEXT,
  `brand_name` TEXT,
  `category_name` TEXT,
  `sales_qty` BIGINT,
  `gmv` DECIMAL(18,4),
  `rank_no` BIGINT,
  KEY `idx_t2_ads_product_rank_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS product_rank';

DROP TABLE IF EXISTS `t2_ads_product_stock_warn`;
CREATE TABLE `t2_ads_product_stock_warn` (
  `product_id` VARCHAR(255),
  `product_name` TEXT,
  `stock_qty` BIGINT,
  `sales_qty_30d` DECIMAL(18,4),
  `turnover_days` DECIMAL(18,4),
  `warn_level` VARCHAR(255),
  KEY `idx_t2_ads_product_stock_warn_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS product_stock_warn';

DROP TABLE IF EXISTS `t2_ads_core_kpi`;
CREATE TABLE `t2_ads_core_kpi` (
  `metric_key` VARCHAR(255),
  `metric_name` TEXT,
  `metric_value` DECIMAL(18,4),
  `metric_unit` VARCHAR(255),
  `metric_group` VARCHAR(255),
  `definition` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS core_kpi';

DROP TABLE IF EXISTS `t2_ads_kpi_trend`;
CREATE TABLE `t2_ads_kpi_trend` (
  `stat_date` VARCHAR(255) NOT NULL,
  `gmv` DECIMAL(18,4),
  `orders` BIGINT,
  `uv` BIGINT,
  `aov` DECIMAL(18,4),
  `pay_rate` DECIMAL(18,4),
  `refund_rate` DECIMAL(18,4),
  `conversion_rate` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS kpi_trend';

DROP TABLE IF EXISTS `t2_ads_inventory_alarm`;
CREATE TABLE `t2_ads_inventory_alarm` (
  `product_id` VARCHAR(255),
  `product_name` TEXT,
  `brand_id` VARCHAR(255),
  `stock_qty` BIGINT,
  `safety_stock` BIGINT,
  `shortage` BIGINT,
  `alarm_level` VARCHAR(255),
  KEY `idx_t2_ads_inventory_alarm_product_id` (`product_id`),
  KEY `idx_t2_ads_inventory_alarm_brand_id` (`brand_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS inventory_alarm';

DROP TABLE IF EXISTS `t2_ads_sales_forecast`;
CREATE TABLE `t2_ads_sales_forecast` (
  `forecast_date` VARCHAR(255),
  `predicted_gmv` DECIMAL(18,4),
  `lower_bound` BIGINT,
  `upper_bound` DECIMAL(18,4),
  `model_name` TEXT,
  `mae` DECIMAL(18,4),
  `rmse` DECIMAL(18,4),
  `r2` DECIMAL(18,4),
  `mape` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS sales_forecast';

DROP TABLE IF EXISTS `t2_ads_user_churn_predict`;
CREATE TABLE `t2_ads_user_churn_predict` (
  `user_id` VARCHAR(255),
  `churn_prob` DECIMAL(18,4),
  `risk_level` VARCHAR(255),
  `recency_days` BIGINT,
  `frequency` BIGINT,
  `monetary` DECIMAL(18,4),
  `member_level` BIGINT,
  `rank_no` BIGINT,
  KEY `idx_t2_ads_user_churn_predict_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ADS user_churn_predict';
