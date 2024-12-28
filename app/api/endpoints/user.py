from fastapi import APIRouter, HTTPException, status

from app.service.user import UserAlreadyExistsError

from .schemes.user import UserBasicResponse, UserCreateInputData
from .utils.oauth import CurrentUser
from .utils.di_deps import UserServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserBasicResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateInputData, user_service: UserServiceDep) -> UserBasicResponse:
    """
    Create a new user.

    This endpoint allows for the creation of a new user with the provided login and password.
    If the login already exists, a 400 Bad Request error is returned.

    Args:
        user_data (UserCreateInputData): The input data containing the login and password for the new user.
        user_service (UserServiceDep): The UserService dependency for handling user creation.

    Raises:
        HTTPException: A response object containing the basic details of the created user.

    Returns:
        UserBasicResponse: If a user with the given login already exists.
    """

    try:
        user = await user_service.create(user_data.login, user_data.password)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from exc

    return UserBasicResponse.model_validate(user, from_attributes=True)


@router.get("/me", response_model=UserBasicResponse, status_code=status.HTTP_200_OK)
async def get_user_me(user: CurrentUser) -> UserBasicResponse:
    """
    Retrieve the current user's details.

    This endpoint returns the details of the currently authenticated user.

    Args:
        user (CurrentUser): The currently authenticated user injected through OAuth.

    Returns:
        UserBasicResponse: A response object containing the details of the current user.
    """

    return UserBasicResponse.model_validate(user, from_attributes=True)
