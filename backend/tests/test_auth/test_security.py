"""Tests for JWT + bcrypt utilities."""
import time
from datetime import timedelta
from uuid import uuid4

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_secret,
    verify_secret,
)


class TestJWT:
    def test_roundtrip(self):
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)

    def test_string_subject(self):
        token = create_access_token("user-abc-123")
        payload = decode_access_token(token)
        assert payload["sub"] == "user-abc-123"

    def test_extra_claims_preserved(self):
        token = create_access_token(
            "u1", extra_claims={"role": "owner", "biz_id": "b1"}
        )
        payload = decode_access_token(token)
        assert payload["role"] == "owner"
        assert payload["biz_id"] == "b1"

    def test_expired_token_returns_none(self):
        token = create_access_token(
            "u1", expires_delta=timedelta(seconds=-1)
        )
        assert decode_access_token(token) is None

    def test_invalid_token_returns_none(self):
        assert decode_access_token("not.a.jwt") is None
        assert decode_access_token("") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token("u1")
        # Modify last char of signature
        tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
        assert decode_access_token(tampered) is None

    def test_includes_iat_and_exp(self):
        token = create_access_token("u1")
        payload = decode_access_token(token)
        assert "iat" in payload
        assert "exp" in payload
        assert payload["exp"] > payload["iat"]


class TestHashing:
    def test_hash_and_verify(self):
        plain = "myCode1234"
        hashed = hash_secret(plain)
        assert hashed != plain
        assert verify_secret(plain, hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_secret("correct")
        assert verify_secret("wrong", hashed) is False

    def test_empty_input(self):
        assert verify_secret("", "not-a-real-hash") is False

    def test_hash_is_different_each_time(self):
        """Bcrypt uses random salts → same input produces different hashes."""
        plain = "same"
        assert hash_secret(plain) != hash_secret(plain)
