CREATE DATABASE IF NOT EXISTS t2_ecommerce;
USE t2_ecommerce;

DROP TABLE IF EXISTS `t2_dim_user_info`;
CREATE TABLE `t2_dim_user_info` (
  `user_id` STRING COMMENT 'user_id',
  `user_name` STRING COMMENT 'user_name',
  `gender` STRING COMMENT 'gender',
  `age` BIGINT COMMENT 'age',
  `age_group` STRING COMMENT 'age_group',
  `phone` STRING COMMENT 'phone',
  `email` STRING COMMENT 'email',
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city',
  `register_time` STRING COMMENT 'register_time',
  `register_date` STRING COMMENT 'register_date',
  `user_level` STRING COMMENT 'user_level',
  `member_level_num` BIGINT COMMENT 'member_level_num',
  `is_member` STRING COMMENT 'is_member',
  `last_login_time` STRING COMMENT 'last_login_time'
) COMMENT 't2 运动电商 DIM user_info' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dim_product_info`;
CREATE TABLE `t2_dim_product_info` (
  `product_id` STRING COMMENT 'product_id',
  `product_name` STRING COMMENT 'product_name',
  `category_id` STRING COMMENT 'category_id',
  `brand_id` STRING COMMENT 'brand_id',
  `shop_id` STRING COMMENT 'shop_id',
  `price` DOUBLE COMMENT 'price',
  `original_price` DOUBLE COMMENT 'original_price',
  `stock_qty` BIGINT COMMENT 'stock_qty',
  `sales_qty` BIGINT COMMENT 'sales_qty',
  `size` STRING COMMENT 'size',
  `color` STRING COMMENT 'color',
  `material` STRING COMMENT 'material',
  `target_group` STRING COMMENT 'target_group',
  `season` STRING COMMENT 'season',
  `listing_date` STRING COMMENT 'listing_date',
  `status` STRING COMMENT 'status',
  `image_url` STRING COMMENT 'image_url',
  `brand_name` STRING COMMENT 'brand_name',
  `brand_level` STRING COMMENT 'brand_level',
  `brand_country` STRING COMMENT 'brand_country',
  `shop_name` STRING COMMENT 'shop_name',
  `shop_type` STRING COMMENT 'shop_type',
  `cat1_name` STRING COMMENT 'cat1_name',
  `cat2_name` STRING COMMENT 'cat2_name',
  `category_path` STRING COMMENT 'category_path',
  `product_level` STRING COMMENT 'product_level'
) COMMENT 't2 运动电商 DIM product_info' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dim_category`;
CREATE TABLE `t2_dim_category` (
  `category_id` STRING COMMENT 'category_id',
  `category_name` STRING COMMENT 'category_name',
  `parent_id` STRING COMMENT 'parent_id',
  `category_level` STRING COMMENT 'category_level',
  `category_path` STRING COMMENT 'category_path',
  `sort_no` STRING COMMENT 'sort_no',
  `product_count` DOUBLE COMMENT 'product_count'
) COMMENT 't2 运动电商 DIM category' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dim_date`;
CREATE TABLE `t2_dim_date` (
  `date_key` BIGINT COMMENT 'date_key',
  `stat_date` STRING COMMENT 'stat_date',
  `year` BIGINT COMMENT 'year',
  `month` BIGINT COMMENT 'month',
  `day` BIGINT COMMENT 'day',
  `week` BIGINT COMMENT 'week',
  `quarter` BIGINT COMMENT 'quarter',
  `day_of_week` BIGINT COMMENT 'day_of_week',
  `day_name` STRING COMMENT 'day_name',
  `is_weekend` BIGINT COMMENT 'is_weekend',
  `is_promo` BIGINT COMMENT 'is_promo',
  `promo_name` STRING COMMENT 'promo_name'
) COMMENT 't2 运动电商 DIM date'
PARTITIONED BY (`dt` STRING COMMENT '分区日期') STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dim_region`;
CREATE TABLE `t2_dim_region` (
  `region_id` STRING COMMENT 'region_id',
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city',
  `city_level` STRING COMMENT 'city_level'
) COMMENT 't2 运动电商 DIM region' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dim_brand`;
CREATE TABLE `t2_dim_brand` (
  `brand_id` STRING COMMENT 'brand_id',
  `brand_name` STRING COMMENT 'brand_name',
  `brand_country` STRING COMMENT 'brand_country',
  `brand_level` STRING COMMENT 'brand_level',
  `main_category` STRING COMMENT 'main_category',
  `establish_year` STRING COMMENT 'establish_year',
  `product_count` BIGINT COMMENT 'product_count'
) COMMENT 't2 运动电商 DIM brand' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');
