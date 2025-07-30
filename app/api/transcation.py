# routers/transactions.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Wallet, Transaction, LedgerEntry
from app.schemas.transaction import TransactionCreate
import uuid

router = APIRouter()

@router.post("/transactions")
async def create_transaction(payload: TransactionCreate, db: AsyncSession = Depends(get_db)):
    if payload.sender_wallet_id == payload.receiver_wallet_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to same wallet")

    async with db.begin():
        # Fetch both wallets
        sender = await db.get(Wallet, payload.sender_wallet_id)
        receiver = await db.get(Wallet, payload.receiver_wallet_id)

        if not sender or not receiver:
            raise HTTPException(status_code=404, detail="Wallet not found")

        if sender.balance < payload.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Debit sender, credit receiver
        sender.balance -= payload.amount
        receiver.balance += payload.amount

        txn = Transaction(
            id=uuid.uuid4(),
            sender_wallet_id=payload.sender_wallet_id,
            receiver_wallet_id=payload.receiver_wallet_id,
            amount=payload.amount,
        )
        db.add(txn)

        # Ledger entries
        db.add_all([
            LedgerEntry(wallet_id=sender.id, transaction_id=txn.id, amount=-payload.amount),
            LedgerEntry(wallet_id=receiver.id, transaction_id=txn.id, amount=payload.amount)
        ])

    return {"message": "Transaction successful", "transaction_id": str(txn.id)}
