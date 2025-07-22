# app/schemas/transaction.py

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TransactionCreate(BaseModel):
    org_id: UUID
    reference_id: str | None = None
    description: str | None = None

class TransactionOut(BaseModel):
    id: UUID
    org_id: UUID
    reference_id: str | None
    description: str | None
    created_at: datetime
