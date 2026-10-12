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
kw = quote("运动")
cands = [
    f"https://re.jd.com/search?keyword={kw}&ev=exprice_0-60",
    f"https://re.jd.com/search?keyword={kw}&price=0-60",
    f"https://re.jd.com/search?keyword={kw}&min=0&max=60",
    f"https://re.jd.com/search?keyword={kw}&page=1&sort=1",
    f"https://re.jd.com/search?keyword={kw}&ev=exbrand_李宁",
]
for url in cands:
    r = httpx.get(url, headers=headers, timeout=25, follow_redirects=True)
    m = re.search(r"var configs = (\{.*?\});\s*</script>", r.text, re.S)
    if not m:
        print("FAIL", r.status_code, url)
        continue
    cfg = json.loads(m.group(1))
    n = 0
    prices = []
    for mod in cfg.get("moduleInfo") or []:
        data = mod.get("data")
        if isinstance(data, list) and data and isinstance(data[0], dict) and "price" in data[0]:
            n += len(data)
            prices = [x.get("price") for x in data[:5]]
    print("summary", cfg.get("summary"), "n", n, "prices", prices, "url", url)
