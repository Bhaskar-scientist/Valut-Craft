from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    org_id: UUID

class UserOut(BaseModel):
    id: UUID
    email: str
    org_id: UUID
    created_at: datetime
