CREATE DATABASE IF NOT EXISTS t2_ecommerce;
USE t2_ecommerce;

DROP TABLE IF EXISTS `t2_dwd_order`;
CREATE TABLE `t2_dwd_order` (
  `order_id` STRING COMMENT 'order_id',
  `user_id` STRING COMMENT 'user_id',
  `order_time` STRING COMMENT 'order_time',
  `order_date` STRING COMMENT 'order_date',
  `order_status` STRING COMMENT 'order_status',
  `total_amount` DOUBLE COMMENT 'total_amount',
  `discount_amount` DOUBLE COMMENT 'discount_amount',
  `shipping_fee` DOUBLE COMMENT 'shipping_fee',
  `coupon_amount` DOUBLE COMMENT 'coupon_amount',
  `pay_amount` DOUBLE COMMENT 'pay_amount',
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city',
  `channel` STRING COMMENT 'channel',
  `promo_id` STRING COMMENT 'promo_id',
  `is_paid` BIGINT COMMENT 'is_paid'
) COMMENT 't2 运动电商 DWD order' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dwd_order_detail`;
CREATE TABLE `t2_dwd_order_detail` (
  `detail_id` STRING COMMENT 'detail_id',
  `order_id` STRING COMMENT 'order_id',
  `product_id` STRING COMMENT 'product_id',
  `quantity` BIGINT COMMENT 'quantity',
  `unit_price` DOUBLE COMMENT 'unit_price',
  `discount_amount` STRING COMMENT 'discount_amount',
  `line_amount` DOUBLE COMMENT 'line_amount',
  `total_amount` DOUBLE COMMENT 'total_amount',
  `pay_amount` DOUBLE COMMENT 'pay_amount',
  `order_date` STRING COMMENT 'order_date',
  `line_gmv` DOUBLE COMMENT 'line_gmv',
  `product_name` STRING COMMENT 'product_name',
  `category_id` STRING COMMENT 'category_id',
  `brand_id` STRING COMMENT 'brand_id',
  `shop_id` STRING COMMENT 'shop_id'
) COMMENT 't2 运动电商 DWD order_detail' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dwd_payment`;
CREATE TABLE `t2_dwd_payment` (
  `payment_id` STRING COMMENT 'payment_id',
  `order_id` STRING COMMENT 'order_id',
  `pay_time` STRING COMMENT 'pay_time',
  `pay_amount` DOUBLE COMMENT 'pay_amount',
  `pay_method` STRING COMMENT 'pay_method',
  `pay_status` STRING COMMENT 'pay_status',
  `transaction_no` STRING COMMENT 'transaction_no',
  `pay_date` STRING COMMENT 'pay_date'
) COMMENT 't2 运动电商 DWD payment' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dwd_refund`;
CREATE TABLE `t2_dwd_refund` (
  `refund_id` STRING COMMENT 'refund_id',
  `order_id` STRING COMMENT 'order_id',
  `refund_time` STRING COMMENT 'refund_time',
  `refund_amount` DOUBLE COMMENT 'refund_amount',
  `refund_reason` STRING COMMENT 'refund_reason',
  `refund_status` STRING COMMENT 'refund_status',
  `refund_type` STRING COMMENT 'refund_type',
  `refund_date` STRING COMMENT 'refund_date'
) COMMENT 't2 运动电商 DWD refund' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dwd_logistics`;
CREATE TABLE `t2_dwd_logistics` (
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
) COMMENT 't2 运动电商 DWD logistics' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dwd_review`;
CREATE TABLE `t2_dwd_review` (
  `review_id` STRING COMMENT 'review_id',
  `order_id` STRING COMMENT 'order_id',
  `product_id` STRING COMMENT 'product_id',
  `user_id` STRING COMMENT 'user_id',
  `review_time` STRING COMMENT 'review_time',
  `rating` BIGINT COMMENT 'rating',
  `review_content` STRING COMMENT 'review_content',
  `is_anonymous` STRING COMMENT 'is_anonymous',
  `images_count` STRING COMMENT 'images_count',
  `sentiment` STRING COMMENT 'sentiment',
  `review_date` STRING COMMENT 'review_date'
) COMMENT 't2 运动电商 DWD review' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dwd_cart`;
CREATE TABLE `t2_dwd_cart` (
  `cart_id` STRING COMMENT 'cart_id',
  `user_id` STRING COMMENT 'user_id',
  `product_id` STRING COMMENT 'product_id',
  `add_time` STRING COMMENT 'add_time',
  `quantity` BIGINT COMMENT 'quantity',
  `cart_status` STRING COMMENT 'cart_status',
  `source_page` STRING COMMENT 'source_page',
  `action_date` STRING COMMENT 'action_date'
) COMMENT 't2 运动电商 DWD cart' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dwd_search_log`;
CREATE TABLE `t2_dwd_search_log` (
  `log_id` STRING COMMENT 'log_id',
  `user_id` STRING COMMENT 'user_id',
  `search_time` STRING COMMENT 'search_time',
  `keyword` STRING COMMENT 'keyword',
  `scene` STRING COMMENT 'scene',
  `result_count` STRING COMMENT 'result_count',
  `click_count` BIGINT COMMENT 'click_count',
  `duration_sec` BIGINT COMMENT 'duration_sec',
  `device` STRING COMMENT 'device',
  `session_id` STRING COMMENT 'session_id',
  `search_date` STRING COMMENT 'search_date'
) COMMENT 't2 运动电商 DWD search_log' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dwd_user_action`;
CREATE TABLE `t2_dwd_user_action` (
  `action_id` STRING COMMENT 'action_id',
  `user_id` STRING COMMENT 'user_id',
  `action_time` STRING COMMENT 'action_time',
  `keyword` STRING COMMENT 'keyword',
  `click_count` BIGINT COMMENT 'click_count',
  `duration_sec` BIGINT COMMENT 'duration_sec',
  `device` STRING COMMENT 'device',
  `action_type` STRING COMMENT 'action_type',
  `page` STRING COMMENT 'page',
  `product_id` STRING COMMENT 'product_id',
  `order_id` STRING COMMENT 'order_id',
  `province` STRING COMMENT 'province',
  `city` STRING COMMENT 'city',
  `quantity` DOUBLE COMMENT 'quantity',
  `action_date` STRING COMMENT 'action_date'
) COMMENT 't2 运动电商 DWD user_action' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');

DROP TABLE IF EXISTS `t2_dwd_inventory`;
CREATE TABLE `t2_dwd_inventory` (
  `product_id` STRING COMMENT 'product_id',
  `product_name` STRING COMMENT 'product_name',
  `brand_id` STRING COMMENT 'brand_id',
  `shop_id` STRING COMMENT 'shop_id',
  `stock_qty` BIGINT COMMENT 'stock_qty',
  `sales_qty` BIGINT COMMENT 'sales_qty',
  `price` DOUBLE COMMENT 'price',
  `sales_qty_30d` DOUBLE COMMENT 'sales_qty_30d',
  `avg_daily_sales` DOUBLE COMMENT 'avg_daily_sales',
  `turnover_days` DOUBLE COMMENT 'turnover_days',
  `stock_status` STRING COMMENT 'stock_status'
) COMMENT 't2 运动电商 DWD inventory' STORED AS ORC TBLPROPERTIES ('orc.compress'='SNAPPY');
