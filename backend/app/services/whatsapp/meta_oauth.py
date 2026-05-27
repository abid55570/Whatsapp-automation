"""Meta Embedded Signup OAuth code → access token exchange."""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.facebook.com"


class MetaOAuthError(Exception):
    """Meta OAuth code exchange failed."""


async def exchange_code_for_token(
    code: str,
    redirect_uri: str | None = None,
) -> str:
    """Exchange OAuth code from Embedded Signup → permanent access token.

    Returns: access_token string. Raises MetaOAuthError on failure.
    """
    if not (settings.META_APP_ID and settings.META_APP_SECRET):
        raise MetaOAuthError("META_APP_ID / META_APP_SECRET not configured")
    if not code:
        raise MetaOAuthError("code is empty")

    version = settings.META_GRAPH_API_VERSION
    params: dict[str, str] = {
        "client_id": settings.META_APP_ID,
        "client_secret": settings.META_APP_SECRET,
        "code": code,
    }
    if redirect_uri:
        params["redirect_uri"] = redirect_uri

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.get(
                f"{GRAPH_BASE}/{version}/oauth/access_token",
                params=params,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Meta OAuth exchange failed: %s — %s",
                exc.response.status_code,
                exc.response.text[:500],
            )
            raise MetaOAuthError(
                f"Meta returned {exc.response.status_code}: {exc.response.text[:200]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise MetaOAuthError(f"HTTP error: {exc}") from exc

    data = resp.json()
    access_token = data.get("access_token")
    if not access_token:
        raise MetaOAuthError(f"No access_token in response: {data}")
    return access_token


async def fetch_phone_number_display(
    phone_number_id: str, access_token: str
) -> str | None:
    """Look up the display phone number for a Meta phone_number_id.

    Best-effort: returns None if call fails.
    """
    if not (phone_number_id and access_token):
        return None
    version = settings.META_GRAPH_API_VERSION
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(
                f"{GRAPH_BASE}/{version}/{phone_number_id}",
                params={"fields": "display_phone_number,verified_name"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
        except httpx.HTTPError:
            return None
    data = resp.json()
    return data.get("display_phone_number")
