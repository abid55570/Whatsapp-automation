"""Shared pytest fixtures for the WhatsApp SaaS backend.

Tests run inside the backend container (docker compose run --rm backend pytest)
against a dedicated `whatsapp_saas_test` Postgres DB. The conftest:
  1. Sets test-only env vars BEFORE app is imported.
  2. Creates the test DB (idempotent).
  3. Creates all tables once per session, wipes them between tests.
  4. Overrides `get_db` so the FastAPI app uses the test session.
  5. Provides factories for User, Business, Subscription, etc.
  6. Mocks every external HTTP call (Meta, Razorpay, AI).
"""
from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import AsyncGenerator, Iterator
from datetime import datetime, timedelta, timezone
from typing import Any

# ============================================================
# Environment setup — MUST run before app imports
# ============================================================
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@postgres:5432/whatsapp_saas_test",
)
os.environ.setdefault(
    "SYNC_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@postgres:5432/whatsapp_saas_test",
)
os.environ.setdefault("REDIS_URL", "memory://")
os.environ.setdefault("CELERY_BROKER_URL", "memory://")
os.environ.setdefault("CELERY_RESULT_BACKEND", "cache+memory://")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("SECRET_KEY", "test-secret-key-only-for-tests")
os.environ.setdefault("ENCRYPTION_KEY", "")
os.environ.setdefault("RAZORPAY_KEY_ID", "rzp_test_key")
os.environ.setdefault("RAZORPAY_KEY_SECRET", "rzp_test_secret")
os.environ.setdefault("RAZORPAY_WEBHOOK_SECRET", "rzp_webhook_secret")
os.environ.setdefault("RAZORPAY_PLAN_ID_STARTER", "plan_starter")
os.environ.setdefault("RAZORPAY_PLAN_ID_GROWTH", "plan_growth")
os.environ.setdefault("RAZORPAY_PLAN_ID_PRO", "plan_pro")
os.environ.setdefault("RAZORPAY_PLAN_ID_AI_ADDON", "plan_ai_addon")
os.environ.setdefault("META_APP_ID", "test_meta_app")
os.environ.setdefault("META_APP_SECRET", "test_meta_secret")
os.environ.setdefault("META_WEBHOOK_VERIFY_TOKEN", "verify_token_xyz")
os.environ.setdefault("PLATFORM_WHATSAPP_PHONE_NUMBER", "+919999999999")
os.environ.setdefault("PLATFORM_WHATSAPP_PHONE_NUMBER_ID", "0000000000")
os.environ.setdefault("PLATFORM_WHATSAPP_ACCESS_TOKEN", "platform_token")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models import (
    Base,
    Business,
    BusinessIntent,
    Contact,
    Conversation,
    FulfillmentConfig,
    Message,
    Order,
    OrderItem,
    Product,
    Subscription,
    User,
    WebhookEvent,
)
from app.models.enums import (
    BusinessType,
    ConversationCategory,
    ConversationStatus,
    MessageDirection,
    MessageStatus,
    MessageType,
    PlanType,
    SubscriptionStatus,
)


# ============================================================
# Bootstrap test database
# ============================================================


def _ensure_test_database() -> None:
    """Create the test database if it does not exist."""
    url = make_url(settings.SYNC_DATABASE_URL)
    target_db = url.database
    admin_url = url.set(database="postgres")
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :n"),
                {"n": target_db},
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{target_db}"'))
    finally:
        engine.dispose()


# ============================================================
# Engine & session
# ============================================================


@pytest_asyncio.fixture(scope="session")
async def _engine():
    _ensure_test_database()
    engine = create_async_engine(settings.DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def _session_factory(_engine):
    return async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture()
async def db(_engine, _session_factory) -> AsyncGenerator[AsyncSession, None]:
    """A fresh DB session per test. Truncates every table after the test."""
    async with _session_factory() as session:
        try:
            yield session
        finally:
            try:
                await session.rollback()
            except Exception:
                pass

    # Wipe all tables (order doesn't matter with CASCADE)
    async with _engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))


