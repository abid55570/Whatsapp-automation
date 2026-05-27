"""Pickup ready-time calculator + fulfillment helpers."""
from datetime import datetime, time, timedelta

from app.models.enums import PickupPrepStrategy
from app.models.fulfillment import FulfillmentConfig


def _parse_hhmm(s: str) -> time:
    """Parse 'HH:MM' to time. Default to 10:00 / 21:00 on error."""
    try:
        h, m = s.split(":")
        return time(int(h), int(m))
    except (ValueError, AttributeError):
        return time(10, 0)


def compute_ready_by(
    config: FulfillmentConfig | None,
    item_count: int,
    now: datetime,
) -> datetime:
    """Return when the order will be ready for pickup.

    Strategies:
      FIXED:    now + pickup_fixed_minutes
      PER_ITEM: now + (item_count × pickup_per_item_minutes)
      AUTO:     bucketed by item count
      SLOTS:    next available slot
    Result clamped to pickup_hours window. If past close → next open.
    """
    if config is None:
        # Sensible default: 30 min from now
        return now + timedelta(minutes=30)

    strategy = config.pickup_prep_strategy

    if strategy == PickupPrepStrategy.SLOTS:
        return _next_slot(config, now)

    if strategy == PickupPrepStrategy.PER_ITEM:
        prep = max(5, item_count * config.pickup_per_item_minutes)
    elif strategy == PickupPrepStrategy.AUTO:
        prep = _auto_minutes(item_count)
    else:  # FIXED
        prep = config.pickup_fixed_minutes

    ready = now + timedelta(minutes=prep)
    return _clamp_to_hours(ready, config)


def _auto_minutes(item_count: int) -> int:
    if item_count <= 3:
        return 15
    if item_count <= 10:
        return 30
    if item_count <= 20:
        return 60
    return 90


def _clamp_to_hours(target: datetime, config: FulfillmentConfig) -> datetime:
    """Push target into business hours.

    - If before open today → open today
    - If after close today → open tomorrow
    """
    open_t = _parse_hhmm(config.pickup_hours_start)
    close_t = _parse_hhmm(config.pickup_hours_end)

    open_dt = target.replace(
        hour=open_t.hour, minute=open_t.minute, second=0, microsecond=0
    )
    close_dt = target.replace(
        hour=close_t.hour, minute=close_t.minute, second=0, microsecond=0
    )

    if target < open_dt:
        return _skip_closed_days(open_dt, config)
    if target > close_dt:
        next_open = open_dt + timedelta(days=1)
        return _skip_closed_days(next_open, config)

    # Within hours — still check if day is closed
    if target.weekday() in (config.pickup_closed_days or []):
        next_open = open_dt + timedelta(days=1)
        return _skip_closed_days(next_open, config)

    return target


def _skip_closed_days(target: datetime, config: FulfillmentConfig) -> datetime:
    """If target lands on a closed day, advance to next open day."""
    closed = set(config.pickup_closed_days or [])
    if not closed:
        return target
    safeguard = 0
    while target.weekday() in closed and safeguard < 8:
        target += timedelta(days=1)
        safeguard += 1
    return target


def _next_slot(config: FulfillmentConfig, now: datetime) -> datetime:
    """Return the next available time slot from config.pickup_slots."""
    slots = config.pickup_slots or []
    if not slots:
        # No slots configured → fall back to FIXED 30min
        return now + timedelta(minutes=30)

    for slot in sorted(slots):
        slot_time = _parse_hhmm(slot)
        candidate = now.replace(
            hour=slot_time.hour, minute=slot_time.minute, second=0, microsecond=0
        )
        if candidate > now:
            return _skip_closed_days(candidate, config)

    # All today's slots passed → first slot tomorrow
    first = _parse_hhmm(sorted(slots)[0])
    tomorrow = (now + timedelta(days=1)).replace(
        hour=first.hour, minute=first.minute, second=0, microsecond=0
    )
    return _skip_closed_days(tomorrow, config)


def format_pickup_time(dt: datetime, lang: str | None = None) -> str:
    """Render a pickup time for a WhatsApp message."""
    # Today vs tomorrow
    return dt.strftime("%I:%M %p, %a %d %b").lstrip("0")
