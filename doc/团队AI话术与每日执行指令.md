# 团队 AI 话术与每日执行指令

> 适用：第 2 组（运动）电商经营分析平台  
> 仓库：GitHub `jd-sports-analytics`  
> 正式按天提交仓库：Gitee `t2_ecommerce`（公开 Public）  
> 组型：3 人组，只执行蓝色“3人”标签，不设 Coder C  
> 使用方式：每个人复制“公共开场”+ 自己当天的角色段，发给自己的 AI。

---

## 团队下载

GitHub 仓库：

```text
https://github.com/zhk0567/jd-sports-analytics
```

有权限的同学直接：

```powershell
git clone https://github.com/zhk0567/jd-sports-analytics.git
cd jd-sports-analytics
git pull
```

没有配置 Git 的同学，在 GitHub 页面点：

```text
Code → Download ZIP
```

下载后重点看：

- `doc/每日提交顺序_组长A_B.md`
- `doc/三人分工与每日提交计划.md`
- `doc/团队AI话术与每日执行指令.md`

---

## 重要：什么时候真正提交

角色段里的 `提交信息` 是给你之后发“提交确认话术”时用的清单，不是让 AI 立刻提交。

统一流程：

```text
AI 完成开发
→ 输出改动文件和验证结果
→ 你检查
→ 你发送“提交确认话术”
→ AI 才 commit/push
```

角色段里的“push 后停下”理解为：按提交确认话术完成 commit/push 后停下。

---

## 一、公共开场（每次先发）

```text
你是第2组（运动）电商经营分析平台项目的【组长 / Coder A / Coder B】。
工作目录：F:\commercial\Sport。
今天日期：【2026-10-20 / 2026-10-21 / 2026-10-22 / 2026-10-26 / 2026-10-27】。

先阅读：
1. doc/每日提交顺序_组长A_B.md
2. doc/三人分工与每日提交计划.md
3. doc/团队AI话术与每日执行指令.md

开始前执行：
git status
git pull --rebase

规则：
- 只做我下面指定的当天任务；
- 只改我这个角色的主责文件；
- 不改其他角色的文件，不覆盖别人的改动；
- 不建新分支，不 force push；
- 如果 git status 不干净，或 pull 有冲突，立即停下，把冲突文件列给我；
- 开发完成后先输出改动文件、验证命令和结果，等我明确说“提交”再 commit/push；
- 提交时只 add 本轮文件，不要 git add .。
```

---

## 二、提交确认话术（开发完成后发）

```text
现在执行提交。

先执行：
git pull --rebase
git status

只 add 本轮你改过的文件，不要 git add .。
commit message 按我指定的写。
然后：
git push origin main

输出：
1. commit hash
2. git status
3. 本次提交包含的文件
4. push 是否成功

如果 push 失败或出现冲突，停止，不要 reset --hard，不要 force push，把错误原文发给我。
```

---

## 三、角色交接话术

### 组长完成后，交给 Coder A

```text
组长本轮已完成并 push，commit hash 是【填写】。
现在切换为 Coder A。先 git pull --rebase，确认工作区干净，再执行 Coder A 当天话术。
```

### Coder A 完成后，交给 Coder B

```text
Coder A 本轮已完成并 push，commit hash 是【填写】。
现在切换为 Coder B。先 git pull --rebase，确认工作区干净，再执行 Coder B 当天话术。
```

### 下一轮重新回到组长

```text
Coder B 本轮已完成并 push，commit hash 是【填写】。
现在回到组长。先 git pull --rebase，确认工作区干净，再执行组长下一轮话术。
```

---

## 四、Day 1：2026-10-20（周二下午，半天）

### Day 1 · 组长

```text
【Day 1 · 组长｜2026-10-20 下午】

第 1 轮：
1. 初始化 t2_ecommerce 项目目录；
2. 写 .gitignore、README.md、requirements.txt；
3. 写 doc/品类特征数据分布规范.md；
4. 画 doc/ER图.png，写 doc/数仓字段字典.md。

只改：
.gitignore、README.md、requirements.txt、doc/品类特征数据分布规范.md、
doc/ER图.png、doc/数仓字段字典.md

提交信息：
[INIT] 初始化t2_ecommerce目录与main分支
[DOC] 完成运动品类特征数据分布规范
[DOC] 完成ER图与数仓字段字典

push 后停下。

第 2 轮（等我通知）：
1. git pull，确认 A/B 已 push；
2. 完成 5.4 品类特征注入，汇总 scripts/t2_generate_data.py 入口，跑通 24,935 行；
3. 写 doc/process/day1.md；
4. Review A/B 的 ODS 建表、维度数据、事实数据。

提交信息：
[ODS] 汇总生成入口并跑通24935行
[DOC] 完成day1过程文档与代码Review

不要改 A/B 的 t2_generate_dim_data.py 和 t2_generate_fact_data.py。
```

