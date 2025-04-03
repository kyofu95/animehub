from collections.abc import Awaitable
from typing import Annotated, Literal, cast

from fastapi import APIRouter, Depends, HTTPException, status

from .schemes.token import TokenResponse
from .utils.di_deps import RedisDep, UserServiceDep
from .utils.jwt import encode_token
from .utils.oauth import get_current_user_from_refresh_token
from .utils.refresh_request_form import OAuth2PasswordAndRefreshRequestForm

router = APIRouter(prefix="/token", tags=["Auth"])


FormData = Annotated[OAuth2PasswordAndRefreshRequestForm, Depends()]

TOKEN_BLACKLIST = "token_blacklist"


@router.post("/", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def get_tokens(user_data: FormData, service: UserServiceDep, redis: RedisDep) -> TokenResponse:
    """
    Authenticate a user and generate access and refresh tokens.

    This endpoint supports two types of authentication flows:
    - **Password Grant**: If the 'grant_type' is 'password', the user is authenticated using
        the provided username and password.
    - **Refresh Token Grant**: If the 'grant_type' is 'refresh_token', the user is authenticated
        using the provided 'refresh_token'.

    Upon successful authentication, the endpoint returns a JSON response containing a new access token
    and a refresh token, both encoded as JWTs.

    Args:
        user_data (FormData): The login credentials submitted by the user (username and password).
        service (UserServiceDep): The UserService dependency for user authentication.
        redis (RedisDep): The Redis dependency for refresh token blacklisting.

    Raises:
        HTTPException(401): If authentication fails due to incorrect login or password.

    Returns:
        TokenResponse: A response containing the access token, refresh token, and token type.
    """
    if user_data.grant_type == "refresh_token":
        refresh_token = user_data.refresh_token

        # redis-py type hinting is borked, so we ignore it
        redis_result = cast(Awaitable[Literal[0, 1]], redis.sismember(TOKEN_BLACKLIST, refresh_token))
        in_blacklist = await redis_result
        if bool(in_blacklist):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await get_current_user_from_refresh_token(token=refresh_token, user_service=service)
    else:
        user = await service.get_by_login_auth(user_data.username, user_data.password)  # type: ignore

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user_data.grant_type == "refresh_token":
        old_refresh_token = user_data.refresh_token

        # redis-py type hinting is borked, so we ignore it
        await cast(Awaitable[int], redis.sadd(TOKEN_BLACKLIST, old_refresh_token))

    access_token = encode_token(user.id, "access")
    refresh_token = encode_token(user.id, "refresh")

    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
