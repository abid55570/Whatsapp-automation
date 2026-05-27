"""Orchestrator: parse webhook → persist → match intent → auto-reply.

Also detects WhatsApp deep-link verification messages ('verify-XXX') and
processes them as user signups instead of customer messages.
"""
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import (
    Business,
    BusinessIntent,
    Contact,
    Conversation,
    Message,
)
from app.models.enums import (
    ConversationCategory,
    ConversationStatus,
    MessageDirection,
    MessageStatus,
    MessageType,
)
from app.services.auth.verification import (
    consume_verification_code,
    extract_verification_code,
    looks_like_verification_message,
)
from app.services.matching import get_matching_engine
from app.services.matching.schemas import IntentDefinition
from app.services.sheets.syncer import SHEET_FAQ_PREFIX
from app.services.whatsapp.client import WhatsAppClient, WhatsAppClientError
from app.services.whatsapp.parser import get_message_body, parse_timestamp
from app.services.whatsapp.schemas import WAContact, WAMessage
from app.utils.phone import normalize_phone

logger = logging.getLogger(__name__)


# ======================================================================
# Public entrypoint
# ======================================================================


async def process_inbound_message(
    db: AsyncSession,
    phone_number_id: str,
    msg: WAMessage,
    contact_data: WAContact | None,
) -> Message | None:
    """Process one inbound WhatsApp message."""

    body = get_message_body(msg)
    sender_phone = normalize_phone(msg.from_)

    # ---------- Special case: verification messages to platform number ----------
    if (
        phone_number_id == settings.PLATFORM_WHATSAPP_PHONE_NUMBER_ID
        and looks_like_verification_message(body)
    ):
        await _handle_verification_message(db, sender_phone, body, msg.id)
        return None

    business = await _find_business(db, phone_number_id)
    if business is None:
        logger.warning(
            "No business registered for phone_number_id=%s", phone_number_id
        )
        return None

    # Idempotency check
    existing = await db.execute(
        select(Message).where(Message.whatsapp_message_id == msg.id)
    )
    if existing.scalar_one_or_none() is not None:
        logger.info("Skipping duplicate message %s", msg.id)
        return None

    contact = await _get_or_create_contact(db, business, sender_phone, contact_data)
    conversation = await _get_or_create_conversation(db, business, contact)

    message = Message(
        conversation_id=conversation.id,
        business_id=business.id,
        contact_id=contact.id,
        whatsapp_message_id=msg.id,
        direction=MessageDirection.INBOUND,
        type=_map_message_type(msg.type),
        status=MessageStatus.DELIVERED,
        body=body,
        delivered_at=parse_timestamp(msg.timestamp),
    )
    db.add(message)

    conversation.last_message_at = message.delivered_at
    conversation.unread_count += 1

    if not body:
        await db.commit()
        return message

    # ---------- Match ----------
    enabled_keys, custom_kw, custom_intents = await _load_intent_config(
        db, business.id
    )
    engine = get_matching_engine()
    result = engine.match(
        body,
        enabled_intents=enabled_keys or None,
        custom_keywords=custom_kw,
        custom_intents=custom_intents,
    )

    if result is not None:
        message.matched_intent_key = result.intent_key
        message.matched_confidence = result.confidence
        message.matched_layer = result.matched_layer
        message.detected_language = result.detected_language

    await db.commit()
    await db.refresh(message)

    detected_lang = result.detected_language if result else None

    # ---------- Gate: skip outbound work if subscription not active or over quota ----------
    from app.services.billing import business_can_send, has_conversation_quota

    if not await business_can_send(db, business):
        logger.info(
            "Business %s subscription not active — skipping auto-reply", business.id
        )
        return message

    await db.refresh(business, attribute_names=["subscription"])
    if not has_conversation_quota(business.subscription):
        logger.warning(
            "Business %s over conversation quota — skipping auto-reply",
            business.id,
        )
        return message

    # ---------- Order flow takes precedence over normal intent replies ----------
    if business.whatsapp_access_token:
        handled = await _handle_order_flow(
            db,
            business=business,
            contact=contact,
            conversation=conversation,
            body=body,
            detected_language=detected_lang,
        )
        if handled:
            return message

    if result is not None and business.whatsapp_access_token:
        await _send_auto_reply(
            db,
            business=business,
            contact=contact,
            conversation=conversation,
            intent_key=result.intent_key,
            detected_language=result.detected_language,
        )
    elif business.whatsapp_access_token:
        # No intent matched — try AI smart-reply if add-on enabled
        await _try_ai_smart_reply(
            db,
            business=business,
            contact=contact,
            conversation=conversation,
            customer_message=body,
            detected_language=detected_lang,
        )

    return message


