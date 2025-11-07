"""
Health Insights Service
Analyzes user data to provide personalized health insights and recommendations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.activity import ActivityData
from app.models.meal_plan import MealPlan
from app.models.meal_consumption import MealConsumption
from app.models.health import HealthData
from app.utils.health_calculator import calculate_bmr, calculate_tdee


async def get_daily_insights(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """
    Get today's health insights for the user
    """
    today = datetime.now().date()

    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError("User not found")

    # Get health data separately to avoid lazy-load issues
    health_result = await db.execute(
        select(HealthData).where(HealthData.user_id == user_id)
    )
    health_data_orm = health_result.scalar_one_or_none()

    # Convert health data to dict to avoid lazy-loading issues
    health_data = None
    if health_data_orm:
        health_data = {
            "weight": health_data_orm.weight,
            "height": health_data_orm.height,
            "age": health_data_orm.age,
            "gender": health_data_orm.gender,
            "activity_level": health_data_orm.activity_level,
            "wellness_goal": health_data_orm.wellness_goal
        }

    # Get today's activity
    activity_result = await db.execute(
        select(ActivityData).where(
            ActivityData.user_id == user_id,
            ActivityData.date == today
        )
    )
    today_activity = activity_result.scalar_one_or_none()

    # Get today's meal consumption
    meal_result = await db.execute(
        select(MealConsumption).where(
            MealConsumption.user_id == user_id,
            MealConsumption.date == today
        )
    )
    meal_consumptions = meal_result.scalars().all()

    # Get latest meal plan for calorie info
    meal_plan_result = await db.execute(
        select(MealPlan).where(
            MealPlan.user_id == user_id,
            MealPlan.status == "completed"
        ).order_by(MealPlan.created_at.desc()).limit(1)
    )
    meal_plan = meal_plan_result.scalar_one_or_none()

    # Access meals data eagerly and convert consumptions to simple dicts to avoid lazy-load issues
    meal_plan_meals = meal_plan.meals if meal_plan else None

    # Force evaluation of all ORM attributes in async context
    meal_consumption_data = []
    for m in list(meal_consumptions):
        meal_consumption_data.append({
            "meal_type": str(m.meal_type),
            "consumed": bool(m.consumed)
        })

    # Convert activity data to dict to avoid lazy-load issues
    activity_data = None
    if today_activity:
        activity_data = {
            "steps": today_activity.steps,
            "calories_burned": today_activity.calories_burned,
            "activity_type": today_activity.activity_type,
            "duration_minutes": today_activity.duration_minutes
        }

    # Calculate insights
    insights = {
        "date": today.isoformat(),
        "activity": _analyze_today_activity(activity_data),
        "meals": _analyze_today_meals(meal_consumption_data, meal_plan_meals, today),
        "calories": _analyze_today_calories(meal_plan_meals, meal_consumption_data, health_data, today),
        "recommendations": []
    }

    # Generate recommendations based on data
    insights["recommendations"] = _generate_daily_recommendations(insights, health_data)

    return insights


async def get_weekly_insights(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """
    Get this week's health insights
    """
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = today

    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError("User not found")

    # Get week's activities
    activity_result = await db.execute(
        select(ActivityData).where(
            ActivityData.user_id == user_id,
            ActivityData.date >= week_start,
            ActivityData.date <= week_end
        ).order_by(ActivityData.date)
    )
    week_activities = activity_result.scalars().all()

    # Get week's meal consumptions
    meal_result = await db.execute(
        select(MealConsumption).where(
            MealConsumption.user_id == user_id,
            MealConsumption.date >= week_start,
            MealConsumption.date <= week_end
        )
    )
    week_meals = meal_result.scalars().all()

    # Calculate weekly insights
    insights = {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "activity_summary": _analyze_weekly_activity(week_activities),
        "meal_summary": _analyze_weekly_meals(week_meals),
        "streak": await _calculate_activity_streak(db, user_id, today),
        "consistency_score": _calculate_consistency_score(week_activities, week_meals)
    }

    return insights


def _analyze_today_activity(activity: Optional[Dict]) -> Dict[str, Any]:
    """Analyze today's activity data"""
    if not activity:
        return {
            "steps": 0,
            "steps_goal": 10000,
            "percentage": 0,
            "calories_burned": 0,
            "goal_achieved": False,
            "message": "No activity logged today. Start moving!"
        }

    steps_goal = 10000
    steps = activity.get("steps") or 0
    percentage = min(100, int((steps / steps_goal) * 100)) if steps else 0
    goal_achieved = steps >= steps_goal if steps else False

    if goal_achieved:
        message = f"🎉 Amazing! You hit your {steps_goal:,} step goal!"
    elif percentage >= 75:
        message = f"💪 Almost there! Just {steps_goal - steps:,} more steps"
    elif percentage >= 50:
        message = f"👍 Good progress! {percentage}% to your daily goal"
    else:
        message = f"🚶 Keep moving! {percentage}% of your goal completed"

    return {
        "steps": steps,
        "steps_goal": steps_goal,
        "percentage": percentage,
        "calories_burned": activity.get("calories_burned") or 0,
        "activity_type": activity.get("activity_type"),
        "duration_minutes": activity.get("duration_minutes"),
        "goal_achieved": goal_achieved,
        "message": message
    }


