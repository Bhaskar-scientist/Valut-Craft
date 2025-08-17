from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, description="User password (min 8 characters)"
    )
    organization_name: str = Field(..., description="Organization name")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in minutes")


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    organization_id: str = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="User creation timestamp")

    class Config:
        from_attributes = True


class OrganizationResponse(BaseModel):
    id: str = Field(..., description="Organization ID")
    name: str = Field(..., description="Organization name")
    created_at: datetime = Field(..., description="Organization creation timestamp")

    class Config:
        from_attributes = True
