# Day 3 开发过程文档

## 一、今日任务完成情况

- [x] 10 张 DWD 事实表
- [x] 数据质量报告
- [x] 18 张 DWS 汇总表
- [x] 30 个核心指标
- [x] 交叉验证报告

## 二、DWD 丢弃率

| 表 | 丢弃率 |
|---|---|
| order | 2.2% |
| order_detail | 2.98% |
| payment | 4.9% |
| refund | 43.67% |
| logistics | 5.15% |
| review | 4.8% |
| cart | 1.17% |
| search_log | 2.0% |

## 三、DWS 表量

| DWS 表 | 行数 |
|---|---|
| t2_dws_user_user_1d | 180 |
| t2_dws_user_user_nd | 180 |
| t2_dws_user_user_total | 797 |
| t2_dws_user_rfm | 792 |
| t2_dws_user_retention_1d | 137 |
| t2_dws_traffic_page_1d | 740 |
| t2_dws_traffic_user_1d | 180 |
| t2_dws_user_funnel_1d | 180 |
| t2_dws_trade_product_1d | 4221 |
| t2_dws_trade_product_nd | 37261 |
| t2_dws_trade_category_1d | 2743 |
| t2_dws_trade_category_nd | 6226 |
| t2_dws_trade_brand_1d | 2200 |
| t2_dws_trade_region_1d | 1474 |
| t2_dws_trade_region_nd | 3567 |
| t2_dws_user_region_total | 43 |
| t2_dws_traffic_region_1d | 3426 |
| t2_dws_promo_activity_1d | 180 |

## 四、交叉验证

| 校验项 | 误差 | 结论 |
|---|---|---|
| 订单明细GMV | 0.0% | 通过 |
| 分类汇总GMV | 0.0% | 通过 |
| 地区汇总GMV | 0.0% | 通过 |
| 品牌汇总GMV | 0.0% | 通过 |

## 五、问题与解决

1. 明细金额与订单金额差 2.6%：改为仅保留有有效明细的订单，并按行金额比例分摊实付。
2. 分类/品牌 GMV 映射重复：先去重再 map。
3. 留存 cohort 为空：补充事实期内注册用户，并只对满观察期 cohort 计算留存。

## 六、明日计划

ADS、3 个 ML、20 API、大屏与答辩材料。

## 七、Git 提交记录

```text
ce9b19c Polish brand/price/shelf charts and refresh README screenshots.
3db5ee0 Initial commit: JD sports crawl pipeline and web story UI.
```
