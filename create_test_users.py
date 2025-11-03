"""
Create 5 test users with different lifestyle/health data and meal plans
"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.db.session import get_db
from app.models.user import User
from app.models.lifestyle import LifestyleData
from app.models.health import HealthData
from app.services.meal_plan_generator import auto_generate_meal_plan_for_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define 5 different user profiles
test_users = [
    {
        "name": "test 1",
        "email": "test1@test.com",
        "password": "123456",
        "lifestyle": {
            "transportation_mode": "bike",
            "diet_type": "vegan",
            "shopping_pattern": "local",
            "recycling_habits": "always",
            "reusable_items": True,
            "energy_source": "renewable",
            "travel_frequency": "rarely",
            "paper_preference": "digital"
        },
        "health": {
            "age": 25,
            "height": 170.0,
            "weight": 65.0,
            "activity_level": "very_active",
            "wellness_goal": "build_muscle",
            "dietary_preference": "vegan"
        }
    },
    {
        "name": "test 2",
        "email": "test2@test.com",
        "password": "123456",
        "lifestyle": {
            "transportation_mode": "walk",
            "diet_type": "vegetarian",
            "shopping_pattern": "local",
            "recycling_habits": "often",
            "reusable_items": True,
            "energy_source": "renewable",
            "travel_frequency": "sometimes",
            "paper_preference": "digital"
        },
        "health": {
            "age": 30,
            "height": 165.0,
            "weight": 60.0,
            "activity_level": "active",
            "wellness_goal": "lose_weight",
            "dietary_preference": "vegetarian"
        }
    },
    {
        "name": "test 3",
        "email": "test3@test.com",
        "password": "123456",
        "lifestyle": {
            "transportation_mode": "public_transport",
            "diet_type": "pescatarian",
            "shopping_pattern": "balanced",
            "recycling_habits": "sometimes",
            "reusable_items": True,
            "energy_source": "mixed",
            "travel_frequency": "often",
            "paper_preference": "balanced"
        },
        "health": {
            "age": 35,
            "height": 175.0,
            "weight": 75.0,
            "activity_level": "moderate",
            "wellness_goal": "maintain_health",
            "dietary_preference": "pescatarian"
        }
    },
    {
        "name": "test 4",
        "email": "test4@test.com",
        "password": "123456",
        "lifestyle": {
            "transportation_mode": "car",
            "diet_type": "flexitarian",
            "shopping_pattern": "convenience",
            "recycling_habits": "rarely",
            "reusable_items": False,
            "energy_source": "mixed",
            "travel_frequency": "frequently",
            "paper_preference": "paper"
        },
        "health": {
            "age": 40,
            "height": 180.0,
            "weight": 85.0,
            "activity_level": "sedentary",
            "wellness_goal": "lose_weight",
            "dietary_preference": "flexitarian"
        }
    },
    {
        "name": "test 5",
        "email": "test5@test.com",
        "password": "123456",
        "lifestyle": {
            "transportation_mode": "electric_car",
            "diet_type": "omnivore",
            "shopping_pattern": "balanced",
            "recycling_habits": "often",
            "reusable_items": True,
            "energy_source": "renewable",
            "travel_frequency": "sometimes",
            "paper_preference": "digital"
        },
        "health": {
            "age": 28,
            "height": 172.0,
            "weight": 70.0,
            "activity_level": "active",
            "wellness_goal": "build_muscle",
            "dietary_preference": "omnivore"
        }
    }
]


async def create_test_users():
    """Create 5 test users with different profiles and meal plans"""

    async for db in get_db():
        created_users = []

        print("=" * 60)
        print("Creating 5 Test Users with Meal Plans")
        print("=" * 60)
        print()

        for i, user_data in enumerate(test_users, 1):
            try:
                print(f"[{i}/5] Creating user: {user_data['name']} ({user_data['email']})")

                # Check if user already exists
                result = await db.execute(
                    select(User).where(User.email == user_data['email'])
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print(f"  -> User already exists (ID: {existing_user.id}), skipping...")
                    print()
                    continue

                # 1. Create user
                hashed_password = pwd_context.hash(user_data['password'])
                new_user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    hashed_password=hashed_password
                )
                db.add(new_user)
                await db.commit()
                await db.refresh(new_user)
                print(f"  -> User created (ID: {new_user.id})")

                # 2. Create lifestyle data
                lifestyle = LifestyleData(
                    user_id=new_user.id,
                    **user_data['lifestyle']
                )
                db.add(lifestyle)
                await db.commit()
                print(f"  -> Lifestyle data added ({user_data['lifestyle']['diet_type']}, {user_data['lifestyle']['transportation_mode']})")

                # 3. Create health data
                health = HealthData(
                    user_id=new_user.id,
                    **user_data['health']
                )
                db.add(health)
                await db.commit()
                print(f"  -> Health data added (Age: {user_data['health']['age']}, Goal: {user_data['health']['wellness_goal']})")

                # 4. Generate meal plan
                print(f"  -> Generating 7-day meal plan...")
                meal_plan = await auto_generate_meal_plan_for_user(
                    user_id=new_user.id,
                    dietary_preference=user_data['health']['dietary_preference'],
                    calorie_target=2000,
                    diet_type=user_data['lifestyle']['diet_type']
                )
                print(f"  -> Meal plan generated (ID: {meal_plan.id}, Status: {meal_plan.status})")
                print(f"  -> {len(meal_plan.meals)} days of meals created")

                created_users.append({
                    'user_id': new_user.id,
                    'name': user_data['name'],
                    'email': user_data['email'],
                    'meal_plan_id': meal_plan.id
                })

                print(f"  [SUCCESS] {user_data['name']} setup complete!")
                print()

            except Exception as e:
                print(f"  [ERROR] Failed to create {user_data['name']}: {e}")
                import traceback
                traceback.print_exc()
                print()
                continue

        # Summary
        print("=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Total users created: {len(created_users)}")
        print()

        if created_users:
            print("Test Users:")
            for user in created_users:
                print(f"  - {user['name']}: {user['email']} (password: 123456)")
                print(f"    User ID: {user['user_id']}, Meal Plan ID: {user['meal_plan_id']}")

        print()
        print("You can now login with any of these users on the frontend:")
        print("  Frontend: http://localhost:3000")
        print("  Password: 123456 (for all test users)")
        print()

        break


if __name__ == "__main__":
    asyncio.run(create_test_users())