async def _try_ai_smart_reply(
    db: AsyncSession,
    *,
    business: Business,
    contact: Contact,
    conversation: Conversation,
    customer_message: str,
    detected_language: str | None,
) -> None:
    """Send an AI-generated reply when matching engine missed.

    Only runs if business has AI add-on enabled + quota.
    """
    from app.services.billing import has_ai_quota, increment_ai_usage

    if not (business.subscription and business.subscription.ai_addon_enabled):
        return
    if not has_ai_quota(business.subscription):
        return

    from app.services.ai import generate_smart_reply

    # Load enabled intent names for context (so AI doesn't duplicate FAQs)
    intent_stmt = select(BusinessIntent).where(
        BusinessIntent.business_id == business.id,
        BusinessIntent.enabled.is_(True),
    )
    intents = (await db.execute(intent_stmt)).scalars().all()
    intent_names = [bi.intent_key for bi in intents]

    biz_type = (
        business.business_type.value
        if hasattr(business.business_type, "value")
        else str(business.business_type)
    )
    reply = await generate_smart_reply(
        business_name=business.name,
        business_type=biz_type,
        customer_message=customer_message,
        detected_language=detected_language,
        enabled_intent_names=intent_names,
    )
    if not reply:
        return

    # Send + persist as outbound auto-reply
    client = WhatsAppClient(
        phone_number_id=business.whatsapp_phone_number_id,
        access_token=business.whatsapp_access_token,
    )
    try:
        response = await client.send_text(
            to=contact.whatsapp_phone.lstrip("+"),
            body=reply,
        )
    except WhatsAppClientError as exc:
        logger.warning("AI smart-reply send failed: %s", exc)
        return

    outbound_id = None
    try:
        outbound_id = response.get("messages", [{}])[0].get("id")
    except (AttributeError, IndexError, TypeError):
        pass

    outbound = Message(
        conversation_id=conversation.id,
        business_id=business.id,
        contact_id=contact.id,
        whatsapp_message_id=outbound_id,
        direction=MessageDirection.OUTBOUND,
        type=MessageType.TEXT,
        status=MessageStatus.SENT,
        body=reply,
        is_auto_reply=True,
        matched_intent_key="ai_smart_reply",
        detected_language=detected_language,
        sent_at=datetime.now(timezone.utc),
    )
    db.add(outbound)
    await increment_ai_usage(db, business.id)
    await db.commit()


# ======================================================================
# Order flow state machine
# ======================================================================


