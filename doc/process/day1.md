# Day 1 开发过程文档

## 一、今日任务完成情况

- [x] 项目初始化、目录结构、Gitee/GitHub 仓库
- [x] 运动品类需求分析与 13 张 ODS 关系设计
- [x] ER 图（`doc/ER图.png`）
- [x] 数仓字段字典
- [x] 品类特征数据分布规范
- [x] 13 张 ODS 建表 SQL（MySQL + Hive）
- [x] 数据生成脚本与 CSV（24,935 行）

## 二、详细操作记录

### 2.1 数据生成

```bash
python scripts/t2_generate_data.py
```

结果：13 张 CSV，合计 24,935 行；随机种子 2；男性占比 65.38%。

### 2.2 ODS 建表

- MySQL：`sql/ods/t2_ods_mysql.sql`（13 张）
- Hive：`sql/ods/t2_ods_hive.sql`（13 张外部表，TEXTFILE）

## 三、问题与解决

1. 订单明细总数需精确 5,000：改为先保证每单 1 行，再精确补 3,000 行，单笔上限 4 行。
2. 品类名称映射重复导致 map 失败：分类映射先去重再建索引。
3. 订单金额与明细金额对不上：DWD 层按行金额比例分摊订单实付。

## 四、明日计划

完成 ODS 导入验证、6 张 DIM、DWD 清洗规则与 30 指标设计。

## 五、Git 提交记录

```text
ce9b19c Polish brand/price/shelf charts and refresh README screenshots.
3db5ee0 Initial commit: JD sports crawl pipeline and web story UI.
```
