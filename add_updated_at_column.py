import asyncio
from sqlalchemy import text
from app.db.session import get_db

async def add_column():
    async for db in get_db():
        # Add updated_at column
        await db.execute(text("""
            ALTER TABLE meal_plans
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        """))

        await db.commit()
        print("updated_at column added successfully!")
        break

if __name__ == "__main__":
    asyncio.run(add_column())
