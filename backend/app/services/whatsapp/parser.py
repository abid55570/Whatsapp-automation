"""Helpers to extract structured data from Meta webhook payloads."""
from datetime import datetime, timezone

from app.services.whatsapp.schemas import (
    WAContact,
    WAMessage,
    WAStatus,
    WebhookPayload,
)


def extract_messages(
    payload: WebhookPayload,
) -> list[tuple[str, WAMessage, WAContact | None]]:
    """Extract message events from a payload.

    Returns a list of `(phone_number_id, message, contact)` tuples.
    """
    out: list[tuple[str, WAMessage, WAContact | None]] = []
    for entry in payload.entry:
        for change in entry.changes:
            if change.field != "messages":
                continue
            value = change.value
            pnid = value.metadata.phone_number_id
            contacts_by_id = {c.wa_id: c for c in value.contacts}
            for msg in value.messages:
                out.append((pnid, msg, contacts_by_id.get(msg.from_)))
    return out


def extract_statuses(payload: WebhookPayload) -> list[tuple[str, WAStatus]]:
    """Extract message-status updates (delivered/read/failed)."""
    out: list[tuple[str, WAStatus]] = []
    for entry in payload.entry:
        for change in entry.changes:
            if change.field != "messages":
                continue
            value = change.value
            pnid = value.metadata.phone_number_id
            for status in value.statuses:
                out.append((pnid, status))
    return out


def parse_timestamp(ts: str) -> datetime:
    """Convert Meta's epoch-seconds string into a UTC datetime."""
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def get_message_body(msg: WAMessage) -> str | None:
    """Extract text content from any message type.

    Handles text, button replies, and interactive replies.
    """
    if msg.text:
        return msg.text.body
    if msg.button and isinstance(msg.button, dict):
        return msg.button.get("text") or msg.button.get("payload")
    if msg.interactive and isinstance(msg.interactive, dict):
        button_reply = msg.interactive.get("button_reply") or {}
        list_reply = msg.interactive.get("list_reply") or {}
        return (
            button_reply.get("title")
            or list_reply.get("title")
            or button_reply.get("id")
            or list_reply.get("id")
        )
    return None
