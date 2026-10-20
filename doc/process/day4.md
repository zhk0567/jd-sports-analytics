# Day 4 开发过程文档

## 一、今日任务完成情况

- [x] 16 张 ADS 表
- [x] 16 个 DataX 导出配置
- [x] 3 个 ML 模型与评估报告
- [x] 20 个 Flask API
- [x] 12 图表大屏
- [x] 全链路联调
- [x] API 文档、项目说明、数仓设计、最终检查表
- [x] 答辩 PPT

## 二、ML 结果

- 销售预测：LinearRegression，R² 0.7782，MAPE 40.25%；
- 流失预测：Accuracy 0.9874，F1 0.988；
- RFM：5 级分层，高价值用户 172 人。

## 三、API 与大屏

- 20 个接口全部返回 code=0；
- 大屏 12 个图表，30 秒刷新，ECharts 本地资源，离线可用；
- 截图：`doc/screenshots/dashboard_t2.png`。

## 四、问题与解决

1. 预测 MAPE 过高：将大促窗口改为短窗口，并加入 promo_intensity / 618 / 双11 特征。
2. 地图无内置中国数据：引入本地 `china.json` 并 registerMap。
3. 刷新 ADS 不能重跑全链路：新增 `t2_refresh_ads.py`，仅重算 ADS。

## 五、Git 提交记录

```text
ce9b19c Polish brand/price/shelf charts and refresh README screenshots.
3db5ee0 Initial commit: JD sports crawl pipeline and web story UI.
```
