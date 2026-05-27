"""End-to-end tests for the invoice creation service + endpoints."""
from datetime import date
from decimal import Decimal

from app.models.enums import GstScheme, InvoiceStatus, InvoiceType
from app.services.gst.service import (
    cancel_invoice,
    create_invoice,
    determine_invoice_type,
)
from tests.conftest import auth_headers, create_business, create_user


class TestDetermineInvoiceType:
    def test_composition_is_bill_of_supply(self):
        assert determine_invoice_type(
            cx_gstin=None, cx_state_code=None, seller_state_code="27",
            total_paise=10000, scheme="composition",
        ) == InvoiceType.BILL_OF_SUPPLY

    def test_b2b_with_gstin(self):
        assert determine_invoice_type(
            cx_gstin="27AAPFU0939F1ZV", cx_state_code="27", seller_state_code="27",
            total_paise=10000, scheme="regular",
        ) == InvoiceType.B2B

    def test_b2c_default(self):
        assert determine_invoice_type(
            cx_gstin=None, cx_state_code="27", seller_state_code="27",
            total_paise=10000, scheme="regular",
        ) == InvoiceType.B2C

    def test_b2cl_large_interstate(self):
        assert determine_invoice_type(
            cx_gstin=None, cx_state_code="07", seller_state_code="27",
            total_paise=30_00_000_00, scheme="regular",   # ₹30 lakh
        ) == InvoiceType.B2C_LARGE

    def test_b2c_interstate_under_threshold(self):
        assert determine_invoice_type(
            cx_gstin=None, cx_state_code="07", seller_state_code="27",
            total_paise=10_000_00, scheme="regular",   # ₹10k
        ) == InvoiceType.B2C


# ============================================================
# Service-layer: create_invoice
# ============================================================


async def test_create_invoice_intra_state(db):
    user = await create_user(db, phone="+919000020001")
    biz = await create_business(db, owner=user)
    biz.gstin = "27AAPFU0939F1ZV"
    biz.gst_state_code = "27"
    biz.gst_scheme = GstScheme.REGULAR
    await db.commit()

    inv = await create_invoice(
        db,
        business=biz,
        lines_input=[
            {"description": "Item 1", "quantity": "1", "rate_paise": 10000, "gst_rate": 18},
        ],
        cx_name="Buyer",
        cx_state_code="27",   # same state → intra
    )
    assert inv.invoice_number == "INV-{}-0001".format(str(inv.invoice_date.year if inv.invoice_date.month >= 4 else inv.invoice_date.year - 1)[-2:])
    assert inv.status == InvoiceStatus.ISSUED
    assert inv.cgst_paise == 900
    assert inv.sgst_paise == 900
    assert inv.igst_paise == 0
    assert inv.total_paise == 11800
    assert len(inv.lines) == 1


async def test_create_invoice_inter_state(db):
    user = await create_user(db, phone="+919000020002")
    biz = await create_business(db, owner=user)
    biz.gstin = "27AAPFU0939F1ZV"
    biz.gst_state_code = "27"
    biz.gst_scheme = GstScheme.REGULAR
    await db.commit()

    inv = await create_invoice(
        db,
        business=biz,
        lines_input=[
            {"description": "Item", "quantity": "2", "rate_paise": 5000, "gst_rate": 18},
        ],
        cx_state_code="07",   # different state → IGST
    )
    assert inv.cgst_paise == 0
    assert inv.sgst_paise == 0
    assert inv.igst_paise == 1800
    assert inv.invoice_type in (InvoiceType.B2C, InvoiceType.B2C_LARGE)


async def test_create_invoice_b2b_gstin_infers_state(db):
    user = await create_user(db, phone="+919000020003")
    biz = await create_business(db, owner=user)
    biz.gstin = "27AAPFU0939F1ZV"
    biz.gst_state_code = "27"
    biz.gst_scheme = GstScheme.REGULAR
    await db.commit()

    inv = await create_invoice(
        db, business=biz,
        lines_input=[{"description": "x", "quantity": "1", "rate_paise": 10000, "gst_rate": 18}],
        cx_gstin="07AAAAA1234A1Z5",  # Delhi GSTIN (state inferred from prefix)
    )
    assert inv.invoice_type == InvoiceType.B2B
    assert inv.igst_paise == 1800  # inter-state because buyer state 07 != seller 27


async def test_create_invoice_draft_mode(db):
    user = await create_user(db, phone="+919000020004")
    biz = await create_business(db, owner=user)
    biz.gst_scheme = GstScheme.REGULAR
    await db.commit()

    inv = await create_invoice(
        db, business=biz,
        lines_input=[{"description": "x", "quantity": "1", "rate_paise": 10000, "gst_rate": 5}],
        issue_now=False,
    )
    assert inv.status == InvoiceStatus.DRAFT
    assert inv.issued_at is None


