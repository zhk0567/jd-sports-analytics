"""Clean raw JSONL batches and write processed parquet/csv + summary."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

from src.analysis.build_aggregates import (
    build_aggregates,
    build_quality_report,
    write_summary,
)
from src.processing.enrich import enrich, normalize_numeric
from src.utils import ROOT, ensure_dirs, load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("clean")


def load_raw_jsonl(raw_dir: Path) -> pd.DataFrame:
    files = sorted(raw_dir.glob("products_*.jsonl"))
    if not files:
        raise FileNotFoundError(f"No products_*.jsonl under {raw_dir}")
    frames: list[pd.DataFrame] = []
    for fp in files:
        rows = []
        with fp.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        if rows:
            df = pd.DataFrame(rows)
            df["_source_file"] = fp.name
            frames.append(df)
            logger.info("Loaded %s (%d rows)", fp.name, len(df))
    if not frames:
        raise ValueError("Raw JSONL files contain no rows")
    return pd.concat(frames, ignore_index=True)


def load_jsonl_rows(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def row_richness_score(df: pd.DataFrame) -> pd.Series:
    title = df["title"].fillna("").astype(str) if "title" in df else ""
    shop = df["shop_name"].fillna("").astype(str) if "shop_name" in df else ""
    return (
        title.ne("").astype(int) * 4
        + df["price"].notna().astype(int) * 3
        + shop.ne("").astype(int) * 2
        + df["comment_count"].notna().astype(int)
    )


def clean_frame(
    df: pd.DataFrame,
    bands: list,
    *,
    brands: list[str] | None = None,
    brand_aliases: dict | None = None,
    outlier_quantile: float = 0.99,
    dedupe: bool = True,
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    out = df.copy()
    out["sku_id"] = out["sku_id"].astype(str).str.strip()
    out = out[out["sku_id"].ne("") & out["sku_id"].ne("None") & out["sku_id"].ne("nan")]

    out["price"] = normalize_numeric(out.get("price", pd.Series(dtype=float)))
    out["original_price"] = normalize_numeric(
        out.get("original_price", pd.Series(dtype=float))
    )
    out["comment_count"] = normalize_numeric(
        out.get("comment_count", pd.Series(dtype=float))
    )
    out["comment_count"] = out["comment_count"].round().astype("Int64")

    out["title"] = out.get("title", pd.Series([""] * len(out))).fillna("").astype(str).str.strip()
    out["shop_name"] = (
        out.get("shop_name", pd.Series([""] * len(out))).fillna("").astype(str).str.strip()
    )
    if "brand" not in out.columns:
        out["brand"] = ""
    if "source_query" not in out.columns:
        out["source_query"] = ""

    out = enrich(
        out,
        bands,
        brands=brands,
        brand_aliases=brand_aliases,
        outlier_quantile=outlier_quantile,
    )

    if dedupe:
        out["_score"] = row_richness_score(out)
        out = out.sort_values(["sku_id", "_score"], ascending=[True, False])
        out = out.drop_duplicates(subset=["sku_id"], keep="first")
        out = out.drop(columns=["_score"], errors="ignore")

    out = out.drop(columns=["_source_file"], errors="ignore")
    return out.reset_index(drop=True)


def merge_by_sku(existing: pd.DataFrame, incoming: pd.DataFrame) -> pd.DataFrame:
    if existing is None or existing.empty:
        return incoming.copy()
    if incoming is None or incoming.empty:
        return existing.copy()
    both = pd.concat([existing, incoming], ignore_index=True)
    both["_score"] = row_richness_score(both)
    both = both.sort_values(["sku_id", "_score"], ascending=[True, False])
    both = both.drop_duplicates(subset=["sku_id"], keep="first")
    both = both.drop(columns=["_score"], errors="ignore")
    return both.reset_index(drop=True)


def persist_processed(
    df: pd.DataFrame,
    *,
    write_csv: bool = True,
) -> Path:
    cfg = load_config()
    ensure_dirs(cfg)
    processed_dir = ROOT / cfg["paths"]["processed_dir"]
    proc_cfg = cfg.get("processing") or {}
    aggregates_dir = processed_dir / proc_cfg.get("aggregates_dir", "aggregates")
    shop_top_n = int(proc_cfg.get("shop_top_n", 50))

    parquet_path = processed_dir / "products.parquet"
    csv_path = processed_dir / "products.csv"

    df.to_parquet(parquet_path, index=False)
    if write_csv:
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    agg_paths = build_aggregates(df, aggregates_dir, shop_top_n=shop_top_n)
    # store relative paths in summary
    rel_aggs = {
        k: str(Path(v).resolve().relative_to(ROOT.resolve())).replace("\\", "/")
        for k, v in agg_paths.items()
    }
    write_summary(df, processed_dir=processed_dir, aggregate_paths=rel_aggs, root=ROOT)

    quality = build_quality_report(df)
    (processed_dir / "quality_report.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info("Wrote %s (%d rows) csv=%s", parquet_path, len(df), write_csv)

    try:
        from src.analysis.export_story import export_story

        export_story()
    except Exception as exc:  # keep clean resilient if web path missing
        logger.warning("story.json export skipped: %s", exc)

    return parquet_path


def run(raw_glob_latest_only: bool = False, write_csv: bool = True) -> Path:
    cfg = load_config()
    ensure_dirs(cfg)
    raw_dir = ROOT / cfg["paths"]["raw_dir"]
    proc_cfg = cfg.get("processing") or {}

    if raw_glob_latest_only:
        files = sorted(raw_dir.glob("products_*.jsonl"))
        if not files:
            raise FileNotFoundError(f"No products_*.jsonl under {raw_dir}")
        latest = files[-1]
        rows = [
            json.loads(l)
            for l in latest.read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
        df_raw = pd.DataFrame(rows)
        logger.info("Loaded latest only: %s (%d)", latest.name, len(df_raw))
    else:
        df_raw = load_raw_jsonl(raw_dir)

    bands = cfg.get("price_bands", [])
    df = clean_frame(
        df_raw,
        bands,
        brands=list(cfg.get("brands") or []),
        brand_aliases=dict(cfg.get("brand_aliases") or {}),
        outlier_quantile=float(proc_cfg.get("outlier_quantile", 0.99)),
    )
    return persist_processed(df, write_csv=write_csv)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean & enrich JD sports crawl data.")
    parser.add_argument(
        "--latest-only",
        action="store_true",
        help="Process only the newest products_*.jsonl file.",
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Skip CSV export (parquet/summary/aggregates still written).",
    )
    args = parser.parse_args(argv)
    try:
        run(raw_glob_latest_only=args.latest_only, write_csv=not args.no_csv)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        logger.error("Run crawl first: python -m src.crawler.run_crawl")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
