CREATE DATABASE IF NOT EXISTS t2_ecommerce;
USE t2_ecommerce;

DROP TABLE IF EXISTS `t2_ods_user_info`;
CREATE EXTERNAL TABLE `t2_ods_user_info` (
  `user_id` STRING COMMENT 'user_id',
  `username` STRING COMMENT 'username',
  `gender` STRING COMMENT 'gender',
  `age` STRING COMMENT 'age',
  `phone` STRING COMMENT 'phone',
  `email` STRING COMMENT 'email',
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city',
  `register_time` STRING COMMENT 'register_time',
  `user_level` STRING COMMENT 'user_level',
  `is_member` STRING COMMENT 'is_member',
  `last_login_time` STRING COMMENT 'last_login_time'
) COMMENT 't2 运动电商 ODS user_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_user_info';

DROP TABLE IF EXISTS `t2_ods_category`;
CREATE EXTERNAL TABLE `t2_ods_category` (
  `category_id` STRING COMMENT 'category_id',
  `category_name` STRING COMMENT 'category_name',
  `parent_id` STRING COMMENT 'parent_id',
  `category_level` STRING COMMENT 'category_level',
  `category_path` STRING COMMENT 'category_path',
  `sort_no` STRING COMMENT 'sort_no'
) COMMENT 't2 运动电商 ODS category' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_category';

DROP TABLE IF EXISTS `t2_ods_product_info`;
CREATE EXTERNAL TABLE `t2_ods_product_info` (
  `product_id` STRING COMMENT 'product_id',
  `product_name` STRING COMMENT 'product_name',
  `category_id` STRING COMMENT 'category_id',
  `brand_id` STRING COMMENT 'brand_id',
  `shop_id` STRING COMMENT 'shop_id',
  `price` STRING COMMENT 'price',
  `original_price` STRING COMMENT 'original_price',
  `stock_qty` STRING COMMENT 'stock_qty',
  `sales_qty` STRING COMMENT 'sales_qty',
  `size` STRING COMMENT 'size',
  `color` STRING COMMENT 'color',
  `material` STRING COMMENT 'material',
  `target_group` STRING COMMENT 'target_group',
  `season` STRING COMMENT 'season',
  `listing_date` STRING COMMENT 'listing_date',
  `status` STRING COMMENT 'status',
  `image_url` STRING COMMENT 'image_url'
) COMMENT 't2 运动电商 ODS product_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_product_info';

DROP TABLE IF EXISTS `t2_ods_brand_info`;
CREATE EXTERNAL TABLE `t2_ods_brand_info` (
  `brand_id` STRING COMMENT 'brand_id',
  `brand_name` STRING COMMENT 'brand_name',
  `brand_country` STRING COMMENT 'brand_country',
  `brand_level` STRING COMMENT 'brand_level',
  `main_category` STRING COMMENT 'main_category',
  `establish_year` STRING COMMENT 'establish_year'
) COMMENT 't2 运动电商 ODS brand_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_brand_info';

DROP TABLE IF EXISTS `t2_ods_shop_info`;
CREATE EXTERNAL TABLE `t2_ods_shop_info` (
  `shop_id` STRING COMMENT 'shop_id',
  `shop_name` STRING COMMENT 'shop_name',
  `shop_type` STRING COMMENT 'shop_type',
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city',
  `rating` STRING COMMENT 'rating',
  `open_date` STRING COMMENT 'open_date'
) COMMENT 't2 运动电商 ODS shop_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_shop_info';

DROP TABLE IF EXISTS `t2_ods_order_info`;
CREATE EXTERNAL TABLE `t2_ods_order_info` (
  `order_id` STRING COMMENT 'order_id',
  `user_id` STRING COMMENT 'user_id',
  `order_time` STRING COMMENT 'order_time',
  `order_status` STRING COMMENT 'order_status',
  `total_amount` STRING COMMENT 'total_amount',
  `discount_amount` STRING COMMENT 'discount_amount',
  `shipping_fee` STRING COMMENT 'shipping_fee',
  `pay_amount` STRING COMMENT 'pay_amount',
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city',
  `channel` STRING COMMENT 'channel',
  `promo_id` STRING COMMENT 'promo_id',
  `coupon_amount` STRING COMMENT 'coupon_amount',
  `order_date` STRING COMMENT 'order_date'
) COMMENT 't2 运动电商 ODS order_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_order_info';

