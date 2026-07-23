"""Local YouTube Data API quota ledger.

Google gives no API to read your remaining quota, so we track usage ourselves.
Every call the pipeline makes is recorded with its documented unit cost
(config/settings.yml -> quota.costs). Quota resets at midnight Pacific time —
the ledger keys usage by Pacific date.

`charge()` is the single gate: it warns (and asks for confirmation via the
provided callback) before quota-heavy operations, and raises if the day's
budget would be exceeded.
"""

from __future__ import annotations

import datetime as dt
import json
import zoneinfo

from .. import paths

PACIFIC = zoneinfo.ZoneInfo("America/Los_Angeles")


class QuotaExceeded(RuntimeError):
    pass


def _today() -> str:
    return dt.datetime.now(PACIFIC).strftime("%Y-%m-%d")


def _load() -> dict:
    if paths.QUOTA_LEDGER.exists():
        return json.loads(paths.QUOTA_LEDGER.read_text())
    return {}


def _save(ledger: dict) -> None:
    paths.ensure_dirs()
    paths.QUOTA_LEDGER.write_text(json.dumps(ledger, indent=2))


def cost_of(operation: str) -> int:
    costs = paths.settings()["quota"]["costs"]
    if operation not in costs:
        raise KeyError(f"unknown operation {operation!r} — add its cost to settings.yml")
    return costs[operation]


def used_today() -> int:
    return sum(e["units"] for e in _load().get(_today(), []))


def remaining_today() -> int:
    return paths.settings()["quota"]["daily_limit"] - used_today()


def charge(operation: str, confirm=None) -> int:
    """Record quota usage for `operation`. Call this right before the API call.

    `confirm` is an optional callback(message) -> bool used to warn before
    quota-heavy operations (cost >= quota.warn_at_units). Non-interactive
    callers can pass None (no prompt, still enforced against the daily limit).
    Raises QuotaExceeded if the operation would blow the daily budget.
    """
    units = cost_of(operation)
    cfg = paths.settings()["quota"]
    remaining = remaining_today()
    if units > remaining:
        raise QuotaExceeded(
            f"{operation} costs {units} units but only {remaining} remain today "
            f"(limit {cfg['daily_limit']}, resets midnight Pacific)"
        )
    if confirm is not None and units >= cfg["warn_at_units"]:
        message = (
            f"⚠ {operation} costs {units} quota units "
            f"({remaining} remaining of {cfg['daily_limit']} today). Proceed?"
        )
        if not confirm(message):
            raise QuotaExceeded(f"{operation} declined by user")
    ledger = _load()
    ledger.setdefault(_today(), []).append(
        {"op": operation, "units": units,
         "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    )
    _save(ledger)
    return units
