"""Entry point: crawl JD sports listings into data/raw (target <100k unique)."""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from src.crawler.jd_client import JDClient, dump_jsonl
from src.utils import ROOT, ensure_dirs, load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("crawl")


def _sleep(cfg: dict, *, blocked: bool = False) -> None:
    if blocked:
        time.sleep(float(cfg["crawl"].get("blocked_backoff_sec", 6)))
        return
    lo = float(cfg["crawl"]["delay_min_sec"])
    hi = float(cfg["crawl"]["delay_max_sec"])
    time.sleep(random.uniform(lo, hi))


def _build_queries(cfg: dict) -> list[tuple[str, str | None]]:
    """Return list of (query_text, brand_or_none)."""
    keyword = cfg["search"]["keyword"]
    queries: list[tuple[str, str | None]] = []
    crawl = cfg["crawl"]
    brands = [str(b) for b in (cfg.get("brands") or [])]

    if crawl.get("include_keyword_only", True):
        queries.append((keyword, None))

    if crawl.get("include_extra_queries", True):
        for q in cfg["search"].get("extra_queries") or []:
            q = str(q).strip()
            if q and q != keyword:
                queries.append((q, None))

    if crawl.get("include_brands", True):
        prefix = crawl.get("brand_query_prefix", True)
        for brand in brands:
            q = f"{keyword} {brand}" if prefix else brand
            queries.append((q, brand))

    if crawl.get("include_brand_sport_cross", True):
        facets = [
            str(s).strip()
            for s in (cfg["search"].get("sport_facets") or [])
            if str(s).strip()
        ]
        limit = int(crawl.get("brand_sport_brand_limit", 15))
        for brand in brands[:limit]:
            for sport in facets:
                queries.append((f"{brand} {sport}", None))

    seen: set[str] = set()
    out: list[tuple[str, str | None]] = []
    for q, b in queries:
        if q in seen:
            continue
        seen.add(q)
        out.append((q, b))
    return out


def _load_seen_skus(raw_dir: Path) -> set[str]:
    seen: set[str] = set()
    for path in sorted(raw_dir.glob("products_*.jsonl")):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                text = line.strip()
                if not text:
                    continue
                try:
                    row = json.loads(text)
                except json.JSONDecodeError:
                    continue
                sku = str(row.get("sku_id") or "").strip()
                if sku:
                    seen.add(sku)
    return seen


def _completed_queries(
    meta: dict,
    *,
    max_pages: int,
    stop_after_low: int,
    low_thr: int,
) -> dict[str, int]:
    """Return {query: next_page} for queries already finished; resume page for partial."""
    batches = meta.get("batches") or []
    by_q: dict[str, list[dict]] = {}
    for b in batches:
        q = str(b.get("query") or "")
        if not q:
            continue
        by_q.setdefault(q, []).append(b)

    done_or_resume: dict[str, int] = {}
    for q, rows in by_q.items():
        rows = sorted(rows, key=lambda r: int(r.get("page") or 0))
        last_page = int(rows[-1].get("page") or 0)
        low_streak = 0
        finished = False
        for r in rows:
            count = int(r.get("count") or 0)
            new = int(r.get("new") or 0)
            if count == 0 or new < low_thr:
                low_streak += 1
            else:
                low_streak = 0
            if low_streak >= stop_after_low:
                finished = True
                break
        if finished or last_page >= max_pages:
            done_or_resume[q] = 0  # 0 => skip
        else:
            done_or_resume[q] = last_page + 1
    return done_or_resume


def _latest_raw_file(raw_dir: Path) -> Path | None:
    files = sorted(raw_dir.glob("products_*.jsonl"))
    return files[-1] if files else None