DROP TABLE IF EXISTS `t2_ods_order_detail`;
CREATE EXTERNAL TABLE `t2_ods_order_detail` (
  `detail_id` STRING COMMENT 'detail_id',
  `order_id` STRING COMMENT 'order_id',
  `product_id` STRING COMMENT 'product_id',
  `quantity` STRING COMMENT 'quantity',
  `unit_price` STRING COMMENT 'unit_price',
  `discount_amount` STRING COMMENT 'discount_amount',
  `line_amount` STRING COMMENT 'line_amount'
) COMMENT 't2 运动电商 ODS order_detail' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_order_detail';

DROP TABLE IF EXISTS `t2_ods_payment_info`;
CREATE EXTERNAL TABLE `t2_ods_payment_info` (
  `payment_id` STRING COMMENT 'payment_id',
  `order_id` STRING COMMENT 'order_id',
  `pay_time` STRING COMMENT 'pay_time',
  `pay_amount` STRING COMMENT 'pay_amount',
  `pay_method` STRING COMMENT 'pay_method',
  `pay_status` STRING COMMENT 'pay_status',
  `transaction_no` STRING COMMENT 'transaction_no'
) COMMENT 't2 运动电商 ODS payment_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_payment_info';

DROP TABLE IF EXISTS `t2_ods_refund_info`;
CREATE EXTERNAL TABLE `t2_ods_refund_info` (
  `refund_id` STRING COMMENT 'refund_id',
  `order_id` STRING COMMENT 'order_id',
  `refund_time` STRING COMMENT 'refund_time',
  `refund_amount` STRING COMMENT 'refund_amount',
  `refund_reason` STRING COMMENT 'refund_reason',
  `refund_status` STRING COMMENT 'refund_status',
  `refund_type` STRING COMMENT 'refund_type'
) COMMENT 't2 运动电商 ODS refund_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_refund_info';

DROP TABLE IF EXISTS `t2_ods_logistics_info`;
CREATE EXTERNAL TABLE `t2_ods_logistics_info` (
  `logistics_id` STRING COMMENT 'logistics_id',
  `order_id` STRING COMMENT 'order_id',
  `ship_time` STRING COMMENT 'ship_time',
  `deliver_time` STRING COMMENT 'deliver_time',
  `sign_time` STRING COMMENT 'sign_time',
  `logistics_company` STRING COMMENT 'logistics_company',
  `tracking_no` STRING COMMENT 'tracking_no',
  `logistics_status` STRING COMMENT 'logistics_status',
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city'
) COMMENT 't2 运动电商 ODS logistics_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_logistics_info';

DROP TABLE IF EXISTS `t2_ods_review_info`;
CREATE EXTERNAL TABLE `t2_ods_review_info` (
  `review_id` STRING COMMENT 'review_id',
  `order_id` STRING COMMENT 'order_id',
  `product_id` STRING COMMENT 'product_id',
  `user_id` STRING COMMENT 'user_id',
  `review_time` STRING COMMENT 'review_time',
  `rating` STRING COMMENT 'rating',
  `review_content` STRING COMMENT 'review_content',
  `is_anonymous` STRING COMMENT 'is_anonymous',
  `images_count` STRING COMMENT 'images_count'
) COMMENT 't2 运动电商 ODS review_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_review_info';

DROP TABLE IF EXISTS `t2_ods_cart_info`;
CREATE EXTERNAL TABLE `t2_ods_cart_info` (
  `cart_id` STRING COMMENT 'cart_id',
  `user_id` STRING COMMENT 'user_id',
  `product_id` STRING COMMENT 'product_id',
  `add_time` STRING COMMENT 'add_time',
  `quantity` STRING COMMENT 'quantity',
  `cart_status` STRING COMMENT 'cart_status',
  `source_page` STRING COMMENT 'source_page'
) COMMENT 't2 运动电商 ODS cart_info' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_cart_info';

DROP TABLE IF EXISTS `t2_ods_search_log`;
CREATE EXTERNAL TABLE `t2_ods_search_log` (
  `log_id` STRING COMMENT 'log_id',
  `user_id` STRING COMMENT 'user_id',
  `search_time` STRING COMMENT 'search_time',
  `keyword` STRING COMMENT 'keyword',
  `scene` STRING COMMENT 'scene',
  `result_count` STRING COMMENT 'result_count',
  `click_count` STRING COMMENT 'click_count',
  `duration_sec` STRING COMMENT 'duration_sec',
  `device` STRING COMMENT 'device',
  `session_id` STRING COMMENT 'session_id'
) COMMENT 't2 运动电商 ODS search_log' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/t2_ecommerce.db/t2_ods_search_log';
