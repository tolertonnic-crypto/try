"""Interactive review CLI — the human gate.

`python cli.py review` walks every pending item: shows the script, metadata,
similarity report, factual claims, and the originality checklist. The reviewer
approves (assigning the next publish slot), edits (opens the JSON in $EDITOR),
rejects, or skips. Only approved items can ever be uploaded.
"""

from __future__ import annotations

import json
import os
import subprocess
import textwrap

from .. import paths
from . import queue


def _hr(char="─", width=72):
    print(char * width)


def _wrap(text, indent="  "):
    for para in text.split("\n"):
        print(textwrap.fill(para, width=78, initial_indent=indent, subsequent_indent=indent)
              if para.strip() else "")


def show_item(item: dict) -> None:
    _hr("═")
    kind = item.get("kind", "longform")
    print(f"■ {item['slug']}   [{item['status']}]   {kind}   pillar: {item['topic']['pillar']}")
    if kind == "short":
        print(f"  cut from approved long-form: {item.get('parent_slug')}")
    _hr()
    meta = item.get("metadata", {})
    if meta:
        print(f"TITLE: {meta['title']}")
        alts = meta.get("title_options", [])[1:]
        if alts:
            print(f"  alternates: {' | '.join(alts)}")
    print(f"STRUCTURE: {item['structure']}   HOOK FORMULA: {item['script'].get('hook_formula')}")
    print(f"EDITORIAL ANGLE: {item['script'].get('editorial_angle')}")
    print(f"SYNTHETIC CONTENT FLAG: {item.get('synthetic')}")

    sim = item.get("similarity", {})
    print(f"\nSIMILARITY vs last {paths.settings()['similarity']['window']}: "
          f"{'⚠ FLAGGED' if sim.get('flagged') else 'ok'}")
    for m in sim.get("matches", [])[:3]:
        marker = " ⚠" if m["score"] >= sim.get("threshold", 1) else ""
        print(f"    {m['score']:.2f}  {m['title']}{marker}")

    print("\nHOOK:")
    _wrap(item["script"]["hook"])
    print("\nSECTIONS:")
    for s in item["script"]["sections"]:
        print(f"  ● {s['heading']}")
        _wrap(s["narration"], indent="    ")
    print("\nOUTRO:")
    _wrap(item["script"]["outro"])

    print("\nSHORTS CUTS:")
    for i, sh in enumerate(item["script"].get("shorts", []), 1):
        print(f"  [{i}] {sh['hook']}")

    print("\nFACTUAL CLAIMS TO VERIFY (human, against sources outside this tool):")
    for c in item["script"].get("factual_claims", []):
        flag = {"solid": " ", "needs_verification": "⚠", "contested": "‼"}.get(c["confidence"], "?")
        print(f"  {flag} [{c['confidence']}] {c['claim']}")
        print(f"       check via: {c['verify_via']}")

    if meta:
        print("\nDESCRIPTION (as it will publish — verify FTC disclosure is visible):")
        _wrap(meta["description"])
        print(f"\nTAGS: {', '.join(meta.get('tags', []))}")


def show_checklist() -> None:
    _hr()
    print(paths.ORIGINALITY_CHECKLIST.read_text())
    _hr()


def review_loop() -> None:
    items = queue.pending_items()
    if not items:
        print("Review queue is empty.")
        return
    print(f"{len(items)} item(s) awaiting review.\n")
    for item in items:
        show_item(item)
        while True:
            choice = input(
                "\n[a]pprove  [e]dit json  [r]eject  [s]kip  [c]hecklist  [q]uit > "
            ).strip().lower()
            if choice == "c":
                show_checklist()
            elif choice == "e":
                f = paths.QUEUE_DIR / f"{item['slug']}.json"
                subprocess.call([os.environ.get("EDITOR", "nano"), str(f)])
                item.clear()
                item.update(json.loads(f.read_text()))
                show_item(item)
            elif choice == "a":
                if item.get("status") != "pending_review":
                    print("This item has no metadata yet — run `cli.py metadata` first.")
                    continue
                show_checklist()
                confirmed = input(
                    "Confirm EVERY checklist item is satisfied (type 'yes'): "
                ).strip().lower() == "yes"
                if not confirmed:
                    print("Not approved — checklist not confirmed.")
                    continue
                note = input("Review note (what did you check/change?): ").strip()
                kind = "shorts" if item.get("kind") == "short" else "longform"
                slot = queue.next_publish_slot(kind)
                custom = input(f"Publish slot [{slot}] (enter to accept, or RFC3339): ").strip()
                queue.approve(item, True, custom or slot, note)
                print(f"✔ approved, scheduled for {custom or slot}. "
                      "Upload with: python cli.py upload " + item["slug"])
                break
            elif choice == "r":
                reason = input("Rejection reason: ").strip() or "unspecified"
                queue.reject(item, reason)
                print("✘ rejected.")
                break
            elif choice == "s":
                break
            elif choice == "q":
                return
