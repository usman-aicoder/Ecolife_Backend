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


async def update_meal_plan(
    db: AsyncSession,
    meal_plan_id: int,
    user_id: int,
    updated_meals: List[Dict[str, Any]]
) -> MealPlan:
    """
    Update an existing meal plan with edited meals.
    Backs up original meals if this is the first edit.

    Args:
        db: Database session
        meal_plan_id: ID of the meal plan to update
        user_id: User ID (for authorization)
        updated_meals: Updated 7-day meal plan data

    Returns:
        Updated MealPlan object
    """
    from sqlalchemy import select

    # Fetch the meal plan
    result = await db.execute(
        select(MealPlan).where(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == user_id
        )
    )
    meal_plan = result.scalar_one_or_none()

    if not meal_plan:
        raise ValueError(f"Meal plan {meal_plan_id} not found or unauthorized")

    # Backup original meals if this is the first edit
    if not meal_plan.customized and meal_plan.meals:
        meal_plan.original_meals = meal_plan.meals

    # Update the meals
    meal_plan.meals = updated_meals
    meal_plan.customized = True
    meal_plan.edited_at = datetime.utcnow()

    await db.commit()
    await db.refresh(meal_plan)

    return meal_plan


async def swap_single_meal(
    db: AsyncSession,
    meal_plan_id: int,
    user_id: int,
    day_index: int,
    meal_type: str,
    new_meal: Dict[str, Any]
) -> MealPlan:
    """
    Swap a single meal in the meal plan.

    Args:
        db: Database session
        meal_plan_id: ID of the meal plan
        user_id: User ID (for authorization)
        day_index: Day index (0-6)
        meal_type: Type of meal (breakfast, lunch, dinner)
        new_meal: New meal data

    Returns:
        Updated MealPlan object
    """
    from sqlalchemy import select

    # Fetch the meal plan
    result = await db.execute(
        select(MealPlan).where(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == user_id
        )
    )
    meal_plan = result.scalar_one_or_none()

    if not meal_plan:
        raise ValueError(f"Meal plan {meal_plan_id} not found or unauthorized")

    if not meal_plan.meals or day_index < 0 or day_index >= len(meal_plan.meals):
        raise ValueError(f"Invalid day index: {day_index}")

    if meal_type not in ["breakfast", "lunch", "dinner"]:
        raise ValueError(f"Invalid meal type: {meal_type}")

    # Backup original meals if this is the first edit
    if not meal_plan.customized and meal_plan.meals:
        meal_plan.original_meals = meal_plan.meals[:]

    # Swap the meal
    meals_data = meal_plan.meals[:]  # Create a copy
    old_meal = meals_data[day_index][meal_type]
    meals_data[day_index][meal_type] = new_meal

    # Recalculate daily totals
    day_meals = meals_data[day_index]
    day_meals["total_calories"] = (
        day_meals["breakfast"]["calories"] +
        day_meals["lunch"]["calories"] +
        day_meals["dinner"]["calories"]
    )
    day_meals["total_carbon"] = round(
        day_meals["breakfast"]["carbon_footprint"] +
        day_meals["lunch"]["carbon_footprint"] +
        day_meals["dinner"]["carbon_footprint"],
        2
    )

    # Update the meal plan
    meal_plan.meals = meals_data
    meal_plan.customized = True
    meal_plan.edited_at = datetime.utcnow()

    await db.commit()
    await db.refresh(meal_plan)

    return meal_plan
