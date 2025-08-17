import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, transactions, wallets
from app.core.config import settings
from app.db.session import close_db, init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting VaultCraft application...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down VaultCraft application...")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    VaultCraft - A Ledger-Consistent, Transaction-Safe Backend System for Multi-Tenant Financial Operations
    
    ## Features
    
    * **Multi-tenant Architecture**: Organizations and users with proper isolation
    * **Wallet Management**: Create and manage multiple wallet types
    * **Transaction Engine**: Atomic internal transfers with double-entry ledger
    * **Authentication**: JWT-based secure access control
    * **Audit Trail**: Complete transaction history and ledger entries
    
    ## Getting Started
    
    1. Register a new user and organization at `/auth/signup`
    2. Login to get your access token at `/auth/login`
    3. Create wallets at `/wallets/`
    4. Transfer funds between wallets at `/wallets/transfer`
    5. View transaction history at `/transactions/`
    
    ## Authentication
    
    All protected endpoints require a valid JWT token in the Authorization header:
    `Authorization: Bearer <your_token>`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(wallets.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with application information"""
    return {
        "message": "Welcome to VaultCraft",
        "version": settings.APP_VERSION,
        "description": "Multi-tenant financial backend with transaction safety",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": "2024-01-01T00:00:00Z",  # You can make this dynamic
    }


@app.get("/api/v1/health", tags=["Health"])
async def api_health_check():
    """API health check endpoint"""
    return {"status": "healthy", "api_version": "v1", "service": settings.APP_NAME}


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "path": request.url.path,
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "path": request.url.path,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
