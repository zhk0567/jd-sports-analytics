# 每日提交顺序（执行版）：组长 → Coder A → Coder B

> Gitee 仓库名：`t2_ecommerce`  
> 组型：3 人组，只执行蓝色“3人”标签，不设 Coder C  
> Gitee 可见性：公开（Public）  
> 分支：只使用 `main`  
> 适用：第 2 组（运动）电商经营分析平台  
> 说明：本文只调整提交顺序，不改变任务内容；当前没有提交或推送任何内容。
>
> ODS 口径：手册标题写 12 张，但任务清单实际列出 13 张（含 `search_log`）；本项目按 13 张执行。

---

## 日期安排

| 阶段 | 日期 | 星期 | 安排 |
|---|---|---|---|
| Day 1 | 2026-10-20 | 周二 | 下午半天，项目初始化 + ODS |
| Day 2 | 2026-10-21 | 周三 | 全天，DataX + ODS 验证 + DIM |
| Day 3 | 2026-10-22 | 周四 | 全天，DWD + 质量 + DWS |
| Day 4 | 2026-10-26 | 周一 | 全天，ADS + ML + API + 大屏 + 封版 |
| Day 5 | 2026-10-27 | 周二 | 全天答辩，不再开发 |

按给定日期，2026-10-23（周五）、2026-10-24（周六）、2026-10-25（周日）不安排提交；10-26 是 Day4，10-27 直接进入全天答辩。

---

## 一、串行规则

每天分成 1~3 轮。每一轮都严格按：

```text
组长提交并 push
  ↓
Coder A 先 pull，再提交并 push
  ↓
Coder B 先 pull，再提交并 push
  ↓
下一轮开始
```

任何人都不能在前一个人还没 push 完成时开始提交。

### 每个人开始提交前

```powershell
git pull --rebase
git status
```

### 每个人提交完成后

```powershell
git add <本轮自己负责的文件>
git commit -m "[模块] 简述改动"
git push origin main
```

### 冲突预防

1. 组长先提交公共文件：`README.md`、`.gitignore`、`requirements.txt`、`pipeline.*`、Flask 框架、`doc/` 总文档。
2. Coder A 负责 `sql/ods/`、`sql/dim/`、`sql/ads/`、`config/import/`、`config/export/`、`flask_app/blueprints/`、大屏左半屏。
3. Coder B 负责 `sql/dwd/`、`sql/dws/`、`scripts/t2_generate_fact_data.py`、`scripts/t2_train_models.py`、`models/`、大屏右半屏。
4. 如果两个人必须改同一个文件，后提交的人先 pull，再改，不要 force push。
5. 每轮结束前检查三个人当天都有提交：

```powershell
git log --oneline --author="组长姓名" --since="今天"
git log --oneline --author="Coder A 姓名" --since="今天"
git log --oneline --author="Coder B 姓名" --since="今天"
```

---

## 二、Day 1（2026-10-20 周二下午，半天）：初始化 + ODS

### 第 1 轮

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[INIT] 初始化t2_ecommerce目录与main分支` | `.gitignore`、`README.md`、`requirements.txt`、目录结构；Gitee 仓库改名 `t2_ecommerce`，设为公开，邀请三人 |
| 2 | 组长 | `[DOC] 完成运动品类特征数据分布规范` | `doc/品类特征数据分布规范.md` |
| 3 | 组长 | `[DOC] 完成ER图与数仓字段字典` | `doc/ER图.png`、`doc/数仓字段字典.md` |
| 4 | Coder A | `[ODS] 完成13张MySQL/Hive ODS建表SQL` | `sql/ods/`、`sql/init_databases.sql` |
| 5 | Coder A | `[ENV] 完成环境验证与建库` | `doc/环境验证报告.md` |
| 6 | Coder A | `[ODS] 完成基础5张数据生成脚本` | 5.1 基础：用户 800、分类 40、商品 250、品牌 30、店铺 15 |
| 7 | Coder B | `[ODS] 完成交易5张+内容3张数据生成脚本` | 5.2 交易：订单、明细、支付、退款、物流；5.3 内容：评价、购物车、搜索 |
| 8 | Coder B | `[ODS] 完成事实数据自检脚本` | `scripts/t2_check_ods_facts.py`；行数、外键、金额/数量异常检查 |

### 第 2 轮

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[ODS] 完成品类特征注入并跑通24935行` | 5.4 品类特征规范 + 特征注入 + `scripts/t2_generate_data.py` 联调冻结；13 张 CSV 合计 24,935 行 |
| 2 | 组长 | `[DOC] 完成day1过程文档与代码Review` | `doc/process/day1.md`；至少 3 条问题与解决记录 |
| 3 | Coder A | `[ODS] 修复维度数据分布并复核CSV` | 维度侧分布修正、外键检查、商品属性抽查 |
| 4 | Coder B | `[ODS] 修复事实数据分布并复核CSV` | 事实侧分布修正、金额/数量/时间逻辑抽查 |

