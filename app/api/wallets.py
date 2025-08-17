import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_with_org
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.wallet import (WalletBalanceResponse, WalletCreate,
                                WalletListResponse, WalletResponse,
                                WalletTransferRequest)
from app.services.transaction_service import TransactionService
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.post("/", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    wallet_data: WalletCreate,
    current_user,
    organization=Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new wallet for the authenticated user.

    Users can create multiple wallets of different types (PRIMARY, BONUS, SYSTEM).
    Each user can have only one active PRIMARY wallet.
    """
    try:
        wallet_service = WalletService(db)
        wallet = await wallet_service.create_wallet(
            user_id=current_user.id, wallet_data=wallet_data, org_id=organization.id
        )
        return wallet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create wallet. Please try again.",
        )


@router.get("/", response_model=WalletListResponse)
async def list_wallets(
    current_user,
    organization=Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    List all wallets for the authenticated user within their organization.
    """
    try:
        wallet_service = WalletService(db)
        wallets = await wallet_service.get_user_wallets(
            user_id=current_user.id, org_id=organization.id
        )

        return WalletListResponse(wallets=wallets, total_count=len(wallets))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wallets. Please try again.",
        )


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: str,
    current_user,
    organization=Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a specific wallet.
    Users can only access wallets that belong to them within their organization.
    """
    try:
        wallet_service = WalletService(db)
        wallet = await wallet_service.get_wallet_by_id(
            wallet_id=uuid.UUID(wallet_id), org_id=organization.id
        )

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )

        # Ensure user owns this wallet
        if wallet.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this wallet",
            )

        return wallet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wallet. Please try again.",
        )


@router.get("/{wallet_id}/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    wallet_id: str,
    current_user,
    organization=Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current balance of a specific wallet.
    """
    try:
        wallet_service = WalletService(db)
        balance = await wallet_service.get_wallet_balance(
            wallet_id=uuid.UUID(wallet_id), org_id=organization.id
        )

        return WalletBalanceResponse(
            wallet_id=wallet_id,
            balance=balance,
            currency="INR",  # Assuming single currency for now
            last_updated=datetime.utcnow(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wallet balance. Please try again.",
        )


@router.post("/transfer", response_model=dict)
async def transfer_funds(
    transfer_data: WalletTransferRequest,
    current_user,
    organization=Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Transfer funds between wallets within the same organization.

    This endpoint creates a transaction and updates both wallet balances atomically.
    The transaction is recorded in the ledger for audit purposes.
    """
    try:
        # Verify sender wallet belongs to current user
        wallet_service = WalletService(db)
        sender_wallet = await wallet_service.get_wallet_by_id(
            wallet_id=uuid.UUID(transfer_data.sender_wallet_id), org_id=organization.id
        )

        if not sender_wallet or sender_wallet.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to sender wallet",
            )

        # Create the transaction
        transaction_service = TransactionService(db)
        transaction = await transaction_service.create_internal_transfer(
            transaction_data=transfer_data, org_id=organization.id
        )

        return {
            "message": "Transfer completed successfully",
            "transaction_id": str(transaction.id),
            "amount": float(transfer_data.amount),
            "sender_wallet_id": transfer_data.sender_wallet_id,
            "receiver_wallet_id": transfer_data.receiver_wallet_id,
            "status": "COMPLETED",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transfer failed. Please try again.",
        )


@router.get("/{wallet_id}/transactions")
async def get_wallet_transactions(
    wallet_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user_with_org),
    organization: Organization = Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Get transaction history for a specific wallet.
    Users can only access transaction history for wallets they own.
    """
    try:
        # Verify wallet ownership
        wallet_service = WalletService(db)
        wallet = await wallet_service.get_wallet_by_id(
            wallet_id=uuid.UUID(wallet_id), org_id=organization.id
        )

        if not wallet or wallet.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this wallet",
            )

        # Get transaction history
        transaction_service = TransactionService(db)
        transactions, total = await transaction_service.get_wallet_transaction_history(
            wallet_id=uuid.UUID(wallet_id),
            org_id=organization.id,
            page=page,
            page_size=page_size,
        )

        return {
            "transactions": transactions,
            "total_count": total,
            "page": page,
            "page_size": page_size,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction history. Please try again.",
        )


@router.get("/summary")
async def get_wallet_summary(
    current_user,
    organization=Depends(get_current_user_with_org),
    db: AsyncSession = Depends(get_db),
):
    """
    Get wallet summary for the current user's organization.
    This provides an overview of all wallets and total balances.
    """
    try:
        wallet_service = WalletService(db)
        summary = await wallet_service.get_wallet_summary(org_id=organization.id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wallet summary. Please try again.",
        )
