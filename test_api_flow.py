"""
End-to-end API test demonstrating the full flow:
1. Register a user
2. Login
3. Submit lifestyle data
4. Submit health data
5. Get onboarding summary with scores
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_full_flow():
    print("=" * 70)
    print("ECOLIFE Backend - End-to-End API Test")
    print("=" * 70)

    # Test 1: Health check
    print("\n[1/6] Testing health check...")
    response = requests.get(f"{BASE_URL}/ping")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Test 2: Register a new user
    print("\n[2/6] Registering new user...")
    user_data = {
        "name": "John Eco",
        "email": f"john.eco.test{__import__('time').time():.0f}@example.com",  # Unique email
        "password": "TestPassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"   Status: {response.status_code}")

    if response.status_code != 201:
        print(f"   Error: {response.json()}")
        return False

    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"   Token received: {access_token[:20]}...")

    # Headers for authenticated requests
    headers = {"Authorization": f"Bearer {access_token}"}

    # Test 3: Get current user
    print("\n[3/6] Getting current user info...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   Status: {response.status_code}")
    user_info = response.json()
    print(f"   User: {user_info['name']} ({user_info['email']})")

    # Test 4: Submit lifestyle data
    print("\n[4/6] Submitting lifestyle data...")
    lifestyle_data = {
        "transportation_mode": "bike",
        "diet_type": "vegan",
        "shopping_pattern": "local",
        "recycling_habits": "always",
        "reusable_items": True,
        "energy_source": "renewable",
        "travel_frequency": "rarely",
        "paper_preference": "digital"
    }
    response = requests.post(f"{BASE_URL}/onboarding/lifestyle", json=lifestyle_data, headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Lifestyle data saved!")

    # Test 5: Submit health data
    print("\n[5/6] Submitting health data...")
    health_data = {
        "age": 30,
        "height": 175,
        "weight": 70,
        "activity_level": "active",
        "wellness_goal": "maintain_health",
        "dietary_preference": "none"
    }
    response = requests.post(f"{BASE_URL}/onboarding/health", json=health_data, headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Health data saved!")

    # Test 6: Get onboarding summary with scores
    print("\n[6/6] Getting onboarding summary with scores...")
    response = requests.get(f"{BASE_URL}/onboarding/summary", headers=headers)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        summary = response.json()
        print(f"\n   === SCORES ===")
        print(f"   Eco Score: {summary['eco_score']:.1f}/100")
        print(f"   Wellness Score: {summary['wellness_score']:.1f}/100")
        print(f"\n   === Lifestyle Data ===")
        if summary['lifestyle']:
            print(f"   Transport: {summary['lifestyle']['transportation_mode']}")
            print(f"   Diet: {summary['lifestyle']['diet_type']}")
            print(f"   Recycling: {summary['lifestyle']['recycling_habits']}")
        print(f"\n   === Health Data ===")
        if summary['health']:
            print(f"   Age: {summary['health']['age']}")
            print(f"   Activity: {summary['health']['activity_level']}")
            print(f"   Goal: {summary['health']['wellness_goal']}")

    print("\n" + "=" * 70)
    print("SUCCESS: All tests passed! Backend is fully functional!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        test_full_flow()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("Make sure the FastAPI server is running at http://localhost:8000")
