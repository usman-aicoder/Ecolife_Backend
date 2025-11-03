import asyncio
from sqlalchemy import text
from app.db.session import get_db

async def create_table():
    async for db in get_db():
        # Create meal_plans table
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS meal_plans (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                task_id VARCHAR(255) UNIQUE,
                status VARCHAR(50) DEFAULT 'pending',
                meals JSON,
                dietary_preference VARCHAR(100),
                calorie_target INTEGER,
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE
            );
        """))

        # Create indexes
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_meal_plans_id ON meal_plans (id);
        """))

        await db.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ix_meal_plans_task_id ON meal_plans (task_id);
        """))

        await db.commit()
        print("meal_plans table created successfully!")
        break

if __name__ == "__main__":
    asyncio.run(create_table())
