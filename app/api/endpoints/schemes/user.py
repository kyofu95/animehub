from datetime import datetime

from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    """Base schema representing a user with a unique login identifier."""

    login: str = Field(
        title="User login",
        description="Unique identifier for the user",
        examples=["john.doe@example.com"],
    )


class UserCreateInputData(BaseUser):
    """Schema for user creation input, extending BaseUser with a password field."""

    password: str = Field(
        title="User password",
        description="Password for the user account, must be at least 8 characters long.",
        examples=["MySuperPassword1234"],
        min_length=8,
    )


class UserBasicResponse(BaseUser):
    """Schema for basic user response, including timestamps and status information."""

    created_at: datetime | None = Field(
        title="Account creation date",
        description="Timestamp indicating when the user account was created.",
    )
    updated_at: datetime | None = Field(
        title="Account last update date",
        description="Timestamp indicating the last time the user account was updated.",
    )
    active: bool = Field(title="Account active status", description="Indicates whether the user account is active.")
