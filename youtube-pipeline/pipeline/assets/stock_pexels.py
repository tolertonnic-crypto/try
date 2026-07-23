"""Pexels stock B-roll stub.

Fetches candidate stock videos/photos per section keyword (PEXELS_API_KEY in
.env). Downloads go to renders/<slug>/broll/. Free API, generous limits — but
results are cached per keyword under data/ so repeated runs don't re-hit it.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .. import paths

SEARCH_URL = "https://api.pexels.com/videos/search"
CACHE_FILE = paths.DATA_DIR / "pexels_cache.json"


def _cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def search(keyword: str, per_page: int = 5) -> list[dict]:
    """Return candidate videos [{url, duration, preview}] for a keyword."""
    cache = _cache()
    if keyword in cache:
        return cache[keyword]

    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY not set in .env — cannot search stock footage")
    import requests

    resp = requests.get(
        SEARCH_URL,
        headers={"Authorization": api_key},
        params={"query": keyword, "per_page": per_page, "orientation": "landscape"},
        timeout=60,
    )
    resp.raise_for_status()
    results = [
        {
            "url": max(v["video_files"], key=lambda f: f.get("width") or 0)["link"],
            "duration": v.get("duration"),
            "preview": v.get("image"),
        }
        for v in resp.json().get("videos", [])
    ]
    paths.ensure_dirs()
    cache[keyword] = results
    CACHE_FILE.write_text(json.dumps(cache))
    return results


def fetch_for_item(item: dict) -> dict:
    """Collect B-roll candidates for every section of a queue item's script."""
    plan = {}
    for section in item["script"]["sections"]:
        for kw in section.get("broll_keywords", [])[:2]:
            if kw not in plan:
                plan[kw] = search(kw)
    return plan