### Day 1 · Coder A

```text
【Day 1 · Coder A｜2026-10-20 下午】

第 1 轮：
1. 完成 13 张 ODS 的 MySQL/Hive 建表 SQL；
2. 写 sql/init_databases.sql；
3. 完成环境验证报告；
4. 完成 5.1 基础 5 张数据生成脚本：用户 800、分类 40、商品 250、品牌 30、店铺 15。

只改：
sql/ods/、sql/init_databases.sql、doc/环境验证报告.md、
scripts/t2_generate_dim_data.py

提交信息：
[ODS] 完成13张MySQL/Hive ODS建表SQL
[ENV] 完成环境验证与建库
[ODS] 完成基础5张数据生成脚本

push 后停下。

第 2 轮（等我通知）：
1. git pull；
2. 修复维度数据分布；
3. 复核 5 张维度 CSV 的行数、外键、商品属性；
4. 把检查结果直接发给我；不要写 doc/ODS数据验证报告.md，那是 Coder B Day2 的文件。

提交信息：
[ODS] 修复维度数据分布并复核CSV

不要改事实侧脚本和组长文档。
```

### Day 1 · Coder B

```text
【Day 1 · Coder B｜2026-10-20 下午】

第 1 轮：
1. 完成 5.2 交易 5 张 + 5.3 内容 3 张数据生成脚本；
2. 覆盖订单 2,000、明细 5,000、支付 2,000、退款 300、物流 2,000、评价 1,500、购物车 6,000、搜索 5,000；
3. 写事实数据自检脚本，检查行数、外键、金额/数量/时间异常。

只改：
scripts/t2_generate_fact_data.py、scripts/t2_check_ods_facts.py

提交信息：
[ODS] 完成交易5张+内容3张数据生成脚本
[ODS] 完成事实数据自检脚本

push 后停下。

第 2 轮（等我通知）：
1. git pull；
2. 修复事实数据分布；
3. 复核 8 张事实 CSV 的行数、外键、金额/数量/时间；
4. 输出事实侧检查结果。

提交信息：
[ODS] 修复事实数据分布并复核CSV

不要改维度侧脚本和组长文档。
```

---

## 五、Day 2：2026-10-21（周三）

### Day 2 · 组长

```text
【Day 2 · 组长｜2026-10-21】

第 1 轮：
1. 写 doc/电商经营指标体系.md，覆盖 30 个指标；
2. 提交 DWD 通用清洗函数与 SQL 模板；
3. 明确每个指标在 DWS 还是 ADS 计算。

只改：
doc/电商经营指标体系.md、scripts/t2_clean_common.py、sql/模板文件

提交信息：
[DOC] 完成30个核心指标体系
[DWD] 提交通用清洗函数与模板

push 后停下。

第 2 轮（等我通知）：
1. git pull；
2. 评审 A 的 DIM 表和 B 的 DWD 规则；
3. 修订字段口径；
4. 写 doc/process/day2.md。

提交信息：
[DIM] 评审维度表并修订字段口径
[DOC] 完成day2过程文档与代码Review

不要改 A 的 DIM SQL 和 B 的 DWD SQL。
```

### Day 2 · Coder A

```text
【Day 2 · Coder A｜2026-10-21】

第 1 轮：
1. 完成 26 个 DataX 导入配置：MySQL 13 + Hive 13；
2. 写 scripts/import_all.ps1 和 scripts/import_all.sh；
3. 完成 6 张 DIM 的建表 SQL。

只改：
config/import/、scripts/import_all.ps1、scripts/import_all.sh、sql/dim/

提交信息：
[DATX] 完成26个ODS导入配置与一键脚本
[DIM] 完成6张维度表建表SQL

push 后停下。

第 2 轮（等我通知）：
1. git pull；
2. 完成 DIM 装载 SQL；
3. 验证手机号脱敏、姓名保留姓氏、日期大促标记、商品属性；
4. 写 doc/DIM层质量检查清单.md。

提交信息：
[DIM] 完成维度装载与质量检查

不要改 DWD/DWS 文件。
```

### Day 2 · Coder B

