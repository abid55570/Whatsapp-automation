"""Integration tests for processor.process_inbound_message."""
import uuid

import pytest

from app.services.whatsapp.processor import process_inbound_message
from app.services.whatsapp.schemas import WAContact, WAMessage, WAProfile, WAText
from tests.conftest import (
    create_business,
    create_subscription,
    create_user,
)


def _wamsg(text: str = "hello", msg_type: str = "text", wamid: str | None = None) -> WAMessage:
    return WAMessage(
        id=wamid or f"wamid.{uuid.uuid4().hex[:12]}",
        **{"from": "919876543210"},
        timestamp="1700000000",
        type=msg_type,
        text=WAText(body=text) if msg_type == "text" else None,
    )


def _wacontact(name: str = "Test") -> WAContact:
    return WAContact(wa_id="919876543210", profile=WAProfile(name=name))


async def test_process_no_business_registered(db):
    msg = _wamsg("hi")
    result = await process_inbound_message(
        db, phone_number_id="phid_nonexistent", msg=msg, contact_data=_wacontact()
    )
    assert result is None


async def test_process_inbound_persists_message(db):
    user = await create_user(db, phone="+919000010001")
    biz = await create_business(db, owner=user, whatsapp_connected=True)
    await create_subscription(db, business=biz)
    msg = _wamsg("hi")
    result = await process_inbound_message(
        db,
        phone_number_id=biz.whatsapp_phone_number_id,
        msg=msg,
        contact_data=_wacontact(),
    )
    assert result is not None
    assert result.body == "hi"


async def test_process_idempotent(db):
    user = await create_user(db, phone="+919000010002")
    biz = await create_business(db, owner=user, whatsapp_connected=True)
    await create_subscription(db, business=biz)
    msg = _wamsg("idempotent", wamid="wamid.dup1")
    r1 = await process_inbound_message(
        db, phone_number_id=biz.whatsapp_phone_number_id, msg=msg, contact_data=None
    )
    assert r1 is not None
    # Same wamid → skip
    r2 = await process_inbound_message(
        db, phone_number_id=biz.whatsapp_phone_number_id, msg=msg, contact_data=None
    )
    assert r2 is None


async def test_process_non_text_no_match(db):
    user = await create_user(db, phone="+919000010003")
    biz = await create_business(db, owner=user, whatsapp_connected=True)
    await create_subscription(db, business=biz)
    msg = WAMessage(
        id="wamid.image1",
        **{"from": "919876543210"},
        timestamp="1700000001",
        type="image",
        image={"id": "img1"},
    )
    result = await process_inbound_message(
        db, phone_number_id=biz.whatsapp_phone_number_id, msg=msg, contact_data=None
    )
    # Persisted, no body
    assert result is not None
    assert result.body is None