async def _handle_order_flow(
    db: AsyncSession,
    *,
    business: Business,
    contact: Contact,
    conversation: Conversation,
    body: str,
    detected_language: str | None,
) -> bool:
    """Multi-turn order flow. Returns True if handled (skip auto-reply)."""
    from datetime import datetime, timezone

    from app.models import FulfillmentConfig, Product
    from app.services.orders import (
        CartItem,
        compute_ready_by,
        format_order_summary,
        format_pickup_time,
        is_affirmative,
        is_negative,
        looks_like_order,
        parse_order_text,
        parse_pickup_time,
    )

    state = dict(conversation.state or {})
    stage = state.get("stage", "idle")

    # ---------- Stage: confirming items → check yes/no ----------
    if stage == "confirming":
        if is_affirmative(body):
            # Move to pickup confirmation stage
            await _enter_pickup_stage(
                db, business, contact, conversation, state, detected_language
            )
            return True
        if is_negative(body):
            conversation.state = {}
            await db.commit()
            await _send_text(
                business,
                contact,
                _t_cancel_msg(detected_language),
                conversation,
            )
            return True
        # Anything else while confirming → re-prompt
        cart_items = [CartItem.from_dict(c) for c in state.get("cart", [])]
        if cart_items:
            summary = format_order_summary(cart_items, detected_language)
            await _send_text(business, contact, summary, conversation)
            return True

    # ---------- Stage: awaiting_pickup_confirm → yes/different time/no ----------
    if stage == "awaiting_pickup_confirm":
        if is_affirmative(body):
            # Move to payment method choice (or finalize if Razorpay not configured)
            await _enter_payment_stage(
                db, business, contact, conversation, state, detected_language
            )
            return True
        if is_negative(body):
            conversation.state = {}
            await db.commit()
            await _send_text(
                business,
                contact,
                _t_cancel_msg(detected_language),
                conversation,
            )
            return True
        # Try parsing as a different pickup time
        now = datetime.now(timezone.utc)
        new_time = parse_pickup_time(body, now)
        if new_time is not None:
            state["pickup_time"] = new_time.isoformat()
            conversation.state = state
            await db.commit()
            await _send_text(
                business,
                contact,
                _t_pickup_confirm(business, new_time, detected_language),
                conversation,
            )
            return True
        # Else — re-prompt with current state
        if state.get("pickup_time"):
            cur = datetime.fromisoformat(state["pickup_time"])
            await _send_text(
                business,
                contact,
                _t_pickup_confirm(business, cur, detected_language),
                conversation,
            )
            return True

    # ---------- Stage: awaiting_payment_choice → online/cash ----------
    if stage == "awaiting_payment_choice":
        choice = _detect_payment_choice(body)
        if choice == "online":
            state["payment_method"] = "online"
            conversation.state = state
            await db.commit()
            await _finalize_order(
                db,
                business=business,
                contact=contact,
                conversation=conversation,
                state=state,
                detected_language=detected_language,
            )
            return True
        if choice == "cash":
            state["payment_method"] = "cash_on_pickup"
            conversation.state = state
            await db.commit()
            await _finalize_order(
                db,
                business=business,
                contact=contact,
                conversation=conversation,
                state=state,
                detected_language=detected_language,
            )
            return True
        if is_negative(body):
            conversation.state = {}
            await db.commit()
            await _send_text(
                business, contact, _t_cancel_msg(detected_language), conversation
            )
            return True
        # Re-prompt
        await _send_text(
            business, contact, _t_payment_choice(detected_language), conversation
        )
        return True

    # ---------- Stage: idle → try to parse as order ----------
    if not looks_like_order(body):
        return False

    # Fetch products
    stmt = select(Product).where(Product.business_id == business.id)
    products = list((await db.execute(stmt)).scalars().all())
    if not products:
        return False

    parsed = parse_order_text(body, products)
    if not parsed:
        return False

    # Build cart
    cart_items = [
        CartItem(
            product_id=str(p.id),
            name=p.name,
            quantity=qty,
            unit_price_paise=p.price_paise,
        )
        for (p, qty, _score) in parsed
    ]

    # Save state
    conversation.state = {
        "stage": "confirming",
        "cart": [c.to_dict() for c in cart_items],
    }
    await db.commit()

    # Send order summary
    summary = format_order_summary(cart_items, detected_language)
    await _send_text(business, contact, summary, conversation)
    return True


_ONLINE_PAYMENT_WORDS = frozenset({
    "upi", "gpay", "google pay", "phonepe", "phone pe", "paytm",
    "online", "online pay", "online se", "online payment",
    "card", "credit card", "debit card", "net banking",
    "razorpay", "pay link", "link bhejo",
    "ऑनलाइन", "यूपीआई",
})

_CASH_PAYMENT_WORDS = frozenset({
    "cash", "cod", "cash on pickup", "cash on delivery",
    "nakad", "naqd", "naqdi",
    "pickup pe", "pickup par", "pickup pe doonga",
    "ghar pe", "ghar par",
    "नकद", "ज़मीन पर",
})


def _detect_payment_choice(text: str | None) -> str | None:
    """Return 'online' / 'cash' / None."""
    if not text:
        return None
    norm = text.strip().lower()
    if norm in _ONLINE_PAYMENT_WORDS:
        return "online"
    if norm in _CASH_PAYMENT_WORDS:
        return "cash"
    # Substring check for multi-word
    for w in _ONLINE_PAYMENT_WORDS:
        if w in norm:
            return "online"
    for w in _CASH_PAYMENT_WORDS:
        if w in norm:
            return "cash"
    return None


async def _enter_payment_stage(
    db: AsyncSession,
    business: Business,
    contact: Contact,
    conversation: Conversation,
    state: dict,
    detected_language: str | None,
) -> None:
    """After pickup time confirmed, ask payment method.

    If Razorpay not configured for the platform → skip, finalize w/ COD.
    """
    if not (settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET):
        # No online option available — default to cash
        state["payment_method"] = "cash_on_pickup"
        conversation.state = state
        await db.commit()
        await _finalize_order(
            db,
            business=business,
            contact=contact,
            conversation=conversation,
            state=state,
            detected_language=detected_language,
        )
        return

    state["stage"] = "awaiting_payment_choice"
    conversation.state = state
    await db.commit()
    await _send_text(
        business, contact, _t_payment_choice(detected_language), conversation
    )


