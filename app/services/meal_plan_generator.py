"""
Simplified Synchronous Meal Plan Generator
Auto-generates 7-day meal plans during onboarding
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meal_plan import MealPlan
from app.models.user import User
from app.services.meal_plan_service import generate_7_day_meal_plan
from app.db.session import get_db


async def auto_generate_meal_plan_for_user(
    user_id: int,
    dietary_preference: Optional[str] = None,
    calorie_target: int = 2000,
    diet_type: Optional[str] = None
) -> MealPlan:
    """
    Automatically generate and store a 7-day meal plan for a user.
    Called during onboarding when health form is submitted.
    Uses a fresh database session to avoid async context issues.

    Args:
        user_id: User ID
        dietary_preference: Diet type preference
        calorie_target: Daily calorie target
        diet_type: Optional diet type from lifestyle data

    Returns:
        Created MealPlan object
    """

    # Get a fresh database session
    async for db in get_db():
        try:
            # Determine dietary preference
            if not dietary_preference:
                dietary_preference = diet_type or "balanced"

            # Generate the 7-day meal plan
            meals_data = await generate_7_day_meal_plan(
                dietary_preference=dietary_preference,
                calorie_target=calorie_target,
                exclude_ingredients=[]
            )

            # Create meal plan record
            meal_plan = MealPlan(
                user_id=user_id,
                status="completed",
                meals=meals_data,
                dietary_preference=dietary_preference,
                calorie_target=calorie_target,
                completed_at=datetime.utcnow()
            )

            db.add(meal_plan)
            await db.commit()
            await db.refresh(meal_plan)

            return meal_plan
        finally:
            await db.close()


async def regenerate_meal_plan_for_user(
    db: AsyncSession,
    user: User,
    dietary_preference: Optional[str] = None,
    calorie_target: Optional[int] = None,
    exclude_ingredients: List[str] = None
) -> MealPlan:
    """
    Regenerate a meal plan for a user (manual trigger from dashboard).

    Args:
        db: Database session
        user: User object
        dietary_preference: Optional diet preference override
        calorie_target: Optional calorie target override
        exclude_ingredients: Optional ingredients to exclude

    Returns:
        New MealPlan object
    """

    # Use defaults if not provided
    if not dietary_preference:
        if user.lifestyle_data:
            dietary_preference = user.lifestyle_data.diet_type or "balanced"
        else:
            dietary_preference = "balanced"

    if not calorie_target:
        calorie_target = 2000

    if exclude_ingredients is None:
        exclude_ingredients = []

    # Generate the meal plan
    meals_data = await generate_7_day_meal_plan(
        dietary_preference=dietary_preference,
        calorie_target=calorie_target,
        exclude_ingredients=exclude_ingredients
    )

    # Create new meal plan record
    meal_plan = MealPlan(
        user_id=user.id,
        status="completed",
        meals=meals_data,
        dietary_preference=dietary_preference,
        calorie_target=calorie_target,
        completed_at=datetime.utcnow()
    )

    db.add(meal_plan)
    await db.commit()
    await db.refresh(meal_plan)

    return meal_plan
