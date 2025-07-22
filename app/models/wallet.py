import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Numeric, func
from datetime import datetime

from app.models.base import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    balance: Mapped[float] = mapped_column(Numeric, default=0.0)
    currency: Mapped[str] = mapped_column(String, default="INR")
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Backrefs
    user = relationship("User", back_populates="wallets")
from enum import Enum
# Add inside wallet.py

class WalletType(str, Enum):
    PRIMARY = "PRIMARY"
    BONUS = "BONUS"
    SYSTEM = "SYSTEM"

class WalletStatus(str, Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    CLOSED = "CLOSED"

# Modify Wallet model:
type: Mapped[WalletType] = mapped_column(Enum(WalletType), default=WalletType.PRIMARY)
status: Mapped[WalletStatus] = mapped_column(Enum(WalletStatus), default=WalletStatus.ACTIVE)
