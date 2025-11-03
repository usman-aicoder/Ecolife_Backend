"""
Analytics service for dashboard and analytics endpoints.
Provides functions for calculating metrics, streaks, and progress tracking.
"""

from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.lifestyle import LifestyleData
from app.models.health import HealthData
from app.models.activity import ActivityData
from app.models.meal_consumption import MealConsumption
from app.services.scoring import calculate_eco_score, calculate_wellness_score
from app.schemas.analytics import ProgressDataPoint


async def get_user_with_data(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get user with all related data (lifestyle, health, activities).

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object with relationships loaded, or None if not found
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        # Eagerly load relationships
        await db.refresh(user, ["lifestyle_data", "health_data", "activities"])

    return user


def calculate_carbon_savings(lifestyle: Optional[LifestyleData]) -> float:
    """
    Calculate estimated CO2 savings in kg based on lifestyle choices.
    This is a simplified estimation model.

    Args:
        lifestyle: LifestyleData object

    Returns:
        Estimated CO2 saved in kg per year
    """
    if not lifestyle:
        return 0.0

    co2_saved = 0.0

    # Transportation savings (kg CO2 per year)
    transport_savings = {
        "bike": 2000,
        "walk": 2000,
        "public_transport": 1200,
        "electric_car": 800,
        "carpool": 600,
        "car": 0,
        "motorcycle": 100
    }
    if lifestyle.transportation_mode:
        co2_saved += transport_savings.get(lifestyle.transportation_mode.lower(), 0)

    # Diet savings (kg CO2 per year)
    diet_savings = {
        "vegan": 1500,
        "vegetarian": 1000,
        "pescatarian": 600,
        "flexitarian": 300,
        "omnivore": 0
    }
    if lifestyle.diet_type:
        co2_saved += diet_savings.get(lifestyle.diet_type.lower(), 0)

    # Recycling savings (kg CO2 per year)
    recycling_savings = {
        "always": 500,
        "often": 350,
        "sometimes": 150,
        "rarely": 50,
        "never": 0
    }
    if lifestyle.recycling_habits:
        co2_saved += recycling_savings.get(lifestyle.recycling_habits.lower(), 0)

    # Renewable energy savings (kg CO2 per year)
    energy_savings = {
        "renewable": 2500,
        "mostly_renewable": 1800,
        "mixed": 800,
        "mostly_non_renewable": 200,
        "non_renewable": 0
    }
    if lifestyle.energy_source:
        co2_saved += energy_savings.get(lifestyle.energy_source.lower(), 0)

    # Reusable items savings (kg CO2 per year)
    if lifestyle.reusable_items:
        co2_saved += 200

    # Paper preference savings (kg CO2 per year)
    paper_savings = {
        "digital": 150,
        "mostly_digital": 100,
        "both": 50,
        "mostly_paper": 10,
        "paper": 0
    }
    if lifestyle.paper_preference:
        co2_saved += paper_savings.get(lifestyle.paper_preference.lower(), 0)

    return round(co2_saved, 2)


async def calculate_total_calories_burned(db: AsyncSession, user_id: int) -> float:
    """
    Calculate total calories burned from all user activities.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Total calories burned
    """
    stmt = select(func.sum(ActivityData.calories_burned)).where(
        ActivityData.user_id == user_id
    )
    result = await db.execute(stmt)
    total = result.scalar_one_or_none()

    return round(total if total else 0.0, 2)


async def calculate_activity_streak(db: AsyncSession, user_id: int) -> int:
    """
    Calculate the number of consecutive days with activity data.
    Streak ends if a day is missing.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Number of consecutive days with activity
    """
    # Get all activity dates ordered by date descending
    stmt = select(ActivityData.date).where(
        ActivityData.user_id == user_id
    ).order_by(ActivityData.date.desc()).distinct()

    result = await db.execute(stmt)
    dates = [row[0] for row in result.fetchall()]

    if not dates:
        return 0

    # Check if today or yesterday has activity
    today = date.today()
    if dates[0] < today - timedelta(days=1):
        return 0  # Streak broken if last activity was more than 1 day ago

    # Count consecutive days
    streak = 1
    current_date = dates[0]

    for i in range(1, len(dates)):
        expected_date = current_date - timedelta(days=1)
        if dates[i] == expected_date:
            streak += 1
            current_date = dates[i]
        else:
            break

    return streak


async def calculate_combined_streak(db: AsyncSession, user_id: int) -> int:
    """
    Calculate the number of consecutive days with either activity data OR all meals consumed.
    A day counts towards the streak if the user either:
    - Has activity data for that day, OR
    - Has consumed all 3 meals (breakfast, lunch, dinner) for that day

    Streak ends if a day has neither activity data nor all meals consumed.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Number of consecutive days with activity or completed meals
    """
    from datetime import timedelta
    from collections import defaultdict

    # Get all activity dates
    activity_stmt = select(ActivityData.date).where(
        ActivityData.user_id == user_id
    ).distinct()
    activity_result = await db.execute(activity_stmt)
    activity_dates = set(row[0] for row in activity_result.fetchall())

    # Get all meal consumptions
    meal_stmt = select(MealConsumption.date, MealConsumption.meal_type, MealConsumption.consumed).where(
        MealConsumption.user_id == user_id,
        MealConsumption.consumed == True
    )
    meal_result = await db.execute(meal_stmt)
    meal_data = meal_result.fetchall()

    # Group meals by date and count consumed meals
    meals_by_date = defaultdict(set)
    for row in meal_data:
        meal_date, meal_type, consumed = row
        if consumed:
            meals_by_date[meal_date].add(meal_type)

    # Find dates with all 3 meals consumed
    complete_meal_dates = set()
    required_meals = {'breakfast', 'lunch', 'dinner'}
    for meal_date, consumed_meals in meals_by_date.items():
        if consumed_meals >= required_meals:  # All 3 meals consumed
            complete_meal_dates.add(meal_date)

    # Combine dates: days with either activity or all meals consumed
    valid_dates = sorted(activity_dates | complete_meal_dates, reverse=True)

    if not valid_dates:
        return 0

    # Check if today or yesterday has valid data
    today = date.today()
    if valid_dates[0] < today - timedelta(days=1):
        return 0  # Streak broken if last valid day was more than 1 day ago

    # Count consecutive days
    streak = 1
    current_date = valid_dates[0]

    for i in range(1, len(valid_dates)):
        expected_date = current_date - timedelta(days=1)
        if valid_dates[i] == expected_date:
            streak += 1
            current_date = valid_dates[i]
        else:
            break

    return streak


async def get_dashboard_data(
    db: AsyncSession,
    user_id: int
) -> Tuple[float, float, float, float, int, Optional[datetime]]:
    """
    Get all dashboard metrics for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Tuple of (eco_score, wellness_score, co2_saved, calories_burned, streak_days, last_updated)
    """
    user = await get_user_with_data(db, user_id)

    if not user:
        return 50.0, 50.0, 0.0, 0.0, 0, None

    # Calculate scores
    eco_score = calculate_eco_score(user.lifestyle_data)
    wellness_score = calculate_wellness_score(user.health_data)

    # Calculate carbon savings
    co2_saved = calculate_carbon_savings(user.lifestyle_data)

    # Calculate total calories burned
    calories_burned = await calculate_total_calories_burned(db, user_id)

    # Calculate combined streak (activity + meal consumption)
    streak_days = await calculate_combined_streak(db, user_id)

    # Get last updated timestamp
    last_updated = None
    if user.lifestyle_data and user.health_data:
        last_updated = max(
            user.lifestyle_data.updated_at,
            user.health_data.updated_at
        )
    elif user.lifestyle_data:
        last_updated = user.lifestyle_data.updated_at
    elif user.health_data:
        last_updated = user.health_data.updated_at

    return eco_score, wellness_score, co2_saved, calories_burned, streak_days, last_updated


async def get_progress_data(
    db: AsyncSession,
    user_id: int,
    days: int = 30
) -> List[ProgressDataPoint]:
    """
    Get progress tracking data for the last N days.
    Returns mock data if insufficient activity data exists.

    Args:
        db: Database session
        user_id: User ID
        days: Number of days to look back (default 30)

    Returns:
        List of ProgressDataPoint objects
    """
    user = await get_user_with_data(db, user_id)

    if not user:
        return []

    # Calculate current scores
    eco_score = calculate_eco_score(user.lifestyle_data)
    wellness_score = calculate_wellness_score(user.health_data)

    # Get activity data for the last N days
    start_date = date.today() - timedelta(days=days)
    stmt = select(ActivityData).where(
        ActivityData.user_id == user_id,
        ActivityData.date >= start_date
    ).order_by(ActivityData.date.asc())

    result = await db.execute(stmt)
    activities = result.scalars().all()

    # Create progress data points
    progress_data = []

    if activities:
        # Use actual activity data
        for activity in activities:
            progress_data.append(ProgressDataPoint(
                date=activity.date,
                eco_score=eco_score,  # Assuming eco score remains constant (could be improved)
                wellness_score=wellness_score,  # Assuming wellness score remains constant
                steps=activity.steps or 0,
                calories_burned=activity.calories_burned or 0.0
            ))
    else:
        # Generate mock data for demonstration (last 7 days)
        for i in range(7):
            mock_date = date.today() - timedelta(days=6-i)
            # Clamp scores to stay within 0-100 range
            mock_eco = min(100.0, max(0.0, eco_score - (7-i) * 2))  # Gradually increasing towards current
            mock_wellness = min(100.0, max(0.0, wellness_score - (7-i) * 1.5))  # Gradually increasing towards current
            progress_data.append(ProgressDataPoint(
                date=mock_date,
                eco_score=mock_eco,
                wellness_score=mock_wellness,
                steps=5000 + (i * 500),  # Mock steps
                calories_burned=200 + (i * 25)  # Mock calories
            ))

    return progress_data
