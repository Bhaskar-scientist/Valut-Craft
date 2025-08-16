# schemas/transaction.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

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

class TransactionCreate(BaseModel):
    sender_wallet_id: str = Field(..., description="Source wallet ID")
    receiver_wallet_id: str = Field(..., description="Destination wallet ID")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    description: Optional[str] = Field(None, description="Transaction description")
    reference_id: Optional[str] = Field(None, description="External reference ID")
    transaction_type: TransactionType = Field(default=TransactionType.INTERNAL_TRANSFER, description="Transaction type")

class TransactionResponse(BaseModel):
    id: str = Field(..., description="Transaction ID")
    org_id: str = Field(..., description="Organization ID")
    reference_id: Optional[str] = Field(None, description="External reference ID")
    description: Optional[str] = Field(None, description="Transaction description")
    status: TransactionStatus = Field(..., description="Transaction status")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    amount: Decimal = Field(..., description="Transaction amount")
    sender_wallet_id: str = Field(..., description="Source wallet ID")
    receiver_wallet_id: str = Field(..., description="Destination wallet ID")
    created_at: datetime = Field(..., description="Transaction creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Transaction completion timestamp")

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse] = Field(..., description="List of transactions")
    total_count: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")

class TransactionFilter(BaseModel):
    status: Optional[TransactionStatus] = Field(None, description="Filter by transaction status")
    transaction_type: Optional[TransactionType] = Field(None, description="Filter by transaction type")
    start_date: Optional[datetime] = Field(None, description="Filter transactions from this date")
    end_date: Optional[datetime] = Field(None, description="Filter transactions until this date")
    wallet_id: Optional[str] = Field(None, description="Filter by wallet ID")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Page size")

class LedgerEntryResponse(BaseModel):
    id: str = Field(..., description="Ledger entry ID")
    wallet_id: str = Field(..., description="Wallet ID")
    transaction_id: str = Field(..., description="Transaction ID")
    amount: Decimal = Field(..., description="Entry amount")
    type: str = Field(..., description="Entry type (DEBIT/CREDIT)")
    created_at: datetime = Field(..., description="Entry creation timestamp")

    class Config:
        from_attributes = True
