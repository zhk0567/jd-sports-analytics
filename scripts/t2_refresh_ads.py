"""Recompute the ADS layer from existing DWD/DWS tables."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t2_build_warehouse import build_ads  # noqa: E402
from t2_common import connect, scalar, table  # noqa: E402


def refresh_ads() -> dict:
    conn = connect()
    quality = {}
    build_ads(conn, quality)
    conn.commit()
    result = {
        "ads_rows": quality.get("ads_rows", {}),
        "core_kpi": int(scalar(conn, f'SELECT COUNT(*) FROM "{table("ads", "core_kpi")}"')),
        "refreshed": True,
    }
    conn.close()
    return result


if __name__ == "__main__":
    print(refresh_ads())
