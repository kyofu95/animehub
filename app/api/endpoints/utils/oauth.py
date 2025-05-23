from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import TokenError
from app.entity.user import User

from .di_deps import UserServiceDep
from .jwt import decode_token

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

AccessToken = Annotated[str, Depends(oauth_scheme)]
"""The OAuth2 access token extracted from the request."""

RefreshToken = Annotated[str, Depends(oauth_scheme)]
"""The OAuth2 refresh token extracted from the request."""


async def get_user_from_token(token: str, user_service: UserServiceDep, token_type: str) -> User:
    """
    Retrieve a user from the given token.

    Args:
        token (str): The JWT access or refresh token provided by the user.
        user_service (UserServiceDep): The user service dependency for accessing user data.
        token_type (str): The expected type of the token. Must be either "access" or "refresh".

    Returns:
        User: The user entity associated with the token.

    Raises:
        HTTPException: If the token is invalid, expired, or if the user cannot be found.
    """
    try:
        user_id = decode_token(token, token_type)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_from_access_token(token: AccessToken, user_service: UserServiceDep) -> User:
    """
    Retrieve the currently authenticated user based on the access token.

    Args:
        token (AccessToken): The access token obtained via OAuth2PasswordBearer.
        user_service (UserServiceDep): The user service dependency for accessing user data.

    Returns:
        User: The currently authenticated user.

    Raises:
        HTTPException: If the token is missing or the user cannot be authenticated.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized.")

    return await get_user_from_token(token, user_service, "access")


async def get_current_user_from_refresh_token(token: RefreshToken, user_service: UserServiceDep) -> User:
    """
    Retrieve the currently authenticated user based on the refresh token.

    Args:
        token (RefreshToken): The access token obtained via OAuth2PasswordBearer.
        user_service (UserServiceDep): The user service dependency for accessing user data.

    Returns:
        User: The currently authenticated user.

    Raises:
        HTTPException: If the token is missing or the user cannot be authenticated.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized.")

    return await get_user_from_token(token, user_service, "refresh")


CurrentUser = Annotated[User, Depends(get_current_user_from_access_token)]
"""Currently authenticated user, automatically resolved via dependency."""
