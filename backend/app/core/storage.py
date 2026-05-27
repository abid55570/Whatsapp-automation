"""Cloudflare R2 (S3-compatible) object storage for invoice PDFs.

Why R2 not S3:
  - No egress fees (PDFs are downloaded by customers — could be expensive on S3)
  - ~10× cheaper per-GB
  - S3 API compatible so we use boto3

Object key format:
    invoices/{business_id}/{fiscal_year}/{invoice_number}.pdf
    e.g. invoices/a1b2c3.../2026-27/INV-26-0042.pdf

Public delivery (one of two strategies):
  - Private bucket + signed URLs (default; safer)
  - Public custom domain bound to bucket (faster; relies on URL secrecy via UUID)
"""
from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Bubble-up errors from the storage layer."""


def _client() -> Any:
    """Build a boto3 S3 client pointed at Cloudflare R2.

    Lazily imports boto3 so the dependency is optional for tests that don't
    touch storage.
    """
    if not (settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY and settings.R2_ENDPOINT):
        raise StorageError("R2 not configured — set R2_ENDPOINT / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY")
    try:
        import boto3  # type: ignore
        from botocore.config import Config  # type: ignore
    except ImportError as exc:
        raise StorageError(
            "boto3 not installed. `pip install 'boto3>=1.34'` to use R2 storage."
        ) from exc

    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
    )


def upload_pdf(
    object_key: str,
    pdf_bytes: bytes,
    *,
    content_disposition: str | None = None,
    cache_control: str = "private, max-age=86400",
) -> str:
    """Upload a PDF to R2. Returns the object key on success."""
    if not object_key:
        raise StorageError("object_key required")
    if not pdf_bytes:
        raise StorageError("pdf_bytes empty")

    client = _client()
    extra: dict[str, str] = {
        "ContentType": "application/pdf",
        "CacheControl": cache_control,
    }
    if content_disposition:
        extra["ContentDisposition"] = content_disposition

    try:
        client.put_object(
            Bucket=settings.R2_BUCKET,
            Key=object_key,
            Body=pdf_bytes,
            **extra,
        )
    except Exception as exc:
        logger.error("R2 upload failed for %s: %s", object_key, exc)
        raise StorageError(f"R2 upload failed: {exc}") from exc

    logger.info("Uploaded %d bytes to r2://%s/%s", len(pdf_bytes), settings.R2_BUCKET, object_key)
    return object_key


def signed_url(object_key: str, ttl_seconds: int | None = None) -> str:
    """Generate a time-limited presigned download URL.

    If `R2_PUBLIC_BASE` is set, returns a permanent public URL instead — useful
    when the bucket is fronted by a custom domain and PDFs are intentionally
    public (e.g. customer needs to download anytime).
    """
    if settings.R2_PUBLIC_BASE:
        base = settings.R2_PUBLIC_BASE.rstrip("/")
        return f"{base}/{object_key}"

    ttl = ttl_seconds or settings.INVOICE_SIGNED_URL_TTL_DAYS * 86400
    client = _client()
    try:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.R2_BUCKET, "Key": object_key},
            ExpiresIn=ttl,
        )
    except Exception as exc:
        raise StorageError(f"Failed to sign URL: {exc}") from exc


def delete_object(object_key: str) -> None:
    """Hard-delete an object (used on invoice cancellation, optional)."""
    if not object_key:
        return
    client = _client()
    try:
        client.delete_object(Bucket=settings.R2_BUCKET, Key=object_key)
    except Exception as exc:
        logger.warning("R2 delete failed for %s: %s", object_key, exc)


def build_invoice_object_key(business_id: str, fiscal_year: str, invoice_number: str) -> str:
    """Canonical R2 object key for an invoice PDF."""
    safe_inv = invoice_number.replace("/", "-")
    return f"invoices/{business_id}/{fiscal_year}/{safe_inv}.pdf"
