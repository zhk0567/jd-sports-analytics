"""Market structure charts."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from app.theme import PALETTE, apply_plotly, section_header, sequential_scale
from src.analysis import metrics as M
from src.analysis.metrics import CATEGORY_LABELS


def render(df) -> None:
    section_header("结构 · 市场", "看品牌与品类如何瓜分当前样本货架。")
    left, right = st.columns(2)

    with left:
        bc = M.brand_counts(df, n=15)
        if bc.empty:
            st.info("无品牌数据")
        else:
            fig = px.bar(
                bc.sort_values("count"),
                x="count",
                y="brand",
                orientation="h",
                color_discrete_sequence=[PALETTE[0]],
                labels={"count": "商品数", "brand": ""},
            )
            fig.update_traces(marker_line_width=0)
            apply_plotly(fig, height=420)
            st.plotly_chart(fig, width="stretch")

    with right:
        cc = M.category_counts(df)
        if cc.empty:
            st.info("无品类数据")
        else:
            cc = cc.copy()
            cc["label"] = cc["category_guess"].map(lambda x: CATEGORY_LABELS.get(x, x))
            fig = px.treemap(
                cc,
                path=["label"],
                values="count",
                color="count",
                color_continuous_scale=sequential_scale(),
            )
            fig.update_traces(
                textinfo="label+percent root",
                marker=dict(cornerradius=2),
            )
            apply_plotly(fig, height=420)
            fig.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, width="stretch")

    mat = M.brand_category_matrix(df, top_brands=12)
    if mat.empty:
        return
    pivot = mat.pivot(index="brand", columns="category_label", values="count").fillna(0)
    fig = px.imshow(
        pivot,
        color_continuous_scale=sequential_scale(),
        aspect="auto",
        labels=dict(x="品类", y="品牌", color="商品数"),
    )
    apply_plotly(fig, height=380)
    fig.update_layout(title="品牌 × 品类 热力")
    st.plotly_chart(fig, width="stretch")
