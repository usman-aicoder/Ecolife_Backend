"""
Meal Plan API Routes
Endpoints for generating and retrieving meal plans.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.meal_plan import MealPlan
from app.schemas.meal_plan import (
    MealPlanGenerateRequest,
    MealPlanResponse,
    MealPlanStatusResponse,
    MealPlanListResponse
)
from app.utils.dependencies import get_current_user
from app.tasks.meal_plan import generate_meal_plan_task
from app.services.meal_plan_generator import regenerate_meal_plan_for_user


router = APIRouter(prefix="/meal-plans", tags=["Meal Plans"])


@router.post("/regenerate", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def regenerate_meal_plan_sync(
    request: MealPlanGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Regenerate a new 7-day meal plan synchronously (instant generation).
    This is the simplified version that doesn't require Celery/Redis.
    """

    # Fetch user with relationships
    user_result = await db.execute(
        select(User).where(User.id == current_user.id)
    )
    user = user_result.scalar_one()

    # Generate meal plan synchronously
    meal_plan = await regenerate_meal_plan_for_user(
        db=db,
        user=user,
        dietary_preference=request.dietary_preference,
        calorie_target=request.calorie_target,
        exclude_ingredients=request.exclude_ingredients or []
    )

    # Calculate summary statistics
    total_calories_week = sum(day.get("total_calories", 0) for day in meal_plan.meals)
    total_carbon_week = sum(day.get("total_carbon", 0) for day in meal_plan.meals)
    avg_calories_day = total_calories_week // 7 if total_calories_week else None

    return MealPlanResponse(
        id=meal_plan.id,
        user_id=meal_plan.user_id,
        status=meal_plan.status,
        task_id=meal_plan.task_id,
        meals=meal_plan.meals,
        dietary_preference=meal_plan.dietary_preference,
        calorie_target=meal_plan.calorie_target,
        created_at=meal_plan.created_at,
        completed_at=meal_plan.completed_at,
        error_message=meal_plan.error_message,
        total_calories_week=total_calories_week,
        total_carbon_week=total_carbon_week,
        avg_calories_day=avg_calories_day
    )


@router.post("/generate", response_model=MealPlanStatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_meal_plan(
    request: MealPlanGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a new 7-day meal plan asynchronously.
    Returns immediately with task ID for tracking progress.
    """

    # Create meal plan record
    meal_plan = MealPlan(
        user_id=current_user.id,
        status="pending",
        dietary_preference=request.dietary_preference,
        calorie_target=request.calorie_target
    )

    db.add(meal_plan)
    await db.commit()
    await db.refresh(meal_plan)

    # Trigger Celery task
    task = generate_meal_plan_task.delay(
        meal_plan_id=meal_plan.id,
        user_id=current_user.id,
        dietary_preference=request.dietary_preference or "balanced",
        calorie_target=request.calorie_target or 2000,
        exclude_ingredients=request.exclude_ingredients or []
    )

    # Update meal plan with task ID
    meal_plan.task_id = task.id
    await db.commit()

    return MealPlanStatusResponse(
        id=meal_plan.id,
        task_id=task.id,
        status="pending",
        message="Meal plan generation started. Check status with task ID.",
        progress=0
    )


@router.get("/status/{task_id}", response_model=MealPlanStatusResponse)
async def get_meal_plan_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of a meal plan generation task.
    """

    # Find meal plan by task ID
    result = await db.execute(
        select(MealPlan).where(
            MealPlan.task_id == task_id,
            MealPlan.user_id == current_user.id
        )
    )
    meal_plan = result.scalar_one_or_none()

    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )

    # Get task status from Celery
    from app.celery_app import celery_app
    task = celery_app.AsyncResult(task_id)

    progress = 0
    message = "Pending"

    if task.state == 'PENDING':
        message = "Task is waiting to start"
        progress = 0
    elif task.state == 'PROGRESS':
        info = task.info or {}
        progress = info.get('progress', 50)
        message = info.get('status', 'Processing')
    elif task.state == 'SUCCESS':
        progress = 100
        message = "Meal plan generated successfully"
    elif task.state == 'FAILURE':
        progress = 0
        message = f"Generation failed: {str(task.info)}"

    return MealPlanStatusResponse(
        id=meal_plan.id,
        task_id=task_id,
        status=meal_plan.status,
        message=message,
        progress=progress
    )


@router.get("/{meal_plan_id}", response_model=MealPlanResponse)
async def get_meal_plan(
    meal_plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific meal plan by ID.
    """

    result = await db.execute(
        select(MealPlan).where(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == current_user.id
        )
    )
    meal_plan = result.scalar_one_or_none()

    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )

    # Calculate summary statistics
    total_calories_week = None
    total_carbon_week = None
    avg_calories_day = None

    if meal_plan.meals and meal_plan.status == "completed":
        total_calories_week = sum(day.get("total_calories", 0) for day in meal_plan.meals)
        total_carbon_week = sum(day.get("total_carbon", 0) for day in meal_plan.meals)
        avg_calories_day = total_calories_week // 7 if total_calories_week else None

    return MealPlanResponse(
        id=meal_plan.id,
        user_id=meal_plan.user_id,
        status=meal_plan.status,
        task_id=meal_plan.task_id,
        meals=meal_plan.meals,
        dietary_preference=meal_plan.dietary_preference,
        calorie_target=meal_plan.calorie_target,
        created_at=meal_plan.created_at,
        completed_at=meal_plan.completed_at,
        error_message=meal_plan.error_message,
        total_calories_week=total_calories_week,
        total_carbon_week=total_carbon_week,
        avg_calories_day=avg_calories_day
    )


@router.get("/user/my-plans", response_model=MealPlanListResponse)
async def get_my_meal_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """
    Get all meal plans for the current user.
    """

    result = await db.execute(
        select(MealPlan)
        .where(MealPlan.user_id == current_user.id)
        .order_by(MealPlan.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    meal_plans = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(MealPlan).where(MealPlan.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    # Convert to response format
    meal_plan_responses = []
    for mp in meal_plans:
        total_calories_week = None
        total_carbon_week = None
        avg_calories_day = None

        if mp.meals and mp.status == "completed":
            total_calories_week = sum(day.get("total_calories", 0) for day in mp.meals)
            total_carbon_week = sum(day.get("total_carbon", 0) for day in mp.meals)
            avg_calories_day = total_calories_week // 7 if total_calories_week else None

        meal_plan_responses.append(
            MealPlanResponse(
                id=mp.id,
                user_id=mp.user_id,
                status=mp.status,
                task_id=mp.task_id,
                meals=mp.meals,
                dietary_preference=mp.dietary_preference,
                calorie_target=mp.calorie_target,
                created_at=mp.created_at,
                completed_at=mp.completed_at,
                error_message=mp.error_message,
                total_calories_week=total_calories_week,
                total_carbon_week=total_carbon_week,
                avg_calories_day=avg_calories_day
            )
        )

    return MealPlanListResponse(
        meal_plans=meal_plan_responses,
        total=total
    )


@router.delete("/{meal_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    meal_plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a meal plan.
    """

    result = await db.execute(
        select(MealPlan).where(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == current_user.id
        )
    )
    meal_plan = result.scalar_one_or_none()

    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )

    await db.delete(meal_plan)
    await db.commit()

    return None
