"""
Database Initialization Script
Creates all tables in the PostgreSQL database
"""

import asyncio
from app.db.session import engine, Base
from app.models.user import User
from app.models.lifestyle import LifestyleData
from app.models.health import HealthData
from app.models.activity import ActivityData

async def init_database():
    """Initialize database tables"""
    print("Initializing PostgreSQL database...")
    print(f"Database URL: {engine.url}")

    try:
        # Create all tables using async engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("\n[SUCCESS] Database tables created successfully!")
        print("\nTables created:")
        print("  - users")
        print("  - lifestyle_data")
        print("  - health_data")
        print("  - activity_data")

    except Exception as e:
        print(f"\nError creating database tables: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
