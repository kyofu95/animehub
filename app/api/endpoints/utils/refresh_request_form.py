from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm


class OAuth2PasswordAndRefreshRequestForm(OAuth2PasswordRequestForm):
    """
    Extend OAuth2PasswordRequestForm to support both password and refresh token grant types.

    This form class is a modified version of FastAPI's OAuth2PasswordRequestForm. In addition to the
    standard fields (username, password, client_id, client_secret, and scope), it also accepts a
    'refresh_token' field. The `grant_type` field is validated to ensure it is either "password" or
    'refresh_token'.
    """

    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password|refresh_token"),
        username: str = Form(default=""),
        password: str = Form(default=""),
        refresh_token: str = Form(default=""),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
    ) -> None:
        """
        Initialize the OAuth2PasswordAndRefreshRequestForm with additional support for refresh tokens.

        Args:
            grant_type (str): The OAuth2 grant type. Must be either "password" or "refresh_token".
            username (str): The username for authentication. Defaults to an empty string.
            password (str): The user's password for authentication. Defaults to an empty string.
            refresh_token (str): The refresh token used to obtain a new access token. Defaults to an empty string.
            scope (str): The scope of the authentication request. Defaults to an empty string.
            client_id (str | None): The client identifier, if applicable. Defaults to None.
            client_secret (str | None): The client secret, if applicable. Defaults to None.
        """
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.scopes = scope.split()
        self.refresh_token = refresh_token
