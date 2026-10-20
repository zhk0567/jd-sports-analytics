"""Runtime configuration for the group-2 analytics API."""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("T2_DB_PATH", ROOT / "data" / "t2_ecommerce.db"))
API_PREFIX = "/api/t2"
HOST = os.getenv("T2_API_HOST", "127.0.0.1")
PORT = int(os.getenv("T2_API_PORT", "5000"))
DEBUG = os.getenv("T2_DEBUG", "0") == "1"

