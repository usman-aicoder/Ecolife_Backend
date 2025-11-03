"""
List all PostgreSQL databases to find the correct name.
"""

from sqlalchemy import create_engine, text

# Connect to postgres database (default database)
connection_string = "postgresql://eco_user:xs2P%40kistan%2C2025@localhost:5432/postgres"

print("=" * 60)
print("Listing PostgreSQL Databases")
print("=" * 60)

try:
    engine = create_engine(connection_string, echo=False)

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT datname FROM pg_database
            WHERE datistemplate = false
            ORDER BY datname;
        """))

        databases = result.fetchall()

        print(f"\nFound {len(databases)} database(s):\n")
        for db in databases:
            print(f"  - {db[0]}")

        print("\n" + "=" * 60)

except Exception as e:
    print(f"\nError: {str(e)}")
    print("\nTrying to connect to 'postgres' database...")
    print("If this fails, check if PostgreSQL is running.")
