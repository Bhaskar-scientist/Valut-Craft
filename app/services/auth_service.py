from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import timedelta
import uuid

from app.core.auth import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.models.organization import Organization
from app.schemas.auth import UserCreate, UserLogin

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_organization(self, name: str) -> Organization:
        """Create a new organization"""
        # Check if organization already exists
        result = await self.db.execute(
            select(Organization).where(Organization.name == name)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this name already exists"
            )
        
        # Create new organization
        organization = Organization(
            id=uuid.uuid4(),
            name=name
        )
        self.db.add(organization)
        await self.db.flush()  # Flush to get the ID
        return organization

    async def create_user(self, user_data: UserCreate) -> tuple[User, Organization]:
        """Create a new user with organization"""
        # Check if user already exists
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create organization first
        organization = await self.create_organization(user_data.organization_name)
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            org_id=organization.id
        )
        self.db.add(user)
        
        await self.db.commit()
        return user, organization

    async def authenticate_user(self, user_data: UserLogin) -> User:
        """Authenticate user with email and password"""
        # Get user by email
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        return user

    async def create_access_token_for_user(self, user: User) -> str:
        """Create access token for authenticated user"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        return access_token

    async def register_user(self, user_data: UserCreate) -> dict:
        """Complete user registration flow"""
        user, organization = await self.create_user(user_data)
        access_token = await self.create_access_token_for_user(user)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "organization_id": str(organization.id),
                "organization_name": organization.name
            }
        }

    async def login_user(self, user_data: UserLogin) -> dict:
        """Complete user login flow"""
        user = await self.authenticate_user(user_data)
        access_token = await self.create_access_token_for_user(user)
        
        # Get organization info
        result = await self.db.execute(
            select(Organization).where(Organization.id == user.org_id)
        )
        organization = result.scalar_one()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "organization_id": str(organization.id),
                "organization_name": organization.name
            }
        }
