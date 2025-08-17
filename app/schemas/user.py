from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    org_id: UUID


class UserOut(BaseModel):
    id: UUID
    email: str
    org_id: UUID
    created_at: datetime
