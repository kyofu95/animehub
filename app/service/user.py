from uuid import UUID, uuid4

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.core.security import Hasher
from app.entity.anime import Anime
from app.entity.user import User
from app.entity.watchlist import WatchingEntry, WatchingStatus
from app.interface.uow.base_uow import BaseUnitOfWork


class UserService:
    """
    Service layer for handling operations related to users.

    This class provides methods for creating new users, managing user watchlist,
    and authenticating users based on their login credentials.
    """

    def __init__(self, uow: BaseUnitOfWork) -> None:
        """
        Constructor.

        Args:
            uow (BaseUnitOfWork): An instance of BaseUnitOfWork for managing sessions and user repository.
        """

        self.uow = uow

    async def create(self, login: str, password: str) -> User:
        """
        Creates a new user with the given login and password.

        Args:
            login (str): The login identifier for the new user.
            password (str): The password for the new user.

        Raises:
            AlreadyExistsError: If a user with the same login already exists.

        Returns:
            User: The newly created User object.
        """
        async with self.uow as uow:

            user = await uow.user_repository.get_by_login(login)
            if user:
                raise AlreadyExistsError("Trying to create user with existing login")

            hashed_password = Hasher.hash(password)

            new_user = User(id=uuid4(), login=login, password=hashed_password)

            return await uow.user_repository.add(new_user)

    async def create_watching_entry(
        self, status: WatchingStatus, num_watched_episodes: int, user: User, anime: Anime
    ) -> WatchingEntry:
        """
        Adds a new entry to the user's watchlist.

        Args:
            status (WatchingStatus): The current status of the anime being watched.
            num_watched_episodes (int): The number of episodes watched so far.
            user (User): User adding the entry.
            anime (Anime): Anime being watched.

        Raises:
            AlreadyExistsError: If an entry for the anime already exists in the user's watchlist.

        Returns:
            Watching: The newly created Watching object.
        """

        async with self.uow as uow:

            for item in user.watching_list:
                if item.anime == anime:
                    raise AlreadyExistsError("Anime already added to user's watchlist")

            watching = WatchingEntry(id=uuid4(), status=status, num_watched_episodes=num_watched_episodes, anime=anime)

            user.watching_list.append(watching)

            user = await uow.user_repository.update(user)

            return watching

    async def remove_watchlist_entry(self, user: User, anime: Anime) -> WatchingEntry:
        """
        Remove an anime entry from a users watchlist.

        Args:
            user (User): The 'User' object whose watchlist is being modified.
            anime (Anime): The 'Anime' object to be removed from the watchlist.

        Raises:
            NotFoundError: If the anime is not found in the user's watchlist.

        Returns:
            WatchingEntry: The 'WatchingEntry' object that was removed from the user's watchlist.
        """

        async with self.uow as uow:

            found_entry: WatchingEntry | None = None
            for item in user.watching_list:
                if item.anime == anime:
                    found_entry = item

            if not found_entry:
                raise NotFoundError("Anime is not found")

            user.watching_list.remove(found_entry)

            await uow.user_repository.update(user)

            return found_entry

    async def get_by_login_auth(self, login: str, password: str) -> User | None:
        """
        Retrieves a user by their login and verifies their password.

        Args:
            login (str): The login identifier of the user.
            password (str): The password to verify against the stored hash.

        Returns:
            User | None: The User object if authentication is successful, otherwise None.
        """

        async with self.uow as uow:

            user = await uow.user_repository.get_by_login(login)
            if not user:
                return None

            if not Hasher.verify(password, user.password):
                return None

            return user

    async def get_by_id(self, id_: UUID) -> User | None:
        """
        Retrieves a user by their id.

        Args:
            id_ (UUID): The id of the user to retrieve.

        Returns:
            User | None: The User object if found, otherwise None.
        """

        async with self.uow as uow:
            return await uow.user_repository.get_by_id(id_)
