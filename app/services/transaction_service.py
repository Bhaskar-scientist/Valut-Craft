from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from typing import List, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import uuid
import logging

from app.models.transaction import Transaction, TransactionStatus, TransactionType, LedgerEntry
from app.models.wallet import Wallet
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionFilter
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wallet_service = WalletService(db)

    async def create_internal_transfer(
        self, 
        transaction_data: TransactionCreate, 
        org_id: uuid.UUID
    ) -> Transaction:
        """
        Create an internal transfer between wallets within the same organization.
        This is the core transaction engine that ensures atomicity and consistency.
        """
        try:
            # Validate wallets belong to the same organization
            sender_wallet = await self.wallet_service.get_wallet_by_id(
                uuid.UUID(transaction_data.sender_wallet_id), 
                org_id
            )
            receiver_wallet = await self.wallet_service.get_wallet_by_id(
                uuid.UUID(transaction_data.receiver_wallet_id), 
                org_id
            )
            
            if not sender_wallet or not receiver_wallet:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or both wallets not found"
                )
            
            # Ensure wallets are active
            if sender_wallet.status != "ACTIVE" or receiver_wallet.status != "ACTIVE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or both wallets are not active"
                )
            
            # Check sufficient balance
            if sender_wallet.balance < transaction_data.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient balance in sender wallet"
                )
            
            # Create transaction record
            transaction = Transaction(
                id=uuid.uuid4(),
                org_id=org_id,
                sender_wallet_id=uuid.UUID(transaction_data.sender_wallet_id),
                receiver_wallet_id=uuid.UUID(transaction_data.receiver_wallet_id),
                amount=transaction_data.amount,
                status=TransactionStatus.PENDING,
                transaction_type=transaction_data.transaction_type,
                reference_id=transaction_data.reference_id,
                description=transaction_data.description
            )
            
            self.db.add(transaction)
            await self.db.flush()  # Get the transaction ID
            
            # Create ledger entries (double-entry accounting)
            debit_entry = LedgerEntry(
                id=uuid.uuid4(),
                wallet_id=uuid.UUID(transaction_data.sender_wallet_id),
                transaction_id=transaction.id,
                amount=-transaction_data.amount,  # Negative for debit
                type="DEBIT"
            )
            
            credit_entry = LedgerEntry(
                id=uuid.uuid4(),
                wallet_id=uuid.UUID(transaction_data.receiver_wallet_id),
                transaction_id=transaction.id,
                amount=transaction_data.amount,  # Positive for credit
                type="CREDIT"
            )
            
            self.db.add_all([debit_entry, credit_entry])
            
            # Update wallet balances
            sender_wallet.balance -= transaction_data.amount
            receiver_wallet.balance += transaction_data.amount
            
            # Mark transaction as completed
            transaction.status = TransactionStatus.COMPLETED
            transaction.completed_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(f"Transaction {transaction.id} completed successfully: "
                       f"{transaction_data.amount} transferred from {sender_wallet.id} to {receiver_wallet.id}")
            
            return transaction
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transaction failed. Please try again."
            )

    async def get_transaction_by_id(self, transaction_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Transaction]:
        """Get transaction by ID, ensuring it belongs to the organization"""
        result = await self.db.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.org_id == org_id
            )
        )
        return result.scalar_one_or_none()

    async def get_transactions(
        self, 
        org_id: uuid.UUID, 
        filters: TransactionFilter
    ) -> Tuple[List[Transaction], int]:
        """Get filtered transactions for an organization"""
        query = select(Transaction).where(Transaction.org_id == org_id)
        
        # Apply filters
        if filters.status:
            query = query.where(Transaction.status == filters.status)
        
        if filters.transaction_type:
            query = query.where(Transaction.transaction_type == filters.transaction_type)
        
        if filters.start_date:
            query = query.where(Transaction.created_at >= filters.start_date)
        
        if filters.end_date:
            query = query.where(Transaction.created_at <= filters.end_date)
        
        if filters.wallet_id:
            wallet_uuid = uuid.UUID(filters.wallet_id)
            query = query.where(
                (Transaction.sender_wallet_id == wallet_uuid) |
                (Transaction.receiver_wallet_id == wallet_uuid)
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db.execute(count_query)
        total = total_count.scalar()
        
        # Apply pagination
        query = query.order_by(Transaction.created_at.desc())
        query = query.offset((filters.page - 1) * filters.page_size)
        query = query.limit(filters.page_size)
        
        # Execute query
        result = await self.db.execute(query)
        transactions = result.scalars().all()
        
        return transactions, total

    async def get_transaction_ledger(self, transaction_id: uuid.UUID, org_id: uuid.UUID) -> List[LedgerEntry]:
        """Get ledger entries for a specific transaction"""
        # First verify the transaction belongs to the organization
        transaction = await self.get_transaction_by_id(transaction_id, org_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        result = await self.db.execute(
            select(LedgerEntry).where(LedgerEntry.transaction_id == transaction_id)
        )
        return result.scalars().all()

    async def get_wallet_transaction_history(
        self, 
        wallet_id: uuid.UUID, 
        org_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Transaction], int]:
        """Get transaction history for a specific wallet"""
        # Verify wallet belongs to organization
        wallet = await self.wallet_service.get_wallet_by_id(wallet_id, org_id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
        
        # Get transactions where wallet is sender or receiver
        query = select(Transaction).where(
            (Transaction.sender_wallet_id == wallet_id) |
            (Transaction.receiver_wallet_id == wallet_id),
            Transaction.org_id == org_id
        )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db.execute(count_query)
        total = total_count.scalar()
        
        # Apply pagination
        query = query.order_by(Transaction.created_at.desc())
        query = query.offset((page - 1) * page_size)
        query = query.limit(page_size)
        
        result = await self.db.execute(query)
        transactions = result.scalars().all()
        
        return transactions, total

    async def cancel_transaction(self, transaction_id: uuid.UUID, org_id: uuid.UUID) -> Transaction:
        """Cancel a pending transaction"""
        transaction = await self.get_transaction_by_id(transaction_id, org_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        if transaction.status != TransactionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending transactions can be cancelled"
            )
        
        transaction.status = TransactionStatus.CANCELLED
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction
