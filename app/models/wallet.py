import uuid
from datetime import datetime
from enum import Enum as PyEnum  # ✅ Avoid conflict with SQLAlchemy Enum

from sqlalchemy import (
    ForeignKey,
    String,
    Numeric,
    func,
    Enum as SQLEnum  # ✅ Use this for the DB column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# ✅ Define Python enums
class WalletType(str, PyEnum):
    PRIMARY = "PRIMARY"
    BONUS = "BONUS"
    SYSTEM = "SYSTEM"

class WalletStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    CLOSED = "CLOSED"


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    balance: Mapped[float] = mapped_column(Numeric, default=0.0)
    currency: Mapped[str] = mapped_column(String, default="INR")
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # ✅ Enum columns with proper SQLAlchemy usage
    type: Mapped[WalletType] = mapped_column(SQLEnum(WalletType), default=WalletType.PRIMARY)
    status: Mapped[WalletStatus] = mapped_column(SQLEnum(WalletStatus), default=WalletStatus.ACTIVE)

    # Backrefs
    user = relationship("User", back_populates="wallets")
