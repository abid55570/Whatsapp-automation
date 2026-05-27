"""Tests for the pickup ready-time calculator."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import pytest

from app.models.enums import PickupPrepStrategy
from app.services.orders.fulfillment import compute_ready_by


@dataclass
class FakeConfig:
    """Stand-in for FulfillmentConfig without DB."""

    pickup_prep_strategy: PickupPrepStrategy = PickupPrepStrategy.FIXED
    pickup_fixed_minutes: int = 30
    pickup_per_item_minutes: int = 5
    pickup_slots: list[str] = field(default_factory=list)
    pickup_hours_start: str = "10:00"
    pickup_hours_end: str = "21:00"
    pickup_closed_days: list[int] = field(default_factory=list)


# Tuesday 2026-05-20 12:00 (within hours)
NOW = datetime(2026, 5, 20, 12, 0, 0, tzinfo=timezone.utc)


class TestFixed:
    def test_default_30min(self):
        c = FakeConfig()
        ready = compute_ready_by(c, item_count=5, now=NOW)
        assert ready == NOW + timedelta(minutes=30)

    def test_custom_fixed(self):
        c = FakeConfig(pickup_fixed_minutes=45)
        ready = compute_ready_by(c, item_count=1, now=NOW)
        assert ready == NOW + timedelta(minutes=45)


class TestPerItem:
    def test_5_items(self):
        c = FakeConfig(
            pickup_prep_strategy=PickupPrepStrategy.PER_ITEM,
            pickup_per_item_minutes=5,
        )
        ready = compute_ready_by(c, item_count=5, now=NOW)
        assert ready == NOW + timedelta(minutes=25)

    def test_min_5_for_single_item(self):
        c = FakeConfig(
            pickup_prep_strategy=PickupPrepStrategy.PER_ITEM,
            pickup_per_item_minutes=2,
        )
        # 1 item × 2 min = 2, but min is 5
        ready = compute_ready_by(c, item_count=1, now=NOW)
        assert ready == NOW + timedelta(minutes=5)


class TestAuto:
    @pytest.mark.parametrize(
        "items,expected_min",
        [(1, 15), (3, 15), (4, 30), (10, 30), (11, 60), (20, 60), (21, 90), (50, 90)],
    )
    def test_buckets(self, items, expected_min):
        c = FakeConfig(pickup_prep_strategy=PickupPrepStrategy.AUTO)
        ready = compute_ready_by(c, item_count=items, now=NOW)
        assert ready == NOW + timedelta(minutes=expected_min)


class TestSlots:
    def test_next_slot_today(self):
        c = FakeConfig(
            pickup_prep_strategy=PickupPrepStrategy.SLOTS,
            pickup_slots=["11:00", "14:00", "17:00", "20:00"],
        )
        ready = compute_ready_by(c, item_count=1, now=NOW)
        # NOW = 12:00 → next slot is 14:00
        assert ready.hour == 14
        assert ready.day == 20

    def test_all_slots_passed_rolls_tomorrow(self):
        late = NOW.replace(hour=21, minute=30)
        c = FakeConfig(
            pickup_prep_strategy=PickupPrepStrategy.SLOTS,
            pickup_slots=["11:00", "14:00", "17:00", "20:00"],
        )
        ready = compute_ready_by(c, item_count=1, now=late)
        assert ready.day == 21
        assert ready.hour == 11

    def test_empty_slots_fallback(self):
        c = FakeConfig(
            pickup_prep_strategy=PickupPrepStrategy.SLOTS,
            pickup_slots=[],
        )
        ready = compute_ready_by(c, item_count=1, now=NOW)
        # Falls back to 30min
        assert ready == NOW + timedelta(minutes=30)


class TestBusinessHours:
    def test_after_close_rolls_tomorrow_open(self):
        late = NOW.replace(hour=20, minute=45)  # 8:45 PM
        c = FakeConfig(
            pickup_fixed_minutes=30,
            pickup_hours_start="10:00",
            pickup_hours_end="21:00",
        )
        ready = compute_ready_by(c, item_count=1, now=late)
        # 8:45 + 30min = 9:15 PM → past 9 PM close → tomorrow 10 AM
        assert ready.day == 21
        assert ready.hour == 10

    def test_before_open_clamps_to_open(self):
        early = NOW.replace(hour=8, minute=0)
        c = FakeConfig(pickup_fixed_minutes=10)
        ready = compute_ready_by(c, item_count=1, now=early)
        # 8:10 → before 10:00 open → 10:00
        assert ready.hour == 10
        assert ready.day == 20


class TestClosedDays:
    def test_sunday_closed_rolls_to_monday(self):
        sat_evening = datetime(2026, 5, 23, 22, 0, 0, tzinfo=timezone.utc)
        # Sat 10 PM → after close → tomorrow (Sun)
        # Sunday is closed → roll to Monday
        c = FakeConfig(
            pickup_fixed_minutes=30,
            pickup_closed_days=[6],  # Sunday
        )
        ready = compute_ready_by(c, item_count=1, now=sat_evening)
        assert ready.weekday() == 0  # Monday


class TestNoneConfig:
    def test_default_30min_when_no_config(self):
        ready = compute_ready_by(None, item_count=5, now=NOW)
        assert ready == NOW + timedelta(minutes=30)
