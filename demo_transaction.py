#!/usr/bin/env python3
"""
ValutCraft Transaction Demo Script
This script demonstrates how to perform a transaction using ValutCraft
"""

import asyncio
import uuid
from datetime import datetime
from decimal import Decimal

from app.db.session import get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.wallet import Wallet, WalletType, WalletStatus
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.ledger_entry import LedgerEntry
from app.services.auth_service import AuthService
from app.services.wallet_service import WalletService
from app.services.transaction_service import TransactionService


async def demo_transaction():
    """Demonstrate a complete ValutCraft transaction"""
    print("🚀 Starting ValutCraft Transaction Demo...")
    
    # Get database session
    async for db in get_db():
        try:
            print("📊 Database connection established")
            
            # Create a demo organization
            org = Organization(
                id=uuid.uuid4(),
                name="Demo Corp",
                created_at=datetime.now()
            )
            db.add(org)
            await db.flush()
            print(f"🏢 Organization created: {org.name} (ID: {org.id})")
            
            # Create a demo user
            user = User(
                id=uuid.uuid4(),
                email="demo@valutcraft.com",
                password_hash="demo_hash",
                org_id=org.id
            )
            db.add(user)
            await db.flush()
            print(f"👤 User created: {user.email} (ID: {user.id})")
            
            # Create two wallets
            wallet1 = Wallet(
                id=uuid.uuid4(),
                user_id=user.id,
                balance=Decimal("1000.00"),
                currency="INR",
                org_id=org.id,
                type=WalletType.PRIMARY,
                status=WalletStatus.ACTIVE
            )
            
            wallet2 = Wallet(
                id=uuid.uuid4(),
                user_id=user.id,
                balance=Decimal("0.00"),
                currency="INR",
                org_id=org.id,
                type=WalletType.BONUS,
                status=WalletStatus.ACTIVE
            )
            
            db.add_all([wallet1, wallet2])
            await db.flush()
            print(f"💰 Wallet 1 created: {wallet1.id} (Balance: {wallet1.balance})")
            print(f"💰 Wallet 2 created: {wallet2.id} (Balance: {wallet2.balance})")
            
            # Perform a transaction
            print("\n🔄 Performing transaction...")
            transaction = Transaction(
                id=uuid.uuid4(),
                org_id=org.id,
                sender_wallet_id=wallet1.id,
                receiver_wallet_id=wallet2.id,
                amount=Decimal("500.00"),
                status=TransactionStatus.PENDING,
                transaction_type=TransactionType.INTERNAL_TRANSFER,
                description="Demo transfer from main to bonus wallet"
            )
            
            db.add(transaction)
            await db.flush()
            print(f"📝 Transaction created: {transaction.id}")
            
            # Create ledger entries (double-entry accounting)
            debit_entry = LedgerEntry(
                id=uuid.uuid4(),
                wallet_id=wallet1.id,
                transaction_id=transaction.id,
                amount=Decimal("-500.00"),  # Negative for debit
                type="DEBIT"
            )
            
            credit_entry = LedgerEntry(
                id=uuid.uuid4(),
                wallet_id=wallet2.id,
                transaction_id=transaction.id,
                amount=Decimal("500.00"),  # Positive for credit
                type="CREDIT"
            )
            
            db.add_all([debit_entry, credit_entry])
            
            # Update wallet balances
            wallet1.balance -= Decimal("500.00")
            wallet2.balance += Decimal("500.00")
            
            # Mark transaction as completed
            transaction.status = TransactionStatus.COMPLETED
            transaction.completed_at = datetime.now()
            
            # Commit the transaction
            await db.commit()
            
            print("✅ Transaction completed successfully!")
            print(f"📊 Final balances:")
            print(f"   Wallet 1: {wallet1.balance} {wallet1.currency}")
            print(f"   Wallet 2: {wallet2.balance} {wallet2.currency}")
            print(f"📋 Transaction ID: {transaction.id}")
            print(f"📝 Ledger entries: {debit_entry.id}, {credit_entry.id}")
            
            print("\n🎉 ValutCraft Transaction Demo completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during demo: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(demo_transaction())
