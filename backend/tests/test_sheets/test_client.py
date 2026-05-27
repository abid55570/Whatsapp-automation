"""Tests for sheets client url extraction."""
import pytest

from app.services.sheets.client import extract_sheet_id


class TestExtractSheetId:
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://docs.google.com/spreadsheets/d/1aBcXyZ_1234567890ABCDEFGHIJ/edit", "1aBcXyZ_1234567890ABCDEFGHIJ"),
            ("https://docs.google.com/spreadsheets/d/abc123/edit#gid=0", "abc123"),
            ("https://drive.google.com/file/d/zxy999_def/view", "zxy999_def"),
            ("1aBcXyZ_1234567890ABCDEFGHIJ", "1aBcXyZ_1234567890ABCDEFGHIJ"),
            ("https://example.com/no-match", None),
            ("", None),
            (None, None),
        ],
    )
    def test_extract(self, url, expected):
        assert extract_sheet_id(url) == expected
