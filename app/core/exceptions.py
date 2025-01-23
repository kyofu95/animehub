class BaseError(Exception):
    """A base class for all custom exceptions in the application."""


class NotFoundError(BaseError):
    """Exception raised when a requested resource is not found."""


class AlreadyExistsError(BaseError):
    """Exception raised when attempting to create a resource that already exists."""
