"""GSTR-1 JSON exporter — outward supplies for the GST portal.

Output schema follows the official GSTR-1 offline tool format. Owner downloads
this JSON, then uploads it on gst.gov.in.

Schema (top-level):
{
  "gstin": "27AAPFU0939F1ZV",
  "fp": "052026",            # MMYYYY of the filing month
  "gt": 12345.67,            # Gross turnover (₹) — owner enters separately, we default 0
  "cur_gt": 12345.67,        # Current FY turnover so far — default 0
  "b2b": [...],
  "b2cl": [...],
  "b2cs": [...],
  "hsn": {"data": [...]},
  "nil": {"inv": [...]}      # optional
}

Reference: https://tutorial.gst.gov.in/downloads/news/gstr_1_offline_utility.zip
"""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date
from typing import TYPE_CHECKING, Any

from app.models.enums import InvoiceStatus, InvoiceType
from app.services.gst.validation import gstin_state_code

if TYPE_CHECKING:
    from app.models import Business, Invoice

logger = logging.getLogger(__name__)


def _paise_to_inr(p: int) -> float:
    return round((p or 0) / 100, 2)


def _format_period(d: date) -> str:
    """GST portal wants 'MMYYYY' for the filing period (zero-padded)."""
    return f"{d.month:02d}{d.year}"


def _build_b2b(invoices: list["Invoice"]) -> list[dict[str, Any]]:
    """Group B2B invoices by buyer GSTIN."""
    by_ctin: dict[str, list[dict]] = defaultdict(list)
    for inv in invoices:
        if inv.invoice_type != InvoiceType.B2B or not inv.cx_gstin:
            continue
        # Per-rate breakdown of items in this invoice
        rate_buckets: dict[int, dict] = defaultdict(
            lambda: {"txval": 0, "iamt": 0, "camt": 0, "samt": 0, "csamt": 0}
        )
        for line in inv.lines:
            b = rate_buckets[line.gst_rate]
            b["txval"] += line.taxable_paise
            b["iamt"] += line.igst_paise
            b["camt"] += line.cgst_paise
            b["samt"] += line.sgst_paise
            b["csamt"] += line.cess_paise

        items_arr = [
            {
                "num": idx,
                "itm_det": {
                    "rt": rate,
                    "txval": _paise_to_inr(b["txval"]),
                    "iamt": _paise_to_inr(b["iamt"]),
                    "camt": _paise_to_inr(b["camt"]),
                    "samt": _paise_to_inr(b["samt"]),
                    "csamt": _paise_to_inr(b["csamt"]),
                },
            }
            for idx, (rate, b) in enumerate(sorted(rate_buckets.items()), start=1)
        ]

        pos = inv.cx_state_code or (gstin_state_code(inv.cx_gstin) or "")
        by_ctin[inv.cx_gstin].append(
            {
                "inum": inv.invoice_number,
                "idt": inv.invoice_date.strftime("%d-%m-%Y"),
                "val": _paise_to_inr(inv.total_paise),
                "pos": pos,
                "rchrg": "Y" if inv.reverse_charge else "N",
                "inv_typ": "R",  # Regular B2B
                "itms": items_arr,
            }
        )

    return [{"ctin": ctin, "inv": inv_list} for ctin, inv_list in by_ctin.items()]


def _build_b2cl(invoices: list["Invoice"]) -> list[dict[str, Any]]:
    """Interstate B2C invoices > ₹2.5L — grouped by place-of-supply state code."""
    by_pos: dict[str, list[dict]] = defaultdict(list)
    for inv in invoices:
        if inv.invoice_type != InvoiceType.B2C_LARGE:
            continue
        pos = inv.cx_state_code or ""
        rate_buckets: dict[int, dict] = defaultdict(
            lambda: {"txval": 0, "iamt": 0, "csamt": 0}
        )
        for line in inv.lines:
            b = rate_buckets[line.gst_rate]
            b["txval"] += line.taxable_paise
            b["iamt"] += line.igst_paise
            b["csamt"] += line.cess_paise

        items_arr = [
            {
                "num": idx,
                "itm_det": {
                    "rt": rate,
                    "txval": _paise_to_inr(b["txval"]),
                    "iamt": _paise_to_inr(b["iamt"]),
                    "csamt": _paise_to_inr(b["csamt"]),
                },
            }
            for idx, (rate, b) in enumerate(sorted(rate_buckets.items()), start=1)
        ]
        by_pos[pos].append(
            {
                "inum": inv.invoice_number,
                "idt": inv.invoice_date.strftime("%d-%m-%Y"),
                "val": _paise_to_inr(inv.total_paise),
                "itms": items_arr,
            }
        )
    return [{"pos": pos, "inv": inv_list} for pos, inv_list in by_pos.items()]


