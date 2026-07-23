"""Topic similarity: flag when a candidate is too close to recent videos.

Deliberately dependency-free (token Jaccard over title+angle). This runs on
every generation and costs zero API quota. It is a tripwire for a human, not a
verdict — flagged pairs are surfaced in the review queue for judgment.
"""

from __future__ import annotations

import re

_STOPWORDS = {
    "a", "an", "the", "of", "in", "on", "to", "and", "or", "for", "with",
    "how", "why", "what", "when", "who", "did", "do", "does", "was", "were",
    "is", "are", "it", "its", "that", "this", "they", "their", "actually",
    "history", "story", "never", "ever",
}


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def similarity_report(candidate: dict, recent: list[dict], threshold: float) -> dict:
    """Compare a candidate topic dict (title/angle) against recent topic dicts.

    Returns {"flagged": bool, "matches": [{id, title, score}, ...]} with all
    comparisons sorted by score, flagging any at or above the threshold.
    """
    cand_text = f"{candidate.get('title', '')} {candidate.get('angle', '')}"
    matches = []
    for topic in recent:
        text = f"{topic.get('title', '')} {topic.get('angle', '')}"
        score = jaccard(cand_text, text)
        matches.append({
            "id": topic.get("id"),
            "title": topic.get("title"),
            "score": round(score, 3),
        })
    matches.sort(key=lambda m: m["score"], reverse=True)
    flagged = [m for m in matches if m["score"] >= threshold]
    return {"flagged": bool(flagged), "threshold": threshold, "matches": matches[:5],
            "flagged_matches": flagged}
