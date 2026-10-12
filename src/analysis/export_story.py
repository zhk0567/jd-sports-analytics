"""Export lightweight story.json for the web narrative page."""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.analysis import metrics as M
from src.analysis.metrics import CATEGORY_LABELS
from src.utils import ROOT, load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("export_story")


def _records(df: pd.DataFrame) -> list[dict]:
    if df is None or df.empty:
        return []
    out = df.copy().where(pd.notna(df), None)
    rows = out.to_dict(orient="records")
    cleaned = []
    for row in rows:
        item = {}
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                item[k] = None
            elif hasattr(v, "item"):
                try:
                    item[k] = v.item()
                except Exception:
                    item[k] = v
            else:
                item[k] = v
        cleaned.append(item)
    return cleaned


def _pct(part: float, whole: float) -> float:
    if not whole:
        return 0.0
    return round(100.0 * part / whole, 1)


def _thesis_and_insights(df: pd.DataFrame, ov: dict, extras: dict) -> tuple[dict, dict]:
    n = max(ov["product_count"], 1)
    cats = M.category_counts(df)
    top_cat = "运动商品"
    top_share = 0.0
    if not cats.empty:
        top_cat = CATEGORY_LABELS.get(cats.iloc[0]["category_guess"], cats.iloc[0]["category_guess"])
        top_share = _pct(float(cats.iloc[0]["count"]), n)

    brands = M.brand_counts(df)
    brands = brands[brands["brand"] != "未知品牌"] if not brands.empty else brands
    top_brand = brands.iloc[0]["brand"] if not brands.empty else "运动品牌"
    top_brand_n = int(brands.iloc[0]["count"]) if not brands.empty else 0

    scenes = M.scene_counts(df)
    scenes = scenes[scenes["sport_scene"] != "其他"] if not scenes.empty else scenes
    top_scene = scenes.iloc[0]["sport_scene"] if not scenes.empty else "跑步"
    top_scene_share = _pct(float(scenes.iloc[0]["count"]), n) if not scenes.empty else 0

    genders = M.gender_counts(df)
    male = 0.0
    female = 0.0
    if not genders.empty:
        gmap = {r["gender_guess"]: r["count"] for _, r in genders.iterrows()}
        male = _pct(float(gmap.get("男", 0)), n)
        female = _pct(float(gmap.get("女", 0)), n)

    med = ov.get("price_median")
    mean = ov.get("price_mean")
    med_s = f"¥{med:.0f}" if med is not None else "—"
    mean_s = f"¥{mean:.0f}" if mean is not None else "—"
    self_s = f"{(ov.get('self_operated_rate') or 0) * 100:.0f}%"

    thesis = {
        "open": f"京东运动货架上，{top_cat}约占 {top_share:.0f}%，中位价落在 {med_s}。",
        "scale": "体量先定坐标系：品类切分决定后面所有比较的权重。",
        "brands": f"品牌争夺可见度时，{top_brand}等名字反复出现在列表页。",
        "price": "贵与多并不等同——均价被高端尾部拉高，中位价更能代表日常成交带。",
        "scene": f"场景需求清晰：{top_scene}等场景切开鞋服与装备的不同组合。",
        "shelf": "最后落到具体 SKU：价格、品牌、场景与店铺同时可见。",
        "close": "运动消费不是一张平面饼图，而是价格、品牌与场景叠出的层次。",
    }

    insights = {
        "open": [
            f"样本共 {n:,} 个 SKU，覆盖约 {ov['brand_count']} 个品牌、{ov['shop_count']} 家店铺。",
            f"自营占比约 {self_s}，评论总量约 {ov['comment_sum']:,}。",
            f"中位价 {med_s}，均价 {mean_s}——均值明显高于中位，说明存在高价尾部。",
            f"头部品类「{top_cat}」约占 {top_share:.0f}%，构成货架主视觉。",
            f"价格跨度：P25 {extras['price_p25']} → P90 {extras['price_p90']}，日常带与溢价带并存。",
        ],
        "scale": [
            f"品类结构中，{top_cat}领先（约 {top_share:.0f}%）。",
            f"已知品牌识别率约 {extras['known_brand_rate']:.0f}%，其余多为长尾/标题未命中品牌。",
            f"价格四分位：P25 {extras['price_p25']} · P50 {extras['price_p50']} · P75 {extras['price_p75']} · P90 {extras['price_p90']}。",
            f"性别倾向：男约 {male:.0f}% / 女约 {female:.0f}%（含中性与未知）。",
            "Treemap 面积 = 话语权：后续品牌/价格比较都以此为底图权重。",
        ],
        "brands": [
            f"去未知品牌后，{top_brand}以 {top_brand_n} 个 SKU 居首。",
            f"Top5 已知品牌合计约占已知品牌货架的 {extras['top5_known_share']:.0f}%。",
            "上架密度高 ≠ 均价高：规模品牌与溢价品牌往往落在不同象限。",
            "店铺侧头部集中：Top 店铺贡献显著可见度（见右侧榜单）。",
            "品牌×品类热力图：可看出谁在鞋服/装备上押注更深。",
        ],
        "price": [
            "主流成交带集中在 60–200 与 200–400 元附近。",
            f"均价 {mean_s} 高于中位 {med_s}，高端带拉高了算术平均。",
            f"≥900 元价位约占 {extras['premium_share']:.0f}%，数量少但塑造“贵”的感知。",
            f"四分位跨度 {extras['price_p25']}–{extras['price_p75']}，日常成交落在这一带。",
            "气泡图横轴均价、纵轴上架数：可同时读出规模与定价姿态。",
        ],
        "scene": [
            f"场景「{top_scene}」约占 {top_scene_share:.0f}%（不含“其他”时更高）。",
            "跑步偏鞋类、健身偏装备——流向比口号更接近真实需求。",
            f"性别结构仍以男性倾向更高（约 {male:.0f}%），女性约 {female:.0f}%。",
            "场景×品类矩阵可用来找“缺货/过密”的交叉格子。",
            "场景标签是需求侧切面：同一品类在不同场景下密度差很大。",
        ],
        "shelf": [
            "货架特写优先展示有图、已知品牌、运动品类的样本。",
            "点进商品可回看京东详情页，适合做竞品与定价对照。",
            f"当前导出 {extras['shelf_n']} 个代表 SKU，覆盖多品牌与多价位。",
            "右侧列表补充更多 SKU：品牌、场景、店铺可对照阅读。",
            "收束：把体量、品牌、价格、场景压回一件具体商品。",
        ],
    }
    return thesis, insights