class CrawlState:
    def __init__(
        self,
        *,
        cfg: dict,
        out_path: Path,
        meta_path: Path,
        meta: dict,
        seen_skus: set[str],
        total: int,
    ) -> None:
        self.cfg = cfg
        self.out_path = out_path
        self.meta_path = meta_path
        self.meta = meta
        self.seen_skus = seen_skus
        self.total = total
        self.stop_reason: str | None = None
        self.lock = threading.Lock()
        self._meta_dirty = 0
        self.max_unique = int(cfg["crawl"].get("max_unique", 90000))
        self.max_raw = int(cfg["crawl"].get("max_raw_rows", 120000))

    def should_stop(self) -> bool:
        with self.lock:
            if self.stop_reason:
                return True
            if len(self.seen_skus) >= self.max_unique:
                self.stop_reason = "max_unique"
                return True
            if self.total >= self.max_raw:
                self.stop_reason = "max_raw_rows"
                return True
            return False

    def commit_page(
        self,
        *,
        source_query: str,
        brand: str | None,
        page: int,
        products: list[dict],
        err: str | None,
    ) -> tuple[int, int, int]:
        """Write fresh SKUs; return (page_count, new_count, unique)."""
        with self.lock:
            fresh = []
            for p in products:
                sku = str(p.get("sku_id") or "")
                if not sku or sku in self.seen_skus:
                    continue
                self.seen_skus.add(sku)
                fresh.append(p)
            if fresh:
                dump_jsonl(self.out_path, fresh)
                self.total += len(fresh)

            count = len(products)
            new_count = len(fresh)
            self.meta["batches"].append(
                {
                    "query": source_query,
                    "brand": brand,
                    "page": page,
                    "count": count,
                    "new": new_count,
                    "error": err if count == 0 else None,
                }
            )
            self.meta["total_rows"] = self.total
            self.meta["unique_skus"] = len(self.seen_skus)
            self._meta_dirty += 1
            # flush meta every few pages to cut disk churn
            if self._meta_dirty >= 4 or new_count == 0:
                self._flush_meta_unlocked()
                self._meta_dirty = 0
            return count, new_count, len(self.seen_skus)

    def _flush_meta_unlocked(self) -> None:
        self.meta_path.write_text(
            json.dumps(self.meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def flush_meta(self) -> None:
        with self.lock:
            self._flush_meta_unlocked()
            self._meta_dirty = 0


def _crawl_one_query(
    state: CrawlState,
    client: JDClient,
    query_text: str,
    brand: str | None,
    start_page: int,
) -> str:
    cfg = state.cfg
    crawl = cfg["crawl"]
    keyword = cfg["search"]["keyword"]
    max_pages = int(crawl.get("max_pages_per_query", 80))
    stop_after_low = int(crawl.get("stop_after_low_pages", 3))
    low_thr = int(crawl.get("low_new_threshold", 5))
    low_streak = 0

    for page in range(start_page, max_pages + 1):
        if state.should_stop():
            return "global_stop"

        if brand:
            url = client.build_search_url(keyword, page, brand)
            source_query = query_text
        else:
            url = client.build_search_url(query_text, page, None)
            source_query = query_text

        logger.info(
            "Fetch q=%s page=%s unique=%d raw=%d",
            query_text,
            page,
            len(state.seen_skus),
            state.total,
        )
        html, err = client.fetch(url)
        if not html:
            fb = (
                client.build_fallback_url(keyword, page, brand)
                if brand
                else client.build_fallback_url(query_text, page, None)
            )
            logger.info("  fallback %s", fb)
            html, err = client.fetch(fb)

        products: list[dict] = []
        if html:
            products = client.parse_products(
                html, source_query=source_query, brand=brand, page=page
            )
            if not products:
                err = err or "empty_parse"
                logger.warning("  -> no products (%s)", err)
        else:
            logger.warning("  -> failed: %s", err)

        count, new_count, unique = state.commit_page(
            source_query=source_query,
            brand=brand,
            page=page,
            products=products,
            err=err,
        )
        if products:
            logger.info(
                "  -> page=%d new=%d (page_items=%d) unique=%d",
                page,
                new_count,
                count,
                unique,
            )

        if count == 0 or new_count < low_thr:
            low_streak += 1
        else:
            low_streak = 0
        if low_streak >= stop_after_low:
            logger.info(
                "Stop query %s after %d low-yield pages",
                query_text,
                stop_after_low,
            )
            return "low_yield"

        blocked = (err == "blocked_or_captcha") if count == 0 else False
        _sleep(cfg, blocked=blocked)

    return "max_pages"


def run(demo: bool = False, resume: bool = True) -> Path:
    cfg = load_config()
    ensure_dirs(cfg)

    raw_dir = ROOT / cfg["paths"]["raw_dir"]
    meta_path = raw_dir / "_meta.json"
    crawl = cfg["crawl"]
    max_unique = int(crawl.get("max_unique", 90000))
    max_raw = int(crawl.get("max_raw_rows", 120000))
    max_pages = int(crawl.get("max_pages_per_query", 80))
    stop_after_low = int(crawl.get("stop_after_low_pages", 3))
    low_thr = int(crawl.get("low_new_threshold", 5))
    workers = max(1, int(crawl.get("workers", 1)))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = raw_dir / f"products_{stamp}.jsonl"
    seen_skus: set[str] = set()
    total = 0
    resume_pages: dict[str, int] = {}
    meta: dict = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "project": cfg.get("project_name", "jd-sports-analytics"),
        "demo": demo,
        "mode": "full_under_100k",
        "max_unique": max_unique,
        "workers": workers,
        "batches": [],
        "total_rows": 0,
        "unique_skus": 0,
        "finished_at": None,
        "status": "running",
        "stop_reason": None,
        "resumed": False,
    }

    if resume and not demo:
        prev_meta: dict = {}
        if meta_path.exists():
            try:
                prev_meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                prev_meta = {}
        seen_skus = _load_seen_skus(raw_dir)
        total = len(seen_skus)
        latest = _latest_raw_file(raw_dir)
        if latest is not None and seen_skus:
            out_path = latest
            meta["resumed"] = True
            meta["started_at"] = prev_meta.get("started_at") or meta["started_at"]
            meta["batches"] = list(prev_meta.get("batches") or [])
            meta["resume_at"] = datetime.now(timezone.utc).isoformat()
            resume_pages = _completed_queries(
                prev_meta,
                max_pages=max_pages,
                stop_after_low=stop_after_low,
                low_thr=low_thr,
            )
            logger.info(
                "Resume: file=%s seen=%d queries_tracked=%d",
                out_path.name,
                len(seen_skus),
                len(resume_pages),
            )

    if demo:
        rows = _demo_rows(cfg)
        dump_jsonl(out_path, rows)
        meta["batches"].append(
            {
                "query": "demo",
                "brand": None,
                "page": 1,
                "count": len(rows),
                "new": len(rows),
                "error": None,
            }
        )
        meta["total_rows"] = len(rows)
        meta["unique_skus"] = len(rows)
        meta["status"] = "ok_demo"
        meta["finished_at"] = datetime.now(timezone.utc).isoformat()
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Demo data written: %s (%d rows)", out_path, len(rows))
        return out_path

    client = JDClient(
        user_agent=crawl["user_agent"],
        timeout_sec=float(crawl["timeout_sec"]),
    )
    queries = _build_queries(cfg)

    pending: list[tuple[str, str | None, int]] = []
    skipped = 0
    for query_text, brand in queries:
        marker = resume_pages.get(query_text)
        if marker == 0:
            skipped += 1
            continue
        start_page = marker if marker and marker > 1 else 1
        pending.append((query_text, brand, start_page))

    state = CrawlState(
        cfg=cfg,
        out_path=out_path,
        meta_path=meta_path,
        meta=meta,
        seen_skus=seen_skus,
        total=total,
    )
    state.flush_meta()

    logger.info(
        "Start crawl: workers=%d pending_queries=%d skipped=%d max_pages=%d "
        "max_unique=%d delay=%.2f-%.2fs unique_seed=%d",
        workers,
        len(pending),
        skipped,
        max_pages,
        max_unique,
        float(crawl["delay_min_sec"]),
        float(crawl["delay_max_sec"]),
        len(seen_skus),
    )

    try:
        if workers == 1:
            for query_text, brand, start_page in pending:
                if state.should_stop():
                    break
                _crawl_one_query(state, client, query_text, brand, start_page)
        else:
            with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="crawl") as pool:
                futures = [
                    pool.submit(_crawl_one_query, state, client, q, b, sp)
                    for q, b, sp in pending
                ]
                for fut in as_completed(futures):
                    try:
                        fut.result()
                    except Exception:
                        logger.exception("Worker failed")
                    if state.should_stop():
                        break
    finally:
        client.close()

    if state.stop_reason is None:
        state.stop_reason = "queries_exhausted"

    with state.lock:
        state.meta["finished_at"] = datetime.now(timezone.utc).isoformat()
        state.meta["unique_skus"] = len(state.seen_skus)
        state.meta["total_rows"] = state.total
        state.meta["stop_reason"] = state.stop_reason
        state.meta["status"] = "ok" if state.total > 0 else "empty"
        state.meta["workers"] = workers
        state._flush_meta_unlocked()

    logger.info(
        "Done. unique=%d raw_written=%d stop=%s file=%s",
        len(state.seen_skus),
        state.total,
        state.stop_reason,
        out_path,
    )

    if state.total == 0:
        logger.warning(
            "No products crawled (likely blocked). "
            "Re-run with --demo to generate sample data for pipeline testing."
        )
    return out_path