async def test_create_invoice_sequence_increments(db):
    user = await create_user(db, phone="+919000020005")
    biz = await create_business(db, owner=user)
    biz.gst_scheme = GstScheme.REGULAR
    await db.commit()

    inv1 = await create_invoice(
        db, business=biz,
        lines_input=[{"description": "x", "quantity": "1", "rate_paise": 100, "gst_rate": 0}],
    )
    inv2 = await create_invoice(
        db, business=biz,
        lines_input=[{"description": "y", "quantity": "1", "rate_paise": 100, "gst_rate": 0}],
    )
    assert inv1.invoice_number != inv2.invoice_number
    assert inv1.invoice_number.endswith("0001")
    assert inv2.invoice_number.endswith("0002")


async def test_cancel_invoice(db):
    user = await create_user(db, phone="+919000020006")
    biz = await create_business(db, owner=user)
    biz.gst_scheme = GstScheme.REGULAR
    await db.commit()

    inv = await create_invoice(
        db, business=biz,
        lines_input=[{"description": "x", "quantity": "1", "rate_paise": 100, "gst_rate": 0}],
    )
    cancelled = await cancel_invoice(db, inv, reason="Wrong customer")
    assert cancelled.status == InvoiceStatus.CANCELLED
    assert cancelled.cancellation_reason == "Wrong customer"
    assert cancelled.cancelled_at is not None


# ============================================================
# API endpoints
# ============================================================


async def test_get_gst_settings(client, authed_user, business):
    resp = await client.get(
        "/api/v1/businesses/me/gst-settings",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["gst_scheme"] == "unregistered"
    assert body["invoice_prefix"] == "INV"


async def test_update_gst_settings(client, authed_user, business):
    resp = await client.put(
        "/api/v1/businesses/me/gst-settings",
        json={
            "gstin": "27AAPFU0939F1ZV",
            "gst_scheme": "regular",
            "legal_name": "Sharma Kirana LLP",
            "pan": "AAPFU0939F",
            "business_address_line1": "Shop 5",
            "business_city": "Pune",
            "business_state": "Maharashtra",
            "business_pincode": "411001",
            "invoice_prefix": "SHM",
        },
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["gstin"] == "27AAPFU0939F1ZV"
    assert body["gst_state_code"] == "27"   # auto-derived
    assert body["invoice_prefix"] == "SHM"


async def test_update_gst_settings_invalid_gstin(client, authed_user, business):
    resp = await client.put(
        "/api/v1/businesses/me/gst-settings",
        json={"gstin": "27AAPFU0939F1ZW"},   # bad checksum
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 422


async def test_create_invoice_endpoint(client, authed_user, business, db):
    business.gstin = "27AAPFU0939F1ZV"
    business.gst_state_code = "27"
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    resp = await client.post(
        "/api/v1/businesses/me/invoices",
        json={
            "cx_name": "Test Buyer",
            "cx_state_code": "27",
            "lines": [
                {
                    "description": "Atta 5kg",
                    "hsn_code": "1101",
                    "quantity": "2",
                    "unit": "kg",
                    "rate_paise": 25000,
                    "gst_rate": 5,
                },
            ],
        },
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["total_paise"] == 52500   # 50000 + 5% GST = 52500
    assert body["status"] == "issued"
    assert len(body["lines"]) == 1


async def test_list_invoices(client, authed_user, business, db):
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    # Create 3 invoices
    for i in range(3):
        await client.post(
            "/api/v1/businesses/me/invoices",
            json={
                "lines": [{"description": f"Item {i}", "quantity": "1", "rate_paise": 100, "gst_rate": 0}],
            },
            headers=auth_headers(authed_user),
        )

    resp = await client.get(
        "/api/v1/businesses/me/invoices",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3


async def test_get_invoice_not_found(client, authed_user, business):
    fake = "00000000-0000-0000-0000-000000000000"
    resp = await client.get(
        f"/api/v1/businesses/me/invoices/{fake}",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 404


async def test_cancel_invoice_endpoint(client, authed_user, business, db):
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    r1 = await client.post(
        "/api/v1/businesses/me/invoices",
        json={"lines": [{"description": "x", "quantity": "1", "rate_paise": 100, "gst_rate": 0}]},
        headers=auth_headers(authed_user),
    )
    inv_id = r1.json()["id"]

    r2 = await client.post(
        f"/api/v1/businesses/me/invoices/{inv_id}/cancel",
        json={"reason": "Test cancellation"},
        headers=auth_headers(authed_user),
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "cancelled"
    assert r2.json()["cancellation_reason"] == "Test cancellation"


async def test_invoice_endpoints_require_auth(client):
    resp = await client.get("/api/v1/businesses/me/invoices")
    assert resp.status_code == 401
