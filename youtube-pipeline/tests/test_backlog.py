import pytest

from pipeline import backlog


def test_add_topic_assigns_sequential_id(backlog_file):
    t = backlog.add_topic("New topic", "an angle", "myths-vs-records", path=backlog_file)
    assert t["id"] == "t0004"
    assert t["status"] == "unused"
    assert any(x["id"] == "t0004" for x in backlog.list_topics(path=backlog_file))


def test_add_topic_rejects_bad_pillar(backlog_file):
    with pytest.raises(ValueError):
        backlog.add_topic("x", "y", "not-a-pillar", path=backlog_file)


def test_next_topic_picks_first_unused(backlog_file):
    assert backlog.next_topic(path=backlog_file)["id"] == "t0003"


def test_next_topic_by_id_rejects_consumed(backlog_file):
    with pytest.raises(ValueError):
        backlog.next_topic("t0001", path=backlog_file)


def test_set_status_and_used_at(backlog_file):
    t = backlog.set_status("t0003", "used", path=backlog_file)
    assert t["status"] == "used"
    assert "used_at" in t


def test_set_status_unknown_id(backlog_file):
    with pytest.raises(KeyError):
        backlog.set_status("t9999", "used", path=backlog_file)


def test_recent_topics_window(backlog_file):
    recent = backlog.recent_topics(window=1, path=backlog_file)
    assert [t["id"] for t in recent] == ["t0002"]


def test_check_topic_flags_similar(backlog_file):
    candidate = {"title": "Why do clocks run clockwise?", "angle": "sundials set the direction"}
    report = backlog.check_topic(candidate, path=backlog_file)
    assert report["flagged"]
