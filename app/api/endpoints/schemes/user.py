from datetime import datetime

from pydantic import BaseModel


class BaseUser(BaseModel):
    login: str


class UserCreateInputData(BaseUser):
    password: str


class UserBasicResponse(BaseUser):
    created_at: datetime | None
    updated_at: datetime | None
    active: bool
