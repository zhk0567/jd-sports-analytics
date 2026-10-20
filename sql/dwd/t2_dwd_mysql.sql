CREATE DATABASE IF NOT EXISTS `t2_ecommerce_ads` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `t2_ecommerce_ads`;

DROP TABLE IF EXISTS `t2_dwd_order`;
CREATE TABLE `t2_dwd_order` (
  `order_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `order_time` VARCHAR(255),
  `order_date` VARCHAR(255),
  `order_status` VARCHAR(255),
  `total_amount` DECIMAL(18,4),
  `discount_amount` DECIMAL(18,4),
  `shipping_fee` DECIMAL(18,4),
  `coupon_amount` DECIMAL(18,4),
  `pay_amount` DECIMAL(18,4),
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  `channel` VARCHAR(255),
  `promo_id` VARCHAR(255),
  `is_paid` BIGINT,
  PRIMARY KEY (`order_id`),
  KEY `idx_t2_dwd_order_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD order';

DROP TABLE IF EXISTS `t2_dwd_order_detail`;
CREATE TABLE `t2_dwd_order_detail` (
  `detail_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `product_id` VARCHAR(255),
  `quantity` BIGINT,
  `unit_price` DECIMAL(18,4),
  `discount_amount` VARCHAR(255),
  `line_amount` DECIMAL(18,4),
  `total_amount` DECIMAL(18,4),
  `pay_amount` DECIMAL(18,4),
  `order_date` VARCHAR(255),
  `line_gmv` DECIMAL(18,4),
  `product_name` TEXT,
  `category_id` VARCHAR(255),
  `brand_id` VARCHAR(255),
  `shop_id` VARCHAR(255),
  PRIMARY KEY (`detail_id`),
  KEY `idx_t2_dwd_order_detail_order_id` (`order_id`),
  KEY `idx_t2_dwd_order_detail_product_id` (`product_id`),
  KEY `idx_t2_dwd_order_detail_category_id` (`category_id`),
  KEY `idx_t2_dwd_order_detail_brand_id` (`brand_id`),
  KEY `idx_t2_dwd_order_detail_shop_id` (`shop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD order_detail';

DROP TABLE IF EXISTS `t2_dwd_payment`;
CREATE TABLE `t2_dwd_payment` (
  `payment_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `pay_time` VARCHAR(255),
  `pay_amount` DECIMAL(18,4),
  `pay_method` VARCHAR(255),
  `pay_status` VARCHAR(255),
  `transaction_no` VARCHAR(255),
  `pay_date` VARCHAR(255),
  PRIMARY KEY (`payment_id`),
  KEY `idx_t2_dwd_payment_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD payment';

DROP TABLE IF EXISTS `t2_dwd_refund`;
CREATE TABLE `t2_dwd_refund` (
  `refund_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `refund_time` VARCHAR(255),
  `refund_amount` DECIMAL(18,4),
  `refund_reason` VARCHAR(255),
  `refund_status` VARCHAR(255),
  `refund_type` VARCHAR(255),
  `refund_date` VARCHAR(255),
  PRIMARY KEY (`refund_id`),
  KEY `idx_t2_dwd_refund_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD refund';

DROP TABLE IF EXISTS `t2_dwd_logistics`;
CREATE TABLE `t2_dwd_logistics` (
  `logistics_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `ship_time` VARCHAR(255),
  `deliver_time` VARCHAR(255),
  `sign_time` VARCHAR(255),
  `logistics_company` VARCHAR(255),
  `tracking_no` VARCHAR(255),
  `logistics_status` VARCHAR(255),
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  PRIMARY KEY (`logistics_id`),
  KEY `idx_t2_dwd_logistics_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD logistics';

DROP TABLE IF EXISTS `t2_dwd_review`;
CREATE TABLE `t2_dwd_review` (
  `review_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `product_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `review_time` VARCHAR(255),
  `rating` BIGINT,
  `review_content` TEXT,
  `is_anonymous` VARCHAR(255),
  `images_count` VARCHAR(255),
  `sentiment` VARCHAR(255),
  `review_date` VARCHAR(255),
  PRIMARY KEY (`review_id`),
  KEY `idx_t2_dwd_review_order_id` (`order_id`),
  KEY `idx_t2_dwd_review_product_id` (`product_id`),
  KEY `idx_t2_dwd_review_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD review';

DROP TABLE IF EXISTS `t2_dwd_cart`;
CREATE TABLE `t2_dwd_cart` (
  `cart_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `product_id` VARCHAR(255),
  `add_time` VARCHAR(255),
  `quantity` BIGINT,
  `cart_status` VARCHAR(255),
  `source_page` VARCHAR(255),
  `action_date` VARCHAR(255),
  PRIMARY KEY (`cart_id`),
  KEY `idx_t2_dwd_cart_user_id` (`user_id`),
  KEY `idx_t2_dwd_cart_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD cart';

DROP TABLE IF EXISTS `t2_dwd_search_log`;
CREATE TABLE `t2_dwd_search_log` (
  `log_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `search_time` VARCHAR(255),
  `keyword` VARCHAR(255),
  `scene` VARCHAR(255),
  `result_count` VARCHAR(255),
  `click_count` BIGINT,
  `duration_sec` BIGINT,
  `device` VARCHAR(255),
  `session_id` VARCHAR(255),
  `search_date` VARCHAR(255),
  PRIMARY KEY (`log_id`),
  KEY `idx_t2_dwd_search_log_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD search_log';

DROP TABLE IF EXISTS `t2_dwd_user_action`;
CREATE TABLE `t2_dwd_user_action` (
  `action_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `action_time` VARCHAR(255),
  `keyword` VARCHAR(255),
  `click_count` BIGINT,
  `duration_sec` BIGINT,
  `device` VARCHAR(255),
  `action_type` VARCHAR(255),
  `page` VARCHAR(255),
  `product_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  `quantity` DECIMAL(18,4),
  `action_date` VARCHAR(255),
  PRIMARY KEY (`user_id`),
  KEY `idx_t2_dwd_user_action_product_id` (`product_id`),
  KEY `idx_t2_dwd_user_action_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD user_action';

DROP TABLE IF EXISTS `t2_dwd_inventory`;
CREATE TABLE `t2_dwd_inventory` (
  `product_id` VARCHAR(255),
  `product_name` TEXT,
  `brand_id` VARCHAR(255),
  `shop_id` VARCHAR(255),
  `stock_qty` BIGINT,
  `sales_qty` BIGINT,
  `price` DECIMAL(18,4),
  `sales_qty_30d` DECIMAL(18,4),
  `avg_daily_sales` DECIMAL(18,4),
  `turnover_days` DECIMAL(18,4),
  `stock_status` VARCHAR(255),
  PRIMARY KEY (`product_id`),
  KEY `idx_t2_dwd_inventory_brand_id` (`brand_id`),
  KEY `idx_t2_dwd_inventory_shop_id` (`shop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DWD inventory';
