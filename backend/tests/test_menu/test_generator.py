"""Tests for menu / services text generation."""
from dataclasses import dataclass

import pytest

from app.services.menu.generator import (
    category_emoji,
    generate_menu_text,
    generate_services_text,
)


# Lightweight stand-ins so we don't need real ORM rows
@dataclass
class FakeProduct:
    name: str
    price_paise: int
    category: str | None = None
    in_stock: bool = True


@dataclass
class FakeService:
    name: str
    price_paise: int = 0
    duration_minutes: int = 30
    is_active: bool = True


# ============================================================
# category_emoji
# ============================================================


class TestCategoryEmoji:
    @pytest.mark.parametrize(
        "cat,expected",
        [
            ("Pizza", "🍕"),
            ("Burgers", "🍔"),
            ("Drinks", "🥤"),
            ("Beverages", "🥤"),
            ("Flour & Grains", "🌾"),
            ("Pulses", "🫘"),
            ("Spices", "🧂"),
            ("Oils", "🛢️"),
            ("Snacks", "🍪"),
            ("Hair Services", "💇"),
            ("Facial", "🧖"),
        ],
    )
    def test_known_categories(self, cat, expected):
        assert category_emoji(cat) == expected

    def test_unknown_category(self):
        assert category_emoji("XYZ Random") == "•"

    def test_none_category(self):
        assert category_emoji(None) == "•"
        assert category_emoji("") == "•"


# ============================================================
# Menu generation
# ============================================================


class TestMenuGen:
    def test_empty_products(self):
        assert generate_menu_text("Shop", []) == ""

    def test_basic_menu(self):
        products = [
            FakeProduct("Margherita Pizza", 25000, "Pizza"),
            FakeProduct("Cheese Burger", 15000, "Burgers"),
        ]
        text = generate_menu_text("Sharma Restaurant", products)
        assert "Sharma Restaurant" in text
        assert "🍕 *Pizza*" in text
        assert "🍔 *Burgers*" in text
        assert "Margherita Pizza" in text
        assert "₹250" in text
        assert "₹150" in text

    def test_out_of_stock_marked(self):
        products = [
            FakeProduct("Atta", 25000, "Flour", in_stock=True),
            FakeProduct("Rice", 80000, "Flour", in_stock=False),
        ]
        text = generate_menu_text("Kirana", products, detected_language="english")
        assert "✅" in text
        assert "❌" in text
        assert "Sold out" in text

    def test_hindi_header(self):
        products = [FakeProduct("Atta", 25000, "Flour")]
        text = generate_menu_text(
            "किराना", products, detected_language="hindi"
        )
        assert "मेन्यू" in text
        assert "ऑर्डर" in text  # Hindi footer

    def test_hinglish_footer(self):
        products = [FakeProduct("Atta", 25000, "Flour")]
        text = generate_menu_text(
            "Kirana", products, detected_language="hinglish"
        )
        assert "Order" in text
        assert "likhein" in text.lower()

    def test_in_stock_first(self):
        products = [
            FakeProduct("B-out", 100, "X", in_stock=False),
            FakeProduct("A-in", 100, "X", in_stock=True),
        ]
        text = generate_menu_text("S", products)
        a_idx = text.index("A-in")
        b_idx = text.index("B-out")
        assert a_idx < b_idx

    def test_default_items_category_last(self):
        products = [
            FakeProduct("Generic", 100, None),  # → "Items"
            FakeProduct("Pizza1", 100, "Pizza"),
        ]
        text = generate_menu_text("S", products)
        pizza_idx = text.index("Pizza1")
        items_idx = text.index("Generic")
        assert pizza_idx < items_idx

    def test_exclude_out_of_stock(self):
        products = [
            FakeProduct("A", 100, "X", in_stock=True),
            FakeProduct("B", 100, "X", in_stock=False),
        ]
        text = generate_menu_text("S", products, include_out_of_stock=False)
        assert "A" in text
        assert "B" not in text

    def test_kirana_scenario(self):
        products = [
            FakeProduct("Atta 5 kg", 25000, "Flour & Grains"),
            FakeProduct("Toor Dal 1 kg", 18000, "Pulses"),
            FakeProduct("Mustard Oil 1 L", 18000, "Oils"),
            FakeProduct("Tata Salt 1 kg", 2000, "Spices"),
        ]
        text = generate_menu_text(
            "Sharma Kirana", products, detected_language="hinglish"
        )
        assert "Atta 5 kg" in text
        assert "₹250" in text
        assert "🌾" in text
        assert "🫘" in text
        assert "🛢️" in text
        assert "🧂" in text


# ============================================================
# Services generation
# ============================================================


class TestServicesGen:
    def test_empty(self):
        assert generate_services_text("Salon", []) == ""

    def test_basic(self):
        services = [
            FakeService("Haircut", 30000, 30),
            FakeService("Facial", 80000, 60),
        ]
        text = generate_services_text("Sharma Salon", services)
        assert "Sharma Salon" in text
        assert "Services" in text
        assert "Haircut" in text
        assert "30 min" in text
        assert "₹300" in text

    def test_skip_inactive(self):
        services = [
            FakeService("Active", 100, 30, is_active=True),
            FakeService("Hidden", 100, 30, is_active=False),
        ]
        text = generate_services_text("S", services)
        assert "Active" in text
        assert "Hidden" not in text

    def test_hindi(self):
        services = [FakeService("Haircut", 30000, 30)]
        text = generate_services_text(
            "Sharma", services, detected_language="hindi"
        )
        assert "सेवाएं" in text
