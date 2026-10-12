"""Shops and product catalog."""

from __future__ import annotations

import html

import pandas as pd
import plotly.express as px
import streamlit as st

from app.theme import PALETTE, apply_plotly, section_header
from src.analysis import metrics as M
from src.analysis.metrics import CATEGORY_LABELS


def _product_cards_html(df: pd.DataFrame) -> str:
    cards = []
    for _, row in df.iterrows():
        title = html.escape(str(row.get("title") or ""))
        brand = html.escape(str(row.get("brand") or ""))
        price = row.get("price")
        price_s = f"¥{float(price):.0f}" if pd.notna(price) else "—"
        url = str(row.get("product_url") or "#")
        img = str(row.get("image_url") or "").strip()
        if img:
            thumb = f'<div class="thumb" style="background-image:url(\'{html.escape(img, quote=True)}\')"></div>'
        else:
            thumb = '<div class="thumb empty">NO IMAGE</div>'
        cards.append(
            f'<a class="jsa-card" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">'
            f"{thumb}"
            f'<div class="body"><div class="brand">{brand}</div>'
            f'<div class="title">{title}</div>'
            f'<div class="price">{price_s}</div></div></a>'
        )
    return f'<div class="jsa-grid">{"".join(cards)}</div>'


def render(df: pd.DataFrame) -> None:
    section_header("店铺与商品", "热门店铺与可视化货架浏览；可下载当前筛选明细。")

    by = st.radio(
        "店铺排序",
        ["products", "comments"],
        horizontal=True,
        format_func=lambda x: "按商品数" if x == "products" else "按评论量",
    )
    shops = M.top_shops(df, n=15, by=by)
    if shops.empty:
        st.info("无店铺数据")
    else:
        fig = px.bar(
            shops.sort_values("value"),
            x="value",
            y="shop_name",
            orientation="h",
            color_discrete_sequence=[PALETTE[1]],
            labels={"shop_name": "", "value": "数值"},
        )
        apply_plotly(fig, height=430)
        st.plotly_chart(fig, width="stretch")

    products = M.top_products(df, n=12)
    if products.empty:
        st.info("无商品可展示")
    else:
        st.markdown("##### 货架浏览")
        st.markdown(_product_cards_html(products), unsafe_allow_html=True)

    show_cols = [
        c
        for c in [
            "sku_id",
            "title",
            "brand",
            "price",
            "price_band",
            "category_guess",
            "sport_scene",
            "gender_guess",
            "is_self_operated",
            "shop_name",
            "comment_count",
            "product_url",
        ]
        if c in df.columns
    ]
    table = df[show_cols].copy()
    if "category_guess" in table.columns:
        table["category_guess"] = table["category_guess"].map(
            lambda x: CATEGORY_LABELS.get(x, x)
        )
    st.dataframe(table, width="stretch", height=360)
    csv_bytes = table.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "下载当前筛选结果 CSV",
        data=csv_bytes,
        file_name="jd_sports_filtered.csv",
        mime="text/csv",
        type="primary",
    )
