from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import TypeAdapter

from .schemes.watchlist import WatchlistEntryRequest, WatchlistEntryResponse
from .utils.di_deps import AnimeServiceDep, UserServiceDep
from .utils.oauth import CurrentUser

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("/", response_model=List[WatchlistEntryResponse], status_code=status.HTTP_200_OK)
async def get_list(user: CurrentUser) -> List[WatchlistEntryResponse]:
    """
    Retrieve the users watchlist.
    This endpoint returns the list of all 'WatchingEntry' objects in the current users watchlist.

    Args:
        user (CurrentUser): The authenticated user whose watchlist is being retrieved.

    Returns:
        List[WatchlistEntryResponse]: A list of 'WatchlistEntryResponse' objects representing the users watchlist.
    """

    # The `TypeAdapter` is used to validate and transform the users 'watching_list'
    # into the desired response model format.
    type_adapter = TypeAdapter(List[WatchlistEntryResponse])

    return type_adapter.validate_python(user.watching_list, from_attributes=True)


@router.post("/", response_model=WatchlistEntryResponse, status_code=status.HTTP_201_CREATED)
async def add_to_list(
    user: CurrentUser,
    anime_id: UUID,
    entry_request: WatchlistEntryRequest,
    user_service: UserServiceDep,
    anime_service: AnimeServiceDep,
) -> WatchlistEntryResponse:
    """
    Add an anime to the users watchlist.
    This endpoint allows the user to add a new entry to their watchlist by providing the anime ID
    and additional details, such as status and the number of watched episodes.

    Args:
        user (CurrentUser): The authenticated user adding the anime to their watchlist.
        anime_id (UUID): The unique identifier of the anime to add.
        entry_request (WatchlistEntryRequest): A request body containing details about the watchlist entry,
            including the status and number of watched episodes.
        user_service (UserServiceDep): Dependency for interacting with user-related operations.
        anime_service (AnimeServiceDep): Dependency for interacting with anime-related operations.

    Raises:
        HTTPException: If the anime with the given ID is not found.

    Returns:
        WatchlistEntryResponse: The newly created watchlist entry, serialized as a response model.
    """

    anime = await anime_service.get_by_id(anime_id)
    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Anime with id '{anime_id}' not found")

    entry = await user_service.create_watching_entry(
        status=entry_request.status, num_watched_episodes=entry_request.num_watched_episodes, user=user, anime=anime
    )

    return WatchlistEntryResponse.model_validate(entry, from_attributes=True)


@router.delete("/", response_model=WatchlistEntryResponse, status_code=status.HTTP_200_OK)
async def remove_from_list(
    user: CurrentUser, anime_id: UUID, user_service: UserServiceDep, anime_service: AnimeServiceDep
) -> WatchlistEntryResponse:
    """
    Remove an anime from the users watchlist.
    This endpoint removes an existing anime entry from the users watchlist.

    Args:
        user (CurrentUser): The authenticated user requesting to remove an anime from their watchlist.
        anime_id (UUID): The unique identifier of the anime to remove.
        user_service (UserServiceDep): Dependency for handling user-related operations.
        anime_service (AnimeServiceDep): Dependency for fetching anime-related data.

    Raises:
        HTTPException: If the anime with the given ID is not found.

    Returns:
        WatchlistEntryResponse: he details of the removed watchlist entry, serialized as a response model.
    """

    anime = await anime_service.get_by_id(anime_id)
    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Anime with id '{anime_id}' not found")

    entry = await user_service.remove_watchlist_entry(user, anime)

    return WatchlistEntryResponse.model_validate(entry, from_attributes=True)


@router.patch("/", response_model=WatchlistEntryResponse, status_code=status.HTTP_200_OK)
async def update_entry(
    user: CurrentUser, entry_id: UUID, entry_request: WatchlistEntryRequest, user_service: UserServiceDep
) -> WatchlistEntryResponse:
    """
    Update an anime entry in the users watchlist.
    This endpoint allows the user to update details of an existing entry in their watchlist, such as
    the status or the number of watched episodes.

    Args:
        user (CurrentUser): The authenticated user making the update request.
        entry_id (UUID): The unique identifier of the watchlist entry to update.
        entry_request (WatchlistEntryRequest): A request body containing the updated fields for the watchlist entry.
        user_service (UserServiceDep): Dependency for handling user-related operations.

    Returns:
        WatchlistEntryResponse: The updated watchlist entry, serialized as a response model.
    """

    update_dict = entry_request.model_dump()

    entry = await user_service.update_watchlist_entry(user, entry_id, update_dict)

    return WatchlistEntryResponse.model_validate(entry, from_attributes=True)
