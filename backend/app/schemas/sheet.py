"""Pydantic schemas for Google Sheets sync endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.enums import SheetType


class SheetSyncCreate(BaseModel):
    """Body for POST /businesses/me/sheets."""

    sheet_url: str = Field(..., description="Google Sheets URL (https://docs.google.com/spreadsheets/d/...)")
    sheet_type: SheetType
    sheet_tab_name: str = Field("Sheet1", max_length=100)
    auto_sync: bool = True
    sync_interval_minutes: int = Field(15, ge=5, le=1440)


class SheetSyncUpdate(BaseModel):
    """Body for PATCH /businesses/me/sheets/{id}."""

    sheet_tab_name: str | None = None
    auto_sync: bool | None = None
    sync_interval_minutes: int | None = Field(None, ge=5, le=1440)


class SheetSyncResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sheet_url: str
    sheet_id: str
    sheet_tab_name: str
    sheet_type: str
    auto_sync: bool
    sync_interval_minutes: int
    last_synced_at: datetime | None = None
    last_sync_status: str | None = None
    last_sync_error: str | None = None
    rows_synced: int
    created_at: datetime


class SyncTriggerResponse(BaseModel):
    """Returned when a manual sync is queued."""

    status: str
    sync_id: UUID
    message: str | None = None
