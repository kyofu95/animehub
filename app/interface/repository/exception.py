class RepositoryError(Exception):
    """
    Base repository exception class.
    """


class NotFoundError(RepositoryError):
    """
    Entity were not found or stored in database.
    """
