from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.wallet import WalletStatus, WalletType


class WalletCreate(BaseModel):
    name: str = Field(..., description="Wallet name")
    type: WalletType = Field(default=WalletType.PRIMARY, description="Wallet type")
    currency: str = Field(default="INR", description="Wallet currency")


class WalletUpdate(BaseModel):
    status: Optional[WalletStatus] = Field(None, description="Wallet status")
    type: Optional[WalletType] = Field(None, description="Wallet type")


class WalletResponse(BaseModel):
    id: str = Field(..., description="Wallet ID")
    user_id: str = Field(..., description="User ID")
    balance: Decimal = Field(..., description="Current wallet balance")
    currency: str = Field(..., description="Wallet currency")
    org_id: Optional[str] = Field(None, description="Organization ID")
    type: WalletType = Field(..., description="Wallet type")
    status: WalletStatus = Field(..., description="Wallet status")
    created_at: datetime = Field(..., description="Wallet creation timestamp")

    class Config:
        from_attributes = True

    @validator("id", "user_id", "org_id", pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class WalletListResponse(BaseModel):
    wallets: List[WalletResponse] = Field(..., description="List of wallets")
    total_count: int = Field(..., description="Total number of wallets")


class WalletBalanceResponse(BaseModel):
    wallet_id: str = Field(..., description="Wallet ID")
    balance: Decimal = Field(..., description="Current balance")
    currency: str = Field(..., description="Currency")
    last_updated: datetime = Field(..., description="Last balance update timestamp")


class WalletTransferRequest(BaseModel):
    sender_wallet_id: str = Field(..., description="Source wallet ID")
    receiver_wallet_id: str = Field(..., description="Destination wallet ID")
    amount: Decimal = Field(..., gt=0, description="Transfer amount (must be positive)")
    description: Optional[str] = Field(None, description="Transfer description")
    reference_id: Optional[str] = Field(None, description="External reference ID")

    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @validator("sender_wallet_id", "receiver_wallet_id")
    def validate_different_wallets(cls, v, values):
        if "sender_wallet_id" in values and v == values["sender_wallet_id"]:
            raise ValueError("Sender and receiver wallets must be different")
        return v
