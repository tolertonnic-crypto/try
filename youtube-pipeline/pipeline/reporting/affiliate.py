"""Affiliate attribution helpers.

Links are UTM-tagged per video at description-build time
(metadata_generator.utm_tag): utm_campaign = the video slug. Your affiliate
dashboards / analytics tools report clicks per utm_campaign, and this module
maintains the local mapping so those reports join back to videos and pillars.

data/affiliate_map.csv: one row per (video, link) emitted.
Export clicks/conversions per campaign from your affiliate dashboard, save as
data/affiliate_clicks.csv with columns [utm_campaign, clicks, conversions],
and the weekly summary joins the two.
"""

from __future__ import annotations

import csv
import json

from .. import paths

MAP_FILE = paths.DATA_DIR / "affiliate_map.csv"
CLICKS_FILE = paths.DATA_DIR / "affiliate_clicks.csv"


def record_links_for_item(item: dict) -> None:
    """Record which affiliate links a queue item's description carries."""
    from ..metadata_generator import pick_links

    paths.ensure_dirs()
    exists = MAP_FILE.exists()
    with open(MAP_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["utm_campaign", "video_slug", "pillar", "link_id"])
        for link in pick_links(item["topic"]["pillar"]):
            writer.writerow([item["slug"], item["slug"], item["topic"]["pillar"], link["id"]])


def clicks_by_video() -> dict[str, dict]:
    """Join the local map with exported click data, keyed by video slug."""
    if not CLICKS_FILE.exists():
        return {}
    clicks: dict[str, dict] = {}
    with open(CLICKS_FILE, newline="") as f:
        for row in csv.DictReader(f):
            slug = row.get("utm_campaign", "")
            entry = clicks.setdefault(slug, {"clicks": 0, "conversions": 0})
            entry["clicks"] += int(row.get("clicks") or 0)
            entry["conversions"] += int(row.get("conversions") or 0)
    return clicks


def pillar_of(slug: str) -> str | None:
    """Look up a video's pillar from the review archive."""
    for directory in (paths.APPROVED_DIR, paths.REJECTED_DIR, paths.QUEUE_DIR):
        f = directory / f"{slug}.json"
        if f.exists():
            return json.loads(f.read_text())["topic"]["pillar"]
    return None