### Day 1 完成标准

- Gitee `t2_ecommerce` 已设为公开（Public），三人有权限。
- 13 张 ODS CSV，合计 24,935 行，seed=2。
- MySQL/Hive 各 13 张 ODS 建表 SQL。
- 外键无悬空，商品至少有 5 个属性字段。
- 三个人 Day 1 都有提交。

---

## 三、Day 2（2026-10-21 周三）：DataX + ODS 验证 + DIM

### 第 1 轮

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[DOC] 完成30个核心指标体系` | `doc/电商经营指标体系.md`；8 流量 + 10 交易 + 6 用户 + 4 商品 + 2 营销 |
| 2 | 组长 | `[DWD] 提交通用清洗函数与模板` | 公共清洗函数、DWD SQL 模板 |
| 3 | Coder A | `[DATX] 完成26个ODS导入配置与一键脚本` | `config/import/` MySQL 13 + Hive 13；`scripts/import_all.ps1/.sh` |
| 4 | Coder A | `[DIM] 完成6张维度表建表SQL` | `sql/dim/` |
| 5 | Coder B | `[ODS] 完成ODS数据验证报告` | `doc/ODS数据验证报告.md` |
| 6 | Coder B | `[DWD] 完成DWD清洗规则文档` | `doc/DWD清洗规则文档.md` |

### 第 2 轮

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[DIM] 评审维度表并修订字段口径` | 检查 DIM 字段、脱敏、日期大促标记 |
| 2 | 组长 | `[DOC] 完成day2过程文档与代码Review` | `doc/process/day2.md` |
| 3 | Coder A | `[DIM] 完成维度装载与质量检查` | `doc/DIM层质量检查清单.md`；手机号脱敏、姓名保留姓氏 |
| 4 | Coder B | `[DWD] 完成评价/购物车/搜索3张事实表` | 先启动 3 张 DWD，评价生成 sentiment |

### Day 2 完成标准

- 26 个 DataX 导入配置可执行。
- 6 张 DIM 完成，日期维度覆盖 2025-05-16 至 2025-11-11。
- ODS 验证报告、DWD 清洗规则、30 指标文档完成。
- 三个人 Day 2 都有提交。

---

## 四、Day 3（2026-10-22 周四）：DWD + 质量 + DWS

### 第 1 轮

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[DWS] 统一汇总SQL模板与指标口径` | DWS 分区/去重/空值模板；指标归属复核 |
| 2 | 组长 | `[QA] 提交交叉验证脚本` | `scripts/t2_validate_cross.py`；明细/分类/地区/品牌四路对账 |
| 3 | Coder A | `[DWD] 完成订单/明细/支付/退款/物流5张事实表` | 金额分摊、状态标准化、时间校验 |
| 4 | Coder A | `[DWS] 完成用户5张+流量3张汇总表` | `user_user_1d`、`_nd`、`_total`、`_rfm`、`_retention_1d`、`traffic_page_1d`、`traffic_user_1d`、`user_funnel_1d` |
| 5 | Coder B | `[DWD] 完成评价/购物车/搜索/行为/库存5张事实表` | 与 Day2 已启动的 3 张合并为 5 张 |
| 6 | Coder B | `[DWD] 完成数据质量报告` | `doc/数据质量报告.md`；行数、空值、重复、丢弃率、外键 |
| 7 | Coder B | `[DWS] 完成商品5+地区4+营销1汇总表` | 共 10 张 DWS |

### 第 2 轮

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[DWS] 复核汇总表结构与指标口径` | 检查 18 张 DWS 的字段、分区、口径，不修改 A/B 的主责 SQL |
| 2 | Coder A | `[DWS] 修复用户/流量指标异常` | 复购率、留存率、漏斗口径修正 |
| 3 | Coder B | `[DWS] 修复商品/地区/营销指标异常` | 商品/地区/品牌/活动汇总修正 |

