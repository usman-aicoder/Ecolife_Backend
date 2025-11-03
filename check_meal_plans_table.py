import asyncio
from sqlalchemy import text
from app.db.session import get_db

async def check_table():
    async for db in get_db():
        # Check if meal_plans table exists
        result = await db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'meal_plans'
            );
        """))
        exists = result.scalar()
        print(f"meal_plans table exists: {exists}")

        if exists:
            # Count meal plans
            count_result = await db.execute(text("SELECT COUNT(*) FROM meal_plans;"))
            count = count_result.scalar()
            print(f"Number of meal plans: {count}")

        break

if __name__ == "__main__":
    asyncio.run(check_table())
