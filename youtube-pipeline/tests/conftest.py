import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import paths  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    """Point all mutable state (data/, review/) at a temp dir; keep real config."""
    monkeypatch.setattr(paths, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(paths, "QUOTA_LEDGER", tmp_path / "data" / "quota_ledger.json")
    monkeypatch.setattr(paths, "STRUCTURE_HISTORY", tmp_path / "data" / "structure_history.json")
    monkeypatch.setattr(paths, "ANALYTICS_DIR", tmp_path / "data" / "analytics")
    monkeypatch.setattr(paths, "REVIEW_DIR", tmp_path / "review")
    monkeypatch.setattr(paths, "QUEUE_DIR", tmp_path / "review" / "queue")
    monkeypatch.setattr(paths, "APPROVED_DIR", tmp_path / "review" / "approved")
    monkeypatch.setattr(paths, "REJECTED_DIR", tmp_path / "review" / "rejected")
    monkeypatch.setattr(paths, "RENDERS_DIR", tmp_path / "renders")
    paths.ensure_dirs()
    yield tmp_path


@pytest.fixture
def backlog_file(tmp_path):
    """A scratch backlog with a mix of statuses."""
    f = tmp_path / "topics.yml"
    import yaml

    topics = [
        {"id": "t0001", "title": "Why do clocks run clockwise?",
         "angle": "Sundials set the direction", "pillar": "objects-with-a-past",
         "status": "used"},
        {"id": "t0002", "title": "The winter the Thames froze",
         "angle": "Frost fairs as economic emergency",
         "pillar": "the-day-everything-changed", "status": "used"},
        {"id": "t0003", "title": "The woman who mapped the ocean floor",
         "angle": "Marie Tharp proved continental drift",
         "pillar": "forgotten-figures", "status": "unused"},
    ]
    f.write_text(yaml.safe_dump({"topics": topics}, sort_keys=False))
    return f


@pytest.fixture
def sample_item():
    return {
        "slug": "test-video",
        "topic": {"id": "t0003", "title": "The woman who mapped the ocean floor",
                  "angle": "x", "pillar": "forgotten-figures"},
        "structure": "cold-open-mystery",
        "similarity": {"flagged": False, "matches": []},
        "script": {
            "hook": "hook", "hook_formula": "object-first", "editorial_angle": "e",
            "sections": [{"heading": "h", "narration": "n", "broll_keywords": ["map"]}],
            "outro": "o", "factual_claims": [], "shorts": [],
        },
        "status": "pending_review",
        "synthetic": True,
        "metadata": {
            "title": "T", "title_options": ["T"], "description": "d",
            "tags": ["history"], "category_id": "27",
        },
    }


def write_queue_item(item):
    f = paths.QUEUE_DIR / f"{item['slug']}.json"
    f.write_text(json.dumps(item))
    return f