### 第 3 轮（对账定稿）

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[QA] 完成交叉验证并修复对账差异` | `doc/交叉验证报告.md`；误差 ≤ 0.1% |
| 2 | 组长 | `[DOC] 完成day3过程文档与代码Review` | `doc/process/day3.md` |
| 3 | Coder A | `[QA] 确认用户/流量DWS无遗留问题` | 只确认，不再改文件；有问题先在群里说明 |
| 4 | Coder B | `[QA] 确认商品/地区/营销DWS无遗留问题` | 只确认，不再改文件；有问题先在群里说明 |

### Day 3 完成标准

- 10 张 DWD 完成，丢弃率 2%~10%，外键 100%。
- 18 张 DWS 完成，按天分区。
- 30 指标有值，四路汇总误差 ≤ 0.1%。
- 三个人 Day 3 都有提交。

---

## 五、Day 4（2026-10-26 周一）：ADS + ML + API + 大屏 + 封版

### 第 1 轮

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[PIPE] 完成一键pipeline与Flask框架` | `pipeline.ps1/.bat/.sh`、`flask_app/app.py`、`config.py`、`db.py`；统一 JSON、CORS、错误处理 |
| 2 | Coder A | `[ADS] 完成14张ADS分析表` | `sql/ads/`；GMV、地区、城市、品类、品牌、漏斗、留存、RFM、商品、库存、KPI |
| 3 | Coder A | `[DATX] 完成16个ADS导出配置` | `config/export/` 16 个；`scripts/export_all.ps1/.sh` |
| 4 | Coder A | `[API] 完成20个REST接口` | `flask_app/blueprints/`；20 个 `/api/t2/*` |
| 5 | Coder A | `[UI] 完成大屏左半屏6图表` | 指标卡、趋势+预测、品类、品牌、动销、滞销 |
| 6 | Coder B | `[ML] 完成销售预测模型与评估` | `scripts/t2_train_models.py` 销售模型；`doc/销售预测模型报告.md` |
| 7 | Coder B | `[ML] 完成流失预测与RFM分层` | 流失模型、RFM；`doc/流失预测模型报告.md`、`doc/RFM模型报告.md` |
| 8 | Coder B | `[UI] 完成大屏右半屏6图表` | 地图、漏斗、RFM、留存、大促、流失列表 |

### 第 2 轮

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[API] 完成接口测试与API文档` | `doc/API接口文档.md`；20/20 接口测试记录 |
| 2 | 组长 | `[QA] 完成全链路联调与Bug修复` | `doc/全链路复查报告.md`；数据→ADS→ML→API→大屏 |
| 3 | Coder A | `[QA] 修复ADS/API/左半屏联调问题` | 只改 A 的主责文件 |
| 4 | Coder B | `[QA] 修复ML/右半屏联调问题` | 只改 B 的主责文件 |

### 第 3 轮（封版）

| 顺序 | 负责人 | 提交信息 | 本轮文件/内容 |
|---:|---|---|---|
| 1 | 组长 | `[DOC] 完成项目说明/数仓设计/README/day4` | `doc/项目说明文档.md`、`doc/数仓设计文档.md`、`README.md`、`doc/process/day4.md` |
| 2 | 组长 | `[REL] 完成答辩PPT与v1.0.0封版` | `doc/答辩PPT.pptx`、`doc/项目最终检查表.md`；最后打 tag `v1.0.0` |
| 3 | Coder A | `[QA] 确认ADS/API/左半屏无遗留问题` | 只确认，不再改文件 |
| 4 | Coder B | `[QA] 确认ML/右半屏无遗留问题` | 只确认，不再改文件 |

### Day 4 完成标准

- 16 张 ADS 有值，30 指标可查。
- 3 个模型可训练、可保存、可加载。
- 20 个 API 全部 `code=0`。
- 12 个图表全部来自 API。
- 全链路跑通，PPT 完成，`v1.0.0` 已打。
- 三个人 Day 4 都有提交。

---

## 六、Day 5（2026-10-27 周二，全天答辩）：答辩材料

只提交讲稿，不改代码，不移动 tag。

| 顺序 | 负责人 | 提交信息 | 内容 |
|---:|---|---|---|
| 1 | 组长 | `[DOC] 答辩流程与演示脚本` | 2.5 分钟：项目介绍、整体架构、项目管理、总结反思 |
| 2 | Coder A | `[DOC] ADS/API/左半屏讲稿` | 3 分钟：数仓设计、ER 图、指标体系、代码亮点 |
| 3 | Coder B | `[DOC] DWD/DWS/ML/右半屏讲稿` | 2.5 分钟：3 个 ML 模型、大屏演示、动效展示 |

---

## 七、每日提交顺序速查

| 天 | 日期 | 第 1 轮 | 第 2 轮 | 第 3 轮 |
|---|---|---|---|---|
| Day 1 | 2026-10-20 下午 | 组长 → A → B | 组长 → A → B | 无 |
| Day 2 | 2026-10-21 | 组长 → A → B | 组长 → A → B | 无 |
| Day 3 | 2026-10-22 | 组长 → A → B | 组长 → A → B | 组长 → A → B（对账定稿） |
| Day 4 | 2026-10-26 | 组长 → A → B | 组长 → A → B | 组长 → A → B（封版） |
| Day 5 | 2026-10-27 | 组长 → A → B | 无 | 无 |

每一轮都必须等前一个人 push 完成后，下一个人再 `git pull --rebase`。

---

## 八、Gitee 改名与远端

仓库名必须是：

```text
t2_ecommerce
```

不是 `jd-sports-analytics`，也不是 `t2-sports-analytics`。

Gitee 可见性必须是 **公开（Public）**，外部可无限制访问。

```text
https://gitee.com/zhk567/t2_ecommerce
```

改名后更新本地远端：

```powershell
git remote set-url gitee https://gitee.com/zhk567/t2_ecommerce.git
git remote -v
```

GitHub 保持：

```text
https://github.com/zhk0567/jd-sports-analytics
```

不删除、不改名。
