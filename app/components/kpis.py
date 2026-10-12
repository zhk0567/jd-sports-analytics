"""KPI strip."""

from __future__ import annotations

import streamlit as st

from src.analysis import metrics as M


def render(df) -> None:
    ov = M.overview(df)
    mean = f"¥{ov['price_mean']:.0f}" if ov["price_mean"] is not None else "—"
    med = f"¥{ov['price_median']:.0f}" if ov["price_median"] is not None else "—"
    self_rate = (
        f"{ov['self_operated_rate'] * 100:.0f}%"
        if ov.get("self_operated_rate") is not None
        else "—"
    )
    items = [
        ("商品数", f"{ov['product_count']:,}", "accent"),
        ("品牌数", f"{ov['brand_count']:,}", ""),
        ("中位价", med, ""),
        ("均价", mean, ""),
        ("评论总量", f"{ov['comment_sum']:,}", ""),
        ("自营占比", self_rate, "green"),
    ]
    cells = "".join(
        f'<div class="jsa-kpi"><div class="label">{lab}</div>'
        f'<div class="value {cls}">{val}</div></div>'
        for lab, val, cls in items
    )
    st.markdown(f'<div class="jsa-kpi-row">{cells}</div>', unsafe_allow_html=True)
