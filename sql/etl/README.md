# ETL SQL 说明

本目录提供 Hive SQL 参考实现，便于在实验虚拟机讲解和复现 DIM/DWD/DWS/ADS 的计算逻辑。

本地演示与一键 pipeline 的权威实现是 `scripts/t2_build_warehouse.py`。它使用 SQLite 物化同样的分层，保证在没有 Hadoop 环境的电脑上也能完整跑通。

文件：

- `01_dim_dwd.sql`：6 张 DIM + 10 张 DWD 的建表后装载逻辑；
- `02_dws_ads.sql`：18 张 DWS + 14 张 ADS 的汇总逻辑（30 指标、漏斗、RFM、库存预警）。

执行前请先执行 `sql/*/t2_*_hive.sql` 建表，并按虚拟机实际的 HDFS/MySQL 地址修改 DataX 配置。
