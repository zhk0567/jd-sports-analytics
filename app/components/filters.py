"""Sidebar filters."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis.metrics import CATEGORY_LABELS


def render(df: pd.DataFrame) -> dict:
    st.sidebar.markdown("### Filter")
    st.sidebar.caption("筛选会联动下方全部图表与商品浏览")

    brands = sorted(df["brand"].dropna().unique().tolist())
    cats = sorted(df["category_guess"].dropna().unique().tolist())
    scenes = (
        sorted(df["sport_scene"].fillna("其他").unique().tolist())
        if "sport_scene" in df.columns
        else []
    )
    genders = (
        sorted(df["gender_guess"].fillna("未知").unique().tolist())
        if "gender_guess" in df.columns
        else []
    )

    # Empty selection = all (keeps sidebar clean)
    sel_brands = st.sidebar.multiselect("品牌", brands, default=[], placeholder="全部品牌")
    sel_cats = st.sidebar.multiselect(
        "品类",
        cats,
        default=[],
        format_func=lambda c: CATEGORY_LABELS.get(c, c),
        placeholder="全部品类",
    )
    sel_scenes = (
        st.sidebar.multiselect("运动场景", scenes, default=[], placeholder="全部场景")
        if scenes
        else []
    )
    sel_genders = (
        st.sidebar.multiselect("性别倾向", genders, default=[], placeholder="全部性别")
        if genders
        else []
    )

    pmin = float(df["price"].min()) if df["price"].notna().any() else 0.0
    pmax = float(df["price"].max()) if df["price"].notna().any() else 1000.0
    if pmax <= pmin:
        pmax = pmin + 1.0
    price_range = st.sidebar.slider(
        "价格区间 (元)",
        min_value=float(max(0.0, pmin)),
        max_value=float(pmax),
        value=(float(max(0.0, pmin)), float(pmax)),
    )
    self_only = st.sidebar.toggle("仅看京东自营", value=False)

    return {
        "brands": sel_brands,
        "categories": sel_cats,
        "scenes": sel_scenes,
        "genders": sel_genders,
        "price_min": price_range[0],
        "price_max": price_range[1],
        "self_operated_only": self_only,
    }
