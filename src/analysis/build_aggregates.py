"""Build analysis-ready aggregate tables and quality report."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.analysis import metrics as M


def _group_stats(df: pd.DataFrame, key: str) -> pd.DataFrame:
    if df.empty or key not in df.columns:
        return pd.DataFrame(
            columns=[key, "count", "price_mean", "price_median", "comment_sum"]
        )
    g = df.groupby(key, dropna=False)
    out = g.agg(
        count=("sku_id", "count"),
        price_mean=("price", "mean"),
        price_median=("price", "median"),
        comment_sum=("comment_count", "sum"),
    ).reset_index()
    out["comment_sum"] = out["comment_sum"].fillna(0).astype("int64")
    return out.sort_values("count", ascending=False)


def build_aggregates(
    df: pd.DataFrame, aggregates_dir: Path, shop_top_n: int = 50
) -> dict[str, str]:
    aggregates_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}

    by_brand = _group_stats(df, "brand")
    p = aggregates_dir / "by_brand.parquet"
    by_brand.to_parquet(p, index=False)
    paths["by_brand"] = str(p)

    by_category = _group_stats(df, "category_guess")
    p = aggregates_dir / "by_category.parquet"
    by_category.to_parquet(p, index=False)
    paths["by_category"] = str(p)

    by_price = _group_stats(df, "price_band")
    # keep band order similar to metrics helper
    order = M.price_band_counts(df)["price_band"].tolist() if len(df) else []
    if order:
        by_price["_ord"] = by_price["price_band"].apply(
            lambda x: order.index(x) if x in order else 99
        )
        by_price = by_price.sort_values("_ord").drop(columns="_ord")
    p = aggregates_dir / "by_price_band.parquet"
    by_price.to_parquet(p, index=False)
    paths["by_price_band"] = str(p)

    if "sport_scene" in df.columns:
        by_scene = _group_stats(df, "sport_scene")
        p = aggregates_dir / "by_sport_scene.parquet"
        by_scene.to_parquet(p, index=False)
        paths["by_sport_scene"] = str(p)

    shops = M.top_shops(df, n=shop_top_n, by="products").rename(
        columns={"value": "count"}
    )
    p = aggregates_dir / "by_shop_top.parquet"
    shops.to_parquet(p, index=False)
    paths["by_shop_top"] = str(p)

    return paths


def build_quality_report(df: pd.DataFrame) -> dict[str, Any]:
    n = int(len(df))
    if n == 0:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "rows": 0,
        }

    flags = df["quality_flags"].fillna("").astype(str) if "quality_flags" in df else pd.Series([""] * n)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": n,
        "missing_price_rate": float(df["price"].isna().mean()),
        "missing_title_rate": float(df["title"].fillna("").astype(str).str.strip().eq("").mean()),
        "missing_shop_rate": float(
            df["shop_name"].fillna("").astype(str).str.strip().eq("").mean()
        ),
        "unknown_brand_rate": float((df["brand"] == "未知品牌").mean())
        if "brand" in df
        else None,
        "price_outlier_count": int(flags.str.contains("price_outlier", na=False).sum()),
        "missing_price_count": int(flags.str.contains("missing_price", na=False).sum()),
        "missing_title_count": int(flags.str.contains("missing_title", na=False).sum()),
        "self_operated_rate": float(df["is_self_operated"].mean())
        if "is_self_operated" in df
        else None,
        "category_counts": df["category_guess"].value_counts().to_dict()
        if "category_guess" in df
        else {},
        "sport_scene_counts": df["sport_scene"].value_counts().to_dict()
        if "sport_scene" in df
        else {},
        "gender_counts": df["gender_guess"].value_counts().to_dict()
        if "gender_guess" in df
        else {},
    }
    return report


def write_summary(
    df: pd.DataFrame,
    *,
    processed_dir: Path,
    aggregate_paths: dict[str, str],
    root: Path,
) -> dict[str, Any]:
    ov = M.overview(df)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": ov["product_count"],
        "brands": ov["brand_count"],
        "shops": ov["shop_count"],
        "price_mean": ov["price_mean"],
        "price_median": ov["price_median"],
        "comment_sum": ov["comment_sum"],
        "category_counts": df["category_guess"].value_counts().to_dict()
        if "category_guess" in df and len(df)
        else {},
        "sport_scene_counts": df["sport_scene"].value_counts().to_dict()
        if "sport_scene" in df and len(df)
        else {},
        "parquet": "data/processed/products.parquet",
        "csv": "data/processed/products.csv",
        "aggregates": {
            k: str(Path(v).resolve().relative_to(root.resolve()))
            if Path(v).is_absolute()
            else v
            for k, v in aggregate_paths.items()
        },
    }
    (processed_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary
