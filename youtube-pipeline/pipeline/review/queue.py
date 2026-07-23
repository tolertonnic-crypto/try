"""Review queue state machine.

review/queue/<slug>.json      draft -> pending_review
review/approved/<slug>.json   approved (only the CLI's approve() writes here,
                              and only after the checklist is confirmed)
review/rejected/<slug>.json   rejected (kept for the record)

Nothing publishes automatically: upload.py refuses items whose status is not
'approved', and approve() is only reachable through the interactive CLI.
"""

from __future__ import annotations

import datetime as dt
import json

from .. import paths


def load_item(slug: str) -> dict:
    for directory in (paths.QUEUE_DIR, paths.APPROVED_DIR, paths.REJECTED_DIR):
        f = directory / f"{slug}.json"
        if f.exists():
            return json.loads(f.read_text())
    raise FileNotFoundError(f"no queue item named {slug!r}")


def pending_items() -> list[dict]:
    paths.ensure_dirs()
    items = [json.loads(f.read_text()) for f in sorted(paths.QUEUE_DIR.glob("*.json"))]
    return [i for i in items if i.get("status") in ("draft", "pending_review")]


def _move(item: dict, dest_dir) -> dict:
    src = paths.QUEUE_DIR / f"{item['slug']}.json"
    dest = dest_dir / f"{item['slug']}.json"
    dest.write_text(json.dumps(item, indent=2))
    if src.exists():
        src.unlink()
    return item


def approve(item: dict, checklist_confirmed: bool, publish_at_iso: str, note: str = "") -> dict:
    if not checklist_confirmed:
        raise PermissionError("cannot approve: originality checklist not confirmed")
    if item.get("status") != "pending_review":
        raise PermissionError(
            f"cannot approve item in status {item.get('status')!r} — it needs "
            "metadata and a pending_review status first"
        )
    item["status"] = "approved"
    item["review"] = {
        "approved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "checklist_confirmed": True,
        "note": note,
    }
    item["publish_at"] = publish_at_iso
    return _move(item, paths.APPROVED_DIR)


def reject(item: dict, reason: str) -> dict:
    item["status"] = "rejected"
    item["review"] = {
        "rejected_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "reason": reason,
    }
    return _move(item, paths.REJECTED_DIR)


def next_publish_slot(kind: str = "longform") -> str:
    """Next unclaimed schedule slot (RFC3339 UTC) after all approved items."""
    cfg = paths.settings()["scheduling"]
    slots = cfg["longform_slots"] if kind == "longform" else cfg["shorts_slots"]
    day_index = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}

    taken = set()
    paths.ensure_dirs()
    for f in paths.APPROVED_DIR.glob("*.json"):
        taken.add(json.loads(f.read_text()).get("publish_at"))

    candidate = dt.datetime.now(dt.timezone.utc)
    for _ in range(120):  # search up to ~17 weeks out
        candidate += dt.timedelta(days=1)
        for slot in slots:
            if day_index[slot["day"]] == candidate.weekday():
                hh, mm = map(int, str(slot["time"]).split(":"))
                ts = candidate.replace(hour=hh, minute=mm, second=0, microsecond=0)
                iso = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
                if iso not in taken:
                    return iso
    raise RuntimeError("no open publish slot found in the next 120 days")
