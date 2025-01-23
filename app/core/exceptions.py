class BaseError(Exception):
    """A base class for all custom exceptions in the application."""


class NotFoundError(BaseError):
    """Exception raised when a requested resource is not found."""


class AlreadyExistsError(BaseError):
    """Exception raised when attempting to create a resource that already exists."""


class DatabaseError(BaseError):
    """This exception is raised when there's an issue interacting with the database, such as connection failures,
    query execution errors, or data inconsistencies."""
