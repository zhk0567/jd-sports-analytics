"""Shared helpers for jd-sports-analytics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or (ROOT / "config.yaml")
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dirs(cfg: dict[str, Any]) -> None:
    paths = cfg["paths"]
    for key in ("raw_dir", "processed_dir", "log_dir"):
        (ROOT / paths[key]).mkdir(parents=True, exist_ok=True)
    proc = cfg.get("processing") or {}
    agg = proc.get("aggregates_dir", "aggregates")
    (ROOT / paths["processed_dir"] / agg).mkdir(parents=True, exist_ok=True)
