class BaseError(Exception):
    """A base class for all custom exceptions in the application."""


class NotFoundError(BaseError):
    """Exception raised when a requested resource is not found."""


class AlreadyExistsError(BaseError):
    """Exception raised when attempting to create a resource that already exists."""


class DatabaseError(BaseError):
    """
    Raised for database interaction issues.

    This may occur due to connection failures, query execution errors, or data inconsistencies.
    """



class HashingError(BaseError):
    """This exception is raised when there's an issue with hashing or validation."""


class TokenError(BaseError):
    """This exception is raised when there is an error encoding or decoding a JWT."""
