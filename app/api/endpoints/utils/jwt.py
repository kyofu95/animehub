from datetime import datetime, timedelta, timezone
from uuid import UUID

from jwt import decode as jwt_decode, encode as jwt_encode
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError

from app.core.config import jwt_settings
from app.core.exceptions import TokenError


def encode_token(user_id: UUID, token_type: str) -> str:
    """
    Encodes a user id into an access or refresh token.

    Args:
        user_id (UUID): The id of the user to be encoded into the token.
        token_type (str): The type of token to generate. Must be either "access" or "refresh".

    Returns:
        str: The encoded JWT token as a string.
    """

    if token_type not in ["access", "refresh"]:
        raise TokenError("Invalid token type")

    if token_type == "access":
        delta = timedelta(minutes=jwt_settings.access_token_expiry)
    else:
        delta = timedelta(minutes=jwt_settings.refresh_token_expiry)

    payload = {
        "exp": datetime.now(timezone.utc) + delta,
        "iat": datetime.now(timezone.utc),
        "sub": str(user_id),
        "type": token_type,
    }

    try:
        token = jwt_encode(payload=payload, key=jwt_settings.secret_key, algorithm=jwt_settings.algorithm)
    except PyJWTError as exc:
        raise TokenError("Token encode failure") from exc

    return token


def decode_token(token: str, token_type: str) -> UUID:
    """
    Decode and validate a JWT token.

    This function verifies a given token, checks its validity, and extracts the user ID.

    Args:
        token (str): The JWT token to decode.
        token_type (str): The expected type of the token. Must be either "access" or "refresh".

    Raises:
        TokenError: If the token is missing or invalid.
        TokenError: If the token type is incorrect.
        TokenError: If the token has expired.
        TokenError: If the token payload is malformed.

    Returns:
        UUID: The user ID extracted from the token.
    """

    if not token:
        raise TokenError("Invalid token")

    if not token_type or token_type not in ["access", "refresh"]:
        raise TokenError("Invalid token type")

    try:
        payload = jwt_decode(jwt=token, key=jwt_settings.secret_key, algorithms=[jwt_settings.algorithm])
    except ExpiredSignatureError as exc:
        raise TokenError(f"Expired {token_type} token signature") from exc
    except InvalidTokenError as exc:
        raise TokenError(f"Invalid {token_type} token") from exc

    token_type_in_payload = payload.get("type")
    if not token_type_in_payload or token_type_in_payload not in ["access", "refresh"]:
        raise TokenError("Invalid payload token type")

    if token_type_in_payload != token_type:
        raise TokenError("Token type mismatch")

    user_id = payload.get("sub")
    if not user_id:
        raise TokenError(f"Invalid {token_type} token payload")

    return UUID(user_id)
