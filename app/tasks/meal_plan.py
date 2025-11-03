"""
Celery task for asynchronous meal plan generation.
Generates a 7-day personalized meal plan based on user preferences.
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from app.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.meal_plan import MealPlan
from app.services.meal_plan_service import generate_7_day_meal_plan


@celery_app.task(bind=True, name='app.tasks.meal_plan.generate_meal_plan_task')
def generate_meal_plan_task(
    self,
    meal_plan_id: int,
    user_id: int,
    dietary_preference: str = "balanced",
    calorie_target: int = 2000,
    exclude_ingredients: list = None
):
    """
    Celery task to generate meal plan asynchronously.

    Args:
        self: Celery task instance (for self.update_state)
        meal_plan_id: Database ID of the MealPlan record
        user_id: ID of the user requesting the meal plan
        dietary_preference: Type of diet
        calorie_target: Daily calorie target
        exclude_ingredients: List of ingredients to exclude

    Returns:
        dict: Result containing meal plan data
    """

    # Run async function in event loop
    return asyncio.run(
        _generate_meal_plan_async(
            self,
            meal_plan_id,
            user_id,
            dietary_preference,
            calorie_target,
            exclude_ingredients or []
        )
    )


async def _generate_meal_plan_async(
    task,
    meal_plan_id: int,
    user_id: int,
    dietary_preference: str,
    calorie_target: int,
    exclude_ingredients: list
):
    """
    Async function to generate meal plan and update database.
    """

    async with AsyncSessionLocal() as session:
        try:
            # Update status to processing
            task.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Starting meal plan generation'})

            result = await session.execute(
                select(MealPlan).where(MealPlan.id == meal_plan_id)
            )
            meal_plan = result.scalar_one_or_none()

            if not meal_plan:
                raise Exception(f"MealPlan with id {meal_plan_id} not found")

            meal_plan.status = "processing"
            await session.commit()

            # Generate meal plan (this is where the heavy computation happens)
            task.update_state(state='PROGRESS', meta={'progress': 25, 'status': 'Generating meals'})

            meals_data = await generate_7_day_meal_plan(
                dietary_preference=dietary_preference,
                calorie_target=calorie_target,
                exclude_ingredients=exclude_ingredients
            )

            task.update_state(state='PROGRESS', meta={'progress': 80, 'status': 'Finalizing meal plan'})

            # Update meal plan in database
            meal_plan.meals = meals_data
            meal_plan.status = "completed"
            meal_plan.completed_at = datetime.utcnow()

            await session.commit()

            task.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Completed'})

            return {
                'status': 'completed',
                'meal_plan_id': meal_plan_id,
                'user_id': user_id,
                'message': 'Meal plan generated successfully'
            }

        except Exception as e:
            # Update status to failed
            result = await session.execute(
                select(MealPlan).where(MealPlan.id == meal_plan_id)
            )
            meal_plan = result.scalar_one_or_none()

            if meal_plan:
                meal_plan.status = "failed"
                meal_plan.error_message = str(e)
                await session.commit()

            raise Exception(f"Meal plan generation failed: {str(e)}")
