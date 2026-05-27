"""Pure helper tests for processor.py — no DB / no network."""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.models.enums import MessageType, PaymentMethod
from app.services.whatsapp.processor import (
    _detect_payment_choice,
    _map_message_type,
    _t_cancel_msg,
    _t_confirm_msg,
    _t_payment_choice,
    _t_pickup_confirm,
)


class TestMapMessageType:
    @pytest.mark.parametrize(
        "meta,expected",
        [
            ("text", MessageType.TEXT),
            ("image", MessageType.IMAGE),
            ("document", MessageType.DOCUMENT),
            ("audio", MessageType.AUDIO),
            ("video", MessageType.VIDEO),
            ("sticker", MessageType.STICKER),
            ("location", MessageType.LOCATION),
            ("contacts", MessageType.CONTACTS),
            ("template", MessageType.TEMPLATE),
            ("interactive", MessageType.INTERACTIVE),
            ("button", MessageType.BUTTON),
            ("anything-else", MessageType.UNKNOWN),
        ],
    )
    def test_map(self, meta, expected):
        assert _map_message_type(meta) == expected


class TestDetectPaymentChoice:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("online", "online"),
            ("upi", "online"),
            ("cash", "cash"),
            ("cod", "cash"),
            ("nothing relevant", None),
            (None, None),
            ("", None),
            ("Online please", "online"),
            ("hum cash karenge", "cash"),
        ],
    )
    def test_detect(self, text, expected):
        assert _detect_payment_choice(text) == expected


class TestCancelMsg:
    @pytest.mark.parametrize("lang", ["english", "hindi", "hinglish", "bengali", "urdu", "bhojpuri"])
    def test_returns_non_empty(self, lang):
        assert "❌" in _t_cancel_msg(lang)

    def test_unknown_lang_defaults_english(self):
        out = _t_cancel_msg("klingon")
        assert "canceled" in out.lower()


class TestConfirmMsg:
    def test_english_cash(self):
        msg = _t_confirm_msg(
            order_number="ORD-1",
            total_paise=10000,
            pickup_time=datetime.now(timezone.utc),
            payment_method=PaymentMethod.CASH_ON_PICKUP,
            payment_link_url=None,
            lang="english",
        )
        assert "Order #ORD-1" in msg
        assert "Cash on pickup" in msg
        assert "₹100" in msg

    def test_english_online(self):
        msg = _t_confirm_msg(
            order_number="ORD-2",
            total_paise=15050,
            pickup_time=datetime.now(timezone.utc),
            payment_method=PaymentMethod.ONLINE,
            payment_link_url="https://rzp.io/i/test",
            lang="english",
        )
        assert "rzp.io" in msg

    @pytest.mark.parametrize("lang", ["hindi", "hinglish", "bengali", "urdu", "bhojpuri"])
    def test_all_langs(self, lang):
        msg = _t_confirm_msg(
            "ORD-3", 9999, datetime.now(timezone.utc),
            PaymentMethod.CASH_ON_PICKUP, None, lang,
        )
        assert "ORD-3" in msg


class TestPaymentChoiceMsg:
    @pytest.mark.parametrize("lang", ["english", "hindi", "hinglish", "bengali", "urdu", "bhojpuri", None])
    def test_returns_msg(self, lang):
        out = _t_payment_choice(lang)
        assert "💳" in out or "online" in out.lower()


class TestPickupConfirmMsg:
    def test_with_address(self):
        biz = SimpleNamespace(
            fulfillment_config=SimpleNamespace(pickup_address="Shop 5, Main Road"),
        )
        msg = _t_pickup_confirm(biz, datetime.now(timezone.utc), "english")
        assert "Shop 5" in msg

    def test_without_address(self):
        biz = SimpleNamespace(fulfillment_config=None)
        msg = _t_pickup_confirm(biz, datetime.now(timezone.utc), "hinglish")
        assert "YES" in msg
