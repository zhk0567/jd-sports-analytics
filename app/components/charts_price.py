"""Price insight charts."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from app.theme import PALETTE, apply_plotly, section_header
from src.analysis import metrics as M


def render(df) -> None:
    section_header("价格洞察", "价格带结构、品牌定价带与规模关系。")
    p1, p2 = st.columns(2)

    priced = df.dropna(subset=["price"])
    with p1:
        if priced.empty:
            st.info("无价格数据")
        else:
            # Cap extreme outliers for readability in hist
            cap = float(priced["price"].quantile(0.98))
            hist_df = priced[priced["price"] <= max(cap, 1)]
            fig = px.histogram(
                hist_df,
                x="price",
                nbins=40,
                color_discrete_sequence=[PALETTE[0]],
                labels={"price": "价格 (元)", "count": "商品数"},
            )
            apply_plotly(fig, height=360)
            fig.update_layout(title="价格分布（截尾 98%）")
            st.plotly_chart(fig, width="stretch")

    with p2:
        pb = M.price_band_counts(df)
        if pb.empty:
            st.info("无分档数据")
        else:
            fig = px.bar(
                pb,
                x="price_band",
                y="count",
                color_discrete_sequence=[PALETTE[1]],
                labels={"price_band": "价格分档", "count": "商品数"},
            )
            apply_plotly(fig, height=360)
            fig.update_layout(title="价格分档占比")
            st.plotly_chart(fig, width="stretch")

    if not priced.empty and priced["brand"].nunique() > 0:
        top_brands = priced["brand"].value_counts().head(10).index.tolist()
        box_df = priced[priced["brand"].isin(top_brands)]
        fig = px.box(
            box_df,
            x="brand",
            y="price",
            color_discrete_sequence=[PALETTE[0]],
            labels={"brand": "品牌", "price": "价格 (元)"},
        )
        apply_plotly(fig, height=400)
        fig.update_layout(title="主要品牌价格分布")
        st.plotly_chart(fig, width="stretch")

    scatter = M.brand_price_scatter(df, top_n=18)
    if not scatter.empty:
        fig = px.scatter(
            scatter,
            x="price_mean",
            y="count",
            size="comment_sum",
            color="brand",
            color_discrete_sequence=PALETTE,
            labels={
                "price_mean": "品牌均价 (元)",
                "count": "商品数",
                "comment_sum": "评论量",
                "brand": "品牌",
            },
            size_max=48,
        )
        apply_plotly(fig, height=420)
        fig.update_layout(title="品牌均价 × 商品规模（气泡=评论量）", showlegend=False)
        st.plotly_chart(fig, width="stretch")
