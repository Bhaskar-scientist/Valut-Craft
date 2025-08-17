# app/schemas/transaction.py

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
