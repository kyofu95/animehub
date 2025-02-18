from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .schemes.token import TokenResponse
from .utils.jwt import encode_access_token, encode_refresh_token
from .utils.di_deps import UserServiceDep
from .utils.oauth import CurrentUserFromRefresh

router = APIRouter(tags=["Auth"])


FormData = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def get_tokens(user_data: FormData, service: UserServiceDep) -> TokenResponse:
    """
    Authenticate a user and generate access and refresh tokens.

    This endpoint validates user credentials and, if correct, returns a JSON response
    containing a Bearer access token and a refresh token.

    Args:
        user_data (FormData): The login credentials submitted by the user (username and password).
        service (UserServiceDep): The UserService dependency for user authentication.

    Raises:
        HTTPException(401): If authentication fails due to incorrect login or password.

    Returns:
        TokenResponse: A response containing the access token, refresh token, and token type.
    """

    user = await service.get_by_login_auth(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = encode_access_token(user.id)
    refresh_token = encode_refresh_token(user.id)

    return TokenResponse(access_token=access_token, refesh_token=refresh_token, token_type="bearer")


@router.post("/token/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_tokens(user: CurrentUserFromRefresh) -> TokenResponse:
    """
    Refresh the access token using a valid refresh token.

    This endpoint generates a new access token and refresh token if the provided refresh
    token is valid.

    Args:
        user (CurrentUserFromRefresh): The currently authenticated user from the refresh token.

    Raises:
        HTTPException(401): If the refresh token is invalid.

    Returns:
        TokenResponse: A response containing the new access token, refresh token, and token type.
    """

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = encode_access_token(user.id)
    refresh_token = encode_refresh_token(user.id)

    return TokenResponse(access_token=access_token, refesh_token=refresh_token, token_type="bearer")
