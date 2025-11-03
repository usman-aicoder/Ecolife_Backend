"""
Database Inspector for Ecolife Application
Displays all user data from PostgreSQL database in a formatted way
"""

import asyncio
import sys
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.lifestyle import LifestyleData
from app.models.health import HealthData
from app.models.activity import ActivityData

def print_separator(title="", width=100):
    """Print a formatted separator line"""
    if title:
        padding = (width - len(title) - 2) // 2
        print("\n" + "=" * padding + f" {title} " + "=" * padding)
    else:
        print("=" * width)

async def check_database():
    """Main function to inspect database"""
    try:
        print_separator("ECOLIFE DATABASE INSPECTION (PostgreSQL)", 100)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        async with AsyncSessionLocal() as session:
            # =====================================================================
            # 1. CHECK ALL USERS
            # =====================================================================
            print_separator("1. ALL USERS", 100)
            result = await session.execute(
                select(User).order_by(User.created_at.desc())
            )
            users = result.scalars().all()

            if users:
                print(f"\nTotal Users: {len(users)}\n")
                for user in users:
                    print(f"ID: {user.id}")
                    print(f"  Name:    {user.name}")
                    print(f"  Email:   {user.email}")
                    print(f"  Created: {user.created_at}")
                    print(f"  Updated: {user.updated_at}")
                    print("-" * 80)
            else:
                print("\n[WARNING] No users found in database")

            # =====================================================================
            # 2. LIFESTYLE DATA FOR ALL USERS
            # =====================================================================
            print_separator("2. LIFESTYLE DATA", 100)
            result = await session.execute(
                select(LifestyleData).options(selectinload(LifestyleData.user))
            )
            lifestyle_records = result.scalars().all()

            if lifestyle_records:
                for record in lifestyle_records:
                    print(f"\n[USER] {record.user.name} (ID: {record.user_id})")
                    print(f"   Email: {record.user.email}")
                    print(f"   Transportation: {record.transportation_mode}")
                    print(f"   Diet Type: {record.diet_type}")
                    print(f"   Shopping: {record.shopping_pattern}")
                    print(f"   Recycling: {record.recycling_habits}")
                    print(f"   Reusable Items: {record.reusable_items}")
                    print(f"   Energy Source: {record.energy_source}")
                    print(f"   Travel Frequency: {record.travel_frequency}")
                    print(f"   Paper Preference: {record.paper_preference}")
                    print(f"   Submitted: {record.created_at}")
                    print("-" * 80)
            else:
                print("\n[WARNING] No lifestyle data found")

            # =====================================================================
            # 3. HEALTH DATA FOR ALL USERS
            # =====================================================================
            print_separator("3. HEALTH DATA", 100)
            result = await session.execute(
                select(HealthData).options(selectinload(HealthData.user))
            )
            health_records = result.scalars().all()

            if health_records:
                for record in health_records:
                    print(f"\n[USER] {record.user.name} (ID: {record.user_id})")
                    print(f"   Email: {record.user.email}")
                    print(f"   Age: {record.age} years")
                    print(f"   Height: {record.height} cm")
                    print(f"   Weight: {record.weight} kg")
                    print(f"   Activity Level: {record.activity_level}")
                    print(f"   Wellness Goal: {record.wellness_goal}")
                    print(f"   Dietary Preference: {record.dietary_preference}")
                    print(f"   Submitted: {record.created_at}")
                    print("-" * 80)
            else:
                print("\n[WARNING] No health data found")

            # =====================================================================
            # 4. ACTIVITY DATA FOR ALL USERS
            # =====================================================================
            print_separator("4. ACTIVITY DATA", 100)
            result = await session.execute(
                select(ActivityData).options(selectinload(ActivityData.user)).order_by(ActivityData.date.desc())
            )
            activity_records = result.scalars().all()

            if activity_records:
                for record in activity_records:
                    print(f"\n[USER] {record.user.name} (ID: {record.user_id})")
                    print(f"   Date: {record.date}")
                    print(f"   Steps: {record.steps}")
                    print(f"   Duration: {record.duration_minutes} minutes")
                    print(f"   Activity Type: {record.activity_type}")
                    print(f"   Calories Burned: {record.calories_burned} cal")
                    print("-" * 80)
            else:
                print("\n[WARNING] No activity data found")

            # =====================================================================
            # 5. COMPLETE PROFILE FOR LATEST USER
            # =====================================================================
            print_separator("5. LATEST USER COMPLETE PROFILE", 100)
            result = await session.execute(
                select(User)
                .options(
                    selectinload(User.lifestyle_data),
                    selectinload(User.health_data)
                )
                .order_by(User.created_at.desc())
                .limit(1)
            )
            latest_user = result.scalar_one_or_none()

            if latest_user:
                print(f"\n[USER PROFILE]")
                print(f"   ID: {latest_user.id}")
                print(f"   Name: {latest_user.name}")
                print(f"   Email: {latest_user.email}")
                print(f"   Created: {latest_user.created_at}")

                print(f"\n[LIFESTYLE DATA]")
                if latest_user.lifestyle_data:
                    lifestyle = latest_user.lifestyle_data[0] if latest_user.lifestyle_data else None
                    if lifestyle:
                        print(f"   Transportation: {lifestyle.transportation_mode}")
                        print(f"   Diet: {lifestyle.diet_type}")
                        print(f"   Shopping: {lifestyle.shopping_pattern}")
                        print(f"   Recycling: {lifestyle.recycling_habits}")
                        print(f"   Reusables: {lifestyle.reusable_items}")
                        print(f"   Energy: {lifestyle.energy_source}")
                        print(f"   Travel: {lifestyle.travel_frequency}")
                        print(f"   Paper: {lifestyle.paper_preference}")
                    else:
                        print("   [WARNING] Not submitted")
                else:
                    print("   [WARNING] Not submitted")

                print(f"\n[HEALTH DATA]")
                if latest_user.health_data:
                    health = latest_user.health_data[0] if latest_user.health_data else None
                    if health:
                        print(f"   Age: {health.age} years")
                        print(f"   Height: {health.height} cm")
                        print(f"   Weight: {health.weight} kg")
                        print(f"   Activity: {health.activity_level}")
                        print(f"   Goal: {health.wellness_goal}")
                        print(f"   Diet Preference: {health.dietary_preference}")
                    else:
                        print("   [WARNING] Not submitted")
                else:
                    print("   [WARNING] Not submitted")
            else:
                print("\n[WARNING] No users found in database")

            # =====================================================================
            # 6. STATISTICS SUMMARY
            # =====================================================================
            print_separator("6. DATABASE STATISTICS", 100)

            # Count users
            user_count = await session.scalar(select(func.count(User.id)))
            lifestyle_count = await session.scalar(select(func.count(LifestyleData.id)))
            health_count = await session.scalar(select(func.count(HealthData.id)))
            activity_count = await session.scalar(select(func.count(ActivityData.id)))

            print(f"\n[Summary Statistics]")
            print(f"   Total Users: {user_count}")
            print(f"   Users with Lifestyle Data: {lifestyle_count}")
            print(f"   Users with Health Data: {health_count}")
            print(f"   Total Activity Records: {activity_count}")

            if user_count > 0:
                completion_rate = ((min(lifestyle_count, health_count) / user_count) * 100)
                print(f"   Onboarding Completion Rate: {completion_rate:.1f}%")

        print_separator("", 100)
        print("\n[SUCCESS] Database inspection completed successfully!\n")

    except Exception as e:
        print(f"\n[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n[INFO] Starting database inspection...\n")
    asyncio.run(check_database())
