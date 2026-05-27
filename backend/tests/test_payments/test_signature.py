"""Test Razorpay webhook signature verification."""
import hashlib
import hmac

from app.services.payments.razorpay_client import verify_razorpay_signature


def test_valid_signature():
    secret = "shhh"
    payload = b'{"event": "payment.captured"}'
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_razorpay_signature(payload, sig, secret) is True


def test_invalid_signature():
    assert verify_razorpay_signature(
        b"payload", "bogus", "secret"
    ) is False


def test_empty_inputs():
    assert verify_razorpay_signature(b"", "sig", "secret") is False
    assert verify_razorpay_signature(b"x", "", "secret") is False
    assert verify_razorpay_signature(b"x", "sig", "") is False
