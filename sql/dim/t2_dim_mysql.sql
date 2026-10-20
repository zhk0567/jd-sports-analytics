CREATE DATABASE IF NOT EXISTS `t2_ecommerce_ads` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `t2_ecommerce_ads`;

DROP TABLE IF EXISTS `t2_dim_user_info`;
CREATE TABLE `t2_dim_user_info` (
  `user_id` VARCHAR(255),
  `user_name` TEXT,
  `gender` VARCHAR(255),
  `age` BIGINT,
  `age_group` VARCHAR(255),
  `phone` VARCHAR(255),
  `email` VARCHAR(255),
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  `register_time` VARCHAR(255),
  `register_date` VARCHAR(255),
  `user_level` VARCHAR(255),
  `member_level_num` BIGINT,
  `is_member` VARCHAR(255),
  `last_login_time` VARCHAR(255),
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DIM user_info';

DROP TABLE IF EXISTS `t2_dim_product_info`;
CREATE TABLE `t2_dim_product_info` (
  `product_id` VARCHAR(255),
  `product_name` TEXT,
  `category_id` VARCHAR(255),
  `brand_id` VARCHAR(255),
  `shop_id` VARCHAR(255),
  `price` DECIMAL(18,4),
  `original_price` DECIMAL(18,4),
  `stock_qty` BIGINT,
  `sales_qty` BIGINT,
  `size` VARCHAR(255),
  `color` VARCHAR(255),
  `material` VARCHAR(255),
  `target_group` VARCHAR(255),
  `season` VARCHAR(255),
  `listing_date` VARCHAR(255),
  `status` VARCHAR(255),
  `image_url` TEXT,
  `brand_name` TEXT,
  `brand_level` VARCHAR(255),
  `brand_country` VARCHAR(255),
  `shop_name` TEXT,
  `shop_type` VARCHAR(255),
  `cat1_name` TEXT,
  `cat2_name` TEXT,
  `category_path` TEXT,
  `product_level` VARCHAR(255),
  PRIMARY KEY (`product_id`),
  KEY `idx_t2_dim_product_info_category_id` (`category_id`),
  KEY `idx_t2_dim_product_info_brand_id` (`brand_id`),
  KEY `idx_t2_dim_product_info_shop_id` (`shop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DIM product_info';

DROP TABLE IF EXISTS `t2_dim_category`;
CREATE TABLE `t2_dim_category` (
  `category_id` VARCHAR(255),
  `category_name` TEXT,
  `parent_id` VARCHAR(255),
  `category_level` VARCHAR(255),
  `category_path` TEXT,
  `sort_no` VARCHAR(255),
  `product_count` DECIMAL(18,4),
  PRIMARY KEY (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DIM category';

DROP TABLE IF EXISTS `t2_dim_date`;
CREATE TABLE `t2_dim_date` (
  `date_key` BIGINT,
  `stat_date` VARCHAR(255) NOT NULL,
  `year` BIGINT,
  `month` BIGINT,
  `day` BIGINT,
  `week` BIGINT,
  `quarter` BIGINT,
  `day_of_week` BIGINT,
  `day_name` TEXT,
  `is_weekend` BIGINT,
  `is_promo` BIGINT,
  `promo_name` TEXT,
  PRIMARY KEY (`date_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DIM date';

DROP TABLE IF EXISTS `t2_dim_region`;
CREATE TABLE `t2_dim_region` (
  `region_id` VARCHAR(255),
  `province` VARCHAR(255),
  `city` VARCHAR(255),
  `city_level` VARCHAR(255),
  PRIMARY KEY (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DIM region';

DROP TABLE IF EXISTS `t2_dim_brand`;
CREATE TABLE `t2_dim_brand` (
  `brand_id` VARCHAR(255),
  `brand_name` TEXT,
  `brand_country` VARCHAR(255),
  `brand_level` VARCHAR(255),
  `main_category` VARCHAR(255),
  `establish_year` VARCHAR(255),
  `product_count` BIGINT,
  PRIMARY KEY (`brand_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='t2 运动电商 DIM brand';
