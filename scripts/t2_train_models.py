"""Train the three required group-2 models and publish their ADS results."""

from __future__ import annotations

import json
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from t2_common import DB_PATH, DOC_DIR, END_DATE, MODEL_DIR, connect, ensure_dirs, table


def write_df(conn, name, df):
    df.to_sql(name, conn, if_exists="replace", index=False)


def mape(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def train_sales_forecast(conn):
    raw = pd.read_sql(f'SELECT order_date, SUM(pay_amount) AS gmv FROM "{table("dwd", "order")}" GROUP BY order_date ORDER BY order_date', conn)
    raw["order_date"] = pd.to_datetime(raw["order_date"])
    idx = pd.date_range(raw["order_date"].min(), raw["order_date"].max(), freq="D")
    daily = raw.set_index("order_date").reindex(idx, fill_value=0).rename_axis("ds").reset_index()
    daily["gmv"] = daily["gmv"].astype(float)
    day_text = daily["ds"].dt.strftime("%Y-%m-%d")
    daily["is_618"] = day_text.between("2025-06-15", "2025-06-18").astype(int)
    daily["is_1111"] = day_text.between("2025-11-08", "2025-11-11").astype(int)
    daily["is_promo"] = ((daily["is_618"] + daily["is_1111"]) > 0).astype(int)
    daily["promo_intensity"] = daily["is_618"] * 3 + daily["is_1111"] * 5
    daily["dow"] = daily["ds"].dt.dayofweek
    daily["is_weekend"] = (daily["dow"] >= 5).astype(int)
    daily["month"] = daily["ds"].dt.month
    daily["day"] = daily["ds"].dt.day
    daily["lag1"] = daily["gmv"].shift(1)
    daily["lag7"] = daily["gmv"].shift(7)
    daily["rolling7"] = daily["gmv"].shift(1).rolling(7).mean()
    daily["rolling30"] = daily["gmv"].shift(1).rolling(30).mean()
    data = daily.dropna().reset_index(drop=True)
    features = ["dow", "is_weekend", "is_promo", "is_618", "is_1111", "promo_intensity", "month", "day", "lag1", "lag7", "rolling7", "rolling30"]
    test_days = 30
    train, test = data.iloc[:-test_days], data.iloc[-test_days:]
    models = {
        "LinearRegression": make_pipeline(StandardScaler(), LinearRegression()),
        "RandomForest": RandomForestRegressor(n_estimators=400, max_depth=8, min_samples_leaf=2, random_state=2, n_jobs=-1),
    }
    results = {}
    fitted = {}
    for name, model in models.items():
        model.fit(train[features], np.log1p(train["gmv"]))
        pred = np.expm1(model.predict(test[features]))
        results[name] = {
            "MAE": round(float(mean_absolute_error(test["gmv"], pred)), 2),
            "RMSE": round(float(np.sqrt(mean_squared_error(test["gmv"], pred))), 2),
            "R2": round(float(r2_score(test["gmv"], pred)), 4),
            "MAPE": round(mape(test["gmv"].values, pred), 2),
        }
        fitted[name] = model
    best_name = min(results, key=lambda k: results[k]["RMSE"])
    model = fitted[best_name]
    test_pred = np.expm1(model.predict(test[features]))
    residual_std = float(np.std(test["gmv"].values - test_pred))

    # Recursive 14-day forecast.
    history = daily[["ds", "gmv"]].copy()
    future_rows = []
    for step in range(1, 15):
        next_date = pd.Timestamp(END_DATE) + timedelta(days=step)
        hist = history["gmv"].tolist()
        row = {
            "dow": next_date.dayofweek,
            "is_weekend": int(next_date.dayofweek >= 5),
            "is_promo": 0,
            "is_618": 0,
            "is_1111": 0,
            "promo_intensity": 0,
            "month": next_date.month,
            "day": next_date.day,
            "lag1": hist[-1],
            "lag7": hist[-7],
            "rolling7": float(np.mean(hist[-7:])),
            "rolling30": float(np.mean(hist[-30:])),
        }
        X = pd.DataFrame([row])[features]
        predicted = float(np.expm1(model.predict(X)[0]))
        future_rows.append({
            "forecast_date": next_date.strftime("%Y-%m-%d"),
            "predicted_gmv": round(max(0, predicted), 2),
            "lower_bound": round(max(0, predicted - 1.96 * residual_std), 2),
            "upper_bound": round(max(0, predicted + 1.96 * residual_std), 2),
            "model_name": best_name,
            "mae": results[best_name]["MAE"],
            "rmse": results[best_name]["RMSE"],
            "r2": results[best_name]["R2"],
            "mape": results[best_name]["MAPE"],
        })
        history.loc[len(history)] = [next_date, max(0, predicted)]
    forecast = pd.DataFrame(future_rows)
    write_df(conn, table("ads", "sales_forecast"), forecast)
    joblib.dump({"model": model, "features": features, "name": best_name}, MODEL_DIR / "t2_sales_forecast.joblib")

    compare = test[["ds", "gmv"]].copy()
    compare["predicted"] = test_pred
    compare["ds"] = compare["ds"].dt.strftime("%Y-%m-%d")
    compare.to_csv(MODEL_DIR / "t2_sales_forecast_holdout.csv", index=False)
    metrics = {
        "model": best_name,
        "metrics": results,
        "chosen": results[best_name],
        "forecast_rows": len(forecast),
        "forecast_total": round(float(forecast["predicted_gmv"].sum()), 2),
    }
    (MODEL_DIR / "t2_sales_forecast_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    report = f"""# 销售趋势预测模型报告

## 一、目标

预测运动品类未来 14 天 GMV，为备货、投放和大促返场提供参考。

## 二、特征工程

| 特征 | 含义 |
|---|---|
| dow / is_weekend | 星期效应与周末效应 |
| is_promo | 是否处于 618 或双11 大促窗口 |
| month / day | 季节性与月中/月末效应 |
| lag1 / lag7 | 前 1 天、前 7 天 GMV |
| rolling7 / rolling30 | 近 7 天、近 30 天均值 |

时间切分：前 150 天训练，最后 30 天测试，避免随机切分造成未来信息泄漏。

## 三、模型对比

| 模型 | MAE | RMSE | R² | MAPE |
|---|---:|---:|---:|---:|
| LinearRegression | {results['LinearRegression']['MAE']} | {results['LinearRegression']['RMSE']} | {results['LinearRegression']['R2']} | {results['LinearRegression']['MAPE']}% |
| RandomForest | {results['RandomForest']['MAE']} | {results['RandomForest']['RMSE']} | {results['RandomForest']['R2']} | {results['RandomForest']['MAPE']}% |

按 RMSE 选择 **{best_name}**。未来 14 天预测 GMV 合计 **{metrics['forecast_total']:,.2f} 元**。

## 四、预测结果

| 日期 | 预测GMV | 下界 | 上界 |
|---|---:|---:|---:|
{chr(10).join(f"| {r.forecast_date} | {r.predicted_gmv:,.2f} | {r.lower_bound:,.2f} | {r.upper_bound:,.2f} |" for r in forecast.itertuples())}

## 五、结论与风险

- 双11 后的自然回落已在递归预测中体现，预测曲线不会延续单日峰值。
- 运动品类季节性强，若出现寒潮或平台追加补贴，实际 GMV 可能高于上界。
- 建议每周用最新数据重训一次，模型文件：`models/t2_sales_forecast.joblib`。
"""
    (DOC_DIR / "销售预测模型报告.md").write_text(report, encoding="utf-8")
    return metrics


def train_churn(conn):
    orders = pd.read_sql(f'SELECT * FROM "{table("dwd", "order")}" WHERE is_paid=1', conn)
    users = pd.read_sql(f'SELECT * FROM "{table("dim", "user_info")}"', conn)
    refunds = pd.read_sql(f'SELECT * FROM "{table("dwd", "refund")}" WHERE refund_status="已退款"', conn)
    snapshot = pd.Timestamp(END_DATE)
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    agg = orders.groupby("user_id").agg(
        last_order=("order_date", "max"), first_order=("order_date", "min"),
        frequency=("order_id", "nunique"), monetary=("pay_amount", "sum"),
    ).reset_index()
    agg["recency_days"] = (snapshot - agg["last_order"]).dt.days
    agg["avg_order_value"] = agg["monetary"] / agg["frequency"].clip(lower=1)
    agg["active_span_days"] = (agg["last_order"] - agg["first_order"]).dt.days
    refund_count = refunds.groupby("order_id").size().rename("refund_rows").reset_index()
    refund_by_user = orders.merge(refund_count, on="order_id", how="left").fillna({"refund_rows": 0}).groupby("user_id")["refund_rows"].sum().rename("refund_count").reset_index()
    data = agg.merge(refund_by_user, on="user_id", how="left").fillna({"refund_count": 0})
    data = data.merge(users[["user_id", "member_level_num", "register_date", "gender", "age"]], on="user_id", how="left")
    data["days_since_register"] = (snapshot - pd.to_datetime(data["register_date"])).dt.days
    data["is_male"] = (data["gender"] == "男").astype(int)
    data["churn"] = (data["recency_days"] > 30).astype(int)
    features = ["recency_days", "frequency", "monetary", "avg_order_value", "active_span_days", "refund_count", "member_level_num", "days_since_register", "is_male"]
    X, y = data[features], data["churn"]
    # Time-agnostic stratified split is acceptable for a churn cross-section.
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=2, stratify=y)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced", random_state=2))
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]
    cm = confusion_matrix(y_test, pred).tolist()
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
        "confusion_matrix": cm,
        "churn_rate": round(float(y.mean() * 100), 2),
        "samples": int(len(data)),
    }
    data["churn_prob"] = model.predict_proba(X)[:, 1]
    data["risk_level"] = np.select(
        [data["churn_prob"] >= 0.75, data["churn_prob"] >= 0.45], ["高风险", "中风险"], default="低风险"
    )
    data = data.sort_values("churn_prob", ascending=False).reset_index(drop=True)
    data["rank_no"] = data.index + 1
    top = data.head(100)[["user_id", "churn_prob", "risk_level", "recency_days", "frequency", "monetary", "member_level_num", "rank_no"]].rename(
        columns={"member_level_num": "member_level"}
    )
    write_df(conn, table("ads", "user_churn_predict"), top)
    joblib.dump({"model": model, "features": features}, MODEL_DIR / "t2_churn_model.joblib")
    (MODEL_DIR / "t2_churn_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    coef = model.named_steps["logisticregression"].coef_[0]
    coef_rows = sorted(zip(features, coef), key=lambda x: abs(x[1]), reverse=True)
    report = f"""# 用户流失预测模型报告

## 一、标签定义

以 {END_DATE} 为快照日，最近 30 天无支付订单的用户标记为流失（1），否则为未流失（0）。样本量 **{metrics['samples']}**，流失率 **{metrics['churn_rate']}%**。

## 二、特征与模型

特征：最近下单天数、累计订单数、累计金额、平均客单价、活跃跨度、退款次数、会员等级、注册天数、性别。

模型：标准化 + LogisticRegression（class_weight=balanced）。按 7:3 分层切分训练/测试。

## 三、评估结果

| 指标 | 数值 |
|---|---:|
| Accuracy | {metrics['accuracy']} |
| Precision | {metrics['precision']} |
| Recall | {metrics['recall']} |
| F1 | {metrics['f1']} |

混淆矩阵：`{cm}`（行=真实，列=预测）。

## 四、特征影响（标准化系数）

| 特征 | 系数 | 方向 |
|---|---:|---|
{chr(10).join(f"| {n} | {c:.4f} | {'提高流失风险' if c > 0 else '降低流失风险'} |" for n, c in coef_rows)}

## 五、结果

高风险流失用户 Top100 已写入 `t2_ads_user_churn_predict`，模型文件 `models/t2_churn_model.joblib`。运营可优先触达“高客单 + 高 recency”人群，用专属券或会员权益召回。
"""
    (DOC_DIR / "流失预测模型报告.md").write_text(report, encoding="utf-8")
    return metrics


def train_rfm(conn):
    orders = pd.read_sql(f'SELECT * FROM "{table("dwd", "order")}" WHERE is_paid=1', conn)
    users = pd.read_sql(f'SELECT * FROM "{table("dim", "user_info")}"', conn)
    snapshot = pd.Timestamp(END_DATE)
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    data = orders.groupby("user_id").agg(
        last_order_date=("order_date", "max"), frequency=("order_id", "nunique"), monetary=("pay_amount", "sum")
    ).reset_index()
    data["recency_days"] = (snapshot - data["last_order_date"]).dt.days
    data["r_score"] = np.clip(np.ceil(data["recency_days"].rank(pct=True, ascending=False) * 5), 1, 5).astype(int)
    data["f_score"] = np.clip(np.ceil(data["frequency"].rank(pct=True) * 5), 1, 5).astype(int)
    data["m_score"] = np.clip(np.ceil(data["monetary"].rank(pct=True) * 5), 1, 5).astype(int)
    data["rfm_score"] = (data["r_score"] * 0.4 + data["f_score"] * 0.3 + data["m_score"] * 0.3).round(2)
    data["segment"] = pd.cut(
        data["rfm_score"], bins=[0, 2.0, 2.8, 3.5, 4.2, 5.01],
        labels=["流失", "流失预警", "稳定", "潜力", "高价值"], include_lowest=True
    ).astype(str)
    data["last_order_date"] = data["last_order_date"].dt.strftime("%Y-%m-%d")
    write_df(conn, table("dws", "user_rfm"), data.rename(columns={"frequency": "order_count", "monetary": "total_gmv"})[[
        "user_id", "r_score", "f_score", "m_score", "rfm_score", "segment", "last_order_date", "order_count", "total_gmv"
    ]].rename(columns={"r_score": "rfm_r", "f_score": "rfm_f", "m_score": "rfm_m"}))

    agg = data.groupby("segment").agg(
        user_count=("user_id", "nunique"), avg_r=("r_score", "mean"), avg_f=("f_score", "mean"),
        avg_m=("m_score", "mean"), avg_monetary=("monetary", "mean")
    ).reset_index()
    agg["user_share"] = agg["user_count"] / len(data) * 100
    order = ["高价值", "潜力", "稳定", "流失预警", "流失"]
    agg["segment"] = pd.Categorical(agg["segment"], categories=order, ordered=True)
    agg = agg.sort_values("segment")
    write_df(conn, table("ads", "user_rfm"), agg)
    (MODEL_DIR / "t2_rfm_rules.json").write_text(json.dumps({
        "weights": {"R": 0.4, "F": 0.3, "M": 0.3},
        "segments": {
            "高价值": ">=4.2", "潜力": "3.5-4.2", "稳定": "2.8-3.5",
            "流失预警": "2.0-2.8", "流失": "<2.0",
        },
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    report = f"""# RFM 用户价值分层报告

## 一、口径

- R：最近一次支付距 {END_DATE} 的天数，越近分越高；
- F：累计支付订单数；
- M：累计支付金额；
- R/F/M 均按分位数打 1~5 分；
- 综合分 = R×0.4 + F×0.3 + M×0.3。

## 二、分层规则与结果

| 分层 | 综合分 | 人数 | 占比 | 平均R | 平均F | 平均M | 平均金额 |
|---|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(f"| {r.segment} | {'>=4.2' if r.segment=='高价值' else '3.5-4.2' if r.segment=='潜力' else '2.8-3.5' if r.segment=='稳定' else '2.0-2.8' if r.segment=='流失预警' else '<2.0'} | {r.user_count} | {r.user_share:.2f}% | {r.avg_r:.2f} | {r.avg_f:.2f} | {r.avg_m:.2f} | {r.avg_monetary:,.2f} |" for r in agg.itertuples())}

## 三、运营建议

- **高价值**：专属客服、限量新品优先购，重点防流失；
- **潜力**：用品类券拉高购买频次，推动向高价值迁移；
- **稳定**：保持常规触达，推荐运动场景组合购；
- **流失预警**：30 天未购人群定向召回；
- **流失**：低成本短信/站内信唤醒，不再投入高额补贴。

结果已写入 `t2_dws_user_rfm` 与 `t2_ads_user_rfm`。
"""
    (DOC_DIR / "RFM模型报告.md").write_text(report, encoding="utf-8")
    return {"segments": agg.to_dict("records")}


def main():
    ensure_dirs()
    conn = connect()
    sales = train_sales_forecast(conn)
    churn = train_churn(conn)
    rfm = train_rfm(conn)
    conn.commit()
    conn.close()
    summary = {"sales_forecast": sales, "churn": churn, "rfm": rfm, "trained_at": datetime.now().isoformat(timespec="seconds")}
    (MODEL_DIR / "t2_ml_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
