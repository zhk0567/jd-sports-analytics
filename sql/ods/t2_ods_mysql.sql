CREATE DATABASE IF NOT EXISTS `t2_ecommerce_ods` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `t2_ecommerce_ods`;

DROP TABLE IF EXISTS `t2_ods_user_info`;
CREATE TABLE `t2_ods_user_info` (
  `user_id` VARCHAR(255),
  `username` TEXT,
  `gender` VARCHAR(255),
  `age` VARCHAR(255),
  `phone` VARCHAR(255),
  `email` VARCHAR(255),
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  `register_time` VARCHAR(255),
  `user_level` VARCHAR(255),
  `is_member` VARCHAR(255),
  `last_login_time` VARCHAR(255),
  KEY `idx_t2_ods_user_info_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS user_info';

DROP TABLE IF EXISTS `t2_ods_category`;
CREATE TABLE `t2_ods_category` (
  `category_id` VARCHAR(255),
  `category_name` TEXT,
  `parent_id` VARCHAR(255),
  `category_level` VARCHAR(255),
  `category_path` TEXT,
  `sort_no` VARCHAR(255),
  KEY `idx_t2_ods_category_category_id` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS category';

DROP TABLE IF EXISTS `t2_ods_product_info`;
CREATE TABLE `t2_ods_product_info` (
  `product_id` VARCHAR(255),
  `product_name` TEXT,
  `category_id` VARCHAR(255),
  `brand_id` VARCHAR(255),
  `shop_id` VARCHAR(255),
  `price` VARCHAR(255),
  `original_price` VARCHAR(255),
  `stock_qty` VARCHAR(255),
  `sales_qty` VARCHAR(255),
  `size` VARCHAR(255),
  `color` VARCHAR(255),
  `material` VARCHAR(255),
  `target_group` VARCHAR(255),
  `season` VARCHAR(255),
  `listing_date` VARCHAR(255),
  `status` VARCHAR(255),
  `image_url` TEXT,
  KEY `idx_t2_ods_product_info_product_id` (`product_id`),
  KEY `idx_t2_ods_product_info_category_id` (`category_id`),
  KEY `idx_t2_ods_product_info_brand_id` (`brand_id`),
  KEY `idx_t2_ods_product_info_shop_id` (`shop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS product_info';

DROP TABLE IF EXISTS `t2_ods_brand_info`;
CREATE TABLE `t2_ods_brand_info` (
  `brand_id` VARCHAR(255),
  `brand_name` TEXT,
  `brand_country` VARCHAR(255),
  `brand_level` VARCHAR(255),
  `main_category` VARCHAR(255),
  `establish_year` VARCHAR(255),
  KEY `idx_t2_ods_brand_info_brand_id` (`brand_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS brand_info';

DROP TABLE IF EXISTS `t2_ods_shop_info`;
CREATE TABLE `t2_ods_shop_info` (
  `shop_id` VARCHAR(255),
  `shop_name` TEXT,
  `shop_type` VARCHAR(255),
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  `rating` VARCHAR(255),
  `open_date` VARCHAR(255),
  KEY `idx_t2_ods_shop_info_shop_id` (`shop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS shop_info';

DROP TABLE IF EXISTS `t2_ods_order_info`;
CREATE TABLE `t2_ods_order_info` (
  `order_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `order_time` VARCHAR(255),
  `order_status` VARCHAR(255),
  `total_amount` VARCHAR(255),
  `discount_amount` VARCHAR(255),
  `shipping_fee` VARCHAR(255),
  `pay_amount` VARCHAR(255),
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  `channel` VARCHAR(255),
  `promo_id` VARCHAR(255),
  `coupon_amount` VARCHAR(255),
  `order_date` VARCHAR(255),
  KEY `idx_t2_ods_order_info_order_id` (`order_id`),
  KEY `idx_t2_ods_order_info_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS order_info';

DROP TABLE IF EXISTS `t2_ods_order_detail`;
CREATE TABLE `t2_ods_order_detail` (
  `detail_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `product_id` VARCHAR(255),
  `quantity` VARCHAR(255),
  `unit_price` VARCHAR(255),
  `discount_amount` VARCHAR(255),
  `line_amount` VARCHAR(255),
  KEY `idx_t2_ods_order_detail_detail_id` (`detail_id`),
  KEY `idx_t2_ods_order_detail_order_id` (`order_id`),
  KEY `idx_t2_ods_order_detail_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS order_detail';

DROP TABLE IF EXISTS `t2_ods_payment_info`;
CREATE TABLE `t2_ods_payment_info` (
  `payment_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `pay_time` VARCHAR(255),
  `pay_amount` VARCHAR(255),
  `pay_method` VARCHAR(255),
  `pay_status` VARCHAR(255),
  `transaction_no` VARCHAR(255),
  KEY `idx_t2_ods_payment_info_payment_id` (`payment_id`),
  KEY `idx_t2_ods_payment_info_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS payment_info';

DROP TABLE IF EXISTS `t2_ods_refund_info`;
CREATE TABLE `t2_ods_refund_info` (
  `refund_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `refund_time` VARCHAR(255),
  `refund_amount` VARCHAR(255),
  `refund_reason` VARCHAR(255),
  `refund_status` VARCHAR(255),
  `refund_type` VARCHAR(255),
  KEY `idx_t2_ods_refund_info_refund_id` (`refund_id`),
  KEY `idx_t2_ods_refund_info_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS refund_info';

DROP TABLE IF EXISTS `t2_ods_logistics_info`;
CREATE TABLE `t2_ods_logistics_info` (
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
  KEY `idx_t2_ods_logistics_info_logistics_id` (`logistics_id`),
  KEY `idx_t2_ods_logistics_info_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS logistics_info';

DROP TABLE IF EXISTS `t2_ods_review_info`;
CREATE TABLE `t2_ods_review_info` (
  `review_id` VARCHAR(255),
  `order_id` VARCHAR(255),
  `product_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `review_time` VARCHAR(255),
  `rating` VARCHAR(255),
  `review_content` TEXT,
  `is_anonymous` VARCHAR(255),
  `images_count` VARCHAR(255),
  KEY `idx_t2_ods_review_info_review_id` (`review_id`),
  KEY `idx_t2_ods_review_info_order_id` (`order_id`),
  KEY `idx_t2_ods_review_info_product_id` (`product_id`),
  KEY `idx_t2_ods_review_info_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS review_info';

DROP TABLE IF EXISTS `t2_ods_cart_info`;
CREATE TABLE `t2_ods_cart_info` (
  `cart_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `product_id` VARCHAR(255),
  `add_time` VARCHAR(255),
  `quantity` VARCHAR(255),
  `cart_status` VARCHAR(255),
  `source_page` VARCHAR(255),
  KEY `idx_t2_ods_cart_info_cart_id` (`cart_id`),
  KEY `idx_t2_ods_cart_info_user_id` (`user_id`),
  KEY `idx_t2_ods_cart_info_product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS cart_info';

DROP TABLE IF EXISTS `t2_ods_search_log`;
CREATE TABLE `t2_ods_search_log` (
  `log_id` VARCHAR(255),
  `user_id` VARCHAR(255),
  `search_time` VARCHAR(255),
  `keyword` VARCHAR(255),
  `scene` VARCHAR(255),
  `result_count` VARCHAR(255),
  `click_count` VARCHAR(255),
  `duration_sec` VARCHAR(255),
  `device` VARCHAR(255),
  `session_id` VARCHAR(255),
  KEY `idx_t2_ods_search_log_log_id` (`log_id`),
  KEY `idx_t2_ods_search_log_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 ODS search_log';
