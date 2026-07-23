"""Topic backlog manager.

Topics live in backlog/topics.yml (human-editable). This module adds topics,
lists them, picks the next unused topic, marks state transitions, and runs the
similarity check against the last N used/queued topics.
"""

from __future__ import annotations

import datetime as dt

import yaml

from . import paths
from .similarity import similarity_report

VALID_STATUSES = {"unused", "queued", "used", "rejected"}
VALID_PILLARS = {
    "objects-with-a-past",
    "the-day-everything-changed",
    "forgotten-figures",
    "how-did-they-actually",
    "myths-vs-records",
}


def _load(path=None) -> dict:
    path = path or paths.BACKLOG_FILE
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("topics", [])
    return data


def _save(data: dict, path=None) -> None:
    path = path or paths.BACKLOG_FILE
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def list_topics(status: str | None = None, path=None) -> list[dict]:
    topics = _load(path)["topics"]
    if status:
        topics = [t for t in topics if t.get("status") == status]
    return topics


def add_topic(title: str, angle: str, pillar: str, path=None) -> dict:
    if pillar not in VALID_PILLARS:
        raise ValueError(f"pillar must be one of {sorted(VALID_PILLARS)}, got {pillar!r}")
    data = _load(path)
    next_num = 1 + max(
        (int(t["id"][1:]) for t in data["topics"] if str(t.get("id", "")).startswith("t")),
        default=0,
    )
    topic = {
        "id": f"t{next_num:04d}",
        "title": title,
        "angle": angle,
        "pillar": pillar,
        "status": "unused",
    }
    data["topics"].append(topic)
    _save(data, path)
    return topic


def set_status(topic_id: str, status: str, path=None) -> dict:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status {status!r}")
    data = _load(path)
    for t in data["topics"]:
        if t.get("id") == topic_id:
            t["status"] = status
            if status == "used":
                t["used_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
            _save(data, path)
            return t
    raise KeyError(f"no topic with id {topic_id}")


def recent_topics(window: int | None = None, path=None) -> list[dict]:
    """Last `window` topics that went into production (queued or used), most recent
    last. 'Recent' is by position in the file among consumed topics, which matches
    upload order because topics are consumed in order."""
    window = window or paths.settings()["similarity"]["window"]
    consumed = [t for t in _load(path)["topics"] if t.get("status") in ("queued", "used")]
    return consumed[-window:]


def check_topic(topic: dict, path=None) -> dict:
    cfg = paths.settings()["similarity"]
    return similarity_report(topic, recent_topics(cfg["window"], path=path), cfg["flag_threshold"])


def next_topic(topic_id: str | None = None, path=None) -> dict:
    """Pick a specific unused topic by id, or the first unused one."""
    topics = list_topics(path=path)
    if topic_id:
        for t in topics:
            if t["id"] == topic_id:
                if t.get("status") != "unused":
                    raise ValueError(f"topic {topic_id} has status {t.get('status')!r}, not 'unused'")
                return t
        raise KeyError(f"no topic with id {topic_id}")
    for t in topics:
        if t.get("status") == "unused":
            return t
    raise LookupError("backlog has no unused topics — add some with `cli.py backlog add`")
