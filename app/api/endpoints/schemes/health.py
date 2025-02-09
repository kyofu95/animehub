from pydantic import BaseModel


class HealthResponce(BaseModel):
    """Schema representing the health check response of the system."""

    status: str
