"""Trackside visual theme for jd-sports-analytics Streamlit app."""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
CSS_PATH = APP_DIR / "assets" / "theme.css"

COLORS = {
    "ink": "#14171C",
    "ink_soft": "#4A5160",
    "accent": "#E0352D",
    "green": "#2F6B4F",
    "mist": "#7A8FA6",
    "slate": "#2C3340",
    "bg": "#F4F6F8",
    "paper": "#FFFFFF",
}

PALETTE = [
    COLORS["accent"],
    COLORS["slate"],
    COLORS["mist"],
    COLORS["green"],
    "#C47B3A",
    "#5C6B7A",
]


def inject_css() -> None:
    css = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def section_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="jsa-section"><h2>{title}</h2><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def apply_plotly(fig: go.Figure, *, height: int = 380) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=36, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Noto Sans SC, Segoe UI, sans-serif",
            color=COLORS["ink"],
            size=12,
        ),
        title=dict(
            font=dict(family="Syne, Noto Sans SC, sans-serif", size=15, color=COLORS["ink"]),
            x=0,
            xanchor="left",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
        ),
        colorway=PALETTE,
        transition=dict(duration=350, easing="cubic-in-out"),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Noto Sans SC"),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(20,23,28,0.08)",
        zeroline=False,
        linecolor="rgba(20,23,28,0.18)",
        tickfont=dict(color=COLORS["ink_soft"]),
        title_font=dict(color=COLORS["ink_soft"]),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(20,23,28,0.08)",
        zeroline=False,
        linecolor="rgba(20,23,28,0.18)",
        tickfont=dict(color=COLORS["ink_soft"]),
        title_font=dict(color=COLORS["ink_soft"]),
    )
    return fig


def sequential_scale() -> list[list]:
    return [
        [0.0, "#F4F6F8"],
        [0.35, "#C8D2DC"],
        [0.65, "#7A8FA6"],
        [1.0, COLORS["accent"]],
    ]
