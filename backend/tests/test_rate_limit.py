"""Tests for app.core.rate_limit helpers."""
from unittest.mock import MagicMock

from app.core.rate_limit import get_ip_key, get_user_key


def _fake_request(headers=None, client_host="127.0.0.1"):
    r = MagicMock()
    r.headers = headers or {}
    r.client.host = client_host
    return r


def test_get_ip_uses_forwarded_for():
    r = _fake_request(headers={"x-forwarded-for": "1.2.3.4, 5.6.7.8"})
    assert get_ip_key(r) == "1.2.3.4"


def test_get_ip_falls_back_to_client():
    r = _fake_request(client_host="10.0.0.1")
    assert get_ip_key(r) == "10.0.0.1"


def test_get_user_key_with_bad_token_falls_back_to_ip():
    r = _fake_request(headers={"authorization": "Bearer garbage"})
    assert get_user_key(r).startswith("ip:")


def test_get_user_key_uses_jwt_subject():
    from app.core.security import create_access_token

    token = create_access_token("11111111-1111-1111-1111-111111111111")
    r = _fake_request(headers={"authorization": f"Bearer {token}"})
    assert get_user_key(r) == "user:11111111-1111-1111-1111-111111111111"
