from pydantic import BaseModel, Field


class Token(BaseModel):
    """Schema representing an authentication token response."""

    access_token: str = Field(..., title="Access Token", description="JWT access token used for authentication.")
    token_type: str = Field(..., title="Token Type", description="Type of the token, typically 'Bearer'.")


TokenResponse = Token
