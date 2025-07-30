# schemas/transaction.py
from pydantic import BaseModel, condecimal
from uuid import UUID

class TransactionCreate(BaseModel):
    sender_wallet_id: UUID
    receiver_wallet_id: UUID
    amount: condecimal(gt=0)
