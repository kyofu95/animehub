# type: ignore
# pylint: disable=redefined-outer-name, missing-function-docstring, unsubscriptable-object

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from jwt import encode as real_jwt_encode

from app.api.endpoints.utils.jwt import decode_token, encode_token
from app.core.config import jwt_settings
from app.core.exceptions import TokenError


@pytest.mark.asyncio
async def test_proper_jwt():

    id_ = uuid4()

    token = encode_token(id_, "access")
    assert token

    decoded_id = decode_token(token, "access")

    assert decoded_id == id_

    token = encode_token(id_, "refresh")
    assert token

    decoded_id = decode_token(token, "refresh")

    assert decoded_id == id_


@pytest.mark.asyncio
async def test_jwt_bad_tokens_access():

    with pytest.raises(TokenError) as exc_info:
        decode_token("", "access")

    assert exc_info.type is TokenError
    assert exc_info.value.args[0] == "Invalid token"

    with pytest.raises(TokenError) as exc_info:
        decode_token("bad_hash", "access")

    assert exc_info.type is TokenError
    assert exc_info.value.args[0] == "Invalid access token"


@pytest.mark.asyncio
async def test_jwt_bad_tokens_refresh():

    with pytest.raises(TokenError) as exc_info:
        decode_token("", "refresh")

    assert exc_info.type is TokenError
    assert exc_info.value.args[0] == "Invalid token"

    with pytest.raises(TokenError) as exc_info:
        decode_token("bad_hash", "refresh")

    assert exc_info.type is TokenError
    assert exc_info.value.args[0] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_jwt_expired_signature_access(monkeypatch):

    id_ = uuid4()

    delta = timedelta(minutes=jwt_settings.access_token_expiry)

    invalid_payload = {
        "exp": datetime(2000, 1, 1) + delta,
        "iat": datetime.now(timezone.utc),
        "sub": str(id_),
    }

    def patched_encode(payload, key, algorithm):
        del payload
        return real_jwt_encode(payload=invalid_payload, key=key, algorithm=algorithm)

    monkeypatch.setattr("app.api.endpoints.utils.jwt.jwt_encode", patched_encode)

    token = encode_token(id_, "access")
    assert token

    with pytest.raises(TokenError) as exc_info:
        decode_token(token, "access")

    assert exc_info.type is TokenError
    assert exc_info.value.args[0] == "Expired access token signature"


@pytest.mark.asyncio
async def test_jwt_expired_signature_refresh(monkeypatch):

    id_ = uuid4()

    delta = timedelta(minutes=jwt_settings.refresh_token_expiry)

    invalid_payload = {
        "exp": datetime(2000, 1, 1) + delta,
        "iat": datetime.now(timezone.utc),
        "sub": str(id_),
    }

    def patched_encode(payload, key, algorithm):
        del payload
        return real_jwt_encode(payload=invalid_payload, key=key, algorithm=algorithm)

    monkeypatch.setattr("app.api.endpoints.utils.jwt.jwt_encode", patched_encode)

    token = encode_token(id_, "refresh")
    assert token

    with pytest.raises(TokenError) as exc_info:
        decode_token(token, "refresh")

    assert exc_info.type is TokenError
    assert exc_info.value.args[0] == "Expired refresh token signature"


@pytest.mark.asyncio
async def test_jwt_invalid_payload_access(monkeypatch):

    id_ = uuid4()

    delta = timedelta(minutes=jwt_settings.access_token_expiry)

    invalid_payload = {
        "exp": datetime.now(timezone.utc) + delta,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }

    def patched_encode(payload, key, algorithm):
        del payload
        return real_jwt_encode(payload=invalid_payload, key=key, algorithm=algorithm)

    monkeypatch.setattr("app.api.endpoints.utils.jwt.jwt_encode", patched_encode)

    token = encode_token(id_, "access")
    assert token

    with pytest.raises(TokenError) as exc_info:
        decode_token(token, "access")

    assert exc_info.type is TokenError
    assert exc_info.value.args[0] == "Invalid access token payload"


@pytest.mark.asyncio
async def test_jwt_invalid_payload_refresh(monkeypatch):

    id_ = uuid4()

    delta = timedelta(minutes=jwt_settings.refresh_token_expiry)

    invalid_payload = {
        "exp": datetime.now(timezone.utc) + delta,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }

    def patched_encode(payload, key, algorithm):
        del payload
        return real_jwt_encode(payload=invalid_payload, key=key, algorithm=algorithm)

    monkeypatch.setattr("app.api.endpoints.utils.jwt.jwt_encode", patched_encode)

    token = encode_token(id_, "refresh")
    assert token

    with pytest.raises(TokenError) as exc_info:
        decode_token(token, "refresh")

    assert exc_info.type is TokenError
    assert exc_info.value.args[0] == "Invalid refresh token payload"
