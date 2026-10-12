"""JD listing page client and parsers (public re.jd.com / search pages)."""

from __future__ import annotations

import json
import logging
import re
import threading
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

JD_ITEM_RE = re.compile(r"item\.jd\.com/(\d+)\.html")
CONFIGS_RE = re.compile(r"var configs\s*=\s*(\{.*?\});\s*</script>", re.S)


class JDClient:
    """Thread-safe client: each thread keeps a reused httpx.Client."""

    def __init__(self, user_agent: str, timeout_sec: float = 20.0) -> None:
        self.timeout = timeout_sec
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": "https://re.jd.com/",
        }
        self._local = threading.local()
        self._clients: list[httpx.Client] = []
        self._clients_lock = threading.Lock()

    def _get_client(self) -> httpx.Client:
        client = getattr(self._local, "client", None)
        if client is None or client.is_closed:
            client = httpx.Client(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
                limits=httpx.Limits(
                    max_connections=20,
                    max_keepalive_connections=10,
                    keepalive_expiry=30.0,
                ),
            )
            self._local.client = client
            with self._clients_lock:
                self._clients.append(client)
        return client

    def close(self) -> None:
        with self._clients_lock:
            for client in self._clients:
                try:
                    client.close()
                except Exception:
                    pass
            self._clients.clear()

    def build_search_url(self, keyword: str, page: int, brand: str | None = None) -> str:
        """Prefer re.jd.com hot-sale search (embeds product JSON)."""
        q = keyword if not brand else f"{keyword} {brand}"
        return f"https://re.jd.com/search?keyword={quote(q)}&page={page}"

    def build_fallback_url(self, keyword: str, page: int, brand: str | None = None) -> str:
        jd_page = page * 2 - 1
        q = keyword if not brand else f"{keyword} {brand}"
        return (
            f"https://search.jd.com/Search?keyword={quote(q)}"
            f"&enc=utf-8&wq={quote(q)}&page={jd_page}"
        )

    def fetch(self, url: str) -> tuple[str | None, str | None]:
        """Return (html, error_reason)."""
        try:
            resp = self._get_client().get(url)
            if resp.status_code != 200:
                return None, f"http_{resp.status_code}"
            text = resp.text
            if self._looks_blocked(text):
                return None, "blocked_or_captcha"
            return text, None
        except httpx.HTTPError as exc:
            return None, f"http_error:{exc.__class__.__name__}"

    @staticmethod
    def _looks_blocked(html: str) -> bool:
        if "risk_handler" in html or "cfe.m.jd.com/privatedomain/risk" in html:
            return True
        markers = ("验证码", "安全验证", "JD_Risk")
        low = html[:8000]
        has_product_signal = (
            "var configs" in html
            or "gl-item" in html
            or "data-sku" in html
            or "goods-pc-search" in html
        )
        if any(m in low for m in markers) and not has_product_signal:
            return True
        return False

    def parse_products(
        self,
        html: str,
        *,
        source_query: str,
        brand: str | None,
        page: int,
    ) -> list[dict[str, Any]]:
        products = self._parse_re_configs(html, source_query, brand, page)
        if products:
            return products

        products = self._parse_gl_items(html, source_query, brand, page)
        if products:
            return products

        return self._parse_from_links(html, source_query, brand, page)

    def _parse_re_configs(
        self,
        html: str,
        source_query: str,
        brand: str | None,
        page: int,
    ) -> list[dict[str, Any]]:
        m = CONFIGS_RE.search(html)
        if not m:
            return []
        try:
            cfg = json.loads(m.group(1))
        except json.JSONDecodeError:
            logger.warning("Failed to decode re.jd.com configs JSON")
            return []

        crawled_at = datetime.now(timezone.utc).isoformat()
        seen: set[str] = set()
        products: list[dict[str, Any]] = []

        for mod in cfg.get("moduleInfo") or []:
            data = mod.get("data")
            if not (
                isinstance(data, list)
                and data
                and isinstance(data[0], dict)
                and ("price" in data[0] or "id" in data[0])
                and ("title" in data[0] or "wname" in data[0])
            ):
                continue
            for item in data:
                sku = str(item.get("id") or item.get("skuId") or "").strip()
                if not sku or sku in seen:
                    continue
                seen.add(sku)
                title = str(item.get("title") or item.get("wname") or "").strip()
                price = self._to_float(item.get("price"))
                shop_name = str(item.get("shopName") or "").strip()
                comment_count = self._parse_comment_count(str(item.get("cc") or ""))
                image_url = str(item.get("imageUrl") or "")
                if image_url and not image_url.startswith("http"):
                    image_url = "https://img14.360buyimg.com/n1/" + image_url.lstrip("/")
                land = str(item.get("landUrl") or item.get("click") or "")
                product_url = land if land.startswith("http") else f"https://item.jd.com/{sku}.html"
                brand_guess = brand or self._guess_brand_from_title(title)
                products.append(
                    {
                        "sku_id": sku,
                        "title": title,
                        "price": price,
                        "original_price": self._to_float(item.get("op") or item.get("originalPrice")),
                        "brand": brand_guess,
                        "shop_name": shop_name,
                        "comment_count": comment_count,
                        "product_url": product_url,
                        "image_url": image_url,
                        "source_query": source_query,
                        "page": page,
                        "crawled_at": crawled_at,
                    }
                )
        return products

    def _parse_gl_items(
        self,
        html: str,
        source_query: str,
        brand: str | None,
        page: int,
    ) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        items = soup.select("li.gl-item")
        products: list[dict[str, Any]] = []
        crawled_at = datetime.now(timezone.utc).isoformat()

        for li in items:
            sku = (li.get("data-sku") or "").strip()
            if not sku:
                continue

            title_el = li.select_one("div.p-name a em") or li.select_one("div.p-name a")
            title = title_el.get_text(" ", strip=True) if title_el else ""

            price = self._parse_price_el(li)
            original_price = self._parse_original_price(li)

            shop_el = li.select_one("div.p-shop a") or li.select_one("span.J_im_icon a")
            shop_name = shop_el.get_text(strip=True) if shop_el else ""

            comment_el = li.select_one("div.p-commit strong a") or li.select_one("div.p-commit a")
            comment_count = self._parse_comment_count(
                comment_el.get_text(strip=True) if comment_el else ""
            )

            img_el = li.select_one("div.p-img img")
            image_url = ""
            if img_el is not None:
                image_url = img_el.get("data-lazy-img") or img_el.get("src") or ""
                if image_url.startswith("//"):
                    image_url = "https:" + image_url

            link_el = li.select_one("div.p-img a") or li.select_one("div.p-name a")
            href = link_el.get("href") if link_el else ""
            if href and href.startswith("//"):
                href = "https:" + href
            product_url = href or f"https://item.jd.com/{sku}.html"

            products.append(
                {
                    "sku_id": str(sku),
                    "title": title,
                    "price": price,
                    "original_price": original_price,
                    "brand": brand or self._guess_brand_from_title(title),
                    "shop_name": shop_name,
                    "comment_count": comment_count,
                    "product_url": product_url,
                    "image_url": image_url,
                    "source_query": source_query,
                    "page": page,
                    "crawled_at": crawled_at,
                }
            )
        return products

    def _parse_from_links(
        self,
        html: str,
        source_query: str,
        brand: str | None,
        page: int,
    ) -> list[dict[str, Any]]:
        crawled_at = datetime.now(timezone.utc).isoformat()
        seen: set[str] = set()
        out: list[dict[str, Any]] = []
        for m in JD_ITEM_RE.finditer(html):
            sku = m.group(1)
            if sku in seen:
                continue
            seen.add(sku)
            out.append(
                {
                    "sku_id": sku,
                    "title": "",
                    "price": None,
                    "original_price": None,
                    "brand": brand or "",
                    "shop_name": "",
                    "comment_count": None,
                    "product_url": f"https://item.jd.com/{sku}.html",
                    "image_url": "",
                    "source_query": source_query,
                    "page": page,
                    "crawled_at": crawled_at,
                }
            )
        return out

    @staticmethod
    def _to_float(v: Any) -> float | None:
        if v is None:
            return None
        try:
            s = str(v).replace(",", "").strip()
            s = re.sub(r"[^\d.]", "", s)
            return float(s) if s else None
        except ValueError:
            return None

    @staticmethod
    def _parse_price_el(li: Any) -> float | None:
        price_el = li.select_one("div.p-price i") or li.select_one("div.p-price strong i")
        if not price_el:
            return None
        text = price_el.get_text(strip=True).replace(",", "")
        try:
            return float(text)
        except ValueError:
            return None

    @staticmethod
    def _parse_original_price(li: Any) -> float | None:
        del_el = li.select_one("div.p-price del") or li.select_one("span.p-price-del")
        if not del_el:
            return None
        text = re.sub(r"[^\d.]", "", del_el.get_text())
        try:
            return float(text) if text else None
        except ValueError:
            return None

    @staticmethod
    def _parse_comment_count(text: str) -> int | None:
        if not text:
            return None
        text = (
            text.replace("+", "")
            .replace("条评价", "")
            .replace("评价", "")
            .replace("人付款", "")
            .strip()
        )
        mult = 1
        if "万" in text:
            mult = 10000
            text = text.replace("万", "")
        text = re.sub(r"[^\d.]", "", text)
        if not text:
            return None
        try:
            return int(float(text) * mult)
        except ValueError:
            return None

    @staticmethod
    def _guess_brand_from_title(title: str) -> str:
        known = [
            "李宁",
            "安踏",
            "特步",
            "361°",
            "361度",
            "匹克",
            "Nike",
            "耐克",
            "Adidas",
            "阿迪达斯",
            "迪卡侬",
            "Keep",
            "安德玛",
            "Under Armour",
            "亚瑟士",
            "ASICS",
            "鸿星尔克",
            "乔丹",
            "回力",
            "匡威",
            "斯凯奇",
        ]
        for b in known:
            if b.lower() in title.lower():
                if b == "耐克":
                    return "Nike"
                if b == "阿迪达斯":
                    return "Adidas"
                if b == "361度":
                    return "361°"
                if b == "Under Armour":
                    return "安德玛"
                if b == "ASICS":
                    return "亚瑟士"
                return b
        return ""


def dump_jsonl(path: Any, rows: list[dict[str, Any]]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
