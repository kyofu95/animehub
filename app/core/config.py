from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """
    Common configuration settings for the application.

    Attributes:
        debug (bool): A flag indicating whether debug mode is enabled.
            Defaults to `False`. Mapped from the `DEBUG` environment variable.
    """

    debug: bool = Field(alias="DEBUG", default=False)
    docs: bool = Field(alias="DOCS", default=False)


common_settings = CommonSettings()


class DatabaseSettings(BaseSettings):
    """
    Configuration settings for database connections.

    Attributes:
        driver (str): The database driver to use, as specified in the DATABASE_DRIVER environment variable.
        user (str): The database username to use, as specified in the DATABASE_USER environment variable.
        password (str): The database password to use, as specified in the DATABASE_PASSWORD environment variable.
        name (str): The database name to use, as specified in the DATABASE_NAME environment variable.
        host (str): The hostname or IP address of the database server, as specified in the DATABASE_HOST
            environment variable.
        port (int): The port number to connect to the database server on, as specified in the DATABASE_PORT
            environment variable.
    """

    driver: str = Field(alias="DATABASE_DRIVER")
    user: str = Field(alias="DATABASE_USER")
    password: str = Field(alias="DATABASE_PASSWORD")
    name: str = Field(alias="DATABASE_NAME")
    host: str = Field(alias="DATABASE_HOST")
    port: int = Field(alias="DATABASE_PORT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


database_settings = DatabaseSettings()


class JWTSettings(BaseSettings):
    """
    Configuration settings for JWT encoding and decoding.

    Attributes:
        secret_key (str): The secret key used to sign and verify the JWT.
        algorithm (str): The cryptographic algorithm used for encoding the JWT. Defaults to "HS256".
        access_token_expiry (int): The time in minutes before the access token expires. Defaults to 25 minutes.
    """

    secret_key: str = Field(alias="JWT_SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expiry: int = 25
    # 5 days
    refresh_token_expiry: int = 60 * 60 * 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


jwt_settings = JWTSettings()
