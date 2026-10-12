"""Feature enrichment: category, price band, brand, scene, gender, quality."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd

FOOTWEAR_PAT = r"鞋|跑鞋|篮球鞋|拖鞋|靴子|sneakers"
APPAREL_PAT = r"衣|裤|T恤|短袖|长袖|外套|卫衣|裙|袜|冲锋衣|背心|内衣"
EQUIPMENT_PAT = (
    r"跳绳|瑜伽垫|哑铃|跑步机|单车|椭圆机|拉力|护腕|护膝|球拍|篮球|足球|装备|动感"
)
NUTRITION_PAT = r"蛋白|乳清|氮泵|肌酸|营养|维生素|支链|增肌"

SCENE_RULES: list[tuple[str, str]] = [
    ("跑步|跑鞋|马拉松", "跑步"),
    ("篮球", "篮球"),
    ("瑜伽", "瑜伽"),
    ("游泳", "游泳"),
    ("羽毛球", "羽毛球"),
    ("足球", "足球"),
    ("网球", "网球"),
    ("乒乓", "乒乓球"),
    ("健身|哑铃|力量|训练|蛋白|跑步机|椭圆|动感单车", "健身"),
    ("户外|登山|冲锋|滑雪|骑行|北面|探路", "户外"),
]

GENDER_CHILD = r"童|儿童|大童|小童|婴童|kids|Kids"
GENDER_MALE = r"(?<![女])男[士款性装]?|男士|男子"
GENDER_FEMALE = r"女[士款性装]?|女士|女子"


def normalize_numeric(series: pd.Series) -> pd.Series:
    def _one(v: Any) -> float | None:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return None
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().replace(",", "")
        s = re.sub(r"[^\d.]", "", s)
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None

    return series.map(_one)


def assign_price_band_series(price: pd.Series, bands: list[list[Any]]) -> pd.Series:
    result = pd.Series("unknown", index=price.index, dtype="object")
    valid = price.notna()
    if not valid.any():
        return result
    p = price.astype(float)
    for lo, hi in bands:
        lo_f = float(lo)
        if hi is None:
            mask = valid & (p >= lo_f)
            result.loc[mask] = f"{int(lo_f)}+"
        else:
            hi_f = float(hi)
            mask = valid & (p >= lo_f) & (p < hi_f)
            result.loc[mask] = f"{int(lo_f)}-{int(hi_f)}"
    return result


def guess_category_series(title: pd.Series) -> pd.Series:
    t = title.fillna("").astype(str)
    out = pd.Series("other", index=title.index, dtype="object")
    out = out.mask(t.str.contains(FOOTWEAR_PAT, regex=True, na=False), "footwear")
    # later rules only fill remaining "other"
    remaining = out.eq("other")
    out = out.mask(
        remaining & t.str.contains(NUTRITION_PAT, regex=True, na=False), "nutrition"
    )
    remaining = out.eq("other")
    out = out.mask(
        remaining & t.str.contains(EQUIPMENT_PAT, regex=True, na=False), "equipment"
    )
    remaining = out.eq("other")
    out = out.mask(
        remaining & t.str.contains(APPAREL_PAT, regex=True, na=False), "apparel"
    )
    return out


def guess_sport_scene_series(title: pd.Series, source_query: pd.Series) -> pd.Series:
    text = (
        title.fillna("").astype(str) + " " + source_query.fillna("").astype(str)
    )
    out = pd.Series("其他", index=title.index, dtype="object")
    for pat, label in SCENE_RULES:
        remaining = out.eq("其他")
        out = out.mask(remaining & text.str.contains(pat, regex=True, na=False), label)
    return out


def guess_gender_series(title: pd.Series) -> pd.Series:
    t = title.fillna("").astype(str)
    out = pd.Series("未知", index=title.index, dtype="object")
    out = out.mask(t.str.contains(GENDER_CHILD, regex=True, na=False), "童")
    remaining = out.eq("未知")
    # female before male to catch 男女同款 later as 中性 if both
    female = t.str.contains(r"女[士款性装]?|女士|女子", regex=True, na=False)
    male = t.str.contains(r"男[士款性装]?|男士|男子", regex=True, na=False)
    both = female & male
    out = out.mask(remaining & both, "中性")
    remaining = out.eq("未知")
    out = out.mask(remaining & female, "女")
    remaining = out.eq("未知")
    out = out.mask(remaining & male, "男")
    remaining = out.eq("未知")
    out = out.mask(
        remaining & t.str.contains(r"男女|情侣|中性|unisex", regex=True, na=False),
        "中性",
    )
    return out


def build_brand_patterns(
    brands: list[str], aliases: dict[str, str]
) -> list[tuple[str, str]]:
    """Longer aliases/brands first for matching."""
    mapping: dict[str, str] = {}
    for b in brands:
        mapping[str(b)] = str(b)
    for alias, canonical in (aliases or {}).items():
        mapping[str(alias)] = str(canonical)
    # sort by length desc
    items = sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True)
    return items


def normalize_brand_series(
    brand: pd.Series,
    title: pd.Series,
    patterns: list[tuple[str, str]],
) -> pd.Series:
    b = brand.fillna("").astype(str).str.strip()
    t = title.fillna("").astype(str)
    out = b.copy()

    # Map aliases already present in brand field
    alias_map = {k.lower(): v for k, v in patterns}
    lower_b = out.str.lower()
    for alias_l, canonical in alias_map.items():
        out = out.mask(lower_b == alias_l, canonical)

    # Fill empty / 未知品牌 from title
    need = out.eq("") | out.eq("未知品牌") | out.eq("None") | out.eq("nan")
    if need.any() and patterns:
        filled = pd.Series("", index=out.index, dtype="object")
        for alias, canonical in patterns:
            # case-insensitive for ascii aliases
            if alias.isascii():
                hit = t.str.contains(re.escape(alias), case=False, regex=True, na=False)
            else:
                hit = t.str.contains(re.escape(alias), regex=True, na=False)
            still = filled.eq("")
            filled = filled.mask(still & hit, canonical)
        out = out.mask(need & filled.ne(""), filled)

    out = out.replace("", "未知品牌")
    out = out.fillna("未知品牌")
    return out


def quality_flags_series(
    df: pd.DataFrame, outlier_quantile: float = 0.99
) -> pd.Series:
    missing_price = df["price"].isna()
    missing_title = df["title"].fillna("").astype(str).str.strip().eq("")
    price_outlier = pd.Series(False, index=df.index)
    priced = df["price"].dropna()
    if len(priced) >= 20:
        thr = float(priced.quantile(outlier_quantile))
        price_outlier = df["price"].notna() & (df["price"] > thr)

    a = pd.Series(np.where(missing_price, "missing_price", ""), index=df.index)
    b = pd.Series(np.where(missing_title, "missing_title", ""), index=df.index)
    c = pd.Series(np.where(price_outlier, "price_outlier", ""), index=df.index)
    joined = (a + "|" + b + "|" + c).str.replace(r"\|+", "|", regex=True).str.strip("|")
    return joined


def enrich(
    df: pd.DataFrame,
    bands: list[list[Any]],
    *,
    brands: list[str] | None = None,
    brand_aliases: dict[str, str] | None = None,
    outlier_quantile: float = 0.99,
) -> pd.DataFrame:
    out = df.copy()
    if "title" not in out.columns:
        out["title"] = ""
    if "source_query" not in out.columns:
        out["source_query"] = ""
    if "shop_name" not in out.columns:
        out["shop_name"] = ""
    if "brand" not in out.columns:
        out["brand"] = ""

    patterns = build_brand_patterns(brands or [], brand_aliases or {})
    out["brand"] = normalize_brand_series(out["brand"], out["title"], patterns)
    out["category_guess"] = guess_category_series(out["title"])
    out["price_band"] = assign_price_band_series(out["price"], bands)
    out["sport_scene"] = guess_sport_scene_series(out["title"], out["source_query"])
    out["gender_guess"] = guess_gender_series(out["title"])
    out["is_self_operated"] = (
        out["shop_name"].fillna("").astype(str).str.contains("自营", na=False)
    )
    out["quality_flags"] = quality_flags_series(out, outlier_quantile=outlier_quantile)
    return out


# Backward-compatible helpers used by older call sites / tests
def guess_category(title: str) -> str:
    return guess_category_series(pd.Series([title])).iloc[0]


def assign_price_band(price: float | None, bands: list[list[Any]]) -> str:
    return assign_price_band_series(pd.Series([price]), bands).iloc[0]
