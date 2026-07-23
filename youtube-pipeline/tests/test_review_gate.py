import pytest

from pipeline.review import queue as rq
from tests.conftest import write_queue_item


def test_pending_items_lists_queue(sample_item):
    write_queue_item(sample_item)
    assert [i["slug"] for i in rq.pending_items()] == ["test-video"]


def test_approve_requires_checklist(sample_item):
    write_queue_item(sample_item)
    with pytest.raises(PermissionError):
        rq.approve(sample_item, checklist_confirmed=False,
                   publish_at_iso="2026-08-01T15:00:00Z")


def test_approve_requires_pending_review_status(sample_item):
    sample_item["status"] = "draft"
    write_queue_item(sample_item)
    with pytest.raises(PermissionError):
        rq.approve(sample_item, True, "2026-08-01T15:00:00Z")


def test_approve_moves_to_approved(sample_item):
    write_queue_item(sample_item)
    item = rq.approve(sample_item, True, "2026-08-01T15:00:00Z", note="checked")
    assert item["status"] == "approved"
    assert item["publish_at"] == "2026-08-01T15:00:00Z"
    assert not rq.pending_items()
    assert rq.load_item("test-video")["review"]["note"] == "checked"


def test_reject_moves_to_rejected(sample_item):
    write_queue_item(sample_item)
    rq.reject(sample_item, "angle too close to t0001")
    assert rq.load_item("test-video")["status"] == "rejected"
    assert not rq.pending_items()


def test_upload_refuses_unapproved(sample_item):
    """The core guarantee: nothing publishes without passing the gate."""
    from pipeline.youtube.upload import upload_video

    with pytest.raises(PermissionError):
        upload_video(sample_item, "video.mp4", "2026-08-01T15:00:00Z")


def test_next_publish_slot_matches_schedule(sample_item):
    slot = rq.next_publish_slot("longform")
    import datetime as dt

    ts = dt.datetime.strptime(slot, "%Y-%m-%dT%H:%M:%SZ")
    assert ts.weekday() in (1, 5)  # TUE or SAT per settings.yml
    assert ts.strftime("%H:%M") == "15:00"


def test_slots_not_double_booked(sample_item):
    write_queue_item(sample_item)
    first = rq.next_publish_slot("longform")
    rq.approve(sample_item, True, first)
    assert rq.next_publish_slot("longform") != first
