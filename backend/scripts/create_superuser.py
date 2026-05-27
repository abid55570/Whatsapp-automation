"""CLI: create a superuser. Run inside the backend container.

Usage (inside docker compose):
    docker compose run --rm backend python scripts/create_superuser.py \\
        --phone "+919876543210" --name "Admin"

Or interactively:
    docker compose run --rm backend python scripts/create_superuser.py
"""
import argparse
import asyncio
import sys
from datetime import datetime, timezone


async def _create_superuser(phone: str, name: str | None) -> None:
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models import User
    from app.utils.phone import is_valid_phone, normalize_phone

    phone = normalize_phone(phone)
    if not is_valid_phone(phone):
        print(f"❌ Invalid phone: {phone}")
        sys.exit(1)

    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.phone == phone)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if user is not None:
            if user.is_superuser:
                print(f"✓ User {phone} already a superuser")
                return
            user.is_superuser = True
            user.is_active = True
            if name and not user.full_name:
                user.full_name = name
            await db.commit()
            print(f"✅ Granted superuser to existing user {phone}")
            return

        user = User(
            phone=phone,
            full_name=name,
            is_active=True,
            is_superuser=True,
            phone_verified=True,
            preferred_language="en",
            last_login_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✅ Created superuser {phone} (id: {user.id})")


def main():
    parser = argparse.ArgumentParser(description="Create a superuser")
    parser.add_argument("--phone", help="Phone (e.g. +919876543210 or 9876543210)")
    parser.add_argument("--name", default=None, help="Full name (optional)")
    args = parser.parse_args()

    phone = args.phone or input("Phone: ").strip()
    name = args.name or input("Name (optional): ").strip() or None

    asyncio.run(_create_superuser(phone, name))


if __name__ == "__main__":
    main()
