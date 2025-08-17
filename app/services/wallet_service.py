import uuid
from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_with_org
from app.models.user import User
from app.models.wallet import Wallet, WalletStatus, WalletType
from app.schemas.wallet import WalletCreate, WalletResponse, WalletUpdate


class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_wallet(
        self, user_id: uuid.UUID, wallet_data: WalletCreate, org_id: uuid.UUID
    ) -> Wallet:
        """Create a new wallet for a user"""
        # Check if user already has a primary wallet of this type
        if wallet_data.type == WalletType.PRIMARY:
            existing_wallet = await self.db.execute(
                select(Wallet).where(
                    Wallet.user_id == user_id,
                    Wallet.type == WalletType.PRIMARY,
                    Wallet.status == WalletStatus.ACTIVE,
                )
            )
            if existing_wallet.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has an active primary wallet",
                )

        # Create new wallet
        wallet = Wallet(
            id=uuid.uuid4(),
            user_id=user_id,
            balance=Decimal("0.00"),
            currency=wallet_data.currency,
            org_id=org_id,
            type=wallet_data.type,
            status=WalletStatus.ACTIVE,
        )

        self.db.add(wallet)
        await self.db.commit()
        await self.db.refresh(wallet)

        return wallet

    async def get_wallet_by_id(
        self, wallet_id: uuid.UUID, org_id: uuid.UUID
    ) -> Optional[Wallet]:
        """Get wallet by ID, ensuring it belongs to the organization"""
        result = await self.db.execute(
            select(Wallet).where(Wallet.id == wallet_id, Wallet.org_id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_user_wallets(
        self, user_id: uuid.UUID, org_id: uuid.UUID
    ) -> List[Wallet]:
        """Get all wallets for a user within an organization"""
        result = await self.db.execute(
            select(Wallet).where(Wallet.user_id == user_id, Wallet.org_id == org_id)
        )
        return result.scalars().all()

    async def update_wallet_status(
        self, wallet_id: uuid.UUID, org_id: uuid.UUID, status: WalletStatus
    ) -> Wallet:
        """Update wallet status"""
        wallet = await self.get_wallet_by_id(wallet_id, org_id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )

        wallet.status = status
        await self.db.commit()
        await self.db.refresh(wallet)

        return wallet

    async def get_wallet_balance(
        self, wallet_id: uuid.UUID, org_id: uuid.UUID
    ) -> Decimal:
        """Get current wallet balance"""
        wallet = await self.get_wallet_by_id(wallet_id, org_id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )

        return wallet.balance

    async def validate_wallet_operation(
        self, wallet_id: uuid.UUID, org_id: uuid.UUID, amount: Decimal
    ) -> Wallet:
        """Validate wallet for operations (exists, active, sufficient balance)"""
        wallet = await self.get_wallet_by_id(wallet_id, org_id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )

        if wallet.status != WalletStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Wallet is not active"
            )

        if amount < 0 and wallet.balance < abs(amount):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance"
            )

        return wallet

    async def update_wallet_balance(
        self, wallet_id: uuid.UUID, amount: Decimal
    ) -> None:
        """Update wallet balance (used internally by transaction service)"""
        result = await self.db.execute(select(Wallet).where(Wallet.id == wallet_id))
        wallet = result.scalar_one()

        if wallet:
            wallet.balance += amount
            await self.db.commit()

    async def get_wallet_summary(self, org_id: uuid.UUID) -> dict:
        """Get wallet summary for an organization"""
        # Total wallets
        total_wallets = await self.db.execute(
            select(func.count(Wallet.id)).where(Wallet.org_id == org_id)
        )

        # Total balance
        total_balance = await self.db.execute(
            select(func.sum(Wallet.balance)).where(
                Wallet.org_id == org_id, Wallet.status == WalletStatus.ACTIVE
            )
        )

        # Active wallets
        active_wallets = await self.db.execute(
            select(func.count(Wallet.id)).where(
                Wallet.org_id == org_id, Wallet.status == WalletStatus.ACTIVE
            )
        )

        return {
            "total_wallets": total_wallets.scalar() or 0,
            "active_wallets": active_wallets.scalar() or 0,
            "total_balance": float(total_balance.scalar() or 0),
            "currency": "INR",  # Assuming single currency for now
        }
