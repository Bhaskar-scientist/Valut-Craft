from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str


class OrganizationOut(BaseModel):
    id: UUID
    name: str
    created_at: datetime
