"""Async client for sending messages via Meta WhatsApp Cloud API."""
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppClientError(Exception):
    """Raised when Meta's Graph API returns an error."""


class WhatsAppClient:
    """Async client wrapping Meta's WhatsApp Cloud API.

    Each business gets its own client instance, with its own
    `phone_number_id` and `access_token`.
    """

    BASE_URL = "https://graph.facebook.com"

    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        api_version: str | None = None,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.api_version = api_version or settings.META_GRAPH_API_VERSION
        self.timeout = timeout
        self._transport = transport

    # ------------------------------------------------------------------
    # URLs and headers
    # ------------------------------------------------------------------

    @property
    def messages_url(self) -> str:
        return f"{self.BASE_URL}/{self.api_version}/{self.phone_number_id}/messages"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Sending messages
    # ------------------------------------------------------------------

    async def send_text(
        self,
        to: str,
        body: str,
        preview_url: bool = False,
    ) -> dict[str, Any]:
        """Send a plain text message."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": preview_url, "body": body},
        }
        return await self._send(payload)

    async def send_image(
        self,
        to: str,
        image_url: str | None = None,
        media_id: str | None = None,
        caption: str | None = None,
    ) -> dict[str, Any]:
        """Send an image, by URL or by pre-uploaded media ID."""
        image_obj: dict[str, Any] = {}
        if media_id:
            image_obj["id"] = media_id
        elif image_url:
            image_obj["link"] = image_url
        else:
            raise ValueError("Either image_url or media_id must be provided")
        if caption:
            image_obj["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": image_obj,
        }
        return await self._send(payload)

    async def send_document(
        self,
        to: str,
        document_url: str | None = None,
        media_id: str | None = None,
        filename: str | None = None,
        caption: str | None = None,
    ) -> dict[str, Any]:
        """Send a document attachment."""
        doc_obj: dict[str, Any] = {}
        if media_id:
            doc_obj["id"] = media_id
        elif document_url:
            doc_obj["link"] = document_url
        else:
            raise ValueError("Either document_url or media_id must be provided")
        if filename:
            doc_obj["filename"] = filename
        if caption:
            doc_obj["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "document",
            "document": doc_obj,
        }
        return await self._send(payload)

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "en_US",
        components: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a pre-approved template (utility / marketing / auth)."""
        template_obj: dict[str, Any] = {
            "name": template_name,
            "language": {"code": language_code},
        }
        if components:
            template_obj["components"] = components

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": template_obj,
        }
        return await self._send(payload)

    async def mark_as_read(self, message_id: str) -> dict[str, Any]:
        """Mark an inbound message as read."""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        return await self._send(payload)

    # ------------------------------------------------------------------
    # Internal: HTTP call
    # ------------------------------------------------------------------

    async def _send(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST to Meta and return the parsed response, or raise."""
        client_kwargs: dict[str, Any] = {"timeout": self.timeout}
        if self._transport is not None:
            client_kwargs["transport"] = self._transport

        async with httpx.AsyncClient(**client_kwargs) as client:
            try:
                resp = await client.post(
                    self.messages_url,
                    json=payload,
                    headers=self.headers,
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Meta API error %s: %s",
                    exc.response.status_code,
                    exc.response.text[:500],
                )
                raise WhatsAppClientError(
                    f"Meta API {exc.response.status_code}: {exc.response.text}"
                ) from exc
            except httpx.HTTPError as exc:
                logger.error("HTTP error calling Meta API: %s", exc)
                raise WhatsAppClientError(f"HTTP error: {exc}") from exc
