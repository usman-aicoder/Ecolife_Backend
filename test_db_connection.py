"""
Test script to verify PostgreSQL database connection.
"""

import sys
from sqlalchemy import create_engine, text
from app.config import settings

def test_connection():
    """Test database connection."""
    print("=" * 60)
    print("Testing PostgreSQL Database Connection")
    print("=" * 60)

    # Print connection details (without password)
    db_url = settings.DATABASE_URL
    print(f"\nDatabase URL: {db_url.split('@')[1] if '@' in db_url else 'Invalid URL'}")

    try:
        # Create engine
        print("\n1. Creating database engine...")
        engine = create_engine(db_url, echo=False)

        # Test connection
        print("2. Testing connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print("SUCCESS: Connection successful!")
            print(f"\nPostgreSQL Version:")
            print(f"   {version}")

            # Test database name
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"\nCurrent Database: {db_name}")

            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()

            print(f"\nExisting Tables: {len(tables)}")
            if tables:
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("   (No tables found - migrations not run yet)")

        print("\n" + "=" * 60)
        print("SUCCESS: Database connection test PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("FAILED: Database connection test FAILED!")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        print("\nPossible issues:")
        print("  1. PostgreSQL service not running")
        print("  2. Database 'eco_life' doesn't exist")
        print("  3. User 'eco_user' doesn't have access")
        print("  4. Incorrect password")
        print("  5. Wrong port or host")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
