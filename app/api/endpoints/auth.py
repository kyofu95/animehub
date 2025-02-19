from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from .schemes.token import TokenResponse
from .utils.di_deps import UserServiceDep
from .utils.jwt import encode_token
from .utils.oauth import get_current_user_from_refresh_token
from .utils.refresh_request_form import OAuth2PasswordAndRefreshRequestForm

router = APIRouter(prefix="/token", tags=["Auth"])


FormData = Annotated[OAuth2PasswordAndRefreshRequestForm, Depends()]


@router.post("/", response_model=TokenResponse, status_code=status.HTTP_200_OK)
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

    if user_data.grant_type == "refresh_token":
        user = await get_current_user_from_refresh_token(token=user_data.refresh_token, user_service=service)
    else:
        user = await service.get_by_login_auth(user_data.username, user_data.password) # type: ignore

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = encode_token(user.id, "access")
    refresh_token = encode_token(user.id, "refresh")

    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
