"""Google Sheets API v4 client."""
import logging
import re
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def extract_sheet_id(url: str) -> str | None:
    """Extract the sheet ID from any Google Sheets URL.

    Supports:
      - https://docs.google.com/spreadsheets/d/{ID}/edit
      - https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0
      - https://drive.google.com/file/d/{ID}/view
    """
    if not url:
        return None
    patterns = [
        r"/spreadsheets/d/([a-zA-Z0-9_-]+)",
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"^([a-zA-Z0-9_-]{20,})$",  # bare sheet ID
    ]
    for p in patterns:
        m = re.search(p, url.strip())
        if m:
            return m.group(1)
    return None


class SheetsClient:
    """Wraps Google Sheets API. Reads rows from a sheet tab."""

    def __init__(self, credentials_path: str | None = None):
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError(
                "Google API libraries not installed. "
                "Run `pip install google-api-python-client google-auth`."
            ) from exc

        path = credentials_path or settings.GOOGLE_SHEETS_CREDENTIALS_PATH
        if not Path(path).exists():
            raise FileNotFoundError(
                f"Google service-account credentials not found at {path}. "
                "Place your service-account JSON there."
            )

        credentials = service_account.Credentials.from_service_account_file(
            path, scopes=SCOPES
        )
        self.service = build(
            "sheets",
            "v4",
            credentials=credentials,
            cache_discovery=False,
        )

    def fetch_rows(
        self,
        spreadsheet_id: str,
        tab_name: str = "Sheet1",
        range_suffix: str = "",
    ) -> list[list[str]]:
        """Return all rows from the given tab as a list of cell-string lists.

        First row is typically the header.
        """
        rng = f"{tab_name}{range_suffix}" if range_suffix else tab_name
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=rng)
                .execute()
            )
        except Exception as exc:
            logger.error("Sheets API fetch failed: %s", exc)
            raise

        return result.get("values", [])

    def get_metadata(self, spreadsheet_id: str) -> dict:
        """Get spreadsheet metadata (title, tabs, etc.)."""
        return (
            self.service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id, fields="properties,sheets.properties")
            .execute()
        )
