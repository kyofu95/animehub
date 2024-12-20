from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error, InvalidHashError, VerifyMismatchError


class HashingError(Exception):
    """Issues with hashing or validation."""


hasher = PasswordHasher()


class Hasher:
    """
    Password hasher utility class.
    """

    @staticmethod
    def hash(password: str) -> str:
        """
        Hash a password using the Argon2 algorithm.

        Args:
            password (str): Plain password.

        Raises:
            HashingError: Raised when hashing failed.

        Returns:
            str: Encoded password.
        """

        try:
            encoded = hasher.hash(password)
        except Argon2Error as exc:
            raise HashingError("Failed to hash password") from exc

        return encoded

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password (str): Plain password.
            hashed_password (str): Encoded password.

        Raises:
            HashingError: Raised when validation failed.

        Returns:
            bool: Returns True if both passwords are equal, owerwise False.
        """

        try:
            password_match = hasher.verify(hash=hashed_password, password=plain_password)
        except VerifyMismatchError:
            return False
        except (Argon2Error, InvalidHashError) as exc:
            raise HashingError("Failed to verify password") from exc

        return password_match