def _analyze_today_meals(
    consumptions: List[Dict],
    meal_plan_meals: Optional[List],
    today: datetime.date
) -> Dict[str, Any]:
    """Analyze today's meal consumption"""
    meals_logged = len(consumptions)
    total_meals = 3  # breakfast, lunch, dinner

    breakfast = any(m["meal_type"] == "breakfast" and m["consumed"] for m in consumptions)
    lunch = any(m["meal_type"] == "lunch" and m["consumed"] for m in consumptions)
    dinner = any(m["meal_type"] == "dinner" and m["consumed"] for m in consumptions)

    meals_consumed = sum([breakfast, lunch, dinner])
    percentage = int((meals_consumed / total_meals) * 100)

    if meals_consumed == 3:
        message = "✅ Perfect! All meals logged today"
    elif meals_consumed == 2:
        message = "👍 Good! 2 out of 3 meals logged"
    elif meals_consumed == 1:
        message = "⚠️ Only 1 meal logged. Don't forget to track!"
    else:
        message = "❌ No meals logged yet today"

    return {
        "meals_consumed": meals_consumed,
        "total_meals": total_meals,
        "percentage": percentage,
        "breakfast": breakfast,
        "lunch": lunch,
        "dinner": dinner,
        "message": message
    }


def _analyze_today_calories(
    meal_plan_meals: Optional[List],
    consumptions: List[Dict],
    health_data: Optional[Dict],
    today: datetime.date
) -> Dict[str, Any]:
    """Analyze today's calorie intake vs target"""

    # Calculate target calories (TDEE)
    target_calories = 2000  # Default

    if health_data:
        bmr = calculate_bmr(
            health_data["weight"],
            health_data["height"],
            health_data["age"],
            health_data["gender"]
        )
        target_calories = calculate_tdee(bmr, health_data["activity_level"])

        # Adjust based on goal
        if health_data["wellness_goal"] == "weight_loss":
            target_calories -= 500  # 500 calorie deficit
        elif health_data["wellness_goal"] == "muscle_gain":
            target_calories += 300  # 300 calorie surplus

    # Calculate consumed calories from meal plan
    consumed_calories = 0
    if meal_plan_meals:
        # Find today's meals in the plan
        for day_meals in meal_plan_meals:
            meal_date = datetime.strptime(day_meals["date"], "%Y-%m-%d").date()
            if meal_date == today:
                # Count calories for consumed meals only
                for consumption in consumptions:
                    if consumption["consumed"]:
                        meal_type = consumption["meal_type"]
                        if meal_type in day_meals:
                            consumed_calories += day_meals[meal_type].get("calories", 0)
                break

    difference = int(consumed_calories - target_calories)
    percentage = int((consumed_calories / target_calories) * 100) if target_calories > 0 else 0

    # Generate message
    if abs(difference) <= 100:
        message = "🎯 Perfect! Right on target with your calories"
        status = "perfect"
    elif difference < -200:
        message = f"⚠️ You're {abs(difference)} calories below target. Eat a bit more!"
        status = "low"
    elif difference > 200:
        message = f"⚠️ You're {difference} calories over target. Consider lighter options"
        status = "high"
    elif difference < 0:
        message = f"👍 Good! {abs(difference)} calories below target"
        status = "good_low"
    else:
        message = f"👍 Slightly over by {difference} calories - still good!"
        status = "good_high"

    return {
        "consumed": int(consumed_calories),
        "target": int(target_calories),
        "difference": difference,
        "percentage": percentage,
        "status": status,
        "message": message
    }


def _analyze_weekly_activity(activities: List[ActivityData]) -> Dict[str, Any]:
    """Analyze weekly activity data"""
    if not activities:
        return {
            "total_steps": 0,
            "avg_steps": 0,
            "total_calories": 0,
            "days_active": 0,
            "goal_days": 0,
            "message": "No activity data for this week"
        }

    total_steps = sum(a.steps or 0 for a in activities)
    total_calories = sum(a.calories_burned or 0 for a in activities)
    days_active = len(activities)
    goal_days = sum(1 for a in activities if (a.steps or 0) >= 10000)
    avg_steps = total_steps // days_active if days_active > 0 else 0

    if goal_days >= 5:
        message = f"🔥 Excellent! Hit your step goal {goal_days}/7 days"
    elif goal_days >= 3:
        message = f"👍 Good effort! {goal_days}/7 days at goal"
    else:
        message = f"💪 Keep pushing! Only {goal_days}/7 days at goal"

    return {
        "total_steps": total_steps,
        "avg_steps": avg_steps,
        "total_calories": total_calories,
        "days_active": days_active,
        "goal_days": goal_days,
        "message": message
    }


