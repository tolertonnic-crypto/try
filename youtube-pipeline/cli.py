#!/usr/bin/env python3
"""Pipeline CLI.

  python cli.py backlog list|add|check      manage the topic backlog
  python cli.py generate [--topic tNNNN]    script for the next (or given) topic
  python cli.py metadata <slug>             title/description/tags for a draft
  python cli.py review                      human review gate (approve/edit/reject)
  python cli.py upload <slug> <video.mp4>   upload an APPROVED item (scheduled)
  python cli.py shorts <parent-slug>        stage Shorts cuts from an approved video
  python cli.py analytics [--days N]        pull analytics -> CSV
  python cli.py weekly                      weekly summary + emphasis suggestion
  python cli.py quota                       show today's quota usage
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def _load_env():
    env = Path(__file__).resolve().parent / ".env"
    if env.exists():
        import os
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


def main() -> int:
    _load_env()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_backlog = sub.add_parser("backlog")
    b_sub = p_backlog.add_subparsers(dest="backlog_cmd", required=True)
    b_sub.add_parser("list").add_argument("--status", default=None)
    p_add = b_sub.add_parser("add")
    p_add.add_argument("title")
    p_add.add_argument("--angle", required=True)
    p_add.add_argument("--pillar", required=True)
    b_sub.add_parser("check").add_argument("topic_id")

    p_gen = sub.add_parser("generate")
    p_gen.add_argument("--topic", default=None, help="topic id, e.g. t0003")
    p_gen.add_argument("--dry-run", action="store_true",
                       help="placeholder output, no API call — for trying the flow")

    p_meta = sub.add_parser("metadata")
    p_meta.add_argument("slug")
    p_meta.add_argument("--dry-run", action="store_true")

    p_shorts = sub.add_parser("shorts", help="stage Shorts cuts from an approved long-form item")
    p_shorts.add_argument("parent_slug")

    sub.add_parser("review")

    p_up = sub.add_parser("upload")
    p_up.add_argument("slug")
    p_up.add_argument("video_file")

    p_an = sub.add_parser("analytics")
    p_an.add_argument("--days", type=int, default=28)

    sub.add_parser("weekly")
    sub.add_parser("quota")

    args = parser.parse_args()

    if args.cmd == "backlog":
        from pipeline import backlog
        if args.backlog_cmd == "list":
            for t in backlog.list_topics(status=args.status):
                print(f"{t['id']}  [{t.get('status','?'):8s}]  ({t['pillar']})  {t['title']}")
        elif args.backlog_cmd == "add":
            t = backlog.add_topic(args.title, args.angle, args.pillar)
            report = backlog.check_topic(t)
            print(f"added {t['id']}: {t['title']}")
            if report["flagged"]:
                print("⚠ similar to recent videos:")
                for m in report["flagged_matches"]:
                    print(f"    {m['score']:.2f}  {m['title']}")
        elif args.backlog_cmd == "check":
            t = backlog.next_topic(args.topic_id)
            report = backlog.check_topic(t)
            print("⚠ FLAGGED" if report["flagged"] else "ok — distinct from recent videos")
            for m in report["matches"]:
                print(f"    {m['score']:.2f}  {m['title']}")

    elif args.cmd == "generate":
        from pipeline import backlog, llm, script_generator
        if args.dry_run:
            llm.DRY_RUN = True
            print("(dry run — placeholder script, no API call)")
        topic = backlog.next_topic(args.topic)
        report = backlog.check_topic(topic)
        if report["flagged"]:
            print("⚠ topic is similar to recent videos:")
            for m in report["flagged_matches"]:
                print(f"    {m['score']:.2f}  {m['title']}")
            if input("Generate anyway? [y/N] ").strip().lower() != "y":
                return 1
        item = script_generator.generate(topic)
        print(f"✔ script staged: review/queue/{item['slug']}.json "
              f"(structure: {item['structure']})")
        print(f"  next: python cli.py metadata {item['slug']}")

    elif args.cmd == "metadata":
        from pipeline import llm, metadata_generator
        from pipeline.review.queue import load_item
        from pipeline.reporting.affiliate import record_links_for_item
        if args.dry_run:
            llm.DRY_RUN = True
            print("(dry run — placeholder metadata, no API call)")
        item = load_item(args.slug)
        item = metadata_generator.generate(item)
        record_links_for_item(item)
        print(f"✔ metadata added — item is pending_review. Run: python cli.py review")

    elif args.cmd == "shorts":
        from pipeline.shorts import stage_shorts
        staged = stage_shorts(args.parent_slug)
        for s in staged:
            print(f"✔ staged {s['slug']} (pending_review)")
        print("Review them with: python cli.py review")

    elif args.cmd == "review":
        from pipeline.review.cli import review_loop
        review_loop()

    elif args.cmd == "upload":
        from pipeline.review.queue import load_item
        from pipeline.youtube.upload import upload_video
        item = load_item(args.slug)
        confirm = lambda msg: input(f"{msg} [y/N] ").strip().lower() == "y"
        video_id = upload_video(item, args.video_file, item["publish_at"], confirm=confirm)
        from pipeline import backlog, paths
        import json
        item["video_id"] = video_id
        (paths.APPROVED_DIR / f"{item['slug']}.json").write_text(json.dumps(item, indent=2))
        backlog.set_status(item["topic"]["id"], "used")

    elif args.cmd == "analytics":
        from pipeline.youtube.analytics import pull
        pull(days=args.days)

    elif args.cmd == "weekly":
        from pipeline.reporting.weekly_summary import summarize
        summarize()

    elif args.cmd == "quota":
        from pipeline.youtube import quota
        from pipeline import paths
        print(f"used today (Pacific): {quota.used_today()} / "
              f"{paths.settings()['quota']['daily_limit']} units "
              f"({quota.remaining_today()} remaining)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
