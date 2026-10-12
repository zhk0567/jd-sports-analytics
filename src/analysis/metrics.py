"""Aggregation helpers for the Streamlit dashboard."""

from __future__ import annotations

import pandas as pd

CATEGORY_LABELS = {
    "footwear": "鞋类",
    "apparel": "服饰",
    "equipment": "装备",
    "nutrition": "营养",
    "other": "其他",
}


def overview(df: pd.DataFrame) -> dict:
    self_rate = None
    if "is_self_operated" in df.columns and len(df):
        self_rate = float(df["is_self_operated"].fillna(False).astype(bool).mean())
    return {
        "product_count": int(len(df)),
        "brand_count": int(df["brand"].nunique()) if len(df) else 0,
        "shop_count": int(df["shop_name"].replace("", pd.NA).nunique(dropna=True))
        if len(df) and "shop_name" in df
        else 0,
        "price_mean": float(df["price"].mean()) if df["price"].notna().any() else None,
        "price_median": float(df["price"].median()) if df["price"].notna().any() else None,
        "comment_sum": int(df["comment_count"].fillna(0).sum()) if len(df) else 0,
        "self_operated_rate": self_rate,
    }


def brand_counts(df: pd.DataFrame, n: int | None = None) -> pd.DataFrame:
    s = df["brand"].value_counts().rename_axis("brand").reset_index(name="count")
    if n is not None:
        s = s.head(n)
    return s


def price_band_counts(df: pd.DataFrame) -> pd.DataFrame:
    order_hint = ["0-60", "60-200", "200-400", "400-900", "900-4000", "4000+", "unknown"]
    s = df["price_band"].value_counts()
    out = s.rename_axis("price_band").reset_index(name="count")
    out["_ord"] = out["price_band"].apply(
        lambda x: order_hint.index(x) if x in order_hint else 99
    )
    return out.sort_values("_ord").drop(columns="_ord")


def category_counts(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df["category_guess"]
        .value_counts()
        .rename_axis("category_guess")
        .reset_index(name="count")
    )


def scene_counts(df: pd.DataFrame) -> pd.DataFrame:
    if "sport_scene" not in df.columns or df.empty:
        return pd.DataFrame(columns=["sport_scene", "count"])
    return (
        df["sport_scene"]
        .fillna("其他")
        .value_counts()
        .rename_axis("sport_scene")
        .reset_index(name="count")
    )


def gender_counts(df: pd.DataFrame) -> pd.DataFrame:
    if "gender_guess" not in df.columns or df.empty:
        return pd.DataFrame(columns=["gender_guess", "count"])
    return (
        df["gender_guess"]
        .fillna("未知")
        .value_counts()
        .rename_axis("gender_guess")
        .reset_index(name="count")
    )


def self_operated_rate(df: pd.DataFrame) -> float | None:
    if "is_self_operated" not in df.columns or df.empty:
        return None
    return float(df["is_self_operated"].fillna(False).astype(bool).mean())


def brand_category_matrix(df: pd.DataFrame, top_brands: int = 12) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    top = df["brand"].value_counts().head(top_brands).index.tolist()
    work = df[df["brand"].isin(top)].copy()
    work["category_label"] = work["category_guess"].map(
        lambda x: CATEGORY_LABELS.get(x, x)
    )
    mat = (
        work.groupby(["brand", "category_label"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    return mat


def brand_price_scatter(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["brand", "count", "price_mean", "comment_sum"])
    top = df["brand"].value_counts().head(top_n).index.tolist()
    work = df[df["brand"].isin(top)]
    g = (
        work.groupby("brand", as_index=False)
        .agg(
            count=("sku_id", "count"),
            price_mean=("price", "mean"),
            comment_sum=("comment_count", "sum"),
        )
        .dropna(subset=["price_mean"])
    )
    return g


def scene_price_band_matrix(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "sport_scene" not in df.columns or "price_band" not in df.columns:
        return pd.DataFrame()
    work = df.copy()
    work["sport_scene"] = work["sport_scene"].fillna("其他")
    order_hint = ["0-60", "60-200", "200-400", "400-900", "900-4000", "4000+", "unknown"]
    mat = (
        work.groupby(["sport_scene", "price_band"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    mat["_ord"] = mat["price_band"].apply(
        lambda x: order_hint.index(x) if x in order_hint else 99
    )
    return mat.sort_values(["sport_scene", "_ord"]).drop(columns="_ord")


def top_shops(df: pd.DataFrame, n: int = 15, by: str = "products") -> pd.DataFrame:
    work = df.copy()
    work = work[work["shop_name"].astype(str).str.len() > 0]
    if work.empty:
        return pd.DataFrame(columns=["shop_name", "value"])
    if by == "comments":
        g = (
            work.groupby("shop_name", as_index=False)["comment_count"]
            .sum()
            .rename(columns={"comment_count": "value"})
        )
    else:
        g = (
            work.groupby("shop_name", as_index=False)
            .size()
            .rename(columns={"size": "value"})
        )
    return g.sort_values("value", ascending=False).head(n)


def top_products(df: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    if df.empty:
        return df
    work = df.copy()
    work["_has_img"] = (
        work.get("image_url", pd.Series([""] * len(work)))
        .fillna("")
        .astype(str)
        .str.len()
        > 8
    )
    work["_known_brand"] = work["brand"].fillna("").ne("未知品牌").astype(int)
    work["_sport_cat"] = (
        work["category_guess"]
        .isin(["footwear", "apparel", "equipment", "nutrition"])
        .astype(int)
    )
    work = work.sort_values(
        ["_sport_cat", "_known_brand", "_has_img", "comment_count", "price"],
        ascending=[False, False, False, False, True],
    )
    return work.head(n).drop(
        columns=["_has_img", "_known_brand", "_sport_cat"], errors="ignore"
    )


def filter_df(
    df: pd.DataFrame,
    brands: list[str] | None = None,
    categories: list[str] | None = None,
    scenes: list[str] | None = None,
    genders: list[str] | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    self_operated_only: bool = False,
) -> pd.DataFrame:
    out = df
    if brands:
        out = out[out["brand"].isin(brands)]
    if categories:
        out = out[out["category_guess"].isin(categories)]
    if scenes and "sport_scene" in out.columns:
        out = out[out["sport_scene"].fillna("其他").isin(scenes)]
    if genders and "gender_guess" in out.columns:
        out = out[out["gender_guess"].fillna("未知").isin(genders)]
    if price_min is not None:
        out = out[out["price"].fillna(-1) >= price_min]
    if price_max is not None:
        out = out[out["price"].fillna(1e18) <= price_max]
    if self_operated_only and "is_self_operated" in out.columns:
        out = out[out["is_self_operated"].fillna(False).astype(bool)]
    return out


def insight_line(df: pd.DataFrame) -> str:
    if df.empty:
        return "当前筛选下暂无商品。"
    ov = overview(df)
    cats = category_counts(df)
    top_cat = "—"
    top_share = 0.0
    if not cats.empty:
        top = cats.iloc[0]
        top_cat = CATEGORY_LABELS.get(top["category_guess"], top["category_guess"])
        top_share = 100.0 * top["count"] / max(ov["product_count"], 1)
    med = f"¥{ov['price_median']:.0f}" if ov["price_median"] is not None else "—"
    return (
        f"当前视图 <strong>{ov['product_count']:,}</strong> 件商品 · "
        f"中位价 <strong>{med}</strong> · "
        f"{top_cat}占比 <strong>{top_share:.0f}%</strong>"
    )