async def _enter_pickup_stage(
    db: AsyncSession,
    business: Business,
    contact: Contact,
    conversation: Conversation,
    state: dict,
    detected_language: str | None,
) -> None:
    """Move from `confirming` items → `awaiting_pickup_confirm`.

    Computes ready_by from FulfillmentConfig, stores in state, sends prompt.
    """
    from datetime import datetime, timezone

    from app.models import FulfillmentConfig
    from app.services.orders import CartItem, compute_ready_by

    cart = [CartItem.from_dict(c) for c in state.get("cart", [])]
    if not cart:
        conversation.state = {}
        await db.commit()
        return

    # Load or auto-default fulfillment config
    stmt = select(FulfillmentConfig).where(
        FulfillmentConfig.business_id == business.id
    )
    config = (await db.execute(stmt)).scalar_one_or_none()

    now = datetime.now(timezone.utc)
    item_count = sum(c.quantity for c in cart)
    ready_by = compute_ready_by(config, item_count=item_count, now=now)

    state["stage"] = "awaiting_pickup_confirm"
    state["pickup_time"] = ready_by.isoformat()
    conversation.state = state
    await db.commit()

    await _send_text(
        business,
        contact,
        _t_pickup_confirm(business, ready_by, detected_language),
        conversation,
    )


async def _finalize_order(
    db: AsyncSession,
    *,
    business: Business,
    contact: Contact,
    conversation: Conversation,
    state: dict,
    detected_language: str | None,
) -> None:
    """Create Order + OrderItem rows from confirmed cart. Send confirmation."""
    from uuid import UUID

    from app.models import FulfillmentConfig, Order, OrderItem
    from app.models.enums import (
        FulfillmentType,
        OrderStatus,
        PaymentMethod,
        PaymentStatus,
    )
    from app.services.orders import CartItem

    cart = [CartItem.from_dict(c) for c in state.get("cart", [])]
    if not cart:
        conversation.state = {}
        await db.commit()
        return

    total_paise = sum(c.subtotal_paise for c in cart)
    order_number = f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{str(contact.id)[:6]}"

    pickup_time = None
    pickup_iso = state.get("pickup_time")
    if pickup_iso:
        try:
            pickup_time = datetime.fromisoformat(pickup_iso)
        except (ValueError, TypeError):
            pickup_time = None

    stmt = select(FulfillmentConfig).where(
        FulfillmentConfig.business_id == business.id
    )
    config = (await db.execute(stmt)).scalar_one_or_none()
    landmark = config.pickup_landmark if config else None

    # Payment method from state (set in payment_choice stage), default COD
    method_str = state.get("payment_method", "cash_on_pickup")
    if method_str == "online":
        payment_method = PaymentMethod.ONLINE
    else:
        payment_method = PaymentMethod.CASH_ON_PICKUP

    order = Order(
        business_id=business.id,
        contact_id=contact.id,
        order_number=order_number,
        status=OrderStatus.CONFIRMED,
        payment_status=PaymentStatus.PENDING,
        fulfillment_type=FulfillmentType.PICKUP,
        pickup_time=pickup_time,
        pickup_landmark=landmark,
        payment_method=payment_method,
        total_paise=total_paise,
        items_count=sum(c.quantity for c in cart),
    )
    db.add(order)
    await db.flush()

    for c in cart:
        try:
            product_uuid = UUID(c.product_id)
        except ValueError:
            product_uuid = None
        item = OrderItem(
            order_id=order.id,
            product_id=product_uuid,
            product_name=c.name,
            price_paise=c.unit_price_paise,
            quantity=c.quantity,
            subtotal_paise=c.subtotal_paise,
        )
        db.add(item)

    # If online payment chosen → create Razorpay link and send
    payment_link_url: str | None = None
    if payment_method == PaymentMethod.ONLINE:
        payment_link_url = await _create_payment_link_safe(
            order=order,
            business=business,
            contact=contact,
            db=db,
        )

    conversation.state = {
        "stage": "complete",
        "last_order_id": str(order.id),
    }
    await db.commit()

    confirm_msg = _t_confirm_msg(
        order_number,
        total_paise,
        pickup_time,
        payment_method,
        payment_link_url,
        detected_language,
    )
    await _send_text(business, contact, confirm_msg, conversation)


