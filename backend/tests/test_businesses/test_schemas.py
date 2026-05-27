"""Tests for business and intent schema validation."""
import pytest
from pydantic import ValidationError

from app.schemas.business import (
    BusinessCreateRequest,
    BusinessUpdateRequest,
    OnboardingStatus,
    WhatsAppConnectRequest,
)
from app.schemas.intent import (
    BusinessIntentConfigure,
    BusinessIntentsBulkRequest,
    BusinessIntentUpdate,
)


# ============================================================
# BusinessCreateRequest
# ============================================================


class TestBusinessCreate:
    def test_valid(self):
        req = BusinessCreateRequest(
            name="Sharma Salon",
            business_type="salon",
            languages=["english", "hindi", "hinglish"],
        )
        assert req.name == "Sharma Salon"
        assert req.business_type.value == "salon"
        assert len(req.languages) == 3

    def test_default_timezone(self):
        req = BusinessCreateRequest(
            name="Test Shop",
            business_type="shop",
            languages=["english"],
        )
        assert req.timezone == "Asia/Kolkata"

    def test_name_too_short(self):
        with pytest.raises(ValidationError):
            BusinessCreateRequest(
                name="X",
                business_type="shop",
                languages=["english"],
            )

    def test_no_languages_rejected(self):
        with pytest.raises(ValidationError):
            BusinessCreateRequest(
                name="Test",
                business_type="shop",
                languages=[],
            )

    def test_invalid_business_type(self):
        with pytest.raises(ValidationError):
            BusinessCreateRequest(
                name="Test",
                business_type="nonexistent",
                languages=["english"],
            )

    def test_invalid_language(self):
        with pytest.raises(ValidationError):
            BusinessCreateRequest(
                name="Test",
                business_type="shop",
                languages=["klingon"],
            )

    @pytest.mark.parametrize(
        "btype",
        ["restaurant", "salon", "clinic", "shop", "gym", "coaching", "custom"],
    )
    def test_all_business_types_accepted(self, btype):
        req = BusinessCreateRequest(
            name="Test",
            business_type=btype,
            languages=["english"],
        )
        assert req.business_type.value == btype


# ============================================================
# BusinessUpdateRequest
# ============================================================


class TestBusinessUpdate:
    def test_partial_update(self):
        req = BusinessUpdateRequest(name="New Name")
        assert req.name == "New Name"
        assert req.business_type is None
        assert req.languages is None

    def test_all_fields_optional(self):
        req = BusinessUpdateRequest()
        assert req.name is None


# ============================================================
# WhatsAppConnectRequest
# ============================================================


class TestWhatsAppConnect:
    def test_valid(self):
        req = WhatsAppConnectRequest(
            phone_number_id="123456789",
            business_account_id="987654321",
            display_phone="+919876543210",
            access_token="EAABxxxxxxxxxxxxxx",
        )
        assert req.access_token == "EAABxxxxxxxxxxxxxx"

    def test_missing_phone_number_id(self):
        with pytest.raises(ValidationError):
            WhatsAppConnectRequest(access_token="EAABxxxxxxxxxxxxxx")

    def test_missing_access_token(self):
        with pytest.raises(ValidationError):
            WhatsAppConnectRequest(phone_number_id="123")

    def test_access_token_too_short(self):
        with pytest.raises(ValidationError):
            WhatsAppConnectRequest(phone_number_id="123", access_token="short")


# ============================================================
# BusinessIntentConfigure
# ============================================================


class TestBusinessIntentConfigure:
    def test_valid(self):
        cfg = BusinessIntentConfigure(
            intent_key="ask_price",
            reply_text="Our prices: ...",
        )
        assert cfg.enabled is True
        assert cfg.custom_keywords == []
        assert cfg.priority == 0

    def test_with_custom_keywords(self):
        cfg = BusinessIntentConfigure(
            intent_key="ask_price",
            reply_text="Reply",
            custom_keywords=["bhav", "bhaav"],
        )
        assert cfg.custom_keywords == ["bhav", "bhaav"]

    def test_disabled_intent(self):
        cfg = BusinessIntentConfigure(
            intent_key="book_appointment",
            reply_text="Reply",
            enabled=False,
        )
        assert cfg.enabled is False

    def test_empty_reply_rejected(self):
        with pytest.raises(ValidationError):
            BusinessIntentConfigure(
                intent_key="ask_price",
                reply_text="",
            )

    def test_too_many_custom_keywords(self):
        with pytest.raises(ValidationError):
            BusinessIntentConfigure(
                intent_key="ask_price",
                reply_text="Reply",
                custom_keywords=[f"kw{i}" for i in range(60)],
            )


# ============================================================
# BusinessIntentsBulkRequest
# ============================================================


class TestBulkIntents:
    def test_valid_bulk(self):
        req = BusinessIntentsBulkRequest(
            intents=[
                BusinessIntentConfigure(intent_key="ask_price", reply_text="R1"),
                BusinessIntentConfigure(intent_key="ask_timing", reply_text="R2"),
            ]
        )
        assert len(req.intents) == 2

    def test_empty_list_rejected(self):
        with pytest.raises(ValidationError):
            BusinessIntentsBulkRequest(intents=[])

    def test_too_many_intents_rejected(self):
        intents = [
            BusinessIntentConfigure(intent_key=f"intent_{i}", reply_text="R")
            for i in range(60)
        ]
        with pytest.raises(ValidationError):
            BusinessIntentsBulkRequest(intents=intents)


# ============================================================
# BusinessIntentUpdate (PATCH)
# ============================================================


class TestBusinessIntentUpdate:
    def test_all_optional(self):
        req = BusinessIntentUpdate()
        assert req.enabled is None
        assert req.reply_text is None

    def test_toggle_only(self):
        req = BusinessIntentUpdate(enabled=False)
        assert req.enabled is False
        assert req.reply_text is None

    def test_empty_reply_rejected_on_update(self):
        with pytest.raises(ValidationError):
            BusinessIntentUpdate(reply_text="")


# ============================================================
# OnboardingStatus
# ============================================================


class TestOnboardingStatus:
    def test_valid_steps(self):
        for step in [
            "create_business",
            "connect_whatsapp",
            "configure_intents",
            "done",
        ]:
            status = OnboardingStatus(
                user_exists=True,
                business_created=False,
                whatsapp_connected=False,
                intents_configured=False,
                onboarding_completed=False,
                next_step=step,
            )
            assert status.next_step == step

    def test_invalid_step_rejected(self):
        with pytest.raises(ValidationError):
            OnboardingStatus(
                user_exists=True,
                business_created=False,
                whatsapp_connected=False,
                intents_configured=False,
                onboarding_completed=False,
                next_step="not_a_real_step",
            )
