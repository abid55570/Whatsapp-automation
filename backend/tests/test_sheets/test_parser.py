"""Tests for sheet parsing logic."""
import pytest

from app.services.sheets.parser import (
    parse_faqs,
    parse_products,
    parse_services,
)


# ======================================================================
# FAQs parser
# ======================================================================


class TestFAQsParser:
    def test_basic_parsing(self):
        rows = [
            ["Keywords", "Reply", "Category"],
            ["price, kitna, rate", "Our prices: ₹300+", "pricing"],
            ["timing, hours", "Mon-Sat 10-9", "info"],
        ]
        result = parse_faqs(rows)
        assert len(result) == 2
        assert result[0]["keywords"] == ["price", "kitna", "rate"]
        assert result[0]["reply"] == "Our prices: ₹300+"
        assert result[0]["category"] == "pricing"

    def test_flexible_column_names(self):
        """Headers can use 'Triggers', 'Question Keywords', 'Answer' etc."""
        rows = [
            ["Question Keywords", "Answer", "Topic"],
            ["address, location", "Shop #5, MG Road", "info"],
        ]
        result = parse_faqs(rows)
        assert len(result) == 1
        assert result[0]["keywords"] == ["address", "location"]

    def test_split_by_pipe_and_semicolon(self):
        rows = [
            ["Keywords", "Reply"],
            ["price|cost;rate", "₹300"],
        ]
        result = parse_faqs(rows)
        assert result[0]["keywords"] == ["price", "cost", "rate"]

    def test_missing_required_columns_raises(self):
        rows = [
            ["Foo", "Bar"],
            ["x", "y"],
        ]
        with pytest.raises(ValueError):
            parse_faqs(rows)

    def test_empty_rows_skipped(self):
        rows = [
            ["Keywords", "Reply"],
            ["", ""],
            ["price", "₹300"],
            ["timing", ""],  # missing reply
            ["", "no keywords"],  # missing keywords
        ]
        result = parse_faqs(rows)
        assert len(result) == 1
        assert result[0]["keywords"] == ["price"]

    def test_optional_columns(self):
        rows = [
            ["Keywords", "Reply"],
            ["price", "₹300"],
        ]
        result = parse_faqs(rows)
        assert result[0]["category"] is None
        assert result[0]["media_url"] is None

    def test_row_numbers_correct(self):
        """row_number should be 2-indexed (1 is header)."""
        rows = [
            ["Keywords", "Reply"],
            ["a", "1"],
            ["b", "2"],
            ["c", "3"],
        ]
        result = parse_faqs(rows)
        assert [r["row_number"] for r in result] == [2, 3, 4]

    def test_empty_sheet(self):
        assert parse_faqs([]) == []
        assert parse_faqs([["Keywords", "Reply"]]) == []


# ======================================================================
# Products parser
# ======================================================================


class TestProductsParser:
    def test_basic(self):
        rows = [
            ["Name", "Price", "Description", "SKU"],
            ["Haircut", "300", "Standard cut", "HC01"],
            ["Facial", "₹800", "Premium", "FC01"],
        ]
        result = parse_products(rows)
        assert len(result) == 2
        assert result[0]["name"] == "Haircut"
        assert result[0]["price_paise"] == 30000  # ₹300 = 30000 paise
        assert result[1]["price_paise"] == 80000

    def test_currency_symbols_stripped(self):
        rows = [
            ["Name", "Price"],
            ["A", "₹1,250"],
            ["B", "Rs. 999"],
            ["C", "500.50"],
        ]
        result = parse_products(rows)
        assert result[0]["price_paise"] == 125000
        assert result[1]["price_paise"] == 99900
        assert result[2]["price_paise"] == 50050

    def test_in_stock_parsing(self):
        rows = [
            ["Name", "Price", "In Stock"],
            ["A", "100", "yes"],
            ["B", "100", "no"],
            ["C", "100", "true"],
            ["D", "100", "out of stock"],
            ["E", "100", ""],
        ]
        result = parse_products(rows)
        assert result[0]["in_stock"] is True
        assert result[1]["in_stock"] is False
        assert result[2]["in_stock"] is True
        assert result[3]["in_stock"] is False
        assert result[4]["in_stock"] is True  # default

    def test_missing_required_columns(self):
        rows = [["Name"], ["A"]]
        with pytest.raises(ValueError):
            parse_products(rows)

    def test_skips_empty_names(self):
        rows = [
            ["Name", "Price"],
            ["", "100"],
            ["A", "100"],
        ]
        result = parse_products(rows)
        assert len(result) == 1
        assert result[0]["name"] == "A"


# ======================================================================
# Services parser
# ======================================================================


class TestServicesParser:
    def test_basic(self):
        rows = [
            ["Name", "Duration", "Price"],
            ["Haircut", "30", "300"],
            ["Facial", "60 min", "800"],
        ]
        result = parse_services(rows)
        assert len(result) == 2
        assert result[0]["duration_minutes"] == 30
        assert result[1]["duration_minutes"] == 60
        assert result[0]["price_paise"] == 30000

    def test_defaults(self):
        rows = [
            ["Name"],
            ["Haircut"],
        ]
        result = parse_services(rows)
        assert result[0]["duration_minutes"] == 30
        assert result[0]["price_paise"] == 0
        assert result[0]["is_active"] is True

    def test_active_parsing(self):
        rows = [
            ["Name", "Active"],
            ["A", "yes"],
            ["B", "false"],
            ["C", "1"],
        ]
        result = parse_services(rows)
        assert result[0]["is_active"] is True
        assert result[1]["is_active"] is False
        assert result[2]["is_active"] is True


# ======================================================================
# extract_sheet_id
# ======================================================================


class TestExtractSheetId:
    def test_standard_url(self):
        from app.services.sheets.client import extract_sheet_id

        url = "https://docs.google.com/spreadsheets/d/1abc-XYZ_12345/edit#gid=0"
        assert extract_sheet_id(url) == "1abc-XYZ_12345"

    def test_url_without_edit(self):
        from app.services.sheets.client import extract_sheet_id

        url = "https://docs.google.com/spreadsheets/d/SHEET123/view"
        assert extract_sheet_id(url) == "SHEET123"

    def test_drive_file_url(self):
        from app.services.sheets.client import extract_sheet_id

        url = "https://drive.google.com/file/d/FILE_ABC_123/view"
        assert extract_sheet_id(url) == "FILE_ABC_123"

    def test_bare_id(self):
        from app.services.sheets.client import extract_sheet_id

        assert extract_sheet_id("a" * 25) == "a" * 25

    def test_invalid(self):
        from app.services.sheets.client import extract_sheet_id

        assert extract_sheet_id("") is None
        assert extract_sheet_id("not a url") is None
        assert extract_sheet_id(None) is None  # type: ignore
