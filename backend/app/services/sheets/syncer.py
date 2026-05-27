"""Sync a Google Sheet → DB tables (FAQs, products, or services)."""
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BusinessIntent, GoogleSheetSync, Product, Service
from app.models.enums import SheetType
from app.services.sheets.client import SheetsClient
from app.services.sheets.parser import (
    parse_faqs,
    parse_products,
    parse_services,
)

logger = logging.getLogger(__name__)

# Prefix for sheet-derived BusinessIntent rows (lets matching engine identify them)
SHEET_FAQ_PREFIX = "sheet_faq_"


async def sync_sheet(
    db: AsyncSession,
    config: GoogleSheetSync,
) -> tuple[int, str | None]:
    """Sync one sheet → DB.

    Returns: (rows_synced, error_message_or_none)
    """
    now = datetime.now(timezone.utc)

    # Fetch rows from Google
    try:
        client = SheetsClient()
        rows = client.fetch_rows(config.sheet_id, config.sheet_tab_name)
    except Exception as exc:
        msg = f"Failed to fetch sheet: {exc}"
        logger.exception(msg)
        config.last_sync_status = "error"
        config.last_sync_error = msg[:500]
        config.last_synced_at = now
        await db.commit()
        return 0, msg

    # Route to type-specific syncer
    try:
        if config.sheet_type == SheetType.FAQS:
            count = await _sync_faqs(db, config.business_id, rows)
        elif config.sheet_type == SheetType.PRODUCTS:
            count = await _sync_products(db, config.business_id, rows)
        elif config.sheet_type == SheetType.SERVICES:
            count = await _sync_services(db, config.business_id, rows)
        else:
            raise ValueError(f"Unsupported sheet type: {config.sheet_type}")
    except Exception as exc:
        msg = f"Sync failed: {exc}"
        logger.exception(msg)
        config.last_sync_status = "error"
        config.last_sync_error = msg[:500]
        config.last_synced_at = now
        await db.commit()
        return 0, msg

    # Success
    config.last_synced_at = now
    config.last_sync_status = "ok"
    config.last_sync_error = None
    config.rows_synced = count
    await db.commit()
    logger.info(
        "Synced sheet %s (%s): %d rows",
        config.sheet_id,
        config.sheet_type,
        count,
    )
    return count, None


# ============================================================
# FAQs sync — sheet rows become BusinessIntent entries
# ============================================================


async def _sync_faqs(
    db: AsyncSession,
    business_id: UUID,
    rows: list[list[str]],
) -> int:
    """Replace all sheet-derived intents with the current sheet contents."""
    parsed = parse_faqs(rows)

    # Delete prior sheet-derived intents (sheet is source of truth)
    await db.execute(
        delete(BusinessIntent).where(
            BusinessIntent.business_id == business_id,
            BusinessIntent.intent_key.like(f"{SHEET_FAQ_PREFIX}%"),
        )
    )
    await db.flush()

    # Insert fresh
    for item in parsed:
        intent = BusinessIntent(
            business_id=business_id,
            intent_key=f"{SHEET_FAQ_PREFIX}{item['row_number']}",
            enabled=True,
            reply_text=item["reply"],
            media_url=item.get("media_url"),
            custom_keywords=item["keywords"],
            priority=10,  # higher than global intents (priority 1-6)
        )
        db.add(intent)

    await db.flush()
    return len(parsed)


# ============================================================
# Products sync
# ============================================================


async def _sync_products(
    db: AsyncSession,
    business_id: UUID,
    rows: list[list[str]],
) -> int:
    """Replace all sheet-derived products."""
    parsed = parse_products(rows)

    await db.execute(
        delete(Product).where(
            Product.business_id == business_id,
            Product.sheet_row_id.is_not(None),
        )
    )
    await db.flush()

    for item in parsed:
        product = Product(
            business_id=business_id,
            name=item["name"],
            description=item.get("description"),
            price_paise=item["price_paise"],
            sku=item.get("sku"),
            category=item.get("category"),
            image_url=item.get("image_url"),
            in_stock=item["in_stock"],
            sheet_row_id=str(item["row_number"]),
        )
        db.add(product)

    await db.flush()
    return len(parsed)


# ============================================================
# Services sync
# ============================================================


async def _sync_services(
    db: AsyncSession,
    business_id: UUID,
    rows: list[list[str]],
) -> int:
    """Replace all sheet-derived services."""
    parsed = parse_services(rows)

    await db.execute(
        delete(Service).where(
            Service.business_id == business_id,
            Service.sheet_row_id.is_not(None),
        )
    )
    await db.flush()

    for item in parsed:
        service = Service(
            business_id=business_id,
            name=item["name"],
            description=item.get("description"),
            duration_minutes=item["duration_minutes"],
            price_paise=item["price_paise"],
            is_active=item["is_active"],
            sheet_row_id=str(item["row_number"]),
        )
        db.add(service)

    await db.flush()
    return len(parsed)