async def _create_payment_link_safe(
    *,
    order: "Order",
    business: Business,
    contact: Contact,
    db: AsyncSession,
) -> str | None:
    """Create Razorpay payment link (best-effort). Returns short_url or None."""
    from app.services.payments import RazorpayClient, RazorpayError

    try:
        client = RazorpayClient()
        result = await client.create_payment_link(
            amount_paise=order.total_paise,
            customer_name=contact.name,
            customer_phone=contact.whatsapp_phone,
            description=f"Order #{order.order_number}",
            order_id=str(order.id),
            business_id=str(business.id),
        )
        order.razorpay_payment_link_id = result.get("id")
        await db.commit()
        return result.get("short_url")
    except RazorpayError as exc:
        logger.warning("Razorpay link creation failed: %s", exc)
        return None
    except Exception as exc:
        logger.exception("Unexpected Razorpay error: %s", exc)
        return None


async def _send_text(
    business: Business,
    contact: Contact,
    body: str,
    conversation: Conversation,
) -> None:
    """Send a plain text message + persist it as outbound Message."""
    if not (business.whatsapp_phone_number_id and business.whatsapp_access_token):
        return
    client = WhatsAppClient(
        phone_number_id=business.whatsapp_phone_number_id,
        access_token=business.whatsapp_access_token,
    )
    try:
        await client.send_text(
            to=contact.whatsapp_phone.lstrip("+"),
            body=body,
        )
    except WhatsAppClientError as exc:
        logger.error("Failed to send order-flow message: %s", exc)


def _t_cancel_msg(lang: str | None) -> str:
    table = {
        "english": "❌ Order canceled. Reply with items anytime to start over.",
        "hindi": "❌ ऑर्डर रद्द हुआ। फिर से शुरू करने के लिए items लिखें।",
        "hinglish": "❌ Order cancel ho gaya. Phir se shuru karne ke liye items likhein.",
        "bengali": "❌ অর্ডার বাতিল। আবার শুরু করতে items লিখুন।",
        "urdu": "❌ Order cancel ho gaya. Phir se shuru karne ke liye items likhein.",
        "bhojpuri": "❌ Order cancel ho gail. Phir se shuru khatir items likhi.",
    }
    return table.get(lang or "english", table["english"])


def _t_confirm_msg(
    order_number: str,
    total_paise: int,
    pickup_time: "datetime | None",
    payment_method: "PaymentMethod | None",
    payment_link_url: str | None,
    lang: str | None,
) -> str:
    from app.models.enums import PaymentMethod
    from app.services.orders import format_pickup_time

    total = total_paise / 100
    total_s = f"₹{int(total)}" if total == int(total) else f"₹{total:.2f}"
    pickup_s = format_pickup_time(pickup_time) if pickup_time else "soon"

    is_online = payment_method == PaymentMethod.ONLINE
    pay_line_en = (
        f"💳 Pay now: {payment_link_url}"
        if is_online and payment_link_url
        else "💵 Payment: Cash on pickup"
    )
    pay_line_hi = (
        f"💳 अभी पे करें: {payment_link_url}"
        if is_online and payment_link_url
        else "💵 भुगतान: पिकअप पर नकद"
    )
    pay_line_hg = (
        f"💳 Abhi pay karein: {payment_link_url}"
        if is_online and payment_link_url
        else "💵 Payment: Cash on pickup"
    )

    table = {
        "english": (
            f"✅ *Order #{order_number} confirmed!*\n\n"
            f"📅 Pickup by: *{pickup_s}*\n"
            f"💰 Total: {total_s}\n"
            f"{pay_line_en}\n\n"
            f"We'll remind you when it's ready."
        ),
        "hindi": (
            f"✅ *ऑर्डर #{order_number} कन्फर्म!*\n\n"
            f"📅 पिकअप: *{pickup_s}*\n"
            f"💰 कुल: {total_s}\n"
            f"{pay_line_hi}\n\n"
            f"जब तैयार होगा हम याद दिलाएंगे।"
        ),
        "hinglish": (
            f"✅ *Order #{order_number} confirmed!*\n\n"
            f"📅 Pickup by: *{pickup_s}*\n"
            f"💰 Total: {total_s}\n"
            f"{pay_line_hg}\n\n"
            f"Ready hone par yaad dilayenge."
        ),
        "bengali": (
            f"✅ *অর্ডার #{order_number} কনফার্ম!*\n\n"
            f"📅 পিকআপ: *{pickup_s}*\n"
            f"💰 মোট: {total_s}\n"
            f"{pay_line_en}"
        ),
        "urdu": (
            f"✅ *Order #{order_number} confirmed!*\n\n"
            f"📅 Pickup: *{pickup_s}*\n"
            f"💰 Total: {total_s}\n"
            f"{pay_line_hg}"
        ),
        "bhojpuri": (
            f"✅ *Order #{order_number} confirmed!*\n\n"
            f"📅 Pickup: *{pickup_s}*\n"
            f"💰 Kul: {total_s}\n"
            f"{pay_line_hg}"
        ),
    }
    return table.get(lang or "english", table["english"])