```text
【Day 2 · Coder B｜2026-10-21】

第 1 轮：
1. 写 doc/ODS数据验证报告.md；
2. 核对 MySQL/Hive 与 CSV 行数；
3. 写 doc/DWD清洗规则文档.md，列出每张表的清洗项、规则、预期丢弃率。

只改：
doc/ODS数据验证报告.md、doc/DWD清洗规则文档.md

提交信息：
[ODS] 完成ODS数据验证报告
[DWD] 完成DWD清洗规则文档

push 后停下。

第 2 轮（等我通知）：
1. git pull；
2. 先完成评价、购物车、搜索 3 张 DWD 事实表；
3. 评价表必须生成 sentiment；
4. 自测 3 张表的行数和外键。

提交信息：
[DWD] 完成评价/购物车/搜索3张事实表

不要改 A 的 DIM 和组长指标文档。
```

---

## 六、Day 3：2026-10-22（周四）

### Day 3 · 组长

```text
【Day 3 · 组长｜2026-10-22】

第 1 轮：
1. 统一 DWS SQL 模板：分区、去重、空值、金额口径；
2. 复核 30 个指标归属；
3. 写 scripts/t2_validate_cross.py，准备四路对账。

只改：
DWS 模板、scripts/t2_validate_cross.py、指标复核文档

提交信息：
[DWS] 统一汇总SQL模板与指标口径
[QA] 提交交叉验证脚本

push 后停下。

第 2 轮（等我通知）：
1. git pull；
2. 复核 18 张 DWS 的字段、分区、口径；
3. 不改 A/B 的主责 SQL，只提出问题。

提交信息：
[DWS] 复核汇总表结构与指标口径

第 3 轮（等 A/B 修复完成）：
1. git pull；
2. 跑交叉验证，修复对账差异；
3. 写 doc/交叉验证报告.md；
4. 写 doc/process/day3.md。

提交信息：
[QA] 完成交叉验证并修复对账差异
[DOC] 完成day3过程文档与代码Review
```

### Day 3 · Coder A

```text
【Day 3 · Coder A｜2026-10-22】

第 1 轮：
1. 完成订单、明细、支付、退款、物流 5 张 DWD 事实表；
2. 实现金额分摊、状态标准化、时间逻辑校验；
3. 完成用户 5 张 + 流量 3 张 DWS。

只改：
sql/dwd/ 中订单类 5 张、sql/dws/ 中用户/流量 8 张

提交信息：
[DWD] 完成订单/明细/支付/退款/物流5张事实表
[DWS] 完成用户5张+流量3张汇总表

push 后停下。

第 2 轮（等我通知）：
1. git pull；
2. 修复复购率、留存率、漏斗口径；
3. 只改自己主责的 DWS。

提交信息：
[DWS] 修复用户/流量指标异常

第 3 轮：
只确认用户/流量 DWS 无遗留问题，不再改文件；有问题先说明。
```

### Day 3 · Coder B

```text
【Day 3 · Coder B｜2026-10-22】

第 1 轮：
1. 完成评价、购物车、搜索、用户行为、库存 5 张 DWD；
2. 与 Day2 已启动的 3 张合并；
3. 写 doc/数据质量报告.md；
4. 完成商品 5 张 + 地区 4 张 + 营销 1 张 DWS。

只改：
sql/dwd/ 中内容类 5 张、sql/dws/ 中商品/地区/营销 10 张、doc/数据质量报告.md

提交信息：
[DWD] 完成评价/购物车/搜索/行为/库存5张事实表
[DWD] 完成数据质量报告
[DWS] 完成商品5+地区4+营销1汇总表

push 后停下。

第 2 轮（等我通知）：
1. git pull；
2. 修复商品/地区/品牌/活动汇总；
3. 只改自己主责的 DWS。

提交信息：
[DWS] 修复商品/地区/营销指标异常

第 3 轮：
只确认商品/地区/营销 DWS 无遗留问题，不再改文件。
```

---

## 七、Day 4：2026-10-26（周一）

### Day 4 · 组长

```text
【Day 4 · 组长｜2026-10-26】

第 1 轮：
1. 写 pipeline.ps1/.bat/.sh；
2. 搭 Flask 框架：app.py、config.py、db.py；
3. 统一 JSON 返回、CORS、错误处理。

只改：
pipeline.ps1、pipeline.bat、pipeline.sh、flask_app/app.py、
flask_app/config.py、flask_app/db.py

提交信息：
[PIPE] 完成一键pipeline与Flask框架

push 后停下。

第 2 轮（等 A/B 第一轮完成后）：
1. git pull；
2. 测试 20 个 API；
3. 写 doc/API接口文档.md；
4. 跑全链路，写 doc/全链路复查报告.md。

提交信息：
[API] 完成接口测试与API文档
[QA] 完成全链路联调与Bug修复

第 3 轮（等 A/B 修复完成）：
1. git pull；
2. 写项目说明、数仓设计、README、day4；
3. 生成答辩 PPT；
4. 最后打 tag v1.0.0。

提交信息：
[DOC] 完成项目说明/数仓设计/README/day4
[REL] 完成答辩PPT与v1.0.0封版

tag 必须在所有代码修复提交之后打。
```

