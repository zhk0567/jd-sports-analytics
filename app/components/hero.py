"""Hero brand block."""

from __future__ import annotations

import streamlit as st

from src.analysis import metrics as M


def render(df) -> None:
    insight = M.insight_line(df)
    st.markdown(
        f"""
        <div class="jsa-hero">
          <p class="jsa-brand">jd-sports<span>-analytics</span></p>
          <p class="jsa-insight">{insight}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
