import json

import pytest

from pipeline import paths
from pipeline.review import queue as rq
from pipeline.shorts import stage_shorts
from tests.conftest import write_queue_item


@pytest.fixture
def approved_parent(sample_item):
    sample_item["script"]["shorts"] = [
        {"hook": "This map lied on purpose", "narration": "n1", "on_screen_text": ["AGLOE"]},
        {"hook": "A town that only existed on paper", "narration": "n2", "on_screen_text": []},
    ]
    write_queue_item(sample_item)
    item = rq.approve(sample_item, True, "2026-08-04T15:00:00Z", note="ok")
    item["video_id"] = "abc123xyz"
    (paths.APPROVED_DIR / f"{item['slug']}.json").write_text(json.dumps(item))
    return item


def test_stage_shorts_creates_queue_items(approved_parent):
    staged = stage_shorts("test-video")
    assert [s["slug"] for s in staged] == ["test-video-short-1", "test-video-short-2"]
    pending = rq.pending_items()
    assert len(pending) == 2
    assert all(i["kind"] == "short" for i in pending)


def test_shorts_link_back_to_parent(approved_parent):
    staged = stage_shorts("test-video")
    assert "https://youtu.be/abc123xyz" in staged[0]["metadata"]["description"]
    assert staged[0]["parent_slug"] == "test-video"
    assert staged[0]["metadata"]["title"].endswith("#Shorts")


def test_shorts_inherit_synthetic_flag_and_claims(approved_parent):
    approved_parent["script"]["factual_claims"] = [
        {"claim": "c", "confidence": "solid", "verify_via": "v"}]
    (paths.APPROVED_DIR / "test-video.json").write_text(json.dumps(approved_parent))
    staged = stage_shorts("test-video")
    assert staged[0]["synthetic"] == approved_parent["synthetic"]
    assert staged[0]["script"]["factual_claims"]


def test_shorts_require_approved_parent(sample_item):
    write_queue_item(sample_item)  # still pending_review, not approved
    with pytest.raises(FileNotFoundError):
        stage_shorts("test-video")


def test_shorts_still_pass_the_gate(approved_parent):
    """A staged Short is not uploadable until it is itself approved."""
    from pipeline.youtube.upload import upload_video

    short = stage_shorts("test-video")[0]
    with pytest.raises(PermissionError):
        upload_video(short, "short.mp4", "2026-08-05T16:00:00Z")


def test_shorts_get_shorts_slots(approved_parent):
    slot = rq.next_publish_slot("shorts")
    import datetime as dt

    ts = dt.datetime.strptime(slot, "%Y-%m-%dT%H:%M:%SZ")
    assert ts.weekday() in (0, 2, 4)  # MON/WED/FRI per settings.yml
