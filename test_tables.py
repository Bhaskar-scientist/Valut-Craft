import asyncio
from app.db.session import get_db
from sqlalchemy import text

async def test_tables():
    async for db in get_db():
        try:
            print("Testing database tables...")
            result = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.fetchall()
            print("Existing tables:")
            for table in tables:
                print(f"  {table[0]}")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    asyncio.run(test_tables())
