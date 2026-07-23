"""Title / description / tags generator.

The model proposes titles, a description body, and tags from the finished
script. Affiliate links and the FTC disclosure are assembled in code, not by
the model: `build_description()` refuses to emit any affiliate link unless the
disclosure is present (guardrail §6 — no exceptions), and every link is
UTM-tagged per video so conversions are attributable.
"""

from __future__ import annotations

import json
import urllib.parse

from . import llm, paths

METADATA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["titles", "description_body", "tags"],
    "properties": {
        "titles": {
            "type": "array",
            "description": "3 title options, best first, each <=70 chars, no clickbait",
            "items": {"type": "string"},
        },
        "description_body": {
            "type": "string",
            "description": "2-3 short paragraphs describing the video, no links, no hashtags",
        },
        "tags": {"type": "array", "items": {"type": "string"}, "description": "10-15 tags"},
    },
}


def utm_tag(url: str, video_slug: str, amazon_tag: str = "") -> str:
    """Append UTM params (and Amazon Associates tag when configured) to a URL."""
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qsl(parsed.query)
    query += [
        ("utm_source", "youtube"),
        ("utm_medium", "description"),
        ("utm_campaign", video_slug),
    ]
    if amazon_tag and "amazon." in parsed.netloc:
        query.append(("tag", amazon_tag))
    return urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query)))


def pick_links(pillar: str, cfg: dict | None = None) -> list[dict]:
    cfg = cfg or paths.links_config()
    max_links = cfg.get("max_links_per_video", 3)
    matched = [l for l in cfg.get("links", []) if pillar in l.get("pillars", [])]
    return matched[:max_links]


def build_description(body: str, pillar: str, video_slug: str, cfg: dict | None = None) -> str:
    """Assemble the final description. FTC disclosure ALWAYS accompanies links."""
    cfg = cfg or paths.links_config()
    links = pick_links(pillar, cfg)
    parts = [body.strip()]
    if links:
        amazon_tag = cfg.get("amazon_tag", "") or ""
        lines = ["", "📚 Mentioned & recommended:"]
        for link in links:
            lines.append(f"▸ {link['label']}: {utm_tag(link['url'], video_slug, amazon_tag)}")
        parts.append("\n".join(lines))
        disclosure = cfg.get("ftc_disclosure", "").strip()
        if not disclosure:
            raise ValueError(
                "links.yml has affiliate links but no ftc_disclosure — refusing to "
                "build a description with undisclosed affiliate links"
            )
        parts.append("\n" + disclosure)
    return "\n".join(parts).strip()


def generate(item: dict) -> dict:
    """Add metadata to a queue item (in place) and rewrite its queue file."""
    style_guide = paths.STYLE_GUIDE.read_text()
    script = item["script"]
    narration = "\n\n".join(s["narration"] for s in script["sections"])
    system = (
        "You write YouTube metadata for a history channel. Titles promise exactly "
        "what the video delivers — specific, concrete, no clickbait, and consistent "
        f"with this style guide:\n<style_guide>\n{style_guide}\n</style_guide>"
    )
    prompt = (
        f"Video hook:\n{script['hook']}\n\nNarration:\n{narration[:6000]}\n\n"
        "Produce 3 title options (best first), a 2-3 paragraph description body "
        "(no links — links are added separately), and 10-15 search tags."
    )
    meta = llm.generate_json(system, prompt, METADATA_SCHEMA, max_tokens=16000)

    description = build_description(
        meta["description_body"], item["topic"]["pillar"], item["slug"]
    )
    item["metadata"] = {
        "title": meta["titles"][0],
        "title_options": meta["titles"],
        "description": description,
        "tags": meta["tags"],
        "category_id": paths.settings()["channel"]["category_id"],
    }
    item["status"] = "pending_review"
    queue_file = paths.QUEUE_DIR / f"{item['slug']}.json"
    queue_file.write_text(json.dumps(item, indent=2))
    return item
