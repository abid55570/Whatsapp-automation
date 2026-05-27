"""Tests for the order text parser."""
from dataclasses import dataclass

import pytest

from app.services.orders.parser import (
    HINDI_NUMBERS,
    fuzzy_match_product,
    looks_like_order,
    parse_order_text,
)


@dataclass
class FakeProduct:
    name: str
    price_paise: int = 0


PRODUCTS = [
    FakeProduct("Atta 5 kg"),
    FakeProduct("Toor Dal 1 kg"),
    FakeProduct("Basmati Rice 5 kg"),
    FakeProduct("Mustard Oil 1 L"),
    FakeProduct("Tata Salt 1 kg"),
    FakeProduct("Cheese Burger"),
    FakeProduct("Margherita Pizza"),
    FakeProduct("Lassi"),
    FakeProduct("Coca-Cola"),
]


class TestLooksLikeOrder:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("2 cheese burger", True),
            ("do atta", True),
            ("pizza 1", True),
            ("hi", False),
            ("menu bhejo", False),
            ("3 pizza, 2 lassi", True),
            ("तीन अट्टा", True),
            ("", False),
            ("123", False),  # no word
        ],
    )
    def test_detection(self, text, expected):
        assert looks_like_order(text) == expected


class TestFuzzyMatch:
    def test_exact_name(self):
        m = fuzzy_match_product("cheese burger", PRODUCTS)
        assert m is not None
        assert m[0].name == "Cheese Burger"

    def test_typo(self):
        m = fuzzy_match_product("chese burgr", PRODUCTS)
        assert m is not None
        assert m[0].name == "Cheese Burger"

    def test_partial_name(self):
        m = fuzzy_match_product("atta", PRODUCTS)
        assert m is not None
        assert m[0].name == "Atta 5 kg"

    def test_low_threshold_no_match(self):
        m = fuzzy_match_product("xyz random thing", PRODUCTS)
        assert m is None


class TestParseOrder:
    def test_single_with_qty(self):
        cart = parse_order_text("2 cheese burger", PRODUCTS)
        assert len(cart) == 1
        assert cart[0][0].name == "Cheese Burger"
        assert cart[0][1] == 2

    def test_multiple_items(self):
        cart = parse_order_text("2 cheese burger, 1 pizza", PRODUCTS)
        assert len(cart) == 2
        names = {c[0].name for c in cart}
        assert "Cheese Burger" in names
        assert "Margherita Pizza" in names

    def test_hindi_numbers(self):
        cart = parse_order_text("do atta", PRODUCTS)
        assert len(cart) == 1
        assert cart[0][1] == 2

    def test_hindi_multiple(self):
        cart = parse_order_text("do atta aur ek toor dal", PRODUCTS)
        assert len(cart) == 2
        qty_by_name = {c[0].name: c[1] for c in cart}
        assert qty_by_name["Atta 5 kg"] == 2
        assert qty_by_name["Toor Dal 1 kg"] == 1

    def test_devanagari_numbers(self):
        cart = parse_order_text("तीन pizza", PRODUCTS)
        assert len(cart) == 1
        assert cart[0][1] == 3

    def test_trailing_x_quantity(self):
        cart = parse_order_text("pizza × 3", PRODUCTS)
        assert len(cart) == 1
        assert cart[0][1] == 3

    def test_trailing_number(self):
        cart = parse_order_text("pizza 2", PRODUCTS)
        assert len(cart) == 1
        assert cart[0][1] == 2

    def test_no_qty_defaults_to_one(self):
        cart = parse_order_text("pizza, lassi", PRODUCTS)
        assert len(cart) == 2
        for _p, qty, _score in cart:
            assert qty == 1

    def test_dedup_same_product(self):
        cart = parse_order_text("1 pizza, 2 pizza", PRODUCTS)
        assert len(cart) == 1
        assert cart[0][1] == 3

    def test_prefix_stripped(self):
        cart = parse_order_text("mujhe 2 atta chahiye", PRODUCTS)
        # "chahiye" at end → not stripped, but fuzzy still matches "atta"
        assert len(cart) >= 1

    def test_unknown_items_skipped(self):
        cart = parse_order_text("2 jetpack, 1 atta", PRODUCTS)
        # jetpack won't match, atta will
        assert len(cart) == 1
        assert cart[0][0].name == "Atta 5 kg"

    def test_empty_text(self):
        assert parse_order_text("", PRODUCTS) == []

    def test_empty_products(self):
        assert parse_order_text("2 pizza", []) == []

    def test_kirana_monthly_ration(self):
        text = "5 kg atta, 1 kg toor dal, 1 L oil, 1 kg salt"
        cart = parse_order_text(text, PRODUCTS)
        names = {c[0].name for c in cart}
        # Should match at least 3 of the 4 items
        assert len(names) >= 3
        assert "Atta 5 kg" in names
        assert "Toor Dal 1 kg" in names

    def test_qty_cap(self):
        cart = parse_order_text("99999 pizza", PRODUCTS)
        assert cart[0][1] == 1000  # capped


class TestHindiNumbers:
    @pytest.mark.parametrize(
        "word,expected",
        [
            ("ek", 1), ("do", 2), ("teen", 3), ("char", 4), ("paanch", 5),
            ("एक", 1), ("दो", 2), ("तीन", 3),
        ],
    )
    def test_word_to_number(self, word, expected):
        assert HINDI_NUMBERS[word] == expected
