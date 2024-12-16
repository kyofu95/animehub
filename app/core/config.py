from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    secret_key: str = Field(alias="JWT_SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expiry: int = 25


jwt_settings = JWTSettings()
