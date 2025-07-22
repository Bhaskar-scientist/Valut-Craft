from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class WalletCreate(BaseModel):
    user_id: UUID
    currency: str = "INR"

class WalletOut(BaseModel):
    id: UUID
    user_id: UUID
    org_id: UUID | None
    balance: Decimal
    currency: str
    created_at: datetime
from enum import Enum

class WalletType(str, Enum):
    PRIMARY = "PRIMARY"
    BONUS = "BONUS"
    SYSTEM = "SYSTEM"

class WalletStatus(str, Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    CLOSED = "CLOSED"

class WalletCreate(BaseModel):
    user_id: UUID
    currency: str = "INR"
    type: WalletType = WalletType.PRIMARY

class WalletOut(BaseModel):
    id: UUID
    user_id: UUID
    org_id: UUID | None
    balance: Decimal
    currency: str
    type: WalletType
    status: WalletStatus
    created_at: datetime