def build_story(df: pd.DataFrame) -> dict:
    ov = M.overview(df)
    n = max(int(ov["product_count"]), 1)
    priced = df["price"].dropna() if "price" in df.columns else pd.Series(dtype=float)

    cats = M.category_counts(df)
    if not cats.empty:
        cats = cats.copy()
        cats["label"] = cats["category_guess"].map(lambda x: CATEGORY_LABELS.get(x, x))
        cats["share"] = (cats["count"] / n * 100).round(1)

    known = df[df["brand"].fillna("") != "未知品牌"] if "brand" in df.columns else df
    known_brand_rate = _pct(len(known), n)

    brand_stats = (
        known.groupby("brand", as_index=False)
        .agg(
            count=("sku_id", "count"),
            price_mean=("price", "mean"),
            price_median=("price", "median"),
            comment_sum=("comment_count", "sum"),
        )
        .sort_values("count", ascending=False)
        .head(15)
    )
    brand_stats["price_mean"] = brand_stats["price_mean"].round(1)
    brand_stats["price_median"] = brand_stats["price_median"].round(1)

    top5 = brand_stats.head(5)["count"].sum()
    top5_known_share = _pct(float(top5), max(len(known), 1))

    bands = M.price_band_counts(df)
    premium = 0
    if not bands.empty:
        premium = int(
            bands[
                bands["price_band"].astype(str).str.contains("900|4000", regex=True)
            ]["count"].sum()
        )

    def q(p: float) -> str:
        if priced.empty:
            return "—"
        return f"¥{priced.quantile(p):.0f}"

    extras = {
        "known_brand_rate": known_brand_rate,
        "top5_known_share": top5_known_share,
        "premium_share": _pct(premium, n),
        "price_p25": q(0.25),
        "price_p50": q(0.5),
        "price_p75": q(0.75),
        "price_p90": q(0.9),
        "shelf_n": 48,
    }

    scene_cat = pd.DataFrame()
    if "sport_scene" in df.columns and not df.empty:
        work = df.copy()
        work["sport_scene"] = work["sport_scene"].fillna("其他")
        work["category_label"] = work["category_guess"].map(
            lambda x: CATEGORY_LABELS.get(x, x)
        )
        scene_cat = (
            work.groupby(["sport_scene", "category_label"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )

    thesis, insights = _thesis_and_insights(df, ov, extras)

    shelf_cols = [
        c
        for c in [
            "sku_id",
            "title",
            "brand",
            "price",
            "category_guess",
            "sport_scene",
            "gender_guess",
            "image_url",
            "product_url",
            "shop_name",
            "comment_count",
        ]
        if c in df.columns
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "jd-sports-analytics",
        "thesis": thesis,
        "insights": insights,
        "overview": {
            **ov,
            "known_brand_rate": known_brand_rate / 100.0,
            "price_p25": float(priced.quantile(0.25)) if not priced.empty else None,
            "price_p75": float(priced.quantile(0.75)) if not priced.empty else None,
            "price_p90": float(priced.quantile(0.9)) if not priced.empty else None,
            "premium_share": extras["premium_share"] / 100.0,
        },
        "by_brand": _records(brand_stats),
        "by_category": _records(cats),
        "by_price_band": _records(bands),
        "by_scene": _records(M.scene_counts(df)),
        "by_gender": _records(M.gender_counts(df)),
        "brand_category": _records(M.brand_category_matrix(df, top_brands=12)),
        "brand_price_scatter": _records(M.brand_price_scatter(df, top_n=18)),
        "scene_category": _records(scene_cat),
        "top_shops": _records(
            M.top_shops(df, n=15, by="products").rename(columns={"value": "count"})
        ),
        "shelf_products": _records(M.top_products(df, n=48)[shelf_cols]),
    }


def export_story(out_path: Path | None = None) -> Path:
    cfg = load_config()
    processed = ROOT / cfg["paths"]["processed_dir"] / "products.parquet"
    if not processed.exists():
        csv = ROOT / cfg["paths"]["processed_dir"] / "products.csv"
        if not csv.exists():
            raise FileNotFoundError("No processed products.parquet/csv; run clean first.")
        df = pd.read_csv(csv)
    else:
        df = pd.read_parquet(processed)

    story = build_story(df)
    target = out_path or (ROOT / "web" / "public" / "data" / "story.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Wrote %s (products=%s)", target, story["overview"].get("product_count"))
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export story.json for web narrative.")
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args(argv)
    try:
        export_story(Path(args.out) if args.out else None)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
