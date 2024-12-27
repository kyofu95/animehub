from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .schemes.token import TokenResponse
from .utils.jwt import encode_access_token
from .utils.di_deps import UserServiceDep

router = APIRouter(tags=["Auth"])


FormData = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def get_token(user_data: FormData, service: UserServiceDep) -> TokenResponse:
    """
    Authenticate the user and return a JWT access token.

    This endpoint validates the user's credentials using the provided
    username and password. If authentication is successful, a JWT access token
    is generated and returned. Otherwise, a 401 Unauthorized error is raised.

    Args:
        user_data (FormData): The login credentials submitted by the user (username and password).
        service (UserServiceDep): The UserService dependency for user authentication.

    Raises:
        HTTPException: If authentication fails due to incorrect login or password.

    Returns:
        TokenResponse: A response object containing the access token and its type.
    """

    user = await service.get_by_login_auth(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = encode_access_token(user.id)

    return TokenResponse(access_token=access_token, token_type="bearer")