def _t_payment_choice(lang: str | None) -> str:
    table = {
        "english": (
            "💳 *How would you like to pay?*\n\n"
            "Reply *online* for UPI/card payment now,\n"
            "or *cash* to pay at pickup."
        ),
        "hindi": (
            "💳 *भुगतान कैसे करेंगे?*\n\n"
            "*online* लिखें UPI/कार्ड से अभी,\n"
            "या *cash* लिखें पिकअप पर देने के लिए।"
        ),
        "hinglish": (
            "💳 *Payment kaise karenge?*\n\n"
            "*online* likhein UPI/card se abhi,\n"
            "ya *cash* likhein pickup pe paid karne ke liye."
        ),
        "bengali": (
            "💳 *পেমেন্ট কীভাবে?*\n\n"
            "*online* — UPI/কার্ড,  *cash* — পিকআপে।"
        ),
        "urdu": (
            "💳 *Payment kaise karenge?*\n\n"
            "*online* — UPI/card,  *cash* — pickup par."
        ),
        "bhojpuri": (
            "💳 *Payment kaise hoi?*\n\n"
            "*online* UPI/card,  *cash* pickup pe."
        ),
    }
    return table.get(lang or "english", table["english"])


def _t_pickup_confirm(
    business: "Business", pickup_time: "datetime", lang: str | None
) -> str:
    """Prompt customer to confirm pickup time (or send different)."""
    from app.services.orders import format_pickup_time

    pickup_s = format_pickup_time(pickup_time)
    addr = ""
    if business.fulfillment_config and business.fulfillment_config.pickup_address:
        addr = f"\n📍 {business.fulfillment_config.pickup_address}"

    table = {
        "english": (
            f"🚶 *Pickup Details*{addr}\n\n"
            f"⏰ Ready by *{pickup_s}*\n\n"
            f"Reply *YES* to confirm, or send a different time (e.g. \"5 pm\")."
        ),
        "hindi": (
            f"🚶 *पिकअप विवरण*{addr}\n\n"
            f"⏰ तैयार होगा *{pickup_s}* तक\n\n"
            f"*YES* लिखें कन्फर्म करने के लिए, या अलग समय भेजें (जैसे \"5 बजे\")।"
        ),
        "hinglish": (
            f"🚶 *Pickup Details*{addr}\n\n"
            f"⏰ Ready by *{pickup_s}*\n\n"
            f"*YES* likhein confirm karne ke liye, ya alag time bhejein (jaise \"5 baje\")."
        ),
        "bengali": (
            f"🚶 *পিকআপ বিবরণ*{addr}\n\n"
            f"⏰ প্রস্তুত হবে *{pickup_s}*\n\n"
            f"*YES* লিখুন কনফার্ম করতে।"
        ),
        "urdu": (
            f"🚶 *Pickup Details*{addr}\n\n"
            f"⏰ Ready by *{pickup_s}*\n\n"
            f"*YES* likhein confirm karne ke liye."
        ),
        "bhojpuri": (
            f"🚶 *Pickup Details*{addr}\n\n"
            f"⏰ Ready by *{pickup_s}*\n\n"
            f"*YES* likhi confirm khatir."
        ),
    }
    return table.get(lang or "english", table["english"])


# ======================================================================
# Verification handler
# ======================================================================


async def _handle_verification_message(
    db: AsyncSession,
    phone: str,
    body: str,
    wamid: str,
) -> None:
    code = extract_verification_code(body)
    if not code:
        return

    user = await consume_verification_code(db, phone=phone, code=code)
    if user is None:
        logger.info("Verification failed for %s", phone)
        await _try_send_platform_reply(
            phone,
            "❌ Verification failed or expired. Return to the app and try again.",
        )
        return

    logger.info("User %s verified via WhatsApp deep link", user.id)
    await _try_send_platform_reply(
        phone,
        "✅ You're verified! Return to the app — you'll be logged in automatically.",
    )


