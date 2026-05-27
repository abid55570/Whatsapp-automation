"""Integration tests for /reports/* + /purchase-invoices/* endpoints."""
from datetime import date

from app.models.enums import GstScheme
from tests.conftest import auth_headers


# ============================================================
# Purchase invoices CRUD
# ============================================================


async def test_create_purchase_invoice(client, authed_user, business, db):
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    resp = await client.post(
        "/api/v1/businesses/me/purchase-invoices",
        json={
            "supplier_name": "Wholesale Suppliers Ltd",
            "supplier_gstin": "29AAGCB7383J1Z4",
            "bill_number": "WS-001",
            "bill_date": "2026-05-10",
            "taxable_paise": 50000,
            "igst_paise": 9000,
            "total_paise": 59000,
            "category": "raw_materials",
        },
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["supplier_name"] == "Wholesale Suppliers Ltd"
    assert body["supplier_state_code"] == "29"  # auto-derived from GSTIN
    assert body["status"] == "recorded"


async def test_create_purchase_invoice_invalid_gstin(client, authed_user, business):
    resp = await client.post(
        "/api/v1/businesses/me/purchase-invoices",
        json={
            "supplier_name": "X",
            "supplier_gstin": "INVALIDGSTIN12X",
            "bill_number": "B1",
            "bill_date": "2026-05-10",
            "taxable_paise": 100,
            "total_paise": 100,
        },
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 422


async def test_list_and_update_purchase_invoice(client, authed_user, business):
    r1 = await client.post(
        "/api/v1/businesses/me/purchase-invoices",
        json={
            "supplier_name": "Supplier",
            "bill_number": "B1",
            "bill_date": "2026-05-10",
            "taxable_paise": 100,
            "total_paise": 100,
        },
        headers=auth_headers(authed_user),
    )
    pi_id = r1.json()["id"]

    r2 = await client.get(
        "/api/v1/businesses/me/purchase-invoices",
        headers=auth_headers(authed_user),
    )
    assert r2.status_code == 200
    assert r2.json()["total"] >= 1

    r3 = await client.patch(
        f"/api/v1/businesses/me/purchase-invoices/{pi_id}",
        json={"is_capital_goods": True, "notes": "Machine"},
        headers=auth_headers(authed_user),
    )
    assert r3.status_code == 200
    assert r3.json()["is_capital_goods"] is True
    assert r3.json()["notes"] == "Machine"


async def test_delete_purchase_invoice(client, authed_user, business):
    r1 = await client.post(
        "/api/v1/businesses/me/purchase-invoices",
        json={
            "supplier_name": "Supplier",
            "bill_number": "B-DEL",
            "bill_date": "2026-05-10",
            "taxable_paise": 100,
            "total_paise": 100,
        },
        headers=auth_headers(authed_user),
    )
    pi_id = r1.json()["id"]

    r2 = await client.delete(
        f"/api/v1/businesses/me/purchase-invoices/{pi_id}",
        headers=auth_headers(authed_user),
    )
    assert r2.status_code == 204


# ============================================================
# Reports overview
# ============================================================


async def test_reports_overview_empty(client, authed_user, business, db):
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    resp = await client.get(
        "/api/v1/businesses/me/reports/overview",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "period" in body
    assert body["sales"]["invoices"] == 0
    assert body["purchases"]["bills"] == 0
    assert body["tax_to_pay_paise"] == 0


async def test_reports_overview_with_data(client, authed_user, business, db):
    business.gstin = "27AAPFU0939F1ZV"
    business.gst_state_code = "27"
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    # Create 1 sale + 1 purchase
    await client.post(
        "/api/v1/businesses/me/invoices",
        json={
            "cx_name": "X",
            "cx_state_code": "27",
            "lines": [
                {"description": "x", "quantity": "1", "rate_paise": 10000, "gst_rate": 18},
            ],
        },
        headers=auth_headers(authed_user),
    )
    await client.post(
        "/api/v1/businesses/me/purchase-invoices",
        json={
            "supplier_name": "S",
            "bill_number": "B1",
            "bill_date": date.today().isoformat(),
            "taxable_paise": 5000,
            "cgst_paise": 450,
            "sgst_paise": 450,
            "total_paise": 5900,
        },
        headers=auth_headers(authed_user),
    )

    today = date.today()
    month = f"{today.year}-{today.month:02d}"
    resp = await client.get(
        f"/api/v1/businesses/me/reports/overview?month={month}",
        headers=auth_headers(authed_user),
    )
    body = resp.json()
    assert body["sales"]["invoices"] == 1
    assert body["sales"]["total_paise"] == 11800
    assert body["purchases"]["bills"] == 1
    assert body["purchases"]["itc_available_paise"] == 900


# ============================================================
# Sales register xlsx export
# ============================================================


async def test_sales_register_endpoint(client, authed_user, business, db):
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    await client.post(
        "/api/v1/businesses/me/invoices",
        json={
            "lines": [{"description": "x", "quantity": "1", "rate_paise": 100, "gst_rate": 0}],
        },
        headers=auth_headers(authed_user),
    )

    resp = await client.get(
        "/api/v1/businesses/me/reports/sales-register",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument"
    )
    assert resp.content[:2] == b"PK"


# ============================================================
# GSTR-1 JSON export
# ============================================================


async def test_gstr1_requires_gstin(client, authed_user, business, db):
    business.gst_scheme = GstScheme.REGULAR
    business.gstin = None
    await db.commit()

    resp = await client.get(
        "/api/v1/businesses/me/reports/gstr1?month=2026-05",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 400


async def test_gstr1_endpoint(client, authed_user, business, db):
    business.gstin = "27AAPFU0939F1ZV"
    business.gst_state_code = "27"
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    resp = await client.get(
        "/api/v1/businesses/me/reports/gstr1?month=2026-05",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/json"
    payload = resp.json()
    assert payload["gstin"] == "27AAPFU0939F1ZV"
    assert payload["fp"] == "052026"


async def test_gstr1_invalid_month(client, authed_user, business, db):
    business.gstin = "27AAPFU0939F1ZV"
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    resp = await client.get(
        "/api/v1/businesses/me/reports/gstr1?month=not-a-month",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 400


# ============================================================
# GSTR-3B summary
# ============================================================


async def test_gstr3b_endpoint(client, authed_user, business, db):
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    resp = await client.get(
        "/api/v1/businesses/me/reports/gstr3b-summary?month=2026-05",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"


# ============================================================
# Purchase register
# ============================================================


async def test_purchase_register_endpoint(client, authed_user, business):
    resp = await client.get(
        "/api/v1/businesses/me/reports/purchase-register",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"


# ============================================================
# Tax Pack toggle
# ============================================================


async def test_tax_pack_enable_disable(client, authed_user, business):
    r1 = await client.post(
        "/api/v1/businesses/me/subscription/tax-pack/enable",
        headers=auth_headers(authed_user),
    )
    assert r1.status_code == 200
    assert r1.json()["tax_pack_enabled"] is True

    r2 = await client.post(
        "/api/v1/businesses/me/subscription/tax-pack/disable",
        headers=auth_headers(authed_user),
    )
    assert r2.status_code == 200
    assert r2.json()["tax_pack_enabled"] is False
