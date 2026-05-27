"""Tests for parsing Meta webhook payloads."""
from datetime import datetime, timezone

from app.services.whatsapp.parser import (
    extract_messages,
    extract_statuses,
    get_message_body,
    parse_timestamp,
)
from app.services.whatsapp.schemas import WAMessage, WebhookPayload


# ======================================================================
# Sample payloads
# ======================================================================

def _text_message_payload(text: str = "kitne ka hai?") -> dict:
    """A typical inbound text message payload from Meta."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WA_BIZ_ID_001",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+919999999999",
                                "phone_number_id": "PHONE_ID_001",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Ramesh"},
                                    "wa_id": "919876543210",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "919876543210",
                                    "id": "wamid.HBgM",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


def _status_payload(status: str = "delivered") -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WA_BIZ_ID_001",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+919999999999",
                                "phone_number_id": "PHONE_ID_001",
                            },
                            "statuses": [
                                {
                                    "id": "wamid.outbound123",
                                    "status": status,
                                    "timestamp": "1700000100",
                                    "recipient_id": "919876543210",
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


# ======================================================================
# Tests
# ======================================================================

class TestExtractMessages:
    def test_single_text_message(self):
        payload = WebhookPayload(**_text_message_payload("hello world"))
        results = extract_messages(payload)
        assert len(results) == 1
        pnid, msg, contact = results[0]
        assert pnid == "PHONE_ID_001"
        assert msg.from_ == "919876543210"
        assert msg.id == "wamid.HBgM"
        assert msg.type == "text"
        assert msg.text is not None
        assert msg.text.body == "hello world"
        assert contact is not None
        assert contact.profile.name == "Ramesh"

    def test_no_messages_returns_empty(self):
        payload = WebhookPayload(**_status_payload())
        assert extract_messages(payload) == []

    def test_multiple_messages_in_one_payload(self):
        d = _text_message_payload()
        # Add a second message
        d["entry"][0]["changes"][0]["value"]["messages"].append(
            {
                "from": "919876543210",
                "id": "wamid.second",
                "timestamp": "1700000050",
                "type": "text",
                "text": {"body": "second"},
            }
        )
        payload = WebhookPayload(**d)
        assert len(extract_messages(payload)) == 2


class TestExtractStatuses:
    def test_delivered_status(self):
        payload = WebhookPayload(**_status_payload("delivered"))
        results = extract_statuses(payload)
        assert len(results) == 1
        pnid, status = results[0]
        assert pnid == "PHONE_ID_001"
        assert status.status == "delivered"
        assert status.id == "wamid.outbound123"

    def test_read_status(self):
        payload = WebhookPayload(**_status_payload("read"))
        results = extract_statuses(payload)
        assert results[0][1].status == "read"

    def test_message_payload_has_no_statuses(self):
        payload = WebhookPayload(**_text_message_payload())
        assert extract_statuses(payload) == []


class TestParseTimestamp:
    def test_valid_epoch(self):
        dt = parse_timestamp("1700000000")
        assert dt.tzinfo is timezone.utc
        assert dt.year == 2023

    def test_invalid_string_falls_back_to_now(self):
        before = datetime.now(timezone.utc)
        dt = parse_timestamp("not-a-number")
        after = datetime.now(timezone.utc)
        assert before <= dt <= after


class TestGetMessageBody:
    def test_text_message(self):
        msg = WAMessage(
            id="wamid.x",
            **{"from": "919"},
            timestamp="1700000000",
            type="text",
            text={"body": "hello"},
        )
        assert get_message_body(msg) == "hello"

    def test_button_reply(self):
        msg = WAMessage(
            id="wamid.x",
            **{"from": "919"},
            timestamp="1700000000",
            type="button",
            button={"text": "Yes", "payload": "yes_payload"},
        )
        assert get_message_body(msg) == "Yes"

    def test_interactive_button_reply(self):
        msg = WAMessage(
            id="wamid.x",
            **{"from": "919"},
            timestamp="1700000000",
            type="interactive",
            interactive={"button_reply": {"id": "b1", "title": "Book now"}},
        )
        assert get_message_body(msg) == "Book now"

    def test_image_returns_none(self):
        msg = WAMessage(
            id="wamid.x",
            **{"from": "919"},
            timestamp="1700000000",
            type="image",
            image={"id": "media123"},
        )
        assert get_message_body(msg) is None
