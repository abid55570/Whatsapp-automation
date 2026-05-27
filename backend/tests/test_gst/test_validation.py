"""Validation tests for GSTIN, PAN, HSN, SAC, pincode."""
import pytest

from app.services.gst.validation import (
    VALID_GST_RATES,
    _gstin_checksum,
    gstin_pan,
    gstin_state_code,
    is_valid_gst_rate,
    is_valid_gstin,
    is_valid_hsn,
    is_valid_hsn_or_sac,
    is_valid_pan,
    is_valid_pincode,
    is_valid_sac,
    normalize_gstin,
    normalize_pan,
)
from app.services.gst.state_codes import (
    code_from_state_name,
    is_valid_state_code,
    state_name,
)


# ============================================================
# State codes
# ============================================================


class TestStateCodes:
    @pytest.mark.parametrize("code,expected", [
        ("07", "Delhi"),
        ("27", "Maharashtra"),
        ("33", "Tamil Nadu"),
        ("09", "Uttar Pradesh"),
        ("19", "West Bengal"),
    ])
    def test_known_codes(self, code, expected):
        assert state_name(code) == expected

    def test_unknown_code(self):
        assert state_name("99") == "Centre Jurisdiction"
        assert state_name("XX") is None
        assert state_name("") is None
        assert state_name(None) is None

    def test_reverse_lookup_exact(self):
        assert code_from_state_name("Delhi") == "07"
        assert code_from_state_name("DL") == "07"

    def test_reverse_lookup_fuzzy(self):
        assert code_from_state_name("delhi") == "07"
        assert code_from_state_name("maharashtra") == "27"

    def test_reverse_lookup_partial(self):
        assert code_from_state_name("Tamil") == "33"  # partial contains

    def test_reverse_lookup_unknown(self):
        assert code_from_state_name("Atlantis") is None
        assert code_from_state_name("") is None

    def test_is_valid_state_code(self):
        assert is_valid_state_code("27") is True
        assert is_valid_state_code("XX") is False
        assert is_valid_state_code(None) is False


# ============================================================
# GSTIN checksum (known real values)
# ============================================================


class TestGstinChecksum:
    @pytest.mark.parametrize("gstin", [
        # GSTINs whose self-computed checksum matches the published 15th char
        "27AAPFU0939F1ZV",   # Maharashtra
        "29AAGCB7383J1Z4",   # Karnataka
    ])
    def test_valid_known_gstins(self, gstin):
        assert is_valid_gstin(gstin) is True

    def test_checksum_matches_self(self):
        # Compute checksum for first 14 chars, ensure it matches the 15th
        for g in ["27AAPFU0939F1ZV", "29AAGCB7383J1Z4"]:
            assert _gstin_checksum(g[:14]) == g[14]


class TestGstinValidation:
    def test_format_too_short(self):
        assert is_valid_gstin("27AAPFU0939F1Z") is False

    def test_format_too_long(self):
        assert is_valid_gstin("27AAPFU0939F1ZVX") is False

    def test_empty(self):
        assert is_valid_gstin("") is False
        assert is_valid_gstin(None) is False

    def test_wrong_checksum(self):
        # Change the last char from V to W → invalid
        assert is_valid_gstin("27AAPFU0939F1ZW") is False

    def test_invalid_state_code(self):
        # State code 99 exists (Centre Jurisdiction) — should be valid; use a fake
        # Construct gstin starting with "00" — not in STATE_CODES
        bad = "00AAPFU0939F1ZV"
        assert is_valid_gstin(bad) is False

    def test_lowercase_input_normalized_internally(self):
        # is_valid_gstin uppercases/strips internally before regex check
        assert is_valid_gstin("27aapfu0939f1zv") is True

    def test_whitespace_input_normalized_internally(self):
        assert is_valid_gstin(" 27AAPFU0939F1ZV ") is True

    def test_normalize_helper(self):
        # The explicit normalize_gstin helper does the same job
        assert normalize_gstin(" 27aapfu0939f1zv ") == "27AAPFU0939F1ZV"


class TestGstinExtraction:
    def test_state_code(self):
        assert gstin_state_code("27AAPFU0939F1ZV") == "27"

    def test_state_code_none(self):
        assert gstin_state_code(None) is None
        assert gstin_state_code("") is None
        assert gstin_state_code("X") is None

    def test_pan_extraction(self):
        assert gstin_pan("27AAPFU0939F1ZV") == "AAPFU0939F"

    def test_pan_none(self):
        assert gstin_pan("short") is None
        assert gstin_pan(None) is None


# ============================================================
# PAN
# ============================================================


class TestPan:
    @pytest.mark.parametrize("pan", [
        "AAACH7409R",   # company (C)
        "AAPFU0939F",   # firm (F)
        "ABCPE1234L",   # individual (P)
    ])
    def test_valid(self, pan):
        assert is_valid_pan(pan) is True

    @pytest.mark.parametrize("pan", [
        "AAACH7409",    # too short
        "AAACH7409RR",  # too long
        "12345678AB",   # leading digits
        "AAACH740R9",   # wrong format
        "",
        None,
    ])
    def test_invalid(self, pan):
        assert is_valid_pan(pan) is False

    def test_normalize(self):
        assert normalize_pan(" aapfu0939f ") == "AAPFU0939F"
        assert normalize_pan(None) is None
        assert normalize_pan("") is None


# ============================================================
# HSN / SAC
# ============================================================


class TestHsn:
    @pytest.mark.parametrize("code", ["10", "1001", "10019910", "8703"])
    def test_valid_lengths(self, code):
        assert is_valid_hsn(code) is True

    @pytest.mark.parametrize("code", ["1", "123456789", "ABCD", "", None])
    def test_invalid(self, code):
        assert is_valid_hsn(code) is False


class TestSac:
    @pytest.mark.parametrize("code", ["996711", "999249", "997331"])
    def test_valid(self, code):
        assert is_valid_sac(code) is True

    @pytest.mark.parametrize("code", ["996", "9967110", "988711", "", None])
    def test_invalid(self, code):
        assert is_valid_sac(code) is False


class TestHsnOrSac:
    def test_either_works(self):
        assert is_valid_hsn_or_sac("1001") is True       # HSN
        assert is_valid_hsn_or_sac("996711") is True     # SAC
        assert is_valid_hsn_or_sac("xyz") is False


# ============================================================
# GST rate
# ============================================================


class TestGstRate:
    @pytest.mark.parametrize("rate", [0, 5, 12, 18, 28])
    def test_valid_slabs(self, rate):
        assert is_valid_gst_rate(rate) is True

    @pytest.mark.parametrize("rate", [1, 6, 10, 15, 30, -1, None])
    def test_invalid(self, rate):
        assert is_valid_gst_rate(rate) is False

    def test_constant(self):
        assert VALID_GST_RATES == frozenset({0, 5, 12, 18, 28})


# ============================================================
# Pincode
# ============================================================


class TestPincode:
    @pytest.mark.parametrize("pin", ["110001", "560001", "400001"])
    def test_valid(self, pin):
        assert is_valid_pincode(pin) is True

    @pytest.mark.parametrize("pin", ["011001", "12345", "1234567", "ABCDEF", "", None])
    def test_invalid(self, pin):
        assert is_valid_pincode(pin) is False
