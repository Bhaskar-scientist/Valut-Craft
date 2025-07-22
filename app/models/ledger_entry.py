# app/models/ledger_entry.py

import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Numeric, Enum, func
from enum import Enum as PyEnum

from app.models.base import Base

class EntryType(str, PyEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wallets.id"))
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    type: Mapped[EntryType] = mapped_column(Enum(EntryType))
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Backrefs
    wallet = relationship("Wallet")
    transaction = relationship("Transaction", back_populates="ledger_entries")
