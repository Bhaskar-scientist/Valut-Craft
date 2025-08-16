from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.db.session import get_db
from app.core.auth import get_current_user_with_org
from app.services.transaction_service import TransactionService
from app.schemas.transaction import (
    TransactionCreate, 
    TransactionResponse, 
    TransactionListResponse, 
    TransactionFilter,
    LedgerEntryResponse
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/transfer", response_model=dict)
async def create_transfer(
    transaction_data: TransactionCreate,
    current_user, organization = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new internal transfer between wallets.
    
    This endpoint handles the complete transaction flow:
    1. Validates wallet ownership and balances
    2. Creates transaction record
    3. Updates wallet balances atomically
    4. Records ledger entries for audit
    """
    try:
        transaction_service = TransactionService(db)
        transaction = await transaction_service.create_internal_transfer(
            transaction_data=transaction_data,
            org_id=organization.id
        )
        
        return {
            "message": "Transfer completed successfully",
            "transaction_id": str(transaction.id),
            "amount": float(transaction.amount),
            "status": transaction.status.value,
            "sender_wallet_id": str(transaction.sender_wallet_id),
            "receiver_wallet_id": str(transaction.receiver_wallet_id),
            "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transfer failed. Please try again."
        )

@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    status: str = Query(None, description="Filter by transaction status"),
    transaction_type: str = Query(None, description="Filter by transaction type"),
    wallet_id: str = Query(None, description="Filter by wallet ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user, organization = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db)
):
    """
    List all transactions for the current user's organization.
    
    Supports filtering by status, type, and wallet ID.
    Results are paginated for performance.
    """
    try:
        # Build filter object
        filters = TransactionFilter(
            status=status,
            transaction_type=transaction_type,
            wallet_id=wallet_id,
            page=page,
            page_size=page_size
        )
        
        transaction_service = TransactionService(db)
        transactions, total = await transaction_service.get_transactions(
            org_id=organization.id,
            filters=filters
        )
        
        return TransactionListResponse(
            transactions=transactions,
            total_count=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions. Please try again."
        )

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user, organization = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific transaction.
    
    Users can only access transactions that belong to their organization.
    """
    try:
        transaction_service = TransactionService(db)
        transaction = await transaction_service.get_transaction_by_id(
            transaction_id=uuid.UUID(transaction_id),
            org_id=organization.id
        )
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction. Please try again."
        )

@router.get("/{transaction_id}/ledger")
async def get_transaction_ledger(
    transaction_id: str,
    current_user, organization = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Get ledger entries for a specific transaction.
    
    This shows the double-entry accounting records:
    - DEBIT entry (negative amount) for the sender wallet
    - CREDIT entry (positive amount) for the receiver wallet
    """
    try:
        transaction_service = TransactionService(db)
        ledger_entries = await transaction_service.get_transaction_ledger(
            transaction_id=uuid.UUID(transaction_id),
            org_id=organization.id
        )
        
        return {
            "transaction_id": transaction_id,
            "ledger_entries": [
                {
                    "id": str(entry.id),
                    "wallet_id": str(entry.wallet_id),
                    "amount": float(entry.amount),
                    "type": entry.type,
                    "created_at": entry.created_at.isoformat()
                }
                for entry in ledger_entries
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ledger entries. Please try again."
        )

@router.post("/{transaction_id}/cancel")
async def cancel_transaction(
    transaction_id: str,
    current_user, organization = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a pending transaction.
    
    Only pending transactions can be cancelled.
    Completed or failed transactions cannot be cancelled.
    """
    try:
        transaction_service = TransactionService(db)
        transaction = await transaction_service.cancel_transaction(
            transaction_id=uuid.UUID(transaction_id),
            org_id=organization.id
        )
        
        return {
            "message": "Transaction cancelled successfully",
            "transaction_id": str(transaction.id),
            "status": transaction.status.value
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel transaction. Please try again."
        )

@router.get("/summary")
async def get_transaction_summary(
    current_user, organization = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db)
):
    """
    Get transaction summary for the current user's organization.
    
    Provides overview statistics including:
    - Total transaction count
    - Total transaction volume
    - Transaction status distribution
    """
    try:
        # Get basic transaction counts
        transaction_service = TransactionService(db)
        
        # Get all transactions for summary
        filters = TransactionFilter(page=1, page_size=1000)  # Get all for summary
        transactions, total = await transaction_service.get_transactions(
            org_id=organization.id,
            filters=filters
        )
        
        # Calculate summary statistics
        total_volume = sum(float(txn.amount) for txn in transactions)
        status_counts = {}
        type_counts = {}
        
        for txn in transactions:
            status_counts[txn.status.value] = status_counts.get(txn.status.value, 0) + 1
            type_counts[txn.transaction_type.value] = type_counts.get(txn.transaction_type.value, 0) + 1
        
        return {
            "total_transactions": total,
            "total_volume": total_volume,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "currency": "INR"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction summary. Please try again."
        )
