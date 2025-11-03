"""
Test script to verify the meal plan API endpoint is working
"""
import asyncio
import httpx
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_api():
    """Test the meal plan API endpoint"""

    base_url = "http://localhost:8000"

    # Step 1: Login as test1@test.com
    print("=" * 70)
    print("Testing Meal Plan API")
    print("=" * 70)
    print("\n1. Logging in as test1@test.com...")

    login_data = {
        "email": "test1@test.com",
        "password": "123456"
    }

    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(f"{base_url}/auth/login", json=login_data)

        if response.status_code != 200:
            print(f"   ✗ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return

        token_data = response.json()
        access_token = token_data.get("access_token")
        print(f"   ✓ Login successful!")
        print(f"   Token: {access_token[:20]}...")

        # Step 2: Fetch meal plans
        print("\n2. Fetching meal plans...")
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get(f"{base_url}/meal-plans/user/my-plans?limit=1&offset=0", headers=headers)

        if response.status_code != 200:
            print(f"   ✗ Fetch failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return

        data = response.json()
        print(f"   ✓ Fetch successful!")
        print(f"   Total meal plans: {data.get('total')}")

        if data.get('meal_plans') and len(data['meal_plans']) > 0:
            plan = data['meal_plans'][0]
            print(f"\n   Latest Meal Plan:")
            print(f"     ID: {plan['id']}")
            print(f"     Status: {plan['status']}")
            print(f"     Dietary Preference: {plan['dietary_preference']}")
            print(f"     Number of days: {len(plan['meals']) if plan.get('meals') else 0}")

            if plan.get('meals') and len(plan['meals']) > 0:
                day1 = plan['meals'][0]
                print(f"\n   Day 1 Meals:")
                print(f"     Day: {day1.get('day')}")
                print(f"     Date: {day1.get('date')}")
                print(f"     Breakfast: {day1.get('breakfast', {}).get('name')}")
                print(f"       - Calories: {day1.get('breakfast', {}).get('calories')}")
                print(f"       - Protein: {day1.get('breakfast', {}).get('protein')}g")
                print(f"       - Carbs: {day1.get('breakfast', {}).get('carbs')}g")
                print(f"       - Fats: {day1.get('breakfast', {}).get('fats')}g")
                print(f"     Lunch: {day1.get('lunch', {}).get('name')}")
                print(f"     Dinner: {day1.get('dinner', {}).get('name')}")
        else:
            print("   ✗ No meal plans found!")

    print("\n" + "=" * 70)
    print("API Test Complete!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_api())
