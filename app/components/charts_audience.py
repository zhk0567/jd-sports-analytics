"""Scene and audience charts."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from app.theme import PALETTE, apply_plotly, section_header, sequential_scale
from src.analysis import metrics as M


def render(df) -> None:
    section_header("场景与人群", "运动场景与性别倾向如何切分货架。")

    if "sport_scene" not in df.columns and "gender_guess" not in df.columns:
        st.warning(
            "当前数据缺少场景/性别字段。请先执行：`python -m src.processing.clean --latest-only`"
        )
        return

    c1, c2 = st.columns(2)
    with c1:
        sc = M.scene_counts(df)
        if sc.empty:
            st.info("无场景数据")
        else:
            fig = px.bar(
                sc.sort_values("count"),
                x="count",
                y="sport_scene",
                orientation="h",
                color_discrete_sequence=[PALETTE[3]],
                labels={"count": "商品数", "sport_scene": ""},
            )
            apply_plotly(fig, height=380)
            fig.update_layout(title="运动场景分布")
            st.plotly_chart(fig, width="stretch")

    with c2:
        gc = M.gender_counts(df)
        if gc.empty:
            st.info("无性别数据")
        else:
            fig = px.pie(
                gc,
                names="gender_guess",
                values="count",
                hole=0.42,
                color_discrete_sequence=PALETTE,
            )
            apply_plotly(fig, height=380)
            fig.update_layout(title="性别倾向")
            st.plotly_chart(fig, width="stretch")

    mat = M.scene_price_band_matrix(df)
    if mat.empty:
        return
    pivot = mat.pivot(index="sport_scene", columns="price_band", values="count").fillna(0)
    # keep band order
    order = ["0-60", "60-200", "200-400", "400-900", "900-4000", "4000+", "unknown"]
    cols = [c for c in order if c in pivot.columns] + [
        c for c in pivot.columns if c not in order
    ]
    pivot = pivot[cols]
    fig = px.imshow(
        pivot,
        color_continuous_scale=sequential_scale(),
        aspect="auto",
        labels=dict(x="价格分档", y="场景", color="商品数"),
    )
    apply_plotly(fig, height=380)
    fig.update_layout(title="场景 × 价格带")
    st.plotly_chart(fig, width="stretch")
