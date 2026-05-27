"""Provider-agnostic AI client (Anthropic / OpenAI).

Both providers use httpx (no SDK dep). Provider chosen via `settings.AI_PROVIDER`.

Cost-optimized models:
  - Anthropic: claude-haiku-4-5 (~₹0.15 per reply)
  - OpenAI:    gpt-4o-mini       (~₹0.10 per reply)
"""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIError(Exception):
    """AI provider call failed."""


async def generate(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 500,
) -> str:
    """Provider-agnostic text generation. Raises AIError on failure."""
    provider = settings.AI_PROVIDER
    if provider == "anthropic":
        return await _anthropic(prompt, system, max_tokens)
    return await _openai(prompt, system, max_tokens)


# ============================================================
# Anthropic Claude (default)
# ============================================================


async def _anthropic(prompt: str, system: str | None, max_tokens: int) -> str:
    if not settings.ANTHROPIC_API_KEY:
        raise AIError("ANTHROPIC_API_KEY not configured")

    body: dict = {
        "model": settings.AI_MODEL or "claude-haiku-4-5",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                json=body,
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Anthropic API error %s: %s",
                exc.response.status_code,
                exc.response.text[:500],
            )
            raise AIError(
                f"Anthropic {exc.response.status_code}: {exc.response.text[:200]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise AIError(f"HTTP error: {exc}") from exc

    data = resp.json()
    content = data.get("content", [])
    if not content:
        return ""
    # Extract text from first content block
    for block in content:
        if block.get("type") == "text":
            return block.get("text", "")
    return ""


# ============================================================
# OpenAI (fallback)
# ============================================================


async def _openai(prompt: str, system: str | None, max_tokens: int) -> str:
    if not settings.OPENAI_API_KEY:
        raise AIError("OPENAI_API_KEY not configured")

    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": settings.AI_MODEL or "gpt-4o-mini",
        "messages": messages,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=body,
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "OpenAI API error %s: %s",
                exc.response.status_code,
                exc.response.text[:500],
            )
            raise AIError(
                f"OpenAI {exc.response.status_code}: {exc.response.text[:200]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise AIError(f"HTTP error: {exc}") from exc

    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content", "")
