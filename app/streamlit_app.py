"""jd-sports-analytics — Trackside designed Streamlit dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.components import catalog, charts_audience, charts_price, charts_structure
from app.components import filters as filter_bar
from app.components import hero, kpis
from app.theme import inject_css
from src.analysis import metrics as M

REQUIRED_HINT_COLS = ("sport_scene", "gender_guess", "is_self_operated")


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    parquet = ROOT / "data" / "processed" / "products.parquet"
    csv = ROOT / "data" / "processed" / "products.csv"
    if parquet.exists():
        return pd.read_parquet(parquet)
    if csv.exists():
        return pd.read_csv(csv)
    return pd.DataFrame()


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "sport_scene" in out.columns:
        out["sport_scene"] = out["sport_scene"].fillna("其他")
    if "gender_guess" in out.columns:
        out["gender_guess"] = out["gender_guess"].fillna("未知")
    if "is_self_operated" in out.columns:
        out["is_self_operated"] = out["is_self_operated"].fillna(False).astype(bool)
    if "image_url" not in out.columns:
        out["image_url"] = ""
    return out


def main() -> None:
    st.set_page_config(
        page_title="jd-sports-analytics",
        page_icon="◾",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()

    df = load_data()
    if df.empty:
        st.markdown(
            '<div class="jsa-hero"><p class="jsa-brand">jd-sports<span>-analytics</span></p>'
            "<p class=\"jsa-insight\">尚未找到处理后的数据。</p></div>",
            unsafe_allow_html=True,
        )
        st.warning(
            "请先在项目根目录执行：\n\n"
            "`python -m src.crawler.run_crawl`\n\n"
            "`python -m src.processing.clean --latest-only`"
        )
        return

    missing = [c for c in REQUIRED_HINT_COLS if c not in df.columns]
    if missing:
        st.info(
            "数据缺少部分 enrichment 字段（"
            + ", ".join(missing)
            + "）。建议执行：`python -m src.processing.clean --latest-only` 后刷新页面。"
        )

    df = _normalize(df)
    filt = filter_bar.render(df)
    view = M.filter_df(
        df,
        brands=filt["brands"] or None,
        categories=filt["categories"] or None,
        scenes=filt["scenes"] or None,
        genders=filt["genders"] or None,
        price_min=filt["price_min"],
        price_max=filt["price_max"],
        self_operated_only=filt["self_operated_only"],
    )

    hero.render(view)
    st.sidebar.markdown(f"**当前结果** {len(view):,} / {len(df):,}")
    kpis.render(view)

    if view.empty:
        st.warning("当前筛选无结果，请放宽条件。")
        return

    charts_structure.render(view)
    charts_price.render(view)
    charts_audience.render(view)
    catalog.render(view)


if __name__ == "__main__":
    main()
