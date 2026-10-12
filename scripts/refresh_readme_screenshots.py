"""Crop Cursor browser screenshots into docs/screenshots for README.

Workflow (Windows):
1. Start web:  cd web; npm run dev -- --host 127.0.0.1 --port 5173
2. In Cursor browser, open http://127.0.0.1:5173/ at ~1440x900
3. For each act, scroll into view, wait ~1s (CountUp finish), save viewport PNG as:
     act-00-open.png ... act-05-shelf.png
   into:  %TEMP%\\cursor\\screenshots\\
4. Run:
     python scripts/refresh_readme_screenshots.py
5. Update README captions if metrics changed.

Re-run this whenever the story UI changes — README images must match the live page.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = Path.home() / "AppData" / "Local" / "Temp" / "cursor" / "screenshots"
# also accept env override
import os

SRC = Path(os.environ.get("SPORT_SHOT_SRC", str(SRC)))
DST = ROOT / "docs" / "screenshots"

NAMES = [
    "act-00-open.png",
    "act-01-scale.png",
    "act-02-brands.png",
    "act-03-price.png",
    "act-04-scene.png",
    "act-05-shelf.png",
]


def crop_story(im: Image.Image, pad: int = 12) -> Image.Image:
    arr = np.asarray(im.convert("RGB"), dtype=np.float32)
    corners = np.concatenate(
        [
            arr[:30, :30].reshape(-1, 3),
            arr[:30, -30:].reshape(-1, 3),
            arr[-30:, :30].reshape(-1, 3),
            arr[-30:, -30:].reshape(-1, 3),
        ]
    )
    bg = corners.mean(axis=0)
    dist = np.linalg.norm(arr - bg, axis=2)
    mask = dist > 16
    row_den = mask.mean(axis=1)
    col_den = mask.mean(axis=0)
    rows = np.where(row_den > 0.004)[0]
    cols = np.where(col_den > 0.004)[0]
    if len(rows) == 0 or len(cols) == 0:
        return im
    y0, y1 = int(rows.min()), int(rows.max()) + 1
    x0, x1 = int(cols.min()), int(cols.max()) + 1
    for y in range(y1 - 1, y0, -1):
        if row_den[y] > 0.01:
            y1 = y + 1
            break
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(im.width, x1 + pad)
    y1 = min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1))


def main() -> int:
    DST.mkdir(parents=True, exist_ok=True)
    missing = [n for n in NAMES if not (SRC / n).exists()]
    if missing:
        print("Missing source shots in", SRC)
        for n in missing:
            print(" -", n)
        print(__doc__)
        return 1

    for name in NAMES:
        im = Image.open(SRC / name)
        cropped = crop_story(im)
        max_w = 1280
        if cropped.width > max_w:
            r = max_w / cropped.width
            cropped = cropped.resize(
                (max_w, int(cropped.height * r)), Image.Resampling.LANCZOS
            )
        out = DST / name
        cropped.save(out, optimize=True)
        print(f"{name}: {im.size} -> {cropped.size} ({out.stat().st_size // 1024} KB)")
    print("Wrote", DST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
