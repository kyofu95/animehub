from datetime import datetime

from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    login: str


class UserCreateInputData(BaseUser):
    password: str = Field(min_length=8)


class UserBasicResponse(BaseUser):
    created_at: datetime | None
    updated_at: datetime | None
    active: bool
