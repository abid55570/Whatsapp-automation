"""Razorpay payment links + webhook signature verification.

Uses the REST API directly (avoids the razorpay SDK so we control retries).
"""
import base64
import hashlib
import hmac
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

RAZORPAY_BASE = "https://api.razorpay.com/v1"


class RazorpayError(Exception):
    """Raised when Razorpay API returns an error."""


class RazorpayClient:
    """Minimal async Razorpay client. Phase E uses payment_links only."""

    def __init__(
        self,
        key_id: str | None = None,
        key_secret: str | None = None,
        timeout: float = 20.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        # `None` means "use settings"; explicit `""` means "no credentials"
        self.key_id = settings.RAZORPAY_KEY_ID if key_id is None else key_id
        self.key_secret = (
            settings.RAZORPAY_KEY_SECRET if key_secret is None else key_secret
        )
        self.timeout = timeout
        self._transport = transport

    @property
    def _auth_header(self) -> dict[str, str]:
        token = base64.b64encode(
            f"{self.key_id}:{self.key_secret}".encode()
        ).decode()
        return {"Authorization": f"Basic {token}"}

    async def create_payment_link(
        self,
        amount_paise: int,
        customer_name: str | None,
        customer_phone: str,
        description: str,
        order_id: str,
        business_id: str,
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        """Create a Razorpay payment link.

        Returns:
            {"id": "plink_...", "short_url": "https://rzp.io/...", ...}
        """
        if not (self.key_id and self.key_secret):
            raise RazorpayError("Razorpay credentials not configured")

        payload: dict[str, Any] = {
            "amount": amount_paise,
            "currency": "INR",
            "accept_partial": False,
            "description": description[:2048],
            "customer": {
                "contact": customer_phone if customer_phone.startswith("+") else f"+{customer_phone}",
            },
            "notify": {"sms": False, "email": False},
            "reminder_enable": False,
            "notes": {
                "order_id": order_id,
                "business_id": business_id,
            },
        }
        if customer_name:
            payload["customer"]["name"] = customer_name[:200]
        if callback_url:
            payload["callback_url"] = callback_url
            payload["callback_method"] = "get"

        return await self._post("/payment_links", payload)

    async def cancel_payment_link(self, link_id: str) -> dict[str, Any]:
        return await self._post(f"/payment_links/{link_id}/cancel", {})

    # ============================================================
    # Subscriptions (for SaaS plans: Starter / Growth / Pro)
    # ============================================================

    async def create_subscription(
        self,
        plan_id: str,
        customer_phone: str,
        customer_name: str | None,
        total_count: int = 12,
        notes: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a Razorpay subscription.

        Returns: {"id": "sub_...", "short_url": "...", "status": "created"}
        """
        if not (self.key_id and self.key_secret):
            raise RazorpayError("Razorpay credentials not configured")
        if not plan_id:
            raise RazorpayError("Razorpay plan_id is empty (check env vars)")

        payload: dict[str, Any] = {
            "plan_id": plan_id,
            "total_count": total_count,
            "customer_notify": 0,
            "notes": notes or {},
        }
        return await self._post("/subscriptions", payload)

    async def cancel_subscription(
        self, subscription_id: str, cancel_at_cycle_end: bool = True
    ) -> dict[str, Any]:
        return await self._post(
            f"/subscriptions/{subscription_id}/cancel",
            {"cancel_at_cycle_end": 1 if cancel_at_cycle_end else 0},
        )

    async def fetch_subscription(self, subscription_id: str) -> dict[str, Any]:
        return await self._get(f"/subscriptions/{subscription_id}")

    async def fetch_payment_link(self, link_id: str) -> dict[str, Any]:
        return await self._get(f"/payment_links/{link_id}")

    async def _post(self, path: str, body: dict) -> dict[str, Any]:
        client_kwargs: dict[str, Any] = {"timeout": self.timeout}
        if self._transport is not None:
            client_kwargs["transport"] = self._transport

        async with httpx.AsyncClient(**client_kwargs) as client:
            try:
                resp = await client.post(
                    f"{RAZORPAY_BASE}{path}",
                    json=body,
                    headers=self._auth_header,
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Razorpay POST %s failed: %s — %s",
                    path,
                    exc.response.status_code,
                    exc.response.text[:500],
                )
                raise RazorpayError(
                    f"Razorpay {exc.response.status_code}: {exc.response.text[:200]}"
                ) from exc
            except httpx.HTTPError as exc:
                raise RazorpayError(f"HTTP error: {exc}") from exc

    async def _get(self, path: str) -> dict[str, Any]:
        client_kwargs: dict[str, Any] = {"timeout": self.timeout}
        if self._transport is not None:
            client_kwargs["transport"] = self._transport

        async with httpx.AsyncClient(**client_kwargs) as client:
            try:
                resp = await client.get(
                    f"{RAZORPAY_BASE}{path}",
                    headers=self._auth_header,
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Razorpay GET %s failed: %s — %s",
                    path,
                    exc.response.status_code,
                    exc.response.text[:500],
                )
                raise RazorpayError(
                    f"Razorpay {exc.response.status_code}: {exc.response.text[:200]}"
                ) from exc
            except httpx.HTTPError as exc:
                raise RazorpayError(f"HTTP error: {exc}") from exc


def verify_razorpay_signature(
    payload: bytes,
    signature: str,
    webhook_secret: str,
) -> bool:
    """Verify Razorpay's `X-Razorpay-Signature` header (HMAC-SHA256)."""
    if not signature or not webhook_secret or not payload:
        return False
    expected = hmac.new(
        webhook_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
