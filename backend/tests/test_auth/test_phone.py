"""Tests for phone normalization."""
import pytest

from app.utils.phone import is_valid_phone, normalize_phone


class TestNormalize:
    @pytest.mark.parametrize(
        "input_phone,expected",
        [
            ("9876543210", "+919876543210"),
            ("919876543210", "+919876543210"),
            ("+919876543210", "+919876543210"),
            ("+91 98765 43210", "+919876543210"),
            ("+91-98765-43210", "+919876543210"),
            ("98765 43210", "+919876543210"),
            ("09876543210", "+919876543210"),
            ("00919876543210", "+919876543210"),
            ("+1 415 555 1234", "+14155551234"),
        ],
    )
    def test_various_inputs(self, input_phone, expected):
        assert normalize_phone(input_phone) == expected

    def test_empty_returns_empty(self):
        assert normalize_phone("") == ""
        assert normalize_phone(None) == ""

    def test_whitespace_only(self):
        assert normalize_phone("   ") == ""


class TestValidate:
    @pytest.mark.parametrize(
        "phone,valid",
        [
            ("+919876543210", True),
            ("+14155551234", True),
            ("9876543210", False),  # missing +
            ("+91", False),  # too short
            ("", False),
            ("+abcdefghij", False),
        ],
    )
    def test_validation(self, phone, valid):
        assert is_valid_phone(phone) is valid
