import json

from pipeline import llm, paths, script_generator
from pipeline.script_generator import STRUCTURES, pick_structure, slugify

FAKE_SCRIPT = {
    "hook": "This map was wrong on purpose.",
    "hook_formula": "object-first",
    "editorial_angle": "The error was a copyright trap",
    "sections": [{"heading": "The trap", "narration": "words " * 50,
                  "broll_keywords": ["old map"]}],
    "outro": "outro",
    "factual_claims": [{"claim": "Agloe, NY was a paper town", "confidence": "solid",
                        "verify_via": "any atlas history"}],
    "shorts": [{"hook": "h", "narration": "n", "on_screen_text": ["AGLOE"]}],
}


def test_slugify():
    assert slugify("Why do clocks run clockwise?") == "why-do-clocks-run-clockwise"


def test_structure_rotation_avoids_recent():
    first = pick_structure()
    script_generator._record_structure(first["name"])
    second = pick_structure()
    assert second["name"] != first["name"]
    # After cycling through everything, all structures were used
    used = {first["name"], second["name"]}
    for _ in range(len(STRUCTURES) * 2):
        s = pick_structure()
        script_generator._record_structure(s["name"])
        used.add(s["name"])
    assert used == {s["name"] for s in STRUCTURES}


def test_generate_stages_item_and_consumes_topic(backlog_file, monkeypatch):
    monkeypatch.setattr(llm, "generate_json", lambda *a, **k: FAKE_SCRIPT)
    from pipeline import backlog

    topic = backlog.next_topic(path=backlog_file)
    item = script_generator.generate(topic, backlog_path=backlog_file)

    queue_file = paths.QUEUE_DIR / f"{item['slug']}.json"
    assert queue_file.exists()
    staged = json.loads(queue_file.read_text())
    assert staged["status"] == "draft"
    assert staged["script"]["factual_claims"], "factual claims must be present for review"
    assert "similarity" in staged

    refreshed = {t["id"]: t for t in backlog.list_topics(path=backlog_file)}
    assert refreshed[topic["id"]]["status"] == "queued"


def test_prompt_includes_style_guide_and_recent(backlog_file):
    from pipeline import backlog

    topic = backlog.next_topic(path=backlog_file)
    system, prompt = script_generator.build_prompt(
        topic, STRUCTURES[0], backlog.recent_topics(path=backlog_file)
    )
    assert "<style_guide>" in system
    assert "never invent" in system.lower() or "never state" in system.lower()
    assert "Thames" in prompt  # recent topics listed for distinctness
    assert topic["title"] in prompt
