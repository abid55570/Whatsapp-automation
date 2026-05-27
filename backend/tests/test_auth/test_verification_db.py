"""DB-backed tests for verification flow."""
from app.services.auth.verification import (
    consume_verification_code,
    create_verification,
)


async def test_create_and_consume(db):
    otp, code, link = await create_verification(
        db, phone="+919000001001", full_name="Tester"
    )
    await db.commit()
    assert link.startswith("https://wa.me/")
    user = await consume_verification_code(
        db, phone="+919000001001", code=code
    )
    assert user is not None
    assert user.phone_verified is True


async def test_consume_invalid_code(db):
    await create_verification(db, phone="+919000001002")
    await db.commit()
    assert await consume_verification_code(
        db, phone="+919000001002", code="wrongcode"
    ) is None


async def test_create_invalidates_priors(db):
    _, c1, _ = await create_verification(db, phone="+919000001003")
    await db.commit()
    _, c2, _ = await create_verification(db, phone="+919000001003")
    await db.commit()
    assert await consume_verification_code(
        db, phone="+919000001003", code=c1
    ) is None
    assert await consume_verification_code(
        db, phone="+919000001003", code=c2
    ) is not None


async def test_consume_for_existing_user(db):
    from tests.conftest import create_user

    await create_user(db, phone="+919000001004", full_name="Old Name")
    _, code, _ = await create_verification(db, phone="+919000001004")
    await db.commit()
    user = await consume_verification_code(
        db, phone="+919000001004", code=code, full_name="Should Not Override"
    )
    assert user is not None
    assert user.full_name == "Old Name"
    assert user.phone_verified is True