def _demo_rows(cfg: dict) -> list[dict]:
    """Synthetic sample so processing/dashboard can be verified offline."""
    brands = list(cfg["brands"])
    templates = [
        ("{b} 男跑步鞋 透气缓震", "footwear", 199, 399, 12000),
        ("{b} 运动短袖T恤 速干", "apparel", 89, 159, 8600),
        ("{b} 女子训练长裤", "apparel", 129, 249, 5400),
        ("{b} 智能跳绳 计数", "equipment", 59, 99, 21000),
        ("{b} 蛋白粉 乳清 2磅", "nutrition", 168, 258, 3200),
        ("{b} 户外冲锋衣 防风", "apparel", 399, 699, 4100),
        ("{b} 篮球鞋 高帮", "footwear", 459, 799, 9800),
        ("{b} 瑜伽垫 加厚", "equipment", 79, 129, 15000),
    ]
    shops = [f"{b}京东自营旗舰店" for b in brands[:6]] + ["运动优选专营店", "户外生活旗舰店"]
    rows: list[dict] = []
    now = datetime.now(timezone.utc).isoformat()
    sku = 10000000001
    for bi, brand in enumerate(brands):
        for ti, (title_tpl, _cat, price, orig, comments) in enumerate(templates):
            for n in range(3):
                p = round(price * (0.9 + 0.05 * n) + bi * 3, 2)
                rows.append(
                    {
                        "sku_id": str(sku),
                        "title": title_tpl.format(b=brand) + f" 款式{n+1}",
                        "price": p,
                        "original_price": float(orig),
                        "brand": brand,
                        "shop_name": shops[(bi + ti) % len(shops)],
                        "comment_count": comments + bi * 100 + n * 17,
                        "product_url": f"https://item.jd.com/{sku}.html",
                        "image_url": "",
                        "source_query": f"运动 {brand}",
                        "page": (n % 3) + 1,
                        "crawled_at": now,
                    }
                )
                sku += 1
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl JD sports listings (full mode, soft-cap <100k unique)."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Write synthetic sample data instead of hitting JD.",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start a fresh JSONL instead of appending / skipping done queries.",
    )
    args = parser.parse_args(argv)
    run(demo=args.demo, resume=not args.no_resume)
    return 0


if __name__ == "__main__":
    sys.exit(main())
