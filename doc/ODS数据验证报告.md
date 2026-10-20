# ODS 数据验证报告

## 一、数据量

| ODS 表 | CSV 行数 | MySQL 表 | Hive 表 |
|---|---|---|---|
| user_info | 800 | t2_ods_user_info | t2_ods_user_info |
| category | 40 | t2_ods_category | t2_ods_category |
| product_info | 250 | t2_ods_product_info | t2_ods_product_info |
| brand_info | 30 | t2_ods_brand_info | t2_ods_brand_info |
| shop_info | 15 | t2_ods_shop_info | t2_ods_shop_info |
| order_info | 2000 | t2_ods_order_info | t2_ods_order_info |
| order_detail | 5000 | t2_ods_order_detail | t2_ods_order_detail |
| payment_info | 2000 | t2_ods_payment_info | t2_ods_payment_info |
| refund_info | 300 | t2_ods_refund_info | t2_ods_refund_info |
| logistics_info | 2000 | t2_ods_logistics_info | t2_ods_logistics_info |
| review_info | 1500 | t2_ods_review_info | t2_ods_review_info |
| cart_info | 6000 | t2_ods_cart_info | t2_ods_cart_info |
| search_log | 5000 | t2_ods_search_log | t2_ods_search_log |

合计 **24,935** 行（约 2.5 万），与生成脚本预期一致。

## 二、外键与品类特征

- 订单 user_id 全部存在于用户表；
- 明细 product_id 全部存在于商品表；
- 订单明细 order_id 全部存在于订单表；
- 男性占比 **65.38%**，Top5 品牌销量占比 **50.66%**；
- 支付订单 **1,924** 单，GMV **2,139,684.21** 元，客单价 **1,112.10** 元；
- 大促日均 GMV **62,248.15** 元，日常日均 **9,544.76** 元，放大 **6.52x**。

## 三、峰值日

| 日期 | GMV | 支付订单 |
|---|---|---|
| 2025-11-11 | 79,511.56 | 95 |
| 2025-11-09 | 70,594.57 | 77 |
| 2025-11-10 | 68,347.59 | 77 |
| 2025-11-08 | 60,873.67 | 67 |
| 2025-11-02 | 20,628.41 | 10 |

## 四、结论

ODS 层保留贴源字段与受控脏数据（负金额、零数量、重复ID、时间倒挂），以便 DWD 层展示真实清洗效果；所有外键均无悬空。
