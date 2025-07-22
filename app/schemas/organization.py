from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class OrganizationCreate(BaseModel):
    name: str

class OrganizationOut(BaseModel):
    id: UUID
    name: str
    created_at: datetime
