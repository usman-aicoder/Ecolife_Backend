"""
Test script to insert a dummy meal plan and verify database functionality
"""
import asyncio
from datetime import datetime
from app.services.meal_plan_generator import auto_generate_meal_plan_for_user

async def test_meal_plan_generation():
    """Test meal plan generation for user ID 9 (the aa@aa.com user)"""

    print("Testing meal plan generation...")
    print("User ID: 9")
    print("Dietary Preference: omnivore")
    print("Calorie Target: 2000")
    print()

    try:
        meal_plan = await auto_generate_meal_plan_for_user(
            user_id=9,
            dietary_preference="omnivore",
            calorie_target=2000,
            diet_type="never"  # from lifestyle data
        )

        print("✓ Meal plan generated successfully!")
        print(f"Meal Plan ID: {meal_plan.id}")
        print(f"Status: {meal_plan.status}")
        print(f"Number of days: {len(meal_plan.meals)}")
        print(f"Created at: {meal_plan.created_at}")
        print()
        print("First day meals:")
        if meal_plan.meals and len(meal_plan.meals) > 0:
            day1 = meal_plan.meals[0]
            print(f"  Day: {day1.get('day')}")
            print(f"  Date: {day1.get('date')}")
            print(f"  Breakfast: {day1.get('breakfast', {}).get('name')}")
            print(f"  Lunch: {day1.get('lunch', {}).get('name')}")
            print(f"  Dinner: {day1.get('dinner', {}).get('name')}")

        return True
    except Exception as e:
        print(f"✗ Failed to generate meal plan: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_meal_plan_generation())
    exit(0 if success else 1)
