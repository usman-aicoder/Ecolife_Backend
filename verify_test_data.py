"""
Verify all test data is in the database
"""
import asyncio
from sqlalchemy import text, select
from app.db.session import get_db
from app.models.user import User
from app.models.meal_plan import MealPlan

async def verify_data():
    async for db in get_db():
        print("=" * 70)
        print("DATABASE VERIFICATION - Test Users & Meal Plans")
        print("=" * 70)
        print()

        # Count users
        user_count = await db.execute(text("SELECT COUNT(*) FROM users;"))
        total_users = user_count.scalar()
        print(f"Total Users: {total_users}")

        # Count meal plans
        meal_plan_count = await db.execute(text("SELECT COUNT(*) FROM meal_plans;"))
        total_meal_plans = meal_plan_count.scalar()
        print(f"Total Meal Plans: {total_meal_plans}")
        print()

        # Get test users details
        result = await db.execute(
            select(User).where(User.email.like('test%@test.com')).order_by(User.id)
        )
        test_users = result.scalars().all()

        print(f"Test Users Found: {len(test_users)}")
        print("-" * 70)

        for user in test_users:
            print(f"\n{user.name} (ID: {user.id})")
            print(f"  Email: {user.email}")

            # Get meal plans for this user
            mp_result = await db.execute(
                select(MealPlan).where(MealPlan.user_id == user.id)
            )
            meal_plans = mp_result.scalars().all()

            if meal_plans:
                for mp in meal_plans:
                    print(f"  Meal Plan ID: {mp.id}")
                    print(f"    Status: {mp.status}")
                    print(f"    Diet: {mp.dietary_preference}")
                    print(f"    Days: {len(mp.meals) if mp.meals else 0}")
                    if mp.meals and len(mp.meals) > 0:
                        day1 = mp.meals[0]
                        print(f"    Day 1 Meals:")
                        print(f"      Breakfast: {day1.get('breakfast', {}).get('name')}")
                        print(f"      Lunch: {day1.get('lunch', {}).get('name')}")
                        print(f"      Dinner: {day1.get('dinner', {}).get('name')}")
            else:
                print("  No meal plans found!")

        print()
        print("=" * 70)
        print("VERIFICATION COMPLETE")
        print("=" * 70)
        print()
        print("Login Credentials for Testing:")
        print("  - test1@test.com / 123456 (Vegan, Bike)")
        print("  - test2@test.com / 123456 (Vegetarian, Walk)")
        print("  - test3@test.com / 123456 (Pescatarian, Public Transport)")
        print("  - test4@test.com / 123456 (Flexitarian, Car)")
        print("  - test5@test.com / 123456 (Omnivore, Electric Car)")
        print()
        print("Frontend: http://localhost:3000")
        print("Backend: http://localhost:8000")

        break

if __name__ == "__main__":
    asyncio.run(verify_data())
