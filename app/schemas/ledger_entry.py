# app/schemas/ledger_entry.py

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum

class EntryType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class LedgerEntryCreate(BaseModel):
    wallet_id: UUID
    transaction_id: UUID
    amount: Decimal
    type: EntryType

class LedgerEntryOut(BaseModel):
    id: UUID
    wallet_id: UUID
    transaction_id: UUID
    amount: Decimal
    type: EntryType
    created_at: datetime
