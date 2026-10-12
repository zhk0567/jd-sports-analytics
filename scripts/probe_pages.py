"""Probe unique yield across re.jd.com pages."""

from __future__ import annotations

import json
import re
from urllib.parse import quote

import httpx

ua = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
headers = {
    "User-Agent": ua,
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://re.jd.com/",
}

seen: set[str] = set()
for page in [1, 2, 3, 5, 10, 20, 30, 50, 80, 100]:
    url = f"https://re.jd.com/search?keyword={quote('运动')}&page={page}"
    r = httpx.get(url, headers=headers, timeout=25, follow_redirects=True)
    m = re.search(r"var configs = (\{.*?\});\s*</script>", r.text, re.S)
    if not m:
        print(f"page={page} no configs status={r.status_code}")
        continue
    cfg = json.loads(m.group(1))
    ids: list[str] = []
    for mod in cfg.get("moduleInfo") or []:
        data = mod.get("data")
        if (
            isinstance(data, list)
            and data
            and isinstance(data[0], dict)
            and "id" in data[0]
            and "title" in data[0]
        ):
            ids.extend(str(x.get("id")) for x in data if x.get("id"))
    fresh = [i for i in ids if i not in seen]
    seen.update(ids)
    print(
        f"page={page} items={len(ids)} new={len(fresh)} "
        f"summary={cfg.get('summary')} cum_unique={len(seen)}"
    )
