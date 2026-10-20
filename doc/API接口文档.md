# API 接口文档

## 一、通用约定

- Base URL：`http://127.0.0.1:5000`
- 前缀：`/api/t2`
- 返回格式：`{"code":0,"msg":"ok","data":...}`
- 错误码：0 成功；400 参数错误；500 服务端错误
- CORS：允许跨域

## 二、接口清单（20 个）

| 方法 | 路径 | 说明 | 参数 |
|---|---|---|---|
| GET | /api/t2/gmv | 当日/累计GMV、环比、同比 | - |
| GET | /api/t2/sales_trend?days=90 | 近N天GMV+订单量+支付率 | days |
| GET | /api/t2/region_sales | 各省GMV+增长率排名 | - |
| GET | /api/t2/city_sales?top=30 | TopN城市销售排行 | top |
| GET | /api/t2/product_rank?top=20 | TopN商品销量+销售额 | top |
| GET | /api/t2/brand_rank | 品牌销量TOP10 | - |
| GET | /api/t2/category_proportion | 各分类GMV占比 | - |
| GET | /api/t2/core_kpi | 全部30个核心KPI最新值 | - |
| GET | /api/t2/kpi_trend?kpi=gmv&days=30 | 单个KPI近N天趋势 | kpi,days |
| GET | /api/t2/inventory_alarm | 低库存/滞销预警 | - |
| GET | /api/t2/user_funnel | 漏斗4层数据 | - |
| GET | /api/t2/user_retention | 次日/7日/30日留存率 | - |
| GET | /api/t2/user_rfm | RFM5级分层人数+比例 | - |
| GET | /api/t2/user_churn?top=100 | 高风险流失用户列表 | top |
| GET | /api/t2/user_list?page=1&size=10 | 用户列表分页+筛选 | page,size,province,gender,user_level,q |
| GET | /api/t2/promo_activity | 大促活动效果 | - |
| GET | /api/t2/sales_forecast | 未来14天GMV预测值 | - |
| GET | /api/t2/sales_forecast_compare | 历史实际值vs预测值对比 | - |
| GET | /api/t2/dashboard_overview | 大屏概览（一次返回全部卡片） | - |
| POST/GET | /api/t2/dashboard_refresh | 刷新所有ADS表 | - |

## 三、示例

### 1. GMV

```bash
curl http://127.0.0.1:5000/api/t2/gmv
```

```json
{"code":0,"msg":"ok","data":{"stat_date":"2025-11-11","total_gmv":2135906.3,"paid_orders":1920}}
```

### 2. 大屏概览

```bash
curl http://127.0.0.1:5000/api/t2/dashboard_overview
```

返回 `gmv_total、kpi、trend、category、brands、regions、funnel、retention、rfm、products、inventory、promo、forecast、churn` 等区块。

### 3. 刷新 ADS

```bash
curl -X POST http://127.0.0.1:5000/api/t2/dashboard_refresh
```

## 四、Python 调用示例

```python
import requests
r = requests.get("http://127.0.0.1:5000/api/t2/core_kpi", timeout=10)
print(r.json()["data"]["dict"]["gmv"])
```

## 五、前端图表映射

| 图表 | 接口 |
|---|---|
| 核心指标卡 | dashboard_overview.kpi / gmv_total |
| 销售趋势+预测 | trend + forecast |
| 分类占比 | category |
| 品牌排行 | brands |
| 动销率 | kpi.sell_through_rate |
| 滞销/库存 | inventory |
| 地区地图 | regions |
| 漏斗 | funnel |
| RFM | rfm |
| 留存雷达 | retention |
| 大促对比 | promo |
| 流失用户 | churn |
