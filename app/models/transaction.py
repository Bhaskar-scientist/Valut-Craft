# app/models/transaction.py

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func, Enum, Numeric
from decimal import Decimal

from app.models.base import Base

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TransactionType(str, Enum):
    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"
    EXTERNAL_TRANSFER = "EXTERNAL_TRANSFER"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"))
    sender_wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wallets.id"))
    receiver_wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wallets.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), default=TransactionType.INTERNAL_TRANSFER)
    reference_id: Mapped[str] = mapped_column(String, nullable=True)  # optional external ref
    description: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    completed_at: Mapped[datetime] = mapped_column(nullable=True)

    # Backrefs
    ledger_entries = relationship("LedgerEntry", back_populates="transaction")
    sender_wallet = relationship("Wallet", foreign_keys=[sender_wallet_id])
    receiver_wallet = relationship("Wallet", foreign_keys=[receiver_wallet_id])
