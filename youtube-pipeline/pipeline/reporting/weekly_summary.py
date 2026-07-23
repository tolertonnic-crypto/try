"""Weekly summary: top/bottom performers + suggested topic emphasis.

Pure local computation over the newest analytics CSV (pipeline.youtube.analytics)
plus the affiliate click join. Prints a report and suggests — never decides —
where next week's emphasis should go. A human reads it and picks topics.
"""

from __future__ import annotations

import csv

from .. import paths
from .affiliate import clicks_by_video, pillar_of
from ..script_generator import slugify


def _latest_csv():
    files = sorted(paths.ANALYTICS_DIR.glob("videos_*.csv"))
    if not files:
        raise FileNotFoundError(
            "no analytics CSVs — run `python cli.py analytics` first"
        )
    return files[-1]


def _rows() -> list[dict]:
    with open(_latest_csv(), newline="") as f:
        rows = []
        for row in csv.DictReader(f):
            try:
                row["_views"] = float(row.get("views") or 0)
                row["_retention"] = float(row.get("averageViewPercentage") or 0)
            except ValueError:
                row["_views"], row["_retention"] = 0.0, 0.0
            rows.append(row)
    return [r for r in rows if r["_views"] > 0]


def summarize(top_n: int = 5) -> str:
    rows = _rows()
    clicks = clicks_by_video()
    lines = [f"WEEKLY SUMMARY — source: {_latest_csv().name}", "=" * 60]

    ranked = sorted(rows, key=lambda r: r["_views"], reverse=True)
    lines.append("\nTOP PERFORMERS (views | retention%):")
    for r in ranked[:top_n]:
        lines.append(f"  ▲ {r['_views']:>8.0f} | {r['_retention']:>5.1f}%  {r['title']}")
    lines.append("\nBOTTOM PERFORMERS:")
    for r in ranked[-top_n:][::-1]:
        lines.append(f"  ▼ {r['_views']:>8.0f} | {r['_retention']:>5.1f}%  {r['title']}")

    # Aggregate by pillar (via the review archive; unknown pillar = skipped).
    pillar_stats: dict[str, dict] = {}
    for r in rows:
        pillar = pillar_of(slugify(r["title"]))
        if not pillar:
            continue
        stats = pillar_stats.setdefault(
            pillar, {"views": 0.0, "retention": [], "clicks": 0, "n": 0}
        )
        stats["views"] += r["_views"]
        stats["retention"].append(r["_retention"])
        stats["clicks"] += clicks.get(slugify(r["title"]), {}).get("clicks", 0)
        stats["n"] += 1

    if pillar_stats:
        lines.append("\nBY PILLAR (avg views | avg retention | affiliate clicks):")
        scored = []
        for pillar, s in pillar_stats.items():
            avg_views = s["views"] / s["n"]
            avg_ret = sum(s["retention"]) / len(s["retention"])
            lines.append(f"  {pillar:28s} {avg_views:>8.0f} | {avg_ret:>5.1f}% | {s['clicks']}")
            # Emphasis score: views weighted by retention, plus affiliate signal.
            scored.append((avg_views * (avg_ret / 100 or 0.01) + 50 * s["clicks"], pillar))
        scored.sort(reverse=True)
        best, worst = scored[0][1], scored[-1][1]
        lines.append(
            f"\nSUGGESTION: lean into '{best}' next week; give '{worst}' a rest or a "
            "format rethink. (Suggestion only — check the videos themselves before "
            "shifting: one bad thumbnail can sink a good pillar.)"
        )
    else:
        lines.append("\n(no pillar mapping yet — pillar stats appear once queue-tracked "
                     "videos have analytics)")

    report = "\n".join(lines)
    print(report)
    return report
