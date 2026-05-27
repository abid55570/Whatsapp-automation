"""Google Sheets sync API endpoints."""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import GoogleSheetSync, User
from app.schemas.sheet import (
    SheetSyncCreate,
    SheetSyncResponse,
    SheetSyncUpdate,
    SyncTriggerResponse,
)
from app.services.onboarding import get_my_business_or_404
from app.services.sheets.client import extract_sheet_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/businesses/me/sheets", tags=["sheets"])


def _to_response(s: GoogleSheetSync) -> SheetSyncResponse:
    return SheetSyncResponse(
        id=s.id,
        sheet_url=s.sheet_url,
        sheet_id=s.sheet_id,
        sheet_tab_name=s.sheet_tab_name,
        sheet_type=(
            s.sheet_type.value if hasattr(s.sheet_type, "value") else str(s.sheet_type)
        ),
        auto_sync=s.auto_sync,
        sync_interval_minutes=s.sync_interval_minutes,
        last_synced_at=s.last_synced_at,
        last_sync_status=s.last_sync_status,
        last_sync_error=s.last_sync_error,
        rows_synced=s.rows_synced,
        created_at=s.created_at,
    )


# ============================================================
# List
# ============================================================


@router.get("", response_model=list[SheetSyncResponse])
async def list_sheets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SheetSyncResponse]:
    business = await get_my_business_or_404(db, current_user)
    stmt = (
        select(GoogleSheetSync)
        .where(GoogleSheetSync.business_id == business.id)
        .order_by(GoogleSheetSync.created_at.desc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [_to_response(s) for s in rows]


# ============================================================
# Create
# ============================================================


@router.post(
    "",
    response_model=SheetSyncResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sheet(
    body: SheetSyncCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SheetSyncResponse:
    business = await get_my_business_or_404(db, current_user)

    sheet_id = extract_sheet_id(body.sheet_url)
    if not sheet_id:
        raise HTTPException(
            status_code=400,
            detail="Could not extract sheet ID from URL. Use the full Google Sheets URL.",
        )

    sync = GoogleSheetSync(
        business_id=business.id,
        sheet_url=body.sheet_url,
        sheet_id=sheet_id,
        sheet_tab_name=body.sheet_tab_name,
        sheet_type=body.sheet_type,
        auto_sync=body.auto_sync,
        sync_interval_minutes=body.sync_interval_minutes,
    )
    db.add(sync)
    await db.commit()
    await db.refresh(sync)

    # Kick off initial sync in background (best-effort)
    try:
        from app.workers.tasks.sheets import sync_one_sheet_task
        sync_one_sheet_task.delay(str(sync.id))
    except Exception as exc:
        logger.warning("Failed to enqueue initial sync: %s", exc)

    return _to_response(sync)


# ============================================================
# Get one
# ============================================================


@router.get("/{sync_id}", response_model=SheetSyncResponse)
async def get_sheet(
    sync_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SheetSyncResponse:
    business = await get_my_business_or_404(db, current_user)
    sync = await db.get(GoogleSheetSync, sync_id)
    if sync is None or sync.business_id != business.id:
        raise HTTPException(404, "Sheet sync not found")
    return _to_response(sync)


# ============================================================
# Update
# ============================================================


@router.patch("/{sync_id}", response_model=SheetSyncResponse)
async def update_sheet(
    sync_id: UUID,
    body: SheetSyncUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SheetSyncResponse:
    business = await get_my_business_or_404(db, current_user)
    sync = await db.get(GoogleSheetSync, sync_id)
    if sync is None or sync.business_id != business.id:
        raise HTTPException(404, "Sheet sync not found")

    if body.sheet_tab_name is not None:
        sync.sheet_tab_name = body.sheet_tab_name
    if body.auto_sync is not None:
        sync.auto_sync = body.auto_sync
    if body.sync_interval_minutes is not None:
        sync.sync_interval_minutes = body.sync_interval_minutes

    await db.commit()
    await db.refresh(sync)
    return _to_response(sync)


# ============================================================
# Trigger manual sync
# ============================================================


@router.post(
    "/{sync_id}/sync",
    response_model=SyncTriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_sync(
    sync_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SyncTriggerResponse:
    business = await get_my_business_or_404(db, current_user)
    sync = await db.get(GoogleSheetSync, sync_id)
    if sync is None or sync.business_id != business.id:
        raise HTTPException(404, "Sheet sync not found")

    try:
        from app.workers.tasks.sheets import sync_one_sheet_task
        sync_one_sheet_task.delay(str(sync.id))
        return SyncTriggerResponse(
            status="queued",
            sync_id=sync.id,
            message="Sync queued — check back in a few seconds.",
        )
    except Exception as exc:
        logger.error("Failed to enqueue sync: %s", exc)
        raise HTTPException(503, "Background worker unavailable")


# ============================================================
# Delete
# ============================================================


@router.delete(
    "/{sync_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sheet(
    sync_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    business = await get_my_business_or_404(db, current_user)
    sync = await db.get(GoogleSheetSync, sync_id)
    if sync is None or sync.business_id != business.id:
        raise HTTPException(404, "Sheet sync not found")
    await db.delete(sync)
    await db.commit()
