import pytest

from pipeline.youtube import quota


def test_charge_records_usage():
    assert quota.used_today() == 0
    quota.charge("videos.list")
    assert quota.used_today() == 1


def test_unknown_operation_raises():
    with pytest.raises(KeyError):
        quota.cost_of("videos.explode")


def test_expensive_op_asks_for_confirmation():
    asked = []

    def confirm(msg):
        asked.append(msg)
        return True

    quota.charge("videos.insert", confirm=confirm)  # 1600 >= warn threshold
    assert asked, "expected a confirmation prompt for a quota-heavy operation"
    assert quota.used_today() == 1600


def test_declined_confirmation_blocks_charge():
    with pytest.raises(quota.QuotaExceeded):
        quota.charge("videos.insert", confirm=lambda msg: False)
    assert quota.used_today() == 0


def test_daily_limit_enforced(monkeypatch):
    for _ in range(6):
        quota.charge("videos.insert")  # 6 * 1600 = 9600
    with pytest.raises(quota.QuotaExceeded):
        quota.charge("videos.insert")  # would exceed 10000
