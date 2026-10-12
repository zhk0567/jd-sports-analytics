"""Incremental processor: watch growing JSONL while crawl runs."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.processing.clean import clean_frame, merge_by_sku, persist_processed
from src.utils import ROOT, ensure_dirs, load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("watch")


def _checkpoint_path(cfg: dict) -> Path:
    processed = ROOT / cfg["paths"]["processed_dir"]
    name = (cfg.get("processing") or {}).get("checkpoint_file", "_checkpoint.json")
    return processed / name


def load_checkpoint(cfg: dict) -> dict:
    path = _checkpoint_path(cfg)
    if not path.exists():
        return {"file": None, "line_offset": 0, "rounds": 0, "updated_at": None}
    return json.loads(path.read_text(encoding="utf-8"))


def save_checkpoint(cfg: dict, data: dict) -> None:
    path = _checkpoint_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def latest_raw_file(raw_dir: Path) -> Path | None:
    files = sorted(raw_dir.glob("products_*.jsonl"))
    return files[-1] if files else None


def read_new_lines(path: Path, line_offset: int) -> tuple[list[dict], int]:
    rows: list[dict] = []
    total = 0
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            total = i + 1
            if i < line_offset:
                continue
            text = line.strip()
            if not text:
                continue
            rows.append(json.loads(text))
    return rows, total


def load_existing_products(processed_dir: Path) -> pd.DataFrame:
    parquet = processed_dir / "products.parquet"
    if parquet.exists():
        return pd.read_parquet(parquet)
    return pd.DataFrame()


def crawl_is_running(raw_dir: Path) -> bool:
    meta = raw_dir / "_meta.json"
    if not meta.exists():
        return False
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return True
    return data.get("status") == "running"


def process_once(cfg: dict, *, write_csv: bool) -> tuple[int, int]:
    """Returns (new_raw_rows, total_unique)."""
    ensure_dirs(cfg)
    raw_dir = ROOT / cfg["paths"]["raw_dir"]
    processed_dir = ROOT / cfg["paths"]["processed_dir"]
    proc_cfg = cfg.get("processing") or {}

    raw_file = latest_raw_file(raw_dir)
    if raw_file is None:
        logger.warning("No products_*.jsonl yet")
        return 0, 0

    ckpt = load_checkpoint(cfg)
    if ckpt.get("file") != raw_file.name:
        # switched to a new batch file
        ckpt = {"file": raw_file.name, "line_offset": 0, "rounds": ckpt.get("rounds", 0)}

    rows, new_offset = read_new_lines(raw_file, int(ckpt.get("line_offset") or 0))
    if not rows:
        existing = load_existing_products(processed_dir)
        logger.info(
            "No new lines (file=%s offset=%s unique=%d)",
            raw_file.name,
            ckpt.get("line_offset"),
            len(existing),
        )
        ckpt["file"] = raw_file.name
        ckpt["line_offset"] = new_offset
        save_checkpoint(cfg, ckpt)
        return 0, len(existing)

    logger.info("Read %d new lines from %s", len(rows), raw_file.name)
    bands = cfg.get("price_bands", [])
    incoming = clean_frame(
        pd.DataFrame(rows),
        bands,
        brands=list(cfg.get("brands") or []),
        brand_aliases=dict(cfg.get("brand_aliases") or {}),
        outlier_quantile=float(proc_cfg.get("outlier_quantile", 0.99)),
        dedupe=True,
    )
    existing = load_existing_products(processed_dir)
    merged = merge_by_sku(existing, incoming)
    persist_processed(merged, write_csv=write_csv)

    ckpt["file"] = raw_file.name
    ckpt["line_offset"] = new_offset
    ckpt["rounds"] = int(ckpt.get("rounds") or 0) + 1
    save_checkpoint(cfg, ckpt)
    logger.info(
        "Merged unique=%d (+incoming_unique=%d raw_new=%d)",
        len(merged),
        len(incoming),
        len(rows),
    )
    return len(rows), len(merged)


def finalize_full(cfg: dict) -> None:
    """Full consolidate from latest JSONL (rebuild parquet)."""
    from src.processing.clean import run as clean_run

    logger.info("Final consolidate from latest JSONL...")
    clean_run(raw_glob_latest_only=True, write_csv=True)
    # sync checkpoint to EOF
    raw_dir = ROOT / cfg["paths"]["raw_dir"]
    raw_file = latest_raw_file(raw_dir)
    if raw_file:
        with raw_file.open("r", encoding="utf-8") as f:
            n = sum(1 for _ in f)
        save_checkpoint(
            cfg,
            {
                "file": raw_file.name,
                "line_offset": n,
                "rounds": 0,
                "finalized": True,
            },
        )


def run_watch(
    *,
    once: bool = False,
    until_idle: bool = False,
) -> int:
    cfg = load_config()
    ensure_dirs(cfg)
    proc_cfg = cfg.get("processing") or {}
    poll_sec = float(proc_cfg.get("poll_sec", 30))
    csv_every_n = int(proc_cfg.get("csv_every_n", 5))
    idle_needed = int(proc_cfg.get("idle_rounds_to_exit", 2))

    round_i = 0
    idle_streak = 0

    while True:
        round_i += 1
        write_csv = (round_i % csv_every_n == 0) or once
        new_rows, unique = process_once(cfg, write_csv=write_csv)

        if once:
            return 0

        if new_rows == 0:
            idle_streak += 1
        else:
            idle_streak = 0

        running = crawl_is_running(ROOT / cfg["paths"]["raw_dir"])
        if until_idle and (not running) and idle_streak >= idle_needed:
            finalize_full(cfg)
            logger.info("Crawl idle; finalized. unique≈%d", unique)
            return 0

        logger.info(
            "Sleep %ss (crawl_running=%s idle_streak=%d unique=%d)",
            poll_sec,
            running,
            idle_streak,
            unique,
        )
        time.sleep(poll_sec)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Incrementally process growing JD sports JSONL."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process new lines once and exit.",
    )
    parser.add_argument(
        "--until-idle",
        action="store_true",
        help="Keep polling until crawl meta is not running and no new lines, then finalize.",
    )
    args = parser.parse_args(argv)
    try:
        return run_watch(once=args.once, until_idle=args.until_idle)
    except KeyboardInterrupt:
        logger.info("Interrupted")
        return 0


if __name__ == "__main__":
    sys.exit(main())
