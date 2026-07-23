"""Shorts repurposing.

Each long-form script carries 1-3 self-contained Shorts cuts. Once the parent
long-form item is APPROVED (and ideally uploaded, so its video ID exists), this
module stages each cut as its own queue item — which then goes through the SAME
human review gate and upload path as long-form. Shorts get shorts schedule
slots, a #Shorts-suffixed title, and a description that points back to the
parent video (the discovery→watch-time funnel in content-strategy.md).

No LLM call is needed here: metadata derives from the parent, which was already
reviewed. The Shorts still require their own approval pass because trimming a
video changes what it claims.
"""

from __future__ import annotations

import datetime as dt
import json

from . import paths


def _parent(slug: str) -> dict:
    f = paths.APPROVED_DIR / f"{slug}.json"
    if not f.exists():
        raise FileNotFoundError(
            f"no approved item named {slug!r} — Shorts are staged from approved "
            "long-form videos only"
        )
    return json.loads(f.read_text())


def stage_shorts(parent_slug: str) -> list[dict]:
    """Create queue items for every Shorts cut of an approved long-form item."""
    paths.ensure_dirs()
    parent = _parent(parent_slug)
    cuts = parent["script"].get("shorts", [])
    if not cuts:
        raise ValueError(f"{parent_slug} has no Shorts cuts in its script")

    parent_link = ""
    if parent.get("video_id"):
        parent_link = f"\n\nFull story: https://youtu.be/{parent['video_id']}"

    staged = []
    for i, cut in enumerate(cuts, 1):
        slug = f"{parent_slug}-short-{i}"
        title = cut["hook"].strip().rstrip(".")
        if len(title) > 90:
            title = title[:87] + "..."
        item = {
            "slug": slug,
            "kind": "short",
            "parent_slug": parent_slug,
            "topic": parent["topic"],
            "structure": parent["structure"],
            "similarity": {"flagged": False, "matches": [],
                           "note": "derived from reviewed parent"},
            "script": {
                "hook": cut["hook"],
                "hook_formula": parent["script"].get("hook_formula", ""),
                "editorial_angle": parent["script"].get("editorial_angle", ""),
                "sections": [{"heading": "short", "narration": cut["narration"],
                              "broll_keywords": []}],
                "outro": "",
                "factual_claims": parent["script"].get("factual_claims", []),
                "shorts": [],
                "on_screen_text": cut.get("on_screen_text", []),
            },
            "status": "pending_review",
            "synthetic": parent.get("synthetic", True),
            "metadata": {
                "title": f"{title} #Shorts",
                "title_options": [f"{title} #Shorts"],
                # No affiliate links in Shorts descriptions (they're barely
                # visible there and dilute the parent-video funnel) — so no
                # FTC disclosure is required either.
                "description": (cut["hook"] + parent_link).strip(),
                "tags": parent.get("metadata", {}).get("tags", [])[:10],
                "category_id": parent.get("metadata", {}).get("category_id", "27"),
            },
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        }
        (paths.QUEUE_DIR / f"{slug}.json").write_text(json.dumps(item, indent=2))
        staged.append(item)
    return staged
