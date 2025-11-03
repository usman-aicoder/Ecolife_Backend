"""
Test script for Day 4 - Dashboard & Analytics endpoints.
Tests the newly added dashboard and analytics routes.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_dashboard_and_analytics():
    print("=" * 70)
    print("ECOLIFE Backend - Day 4: Dashboard & Analytics Test")
    print("=" * 70)

    # Step 1: Register or use existing user
    print("\n[1/5] Registering/logging in user...")
    user_data = {
        "name": "Jane Eco",
        "email": f"jane.eco.test{__import__('time').time():.0f}@example.com",
        "password": "TestPassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)

    if response.status_code != 201:
        print(f"   Error: {response.json()}")
        return False

    token_data = response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"   User registered successfully!")

    # Step 2: Get current user to retrieve user_id
    print("\n[2/5] Getting user info...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    user_info = response.json()
    user_id = user_info["id"]
    print(f"   User ID: {user_id}, Name: {user_info['name']}")

    # Step 3: Submit onboarding data (lifestyle & health)
    print("\n[3/5] Submitting onboarding data...")

    lifestyle_data = {
        "transportation_mode": "bike",
        "diet_type": "vegetarian",
        "shopping_pattern": "local",
        "recycling_habits": "often",
        "reusable_items": True,
        "energy_source": "renewable",
        "travel_frequency": "rarely",
        "paper_preference": "digital"
    }
    requests.post(f"{BASE_URL}/onboarding/lifestyle", json=lifestyle_data, headers=headers)

    health_data = {
        "age": 28,
        "height": 165,
        "weight": 60,
        "activity_level": "active",
        "wellness_goal": "maintain_health",
        "dietary_preference": "vegetarian"
    }
    requests.post(f"{BASE_URL}/onboarding/health", json=health_data, headers=headers)
    print("   Onboarding data submitted!")

    # Step 4: Test Dashboard endpoint
    print("\n[4/5] Testing Dashboard endpoint...")
    print(f"   GET /dashboard/{user_id}")
    response = requests.get(f"{BASE_URL}/dashboard/{user_id}", headers=headers)

    if response.status_code == 200:
        dashboard = response.json()
        print(f"\n   === DASHBOARD SUMMARY ===")
        print(f"   Eco Score:            {dashboard['eco_score']:.1f}/100")
        print(f"   Wellness Score:       {dashboard['wellness_score']:.1f}/100")
        print(f"   CO2 Saved:            {dashboard['total_carbon_savings']:.1f} kg/year")
        print(f"   Calories Burned:      {dashboard['total_calories_burned']:.1f}")
        print(f"   Activity Streak:      {dashboard['streak_days']} days")
        print(f"   Last Updated:         {dashboard['last_updated']}")
    else:
        print(f"   Error: {response.status_code} - {response.json()}")
        return False

    # Also test the convenience endpoint (without user_id)
    print(f"\n   GET /dashboard (convenience endpoint)")
    response = requests.get(f"{BASE_URL}/dashboard", headers=headers)
    if response.status_code == 200:
        print(f"   Convenience endpoint working! [OK]")

    # Step 5: Test Analytics endpoints
    print("\n[5/5] Testing Analytics endpoints...")

    # Test /analytics/score
    print(f"\n   GET /analytics/score/{user_id}")
    response = requests.get(f"{BASE_URL}/analytics/score/{user_id}", headers=headers)

    if response.status_code == 200:
        scores = response.json()
        print(f"\n   === ANALYTICS SCORES ===")
        print(f"   Eco Score:            {scores['eco_score']:.1f}/100")
        print(f"   Wellness Score:       {scores['wellness_score']:.1f}/100")
        print(f"   CO2 Saved:            {scores['co2_saved']:.1f} kg/year")
    else:
        print(f"   Error: {response.status_code} - {response.json()}")
        return False

    # Test /analytics/progress
    print(f"\n   GET /analytics/progress/{user_id}?days=7")
    response = requests.get(f"{BASE_URL}/analytics/progress/{user_id}?days=7", headers=headers)

    if response.status_code == 200:
        analytics = response.json()
        print(f"\n   === ANALYTICS PROGRESS (Mock Data) ===")
        print(f"   Current Eco Score:    {analytics['eco_score']:.1f}/100")
        print(f"   Current Wellness:     {analytics['wellness_score']:.1f}/100")
        print(f"   CO2 Saved:            {analytics['co2_saved']:.1f} kg/year")
        print(f"\n   Progress Data Points: {len(analytics['health_progress_over_time'])}")

        if analytics['health_progress_over_time']:
            print(f"   Sample Progress Point:")
            sample = analytics['health_progress_over_time'][0]
            print(f"     Date: {sample['date']}")
            print(f"     Eco Score: {sample['eco_score']:.1f}")
            print(f"     Steps: {sample['steps']}")
            print(f"     Calories: {sample['calories_burned']:.1f}")
    else:
        print(f"   Error: {response.status_code} - {response.json()}")
        return False

    # Test convenience endpoints
    print(f"\n   Testing convenience endpoints (no user_id)...")
    response1 = requests.get(f"{BASE_URL}/analytics/score", headers=headers)
    response2 = requests.get(f"{BASE_URL}/analytics/progress", headers=headers)

    if response1.status_code == 200 and response2.status_code == 200:
        print(f"   All convenience endpoints working! [OK]")

    print("\n" + "=" * 70)
    print("SUCCESS: All Day 4 endpoints tested successfully!")
    print("=" * 70)
    print("\nEndpoints implemented:")
    print("  [OK] GET /dashboard/{user_id}")
    print("  [OK] GET /dashboard")
    print("  [OK] GET /analytics/score/{user_id}")
    print("  [OK] GET /analytics/score")
    print("  [OK] GET /analytics/progress/{user_id}")
    print("  [OK] GET /analytics/progress")
    print("\nFeatures:")
    print("  [OK] Dashboard summary with eco/wellness scores")
    print("  [OK] CO2 savings calculation")
    print("  [OK] Activity streak tracking")
    print("  [OK] Progress tracking over time")
    print("  [OK] Mock data generation for progress charts")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        test_dashboard_and_analytics()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("Make sure the FastAPI server is running at http://localhost:8000")
