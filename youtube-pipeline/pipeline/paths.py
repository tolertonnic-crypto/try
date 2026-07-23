"""Project paths and config loading. Everything resolves relative to the project
root so the CLI works from any cwd."""

from __future__ import annotations

import functools
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

STYLE_GUIDE = ROOT / "style-guide.md"
CONTENT_STRATEGY = ROOT / "content-strategy.md"
ORIGINALITY_CHECKLIST = ROOT / "originality-checklist.md"

CONFIG_DIR = ROOT / "config"
SETTINGS_FILE = CONFIG_DIR / "settings.yml"
LINKS_FILE = CONFIG_DIR / "links.yml"

BACKLOG_FILE = ROOT / "backlog" / "topics.yml"

DATA_DIR = ROOT / "data"
QUOTA_LEDGER = DATA_DIR / "quota_ledger.json"
STRUCTURE_HISTORY = DATA_DIR / "structure_history.json"
ANALYTICS_DIR = DATA_DIR / "analytics"

REVIEW_DIR = ROOT / "review"
QUEUE_DIR = REVIEW_DIR / "queue"
APPROVED_DIR = REVIEW_DIR / "approved"
REJECTED_DIR = REVIEW_DIR / "rejected"

RENDERS_DIR = ROOT / "renders"


def ensure_dirs() -> None:
    for d in (DATA_DIR, ANALYTICS_DIR, QUEUE_DIR, APPROVED_DIR, REJECTED_DIR, RENDERS_DIR):
        d.mkdir(parents=True, exist_ok=True)


@functools.lru_cache(maxsize=1)
def settings() -> dict:
    with open(SETTINGS_FILE) as f:
        return yaml.safe_load(f)


@functools.lru_cache(maxsize=1)
def links_config() -> dict:
    with open(LINKS_FILE) as f:
        return yaml.safe_load(f)
