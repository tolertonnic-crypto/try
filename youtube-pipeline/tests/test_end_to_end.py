"""Full pipeline walkthrough with DRY_RUN — no network, no keys.

backlog -> generate -> metadata -> approve -> (upload gate) -> shorts staging
"""

import json

import pytest

from pipeline import llm, metadata_generator, paths, script_generator
from pipeline.review import queue as rq


@pytest.fixture(autouse=True)
def dry_run():
    llm.DRY_RUN = True
    yield
    llm.DRY_RUN = False


def test_full_flow(backlog_file):
    from pipeline import backlog

    # generate
    topic = backlog.next_topic(path=backlog_file)
    item = script_generator.generate(topic, backlog_path=backlog_file)
    assert item["status"] == "draft"
    assert item["script"]["sections"], "dry-run stub must satisfy the script schema"

    # metadata (+ FTC/UTM assembly on top of the stub body)
    item = metadata_generator.generate(item)
    assert item["status"] == "pending_review"
    desc = item["metadata"]["description"]
    # forgotten-figures pillar has affiliate links in the real config -> disclosure
    assert ("affiliate" in desc.lower()) == ("utm_campaign" in desc)

    # gate: cannot upload before approval
    from pipeline.youtube.upload import upload_video

    with pytest.raises(PermissionError):
        upload_video(item, "v.mp4", "2026-08-01T15:00:00Z")

    # approve via the queue API (the CLI is a thin wrapper over this)
    slot = rq.next_publish_slot("longform")
    approved = rq.approve(item, checklist_confirmed=True, publish_at_iso=slot, note="e2e")
    assert approved["status"] == "approved"

    # simulate a completed upload, then stage shorts
    approved["video_id"] = "vid001"
    (paths.APPROVED_DIR / f"{approved['slug']}.json").write_text(json.dumps(approved))
    from pipeline.shorts import stage_shorts

    shorts = stage_shorts(approved["slug"])
    assert shorts and all(s["status"] == "pending_review" for s in shorts)
