"""Check if tables exist in the database"""
import asyncio
from app.db.session import engine
from sqlalchemy import text


async def check_tables():
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' "
                "AND table_name IN ('meal_plans', 'meal_consumptions') "
                "ORDER BY table_name"
            )
        )
        tables = [row[0] for row in result]

        if tables:
            print("Tables found:")
            for table in tables:
                print(f"  - {table}")
        else:
            print("No meal_plans or meal_consumptions tables found")

        # Also check all tables
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' ORDER BY table_name"
            )
        )
        all_tables = [row[0] for row in result]
        print(f"\nAll tables in database: {', '.join(all_tables)}")


if __name__ == "__main__":
    asyncio.run(check_tables())
