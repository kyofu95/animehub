from pydantic import BaseModel, Field


class HealthResponce(BaseModel):
    """Schema representing the health check response of the system."""

    status: str = Field(..., title="Service status", description="Indicates the current status of the service.")