async def _try_send_platform_reply(phone: str, body: str) -> None:
    if not (
        settings.PLATFORM_WHATSAPP_PHONE_NUMBER_ID
        and settings.PLATFORM_WHATSAPP_ACCESS_TOKEN
    ):
        return

    client = WhatsAppClient(
        phone_number_id=settings.PLATFORM_WHATSAPP_PHONE_NUMBER_ID,
        access_token=settings.PLATFORM_WHATSAPP_ACCESS_TOKEN,
    )
    try:
        await client.send_text(to=phone.lstrip("+"), body=body)
    except WhatsAppClientError as exc:
        logger.warning("Failed to send platform reply: %s", exc)


# ======================================================================
# Helpers
# ======================================================================


async def _find_business(
    db: AsyncSession, phone_number_id: str
) -> Business | None:
    stmt = select(Business).where(
        Business.whatsapp_phone_number_id == phone_number_id
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def _get_or_create_contact(
    db: AsyncSession,
    business: Business,
    wa_phone: str,
    contact_data: WAContact | None,
) -> Contact:
    stmt = select(Contact).where(
        Contact.business_id == business.id,
        Contact.whatsapp_phone == wa_phone,
    )
    contact = (await db.execute(stmt)).scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if contact is None:
        name = (
            contact_data.profile.name
            if contact_data and contact_data.profile
            else None
        )
        contact = Contact(
            business_id=business.id,
            whatsapp_phone=wa_phone,
            name=name,
            first_seen_at=now,
            last_seen_at=now,
        )
        db.add(contact)
        await db.flush()
    else:
        contact.last_seen_at = now

    return contact


async def _get_or_create_conversation(
    db: AsyncSession, business: Business, contact: Contact
) -> Conversation:
    now = datetime.now(timezone.utc)
    stmt = (
        select(Conversation)
        .where(
            Conversation.business_id == business.id,
            Conversation.contact_id == contact.id,
            Conversation.status == ConversationStatus.OPEN,
            Conversation.expires_at > now,
        )
        .order_by(Conversation.started_at.desc())
        .limit(1)
    )
    conv = (await db.execute(stmt)).scalar_one_or_none()

    if conv is None:
        conv = Conversation(
            business_id=business.id,
            contact_id=contact.id,
            category=ConversationCategory.SERVICE,
            status=ConversationStatus.OPEN,
            started_at=now,
            expires_at=now + timedelta(hours=24),
            last_message_at=now,
        )
        db.add(conv)
        await db.flush()
        # Count this new 24h window against plan quota
        from app.services.billing import increment_conversation_usage
        await increment_conversation_usage(db, business.id)

    return conv


async def _load_intent_config(
    db: AsyncSession, business_id: UUID
) -> tuple[list[str], dict[str, list[str]], dict[str, IntentDefinition]]:
    """Return (enabled_keys, custom_kw_per_intent, synthetic_intents).

    Synthetic intents are built from sheet-derived BusinessIntent rows
    (intent_key starting with sheet_faq_). These don't exist in the
    global intent library, so we construct IntentDefinitions for them.
    """
    stmt = select(BusinessIntent).where(
        BusinessIntent.business_id == business_id,
        BusinessIntent.enabled.is_(True),
    )
    rows = (await db.execute(stmt)).scalars().all()

    enabled = [r.intent_key for r in rows]
    custom_kw: dict[str, list[str]] = {
        r.intent_key: list(r.custom_keywords) for r in rows
    }
    synthetic: dict[str, IntentDefinition] = {}
    for r in rows:
        if r.intent_key.startswith(SHEET_FAQ_PREFIX) and r.custom_keywords:
            synthetic[r.intent_key] = IntentDefinition(
                key=r.intent_key,
                name="Sheet FAQ",
                description="Custom FAQ from Google Sheet",
                default_reply_template=r.reply_text,
                languages={"custom": list(r.custom_keywords)},
                priority=r.priority,
                category="sheet",
            )

    return enabled, custom_kw, synthetic


async def _send_auto_reply(
    db: AsyncSession,
    *,
    business: Business,
    contact: Contact,
    conversation: Conversation,
    intent_key: str,
    detected_language: str | None = None,
) -> None:
    from app.services.intents import pick_reply

    stmt = select(BusinessIntent).where(
        BusinessIntent.business_id == business.id,
        BusinessIntent.intent_key == intent_key,
    )
    intent = (await db.execute(stmt)).scalar_one_or_none()
    if intent is None or not intent.reply_text:
        return

    # Pick reply matching customer's detected language (smart fallback)
    body_to_send = pick_reply(
        reply_text=intent.reply_text,
        reply_translations=intent.reply_translations or {},
        detected_language=detected_language,
    )

    # Dynamic override: ask_menu / ask_services use live catalog data
    dynamic = await _try_dynamic_body(
        db, business, intent_key, detected_language
    )
    if dynamic:
        body_to_send = dynamic

    # AI translation fallback: owner only wrote English, customer wrote
    # in another language, and AI add-on is on
    if (
        detected_language
        and detected_language not in ("english", "en")
        and business.subscription
        and business.subscription.ai_addon_enabled
    ):
        from app.services.billing import has_ai_quota, increment_ai_usage

        translations = intent.reply_translations or {}
        has_owner_translation = any(
            translations.get(k, "").strip()
            for k in ("hi", "hinglish", "bn", "ur", "bho")
        )
        # Only translate if owner didn't provide one AND quota available
        if not has_owner_translation and has_ai_quota(business.subscription):
            from app.services.ai import translate_to

            translated = await translate_to(body_to_send, detected_language)
            if translated:
                body_to_send = translated
                await increment_ai_usage(db, business.id)
                await db.commit()

    client = WhatsAppClient(
        phone_number_id=business.whatsapp_phone_number_id,
        access_token=business.whatsapp_access_token,
    )

    try:
        response = await client.send_text(
            to=contact.whatsapp_phone.lstrip("+"),
            body=body_to_send,
        )
    except WhatsAppClientError as exc:
        logger.error("Failed to send auto-reply: %s", exc)
        return

    outbound_id = None
    try:
        outbound_id = response.get("messages", [{}])[0].get("id")
    except (AttributeError, IndexError, TypeError):
        pass

    outbound = Message(
        conversation_id=conversation.id,
        business_id=business.id,
        contact_id=contact.id,
        whatsapp_message_id=outbound_id,
        direction=MessageDirection.OUTBOUND,
        type=MessageType.TEXT,
        status=MessageStatus.SENT,
        body=body_to_send,
        media_url=intent.media_url,
        is_auto_reply=True,
        matched_intent_key=intent_key,
        detected_language=detected_language,
        sent_at=datetime.now(timezone.utc),
    )
    db.add(outbound)
    await db.commit()


async def _try_dynamic_body(
    db: AsyncSession,
    business: Business,
    intent_key: str,
    detected_language: str | None,
) -> str | None:
    """If intent is ask_menu / ask_services AND catalog data exists,
    return dynamic text built from Products / Services. None → use static.
    """
    if intent_key == "ask_menu":
        from app.models import Product
        from app.services.menu import generate_menu_text

        stmt = (
            select(Product)
            .where(Product.business_id == business.id)
            .order_by(Product.category.nulls_last(), Product.name)
        )
        products = list((await db.execute(stmt)).scalars().all())
        if not products:
            return None
        return generate_menu_text(
            business.name, products, detected_language=detected_language
        ) or None

    if intent_key == "ask_services":
        from app.models import Service
        from app.services.menu import generate_services_text

        stmt = (
            select(Service)
            .where(Service.business_id == business.id, Service.is_active.is_(True))
            .order_by(Service.name)
        )
        services = list((await db.execute(stmt)).scalars().all())
        if not services:
            return None
        return generate_services_text(
            business.name, services, detected_language=detected_language
        ) or None

    return None


def _map_message_type(meta_type: str) -> MessageType:
    mapping = {
        "text": MessageType.TEXT,
        "image": MessageType.IMAGE,
        "document": MessageType.DOCUMENT,
        "audio": MessageType.AUDIO,
        "video": MessageType.VIDEO,
        "sticker": MessageType.STICKER,
        "location": MessageType.LOCATION,
        "contacts": MessageType.CONTACTS,
        "template": MessageType.TEMPLATE,
        "interactive": MessageType.INTERACTIVE,
        "button": MessageType.BUTTON,
    }
    return mapping.get(meta_type, MessageType.UNKNOWN)