def _build_b2cs(invoices: list["Invoice"], seller_state_code: str | None) -> list[dict[str, Any]]:
    """B2C small — aggregate per (rate, place-of-supply, intra/inter)."""
    buckets: dict[tuple, dict] = defaultdict(
        lambda: {"txval": 0, "iamt": 0, "camt": 0, "samt": 0, "csamt": 0}
    )
    for inv in invoices:
        if inv.invoice_type != InvoiceType.B2C:
            continue
        pos = inv.cx_state_code or seller_state_code or ""
        intra = (seller_state_code is not None and pos[:2] == seller_state_code[:2])
        sply_ty = "INTRA" if intra else "INTER"
        for line in inv.lines:
            key = (sply_ty, line.gst_rate, pos)
            b = buckets[key]
            b["txval"] += line.taxable_paise
            b["iamt"] += line.igst_paise
            b["camt"] += line.cgst_paise
            b["samt"] += line.sgst_paise
            b["csamt"] += line.cess_paise

    return [
        {
            "sply_ty": sply_ty,
            "rt": rate,
            "pos": pos,
            "txval": _paise_to_inr(b["txval"]),
            "iamt": _paise_to_inr(b["iamt"]),
            "camt": _paise_to_inr(b["camt"]),
            "samt": _paise_to_inr(b["samt"]),
            "csamt": _paise_to_inr(b["csamt"]),
            "typ": "OE",  # Other than e-commerce
        }
        for (sply_ty, rate, pos), b in sorted(buckets.items())
    ]


def _build_hsn(invoices: list["Invoice"]) -> dict[str, Any]:
    """HSN-wise summary."""
    buckets: dict[tuple, dict] = defaultdict(
        lambda: {
            "desc": "",
            "uqc": "OTH",
            "qty": 0.0,
            "txval": 0,
            "iamt": 0,
            "camt": 0,
            "samt": 0,
            "csamt": 0,
        }
    )
    for inv in invoices:
        for line in inv.lines:
            key = (line.hsn_code or "UNCLASSIFIED", line.gst_rate, line.unit or "OTH")
            b = buckets[key]
            b["desc"] = b["desc"] or line.description
            b["uqc"] = (line.unit or "OTH").upper()[:3]
            b["qty"] += float(line.quantity)
            b["txval"] += line.taxable_paise
            b["iamt"] += line.igst_paise
            b["camt"] += line.cgst_paise
            b["samt"] += line.sgst_paise
            b["csamt"] += line.cess_paise

    data = [
        {
            "num": idx,
            "hsn_sc": hsn,
            "desc": b["desc"][:30],
            "uqc": b["uqc"],
            "qty": round(b["qty"], 3),
            "rt": rate,
            "txval": _paise_to_inr(b["txval"]),
            "iamt": _paise_to_inr(b["iamt"]),
            "camt": _paise_to_inr(b["camt"]),
            "samt": _paise_to_inr(b["samt"]),
            "csamt": _paise_to_inr(b["csamt"]),
        }
        for idx, ((hsn, rate, _unit), b) in enumerate(sorted(buckets.items()), start=1)
    ]
    return {"data": data}


def _gross_turnover(invoices: list["Invoice"]) -> float:
    return _paise_to_inr(sum(i.taxable_paise for i in invoices))


def build_gstr1_json(
    business: "Business",
    invoices: list["Invoice"],
    period_month: date,
) -> dict[str, Any]:
    """Generate a complete GSTR-1 JSON payload.

    Args:
        business: seller business
        invoices: ALL invoices in the period (we filter cancelled internally)
        period_month: any date within the filing month (used to build 'fp')
    """
    active = [i for i in invoices if i.status != InvoiceStatus.CANCELLED]

    return {
        "gstin": business.gstin or "",
        "fp": _format_period(period_month),
        "gt": _gross_turnover(active),
        "cur_gt": _gross_turnover(active),
        "b2b": _build_b2b(active),
        "b2cl": _build_b2cl(active),
        "b2cs": _build_b2cs(active, business.gst_state_code),
        "hsn": _build_hsn(active),
    }