# ============================================================
# FastAPI app + httpx client
# ============================================================


@pytest_asyncio.fixture()
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """An httpx AsyncClient bound to the FastAPI app with db override."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ============================================================
# Factories
# ============================================================


async def create_user(
    db: AsyncSession,
    *,
    phone: str | None = None,
    full_name: str = "Test User",
    is_superuser: bool = False,
    is_active: bool = True,
    phone_verified: bool = True,
    preferred_language: str = "en",
) -> User:
    phone = phone or f"+9198765{uuid.uuid4().int % 100000:05d}"
    user = User(
        phone=phone,
        full_name=full_name,
        is_active=is_active,
        is_superuser=is_superuser,
        phone_verified=phone_verified,
        preferred_language=preferred_language,
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_business(
    db: AsyncSession,
    *,
    owner: User,
    name: str = "Test Kirana",
    business_type: BusinessType = BusinessType.SHOP,
    languages: list[str] | None = None,
    whatsapp_connected: bool = False,
    onboarding_completed: bool = True,
) -> Business:
    biz = Business(
        owner_user_id=owner.id,
        name=name,
        business_type=business_type,
        languages=languages or ["english", "hindi"],
        onboarding_completed=onboarding_completed,
    )
    if whatsapp_connected:
        biz.whatsapp_phone_number_id = f"phid_{uuid.uuid4().hex[:10]}"
        biz.whatsapp_business_account_id = f"wba_{uuid.uuid4().hex[:10]}"
        biz.whatsapp_display_phone = "+919876543210"
        biz.whatsapp_access_token = "EAATESTTOKEN1234"
    db.add(biz)
    await db.commit()
    await db.refresh(biz)
    return biz


async def create_subscription(
    db: AsyncSession,
    *,
    business: Business,
    plan: PlanType = PlanType.TRIAL,
    status: SubscriptionStatus = SubscriptionStatus.TRIALING,
    conversations_included: int = 100,
    conversations_used: int = 0,
    trial_days_remaining: int = 14,
    ai_addon_enabled: bool = False,
) -> Subscription:
    now = datetime.now(timezone.utc)
    sub = Subscription(
        business_id=business.id,
        plan=plan,
        status=status,
        conversations_included=conversations_included,
        conversations_used=conversations_used,
        ai_addon_enabled=ai_addon_enabled,
        trial_started_at=now,
        trial_ends_at=now + timedelta(days=trial_days_remaining),
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


async def create_contact(
    db: AsyncSession,
    *,
    business: Business,
    phone: str | None = None,
    name: str | None = "Test Customer",
) -> Contact:
    contact = Contact(
        business_id=business.id,
        whatsapp_phone=phone or f"+9199876{uuid.uuid4().int % 100000:05d}",
        name=name,
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def create_conversation(
    db: AsyncSession,
    *,
    business: Business,
    contact: Contact,
    status: ConversationStatus = ConversationStatus.OPEN,
    category: ConversationCategory = ConversationCategory.SERVICE,
) -> Conversation:
    conv = Conversation(
        business_id=business.id,
        contact_id=contact.id,
        status=status,
        category=category,
        started_at=datetime.now(timezone.utc),
        last_message_at=datetime.now(timezone.utc),
        unread_count=0,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def create_message(
    db: AsyncSession,
    *,
    business: Business,
    conversation: Conversation,
    direction: MessageDirection = MessageDirection.INBOUND,
    body: str = "hi",
) -> Message:
    msg = Message(
        business_id=business.id,
        conversation_id=conversation.id,
        contact_id=conversation.contact_id,
        direction=direction,
        type=MessageType.TEXT,
        status=MessageStatus.DELIVERED,
        body=body,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


# ============================================================
# Authentication helpers
# ============================================================


def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture()
async def user(db: AsyncSession) -> User:
    return await create_user(db, phone="+919876500001")


@pytest_asyncio.fixture()
async def authed_user(db: AsyncSession) -> User:
    return await create_user(db, phone="+919876500002")


@pytest_asyncio.fixture()
async def superuser(db: AsyncSession) -> User:
    return await create_user(
        db, phone="+919876500003", full_name="Admin", is_superuser=True
    )


@pytest_asyncio.fixture()
async def business(db: AsyncSession, authed_user: User) -> Business:
    biz = await create_business(db, owner=authed_user, whatsapp_connected=True)
    await create_subscription(db, business=biz)
    return biz


# Convenience factories exported for test files
@pytest.fixture()
def factory():
    """Provide all factory functions on one object."""
    class _F:
        user = staticmethod(create_user)
        business = staticmethod(create_business)
        subscription = staticmethod(create_subscription)
        contact = staticmethod(create_contact)
        conversation = staticmethod(create_conversation)
        message = staticmethod(create_message)
    return _F()


# ============================================================
# Mock httpx — block all real outbound calls
# ============================================================


class MockTransport:
    """In-memory httpx transport that returns canned responses based on URL."""

    def __init__(self) -> None:
        self.calls: list[Any] = []
        self._handlers: list[tuple[str, Any]] = []

    def add(self, url_substring: str, response: dict) -> None:
        self._handlers.append((url_substring, response))


_EXTERNAL_HOSTS = (
    "graph.facebook.com",
    "api.razorpay.com",
    "api.openai.com",
    "api.anthropic.com",
)


def _is_external(url) -> bool:
    s = str(url)
    return any(h in s for h in _EXTERNAL_HOSTS)


@pytest.fixture(autouse=True)
def _mock_httpx(monkeypatch):
    """Mock outbound calls to external services. Internal ASGI calls pass through."""
    import httpx

    real_request = httpx.AsyncClient.request

    async def _maybe_mock(self, method, url, **kwargs):
        # If the test client uses a custom MockTransport, let it handle the call
        transport = getattr(self, "_transport", None)
        if isinstance(transport, httpx.MockTransport):
            return await real_request(self, method, url, **kwargs)
        if _is_external(url):
            # Canned response per service
            url_s = str(url)
            if "razorpay.com" in url_s and "payment_links" in url_s:
                payload = {
                    "id": f"plink_{uuid.uuid4().hex[:10]}",
                    "short_url": "https://rzp.io/i/mock",
                    "status": "created",
                }
            elif "razorpay.com" in url_s and "subscriptions" in url_s:
                payload = {
                    "id": f"sub_{uuid.uuid4().hex[:10]}",
                    "short_url": "https://rzp.io/i/submock",
                    "status": "created",
                    "plan_id": "plan_test",
                }
            elif "graph.facebook.com" in url_s and "oauth/access_token" in url_s:
                payload = {
                    "access_token": "EAATESTLONGLIVED",
                    "token_type": "bearer",
                }
            elif "graph.facebook.com" in url_s:
                payload = {
                    "display_phone_number": "+919876543210",
                    "verified_name": "Test Biz",
                }
            else:
                payload = {"ok": True}
            return httpx.Response(
                200,
                json=payload,
                request=httpx.Request(method, url),
            )
        return await real_request(self, method, url, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "request", _maybe_mock, raising=True)
    yield


# ============================================================
# Auto-stub AI client (so tests don't need API keys)
# ============================================================


@pytest.fixture()
def stub_ai(monkeypatch):
    """OPT-IN: force ai.client.generate() to return canned text."""
    async def fake_generate(prompt: str, system: str = "", max_tokens: int = 500, **_):
        return "Yeh ek auto-generated reply hai. (mock)"

    from app.services.ai import client as ai_client
    monkeypatch.setattr(ai_client, "generate", fake_generate, raising=False)
    yield


# ============================================================
# Async test mode marker (pyproject sets asyncio_mode=auto, so plain
# `async def test_*` works without extra decoration)
# ============================================================