### Day 4 · Coder A

```text
【Day 4 · Coder A｜2026-10-26】

第 1 轮：
1. 完成 14 张 ADS 分析表；
2. 完成 16 个 DataX 导出配置和 export_all 脚本；
3. 完成 20 个 Flask API；
4. 完成大屏左半屏 6 个图表。

只改：
sql/ads/、config/export/、scripts/export_all.ps1/.sh、
flask_app/blueprints/、dashboard/ 左半屏

提交信息：
[ADS] 完成14张ADS分析表
[DATX] 完成16个ADS导出配置
[API] 完成20个REST接口
[UI] 完成大屏左半屏6图表

push 后停下。

第 2 轮（等组长通知）：
1. git pull；
2. 修复 ADS/API/左半屏联调问题；
3. 只改自己主责文件。

提交信息：
[QA] 修复ADS/API/左半屏联调问题

第 3 轮：
只确认 ADS/API/左半屏无遗留问题，不再改文件。
```

### Day 4 · Coder B

```text
【Day 4 · Coder B｜2026-10-26】

第 1 轮：
1. 完成销售预测模型；
2. 完成流失预测模型；
3. 完成 RFM 模型；
4. 完成大屏右半屏 6 个图表；
5. 写 3 份模型报告。

只改：
scripts/t2_train_models.py、models/、doc/销售预测模型报告.md、
doc/流失预测模型报告.md、doc/RFM模型报告.md、dashboard/ 右半屏

提交信息：
[ML] 完成销售预测模型与评估
[ML] 完成流失预测与RFM分层
[UI] 完成大屏右半屏6图表

push 后停下。

第 2 轮（等组长通知）：
1. git pull；
2. 修复 ML/右半屏联调问题；
3. 只改自己主责文件。

提交信息：
[QA] 修复ML/右半屏联调问题

第 3 轮：
只确认 ML/右半屏无遗留问题，不再改文件。
```

---

## 八、Day 5：2026-10-27（周二，全天答辩）

### 组长

```text
【Day 5 · 组长｜2026-10-27 答辩】

只写答辩材料，不改代码，不移动 tag。
输出：
1. 2.5 分钟演示顺序；
2. 每页讲稿；
3. 老师可能问的 10 个问题和回答；
4. 全链路演示检查清单。

提交信息：
[DOC] 答辩流程与演示脚本
```

### Coder A

```text
【Day 5 · Coder A｜2026-10-27 答辩】

只写自己负责部分的讲稿，不改代码。
重点讲：
1. 3 分钟讲清 14 张 ADS 的用途；
2. 20 个 API 的路径和返回；
3. 大屏左半屏 6 个图表怎么取数；
4. 为什么金额能对上。

提交信息：
[DOC] ADS/API/左半屏讲稿
```

### Coder B

```text
【Day 5 · Coder B｜2026-10-27 答辩】

只写自己负责部分的讲稿，不改代码。
重点讲：
1. 2.5 分钟讲清 DWD 清洗规则和丢弃率；
2. 18 张 DWS 的主题划分；
3. 3 个 ML 模型的特征、评估和业务解释；
4. 大屏右半屏 6 个图表。

提交信息：
[DOC] DWD/DWS/ML/右半屏讲稿
```

---

## 九、AI 回复格式要求（每次都加在最后）

```text
完成后按以下格式回复：

1. 完成任务
2. 改动文件
3. 验证命令
4. 验证结果
5. 未解决问题
6. 下一步建议

不要只说“已完成”，必须给出具体文件和验证结果。
```

---

## 十、绝对禁止

```text
- 不要建 dev/feature/test 分支；
- 不要 force push；
- 不要 git reset --hard；
- 不要 git add .；
- 不要提交 .venv、node_modules、data/t2_ecommerce.db、models/*.joblib；
- 不要改其他角色主责文件；
- 不要在前一个人还没 push 时开始提交；
- 不要在 Day 4 之前打 v1.0.0；
- 不要动 GitHub 仓库名；
- 不要往 GitHub 推送，GitHub 由组长维护完整备份；
- Gitee 按轮次由当值人 push：组长 push 后 Coder A，A push 后 Coder B。
```
