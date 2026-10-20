CREATE DATABASE IF NOT EXISTS `t2_ecommerce_ads` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `t2_ecommerce_ads`;

DROP TABLE IF EXISTS `t2_dws_user_user_1d`;
CREATE TABLE `t2_dws_user_user_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `new_users` DECIMAL(18,4),
  `active_users` BIGINT,
  `order_users` BIGINT,
  `paid_users` BIGINT,
  `orders` BIGINT,
  `paid_orders` BIGINT,
  `gmv` DECIMAL(18,4),
  `arpu` DECIMAL(18,4),
  `repurchase_users` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS user_user_1d';

DROP TABLE IF EXISTS `t2_dws_user_user_nd`;
CREATE TABLE `t2_dws_user_user_nd` (
  `stat_date` VARCHAR(255) NOT NULL,
  `active_users_7d` BIGINT,
  `active_users_30d` BIGINT,
  `new_users_7d` BIGINT,
  `order_users_7d` BIGINT,
  `gmv_7d` DECIMAL(18,4),
  `gmv_30d` DECIMAL(18,4),
  `repeat_rate_30d` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS user_user_nd';

DROP TABLE IF EXISTS `t2_dws_user_user_total`;
CREATE TABLE `t2_dws_user_user_total` (
  `user_id` VARCHAR(255),
  `first_order_date` VARCHAR(255),
  `last_order_date` VARCHAR(255),
  `order_count` BIGINT,
  `paid_order_count` BIGINT,
  `total_gmv` DECIMAL(18,4),
  `avg_order_amount` DECIMAL(18,4),
  `days_since_last_order` BIGINT,
  `user_level` VARCHAR(255),
  `member_level_num` BIGINT,
  `rfm_r` BIGINT,
  `rfm_f` BIGINT,
  `rfm_m` BIGINT,
  KEY `idx_t2_dws_user_user_total_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS user_user_total';