def _analyze_weekly_meals(consumptions: List[MealConsumption]) -> Dict[str, Any]:
    """Analyze weekly meal consumption"""
    total_possible = 21  # 7 days * 3 meals
    meals_logged = sum(1 for m in consumptions if m.consumed)
    percentage = int((meals_logged / total_possible) * 100)

    # Count by meal type
    breakfast_count = sum(1 for m in consumptions if m.meal_type == "breakfast" and m.consumed)
    lunch_count = sum(1 for m in consumptions if m.meal_type == "lunch" and m.consumed)
    dinner_count = sum(1 for m in consumptions if m.meal_type == "dinner" and m.consumed)

    if percentage >= 90:
        message = "🌟 Outstanding! Almost perfect meal tracking"
    elif percentage >= 70:
        message = "✅ Great! Very consistent meal logging"
    elif percentage >= 50:
        message = "👍 Good! Try to log more meals"
    else:
        message = "⚠️ Low meal tracking. More consistency needed!"

    return {
        "meals_logged": meals_logged,
        "total_possible": total_possible,
        "percentage": percentage,
        "breakfast_count": breakfast_count,
        "lunch_count": lunch_count,
        "dinner_count": dinner_count,
        "message": message
    }


async def _calculate_activity_streak(db: AsyncSession, user_id: int, end_date: datetime.date) -> int:
    """Calculate consecutive days of activity"""
    streak = 0
    current_date = end_date

    for _ in range(30):  # Check last 30 days max
        result = await db.execute(
            select(ActivityData).where(
                ActivityData.user_id == user_id,
                ActivityData.date == current_date
            )
        )
        activity = result.scalar_one_or_none()

        # Activity counts if steps >= 5000 or duration > 0
        if activity and ((activity.steps and activity.steps >= 5000) or (activity.duration_minutes and activity.duration_minutes > 0)):
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break

    return streak


def _calculate_consistency_score(activities: List[ActivityData], meals: List[MealConsumption]) -> int:
    """Calculate overall consistency score (0-100)"""
    scores = []

    # Activity consistency (30%)
    activity_days = len(activities)
    if activity_days > 0:
        activity_score = min(100, int((activity_days / 7) * 100))
        scores.append(activity_score * 0.3)

    # Meal consistency (40%)
    meals_logged = sum(1 for m in meals if m.consumed)
    if meals_logged > 0:
        meal_score = min(100, int((meals_logged / 21) * 100))
        scores.append(meal_score * 0.4)

    # Step goal achievement (30%)
    goal_days = sum(1 for a in activities if (a.steps or 0) >= 10000)
    if goal_days > 0:
        goal_score = min(100, int((goal_days / 7) * 100))
        scores.append(goal_score * 0.3)

    return int(sum(scores)) if scores else 0


def _generate_daily_recommendations(insights: Dict[str, Any], health_data: Optional[Dict]) -> List[str]:
    """Generate personalized recommendations based on today's data"""
    recommendations = []

    # Activity recommendations
    activity = insights.get("activity", {})
    if not activity.get("goal_achieved"):
        steps_remaining = 10000 - activity.get("steps", 0)
        if steps_remaining > 0:
            recommendations.append(f"Walk {steps_remaining:,} more steps to hit your daily goal")

    # Calorie recommendations
    calories = insights.get("calories", {})
    if calories.get("status") == "low":
        recommendations.append(f"Add {abs(calories.get('difference', 0))} calories - try a healthy snack")
    elif calories.get("status") == "high":
        recommendations.append(f"{calories.get('difference', 0)} calories over - consider lighter dinner")

    # Meal recommendations
    meals = insights.get("meals", {})
    if not meals.get("breakfast"):
        recommendations.append("Don't skip breakfast! It boosts your metabolism")
    if not meals.get("lunch"):
        recommendations.append("Log your lunch to track your nutrition properly")
    if not meals.get("dinner"):
        recommendations.append("Remember to log your dinner meal")

    # Activity type variety
    if activity.get("activity_type") == "walking":
        recommendations.append("Try mixing up your activities - cycling or swimming!")

    # If no recommendations, add encouraging message
    if not recommendations:
        recommendations.append("You're doing great! Keep up the excellent work!")

    return recommendations[:5]  # Limit to top 5
