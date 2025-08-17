from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user with organization.

    This endpoint creates a new organization and user account.
    The user will be automatically logged in after successful registration.
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.register_user(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again.",
        )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return access token.

    Provide email and password to receive a JWT access token.
    The token should be included in the Authorization header for protected endpoints.
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.login_user(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again.",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Returns the profile of the currently authenticated user.
    Requires a valid JWT token in the Authorization header.
    """
    return current_user
