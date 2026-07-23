"""Script generator.

Takes a topic from the backlog and produces a long-form script + Shorts cuts
with a unique angle, hook, and structure. Structure varies between videos: a
library of narrative structures rotates, and the last N used structures
(data/structure_history.json) are excluded from selection so no fixed template
gets stamped onto every script.

Every generation reads style-guide.md into the prompt, so voice edits apply
immediately without code changes. The model must also list every factual claim
it makes so the review gate can require human verification (guardrail §6).
"""

from __future__ import annotations

import datetime as dt
import json
import re

from . import llm, paths
from .backlog import check_topic

# Narrative structure library. `beats` are guidance, not a rigid template —
# the model is told to adapt beat lengths to the material.
STRUCTURES = [
    {"name": "cold-open-mystery", "beats": "Open on the unexplained detail; establish stakes; investigate in layers; reveal; reframe what the viewer thought they knew."},
    {"name": "chronological-day", "beats": "Timestamped progression through a single day or event; tension rises with the clock; aftermath as coda."},
    {"name": "object-biography", "beats": "Follow one object across time and owners; each handoff opens a wider historical window; end on where it is now."},
    {"name": "question-cascade", "beats": "Start with an innocent question; each answer raises a better question; the final answer recontextualizes the first."},
    {"name": "myth-vs-record", "beats": "State the popular belief sympathetically; trace where it came from; walk the primary sources; land on what actually happened and why the myth stuck."},
    {"name": "consequence-rewind", "beats": "Open on the ripple effect in the present; rewind to the cause; move forward showing the chain; close the loop back to today."},
    {"name": "two-threads-converge", "beats": "Alternate between two seemingly unrelated storylines; converge them at the midpoint; the collision is the payoff."},
]

SCRIPT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["hook", "hook_formula", "sections", "outro", "factual_claims", "shorts", "editorial_angle"],
    "properties": {
        "hook": {"type": "string", "description": "Opening 15-20 seconds of narration"},
        "hook_formula": {"type": "string", "description": "Which style-guide hook formula was used"},
        "editorial_angle": {"type": "string", "description": "One sentence: the editorial choice that makes this video distinct"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["heading", "narration", "broll_keywords"],
                "properties": {
                    "heading": {"type": "string"},
                    "narration": {"type": "string"},
                    "broll_keywords": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "outro": {"type": "string"},
        "factual_claims": {
            "type": "array",
            "description": "Every checkable factual claim made in the script",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["claim", "confidence", "verify_via"],
                "properties": {
                    "claim": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["solid", "needs_verification", "contested"]},
                    "verify_via": {"type": "string", "description": "Where a human should check this"},
                },
            },
        },
        "shorts": {
            "type": "array",
            "description": "Self-contained vertical Shorts cut from this material",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["hook", "narration", "on_screen_text"],
                "properties": {
                    "hook": {"type": "string", "description": "First 2 seconds"},
                    "narration": {"type": "string", "description": "Max 45 seconds of narration"},
                    "on_screen_text": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
}


def _structure_history() -> list[str]:
    if paths.STRUCTURE_HISTORY.exists():
        return json.loads(paths.STRUCTURE_HISTORY.read_text())
    return []


def _record_structure(name: str) -> None:
    paths.ensure_dirs()
    history = _structure_history()
    history.append(name)
    paths.STRUCTURE_HISTORY.write_text(json.dumps(history[-20:]))


def pick_structure() -> dict:
    """Pick the least-recently-used structure outside the exclusion window."""
    window = paths.settings()["generation"]["structure_history_window"]
    history = _structure_history()
    excluded = set(history[-window:])
    candidates = [s for s in STRUCTURES if s["name"] not in excluded]
    # Prefer the structure used longest ago (or never).
    def last_used(s):
        try:
            return len(history) - 1 - history[::-1].index(s["name"])
        except ValueError:
            return -1
    candidates.sort(key=last_used)
    return candidates[0]


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60]


def build_prompt(topic: dict, structure: dict, recent: list[dict]) -> tuple[str, str]:
    gen = paths.settings()["generation"]
    style_guide = paths.STYLE_GUIDE.read_text()
    recent_list = "\n".join(f"- {t['title']} — {t.get('angle', '')}" for t in recent) or "- (none yet)"

    system = (
        "You are the script writer for a faceless history/micro-history YouTube "
        "channel. You follow the channel style guide exactly. You never invent "
        "quotes, never state contested claims as fact, and you list every "
        "checkable factual claim you make so a human editor can verify it.\n\n"
        f"<style_guide>\n{style_guide}\n</style_guide>"
    )
    prompt = (
        f"Write a long-form video script.\n\n"
        f"TOPIC: {topic['title']}\n"
        f"ANGLE: {topic['angle']}\n"
        f"PILLAR: {topic['pillar']}\n\n"
        f"STRUCTURE for this video (assigned — do not substitute): {structure['name']}\n"
        f"Structure guidance: {structure['beats']}\n"
        f"Adapt beat lengths to the material; the structure is a shape, not a template.\n\n"
        f"Length: {gen['script_words_min']}-{gen['script_words_max']} words of narration total.\n"
        f"Also produce {gen['shorts_per_video']} self-contained Shorts cuts (<=45s narration each) "
        f"from the strongest beats.\n\n"
        f"Recent videos (your angle must be clearly distinct from all of these):\n{recent_list}\n\n"
        f"Every claim a fact-checker could look up goes in factual_claims with an "
        f"honest confidence rating. If the topic involves legend or contested "
        f"history, the narration must label it as such."
    )
    return system, prompt


def generate(topic: dict, backlog_path=None) -> dict:
    """Generate a script package for a topic and stage it in the review queue.

    Returns the queue item dict (also written to review/queue/<slug>.json).
    """
    from .backlog import recent_topics, set_status  # local import to avoid cycles

    paths.ensure_dirs()
    structure = pick_structure()
    recent = recent_topics(path=backlog_path)
    sim = check_topic(topic, path=backlog_path)

    system, prompt = build_prompt(topic, structure, recent)
    script = llm.generate_json(system, prompt, SCRIPT_SCHEMA)

    slug = slugify(topic["title"])
    item = {
        "slug": slug,
        "topic": topic,
        "structure": structure["name"],
        "similarity": sim,
        "script": script,
        "status": "draft",  # draft -> metadata added -> pending_review -> approved/rejected
        "synthetic": paths.settings()["upload"]["default_synthetic"],
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    queue_file = paths.QUEUE_DIR / f"{slug}.json"
    queue_file.write_text(json.dumps(item, indent=2))
    _record_structure(structure["name"])
    set_status(topic["id"], "queued", path=backlog_path)
    return item
