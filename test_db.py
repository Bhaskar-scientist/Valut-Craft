import asyncio
from app.db.session import get_db
from app.models.base import Base

async def test_db():
    async for db in get_db():
        try:
            print("Testing database connection...")
            await db.run_sync(Base.metadata.create_all)
            print("Tables created successfully!")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    asyncio.run(test_db())