DROP TABLE IF EXISTS `t2_dws_user_rfm`;
CREATE TABLE `t2_dws_user_rfm` (
  `user_id` VARCHAR(255),
  `rfm_r` BIGINT,
  `rfm_f` BIGINT,
  `rfm_m` BIGINT,
  `rfm_score` DECIMAL(18,4),
  `segment` VARCHAR(255),
  `last_order_date` VARCHAR(255),
  `order_count` BIGINT,
  `total_gmv` DECIMAL(18,4),
  KEY `idx_t2_dws_user_rfm_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS user_rfm';

DROP TABLE IF EXISTS `t2_dws_user_retention_1d`;
CREATE TABLE `t2_dws_user_retention_1d` (
  `cohort_date` VARCHAR(255),
  `cohort_users` BIGINT,
  `d1_users` BIGINT,
  `d1_rate` DECIMAL(18,4),
  `d7_users` BIGINT,
  `d7_rate` DECIMAL(18,4),
  `d30_users` BIGINT,
  `d30_rate` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS user_retention_1d';

DROP TABLE IF EXISTS `t2_dws_traffic_page_1d`;
CREATE TABLE `t2_dws_traffic_page_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `page` VARCHAR(255),
  `pv` BIGINT,
  `uv` BIGINT,
  `avg_duration` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS traffic_page_1d';

DROP TABLE IF EXISTS `t2_dws_traffic_user_1d`;
CREATE TABLE `t2_dws_traffic_user_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `pv` BIGINT,
  `uv` BIGINT,
  `visits` BIGINT,
  `avg_duration` DECIMAL(18,4),
  `new_user_ratio` DECIMAL(18,4),
  `bounce_rate` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS traffic_user_1d';

DROP TABLE IF EXISTS `t2_dws_user_funnel_1d`;
CREATE TABLE `t2_dws_user_funnel_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `search_users` BIGINT,
  `cart_users` BIGINT,
  `order_users` BIGINT,
  `pay_users` BIGINT,
  `search_to_cart_rate` DECIMAL(18,4),
  `cart_to_order_rate` DECIMAL(18,4),
  `order_to_pay_rate` DECIMAL(18,4),
  `overall_rate` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS user_funnel_1d';

DROP TABLE IF EXISTS `t2_dws_trade_product_1d`;
CREATE TABLE `t2_dws_trade_product_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `product_id` VARCHAR(255),
  `sales_qty` BIGINT,
  `gmv` DECIMAL(18,4),
  `order_count` BIGINT,
  `product_name` TEXT,
  `category_id` VARCHAR(255),
  `brand_id` VARCHAR(255),
  `cat1_name` TEXT,
  `cat2_name` TEXT,
  `uv` DECIMAL(18,4),
  `conversion_rate` DECIMAL(18,4),
  KEY `idx_t2_dws_trade_product_1d_product_id` (`product_id`),
  KEY `idx_t2_dws_trade_product_1d_category_id` (`category_id`),
  KEY `idx_t2_dws_trade_product_1d_brand_id` (`brand_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS trade_product_1d';

DROP TABLE IF EXISTS `t2_dws_trade_product_nd`;
CREATE TABLE `t2_dws_trade_product_nd` (
  `product_id` VARCHAR(255),
  `sales_qty_7d` DECIMAL(18,4),
  `gmv_7d` DECIMAL(18,4),
  `sales_qty_30d` BIGINT,
  `gmv_30d` DECIMAL(18,4),
  `stat_date` VARCHAR(255) NOT NULL,
  `rank_30d` BIGINT,
  KEY `idx_t2_dws_trade_product_nd_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS trade_product_nd';

DROP TABLE IF EXISTS `t2_dws_trade_category_1d`;
CREATE TABLE `t2_dws_trade_category_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `category_id` VARCHAR(255),
  `sales_qty` BIGINT,
  `gmv` DECIMAL(18,4),
  `order_count` BIGINT,
  `category_name` TEXT,
  `gmv_share` DECIMAL(18,4),
  KEY `idx_t2_dws_trade_category_1d_category_id` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS trade_category_1d';

DROP TABLE IF EXISTS `t2_dws_trade_category_nd`;
CREATE TABLE `t2_dws_trade_category_nd` (
  `category_id` VARCHAR(255),
  `gmv_7d` DECIMAL(18,4),
  `gmv_30d` DECIMAL(18,4),
  `gmv_prev_30d` DECIMAL(18,4),
  `growth_rate_30d` DECIMAL(18,4),
  `stat_date` VARCHAR(255) NOT NULL,
  KEY `idx_t2_dws_trade_category_nd_category_id` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS trade_category_nd';

DROP TABLE IF EXISTS `t2_dws_trade_brand_1d`;
CREATE TABLE `t2_dws_trade_brand_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `brand_id` VARCHAR(255),
  `sales_qty` BIGINT,
  `gmv` DECIMAL(18,4),
  `order_count` BIGINT,
  `brand_name` TEXT,
  `gmv_share` DECIMAL(18,4),
  KEY `idx_t2_dws_trade_brand_1d_brand_id` (`brand_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS trade_brand_1d';

DROP TABLE IF EXISTS `t2_dws_trade_region_1d`;
CREATE TABLE `t2_dws_trade_region_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  `order_count` BIGINT,
  `gmv` DECIMAL(18,4),
  `paid_users` BIGINT,
  `aov` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS trade_region_1d';

DROP TABLE IF EXISTS `t2_dws_trade_region_nd`;
CREATE TABLE `t2_dws_trade_region_nd` (
  `province` VARCHAR(255),
  `gmv_7d` DECIMAL(18,4),
  `gmv_30d` DECIMAL(18,4),
  `gmv_prev_30d` DECIMAL(18,4),
  `growth_rate_30d` DECIMAL(18,4),
  `stat_date` VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS trade_region_nd';

DROP TABLE IF EXISTS `t2_dws_user_region_total`;
CREATE TABLE `t2_dws_user_region_total` (
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  `total_users` BIGINT,
  `order_users` BIGINT,
  `total_gmv` DECIMAL(18,4),
  `avg_gmv_per_user` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS user_region_total';

DROP TABLE IF EXISTS `t2_dws_traffic_region_1d`;
CREATE TABLE `t2_dws_traffic_region_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `province` VARCHAR(255),
  `pv` BIGINT,
  `uv` BIGINT,
  `order_users` DECIMAL(18,4),
  `gmv` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS traffic_region_1d';

DROP TABLE IF EXISTS `t2_dws_promo_activity_1d`;
CREATE TABLE `t2_dws_promo_activity_1d` (
  `stat_date` VARCHAR(255) NOT NULL,
  `promo_id` VARCHAR(255),
  `order_count` BIGINT,
  `paid_orders` BIGINT,
  `gmv` DECIMAL(18,4),
  `aov` DECIMAL(18,4),
  `conversion_rate` DECIMAL(18,4),
  `uplift_rate` DECIMAL(18,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWS promo_activity_1d';
