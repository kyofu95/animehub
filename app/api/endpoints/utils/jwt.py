from datetime import datetime, timedelta, timezone
from uuid import UUID

from jwt import decode as jwt_decode, encode as jwt_encode
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError

from app.core.config import jwt_settings
from app.core.exceptions import TokenError


def encode_access_token(user_id: UUID) -> str:
    """
    Encodes a user id into an access token.

    Args:
        user_id (UUID): The id of the user to be encoded into the token.

    Returns:
        str: A string representing the encoded JWT.
    """

    delta = timedelta(minutes=jwt_settings.access_token_expiry)

    payload = {
        "exp": datetime.now(timezone.utc) + delta,
        "iat": datetime.now(timezone.utc),
        "sub": str(user_id),
        "type": "access",
    }

    try:
        token = jwt_encode(payload=payload, key=jwt_settings.secret_key, algorithm=jwt_settings.algorithm)
    except PyJWTError as exc:
        raise TokenError("Token encode failure") from exc

    return token


def encode_refresh_token(user_id: UUID) -> str:
    """
    Encodes a user id into an refersh token.

    Args:
        user_id (UUID): The id of the user to be encoded into the token.

    Returns:
        str: A string representing the encoded JWT.
    """

    delta = timedelta(minutes=jwt_settings.refresh_token_expiry)

    payload = {
        "exp": datetime.now(timezone.utc) + delta,
        "iat": datetime.now(timezone.utc),
        "sub": str(user_id),
        "type": "refresh",
    }
    try:
        token = jwt_encode(payload=payload, key=jwt_settings.secret_key, algorithm=jwt_settings.algorithm)
    except PyJWTError as exc:
        raise TokenError("Token encode failure") from exc

    return token


def decode_access_token(token: str) -> UUID:
    """
    Decodes an access token to extract the user id.

    Args:
        token (str): The access token to decode.

    Raises:
        TokenError: If the token is invalid, expired, or cannot be decoded.

    Returns:
        UUID: The id of the user associated with the token.
    """

    if not token:
        raise TokenError("Invalid token")

    try:
        payload = jwt_decode(jwt=token, key=jwt_settings.secret_key, algorithms=[jwt_settings.algorithm])
    except ExpiredSignatureError as exc:
        raise TokenError("Expired access token signature") from exc
    except InvalidTokenError as exc:
        raise TokenError("Invalid access token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise TokenError("Invalid access token payload")

    return UUID(user_id)


def decode_refresh_token(token: str) -> UUID:
    """
    Decodes a refresh token to extract the user id.

    Args:
        token (str): The refresh token to decode.

    Raises:
        TokenError: If the token is invalid, expired, or cannot be decoded.

    Returns:
        UUID: The id of the user associated with the token.
    """

    if not token:
        raise TokenError("Invalid token")

    try:
        payload = jwt_decode(jwt=token, key=jwt_settings.secret_key, algorithms=[jwt_settings.algorithm])
    except ExpiredSignatureError as exc:
        raise TokenError("Expired refresh token signature") from exc
    except InvalidTokenError as exc:
        raise TokenError("Invalid refresh token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise TokenError("Invalid refresh token payload")

    return UUID(user_id)
