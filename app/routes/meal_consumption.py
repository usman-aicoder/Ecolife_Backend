"""
Meal Consumption routes for tracking which meals users have consumed.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime
from typing import List

from app.db.session import get_db
from app.schemas.meal_consumption import (
    MarkMealConsumedRequest,
    MarkMealConsumedResponse,
    MealConsumptionResponse,
    DailyMealStatus,
    MealConsumptionHistory
)
from app.models.meal_consumption import MealConsumption
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/meal-consumptions", tags=["Meal Consumption"])


@router.post("/mark", response_model=MarkMealConsumedResponse)
async def mark_meal_consumed(
    request: MarkMealConsumedRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a meal as consumed for the authenticated user.

    If a record already exists for this date and meal type, it will be updated.
    Otherwise, a new record will be created.

    Args:
        request: Request containing date, meal_type, and optional meal_plan_id
        db: Database session
        current_user: Currently authenticated user

    Returns:
        MarkMealConsumedResponse with success status and meal consumption data

    Raises:
        HTTPException 400: If meal_type is invalid
    """
    # Check if a record already exists for this date and meal type
    stmt = select(MealConsumption).where(
        and_(
            MealConsumption.user_id == current_user.id,
            MealConsumption.date == request.date,
            MealConsumption.meal_type == request.meal_type
        )
    )
    result = await db.execute(stmt)
    meal_consumption = result.scalar_one_or_none()

    if meal_consumption:
        # Update existing record
        meal_consumption.consumed = True
        meal_consumption.consumed_at = datetime.utcnow()
        if request.meal_plan_id:
            meal_consumption.meal_plan_id = request.meal_plan_id
    else:
        # Create new record
        meal_consumption = MealConsumption(
            user_id=current_user.id,
            meal_plan_id=request.meal_plan_id,
            date=request.date,
            meal_type=request.meal_type,
            consumed=True,
            consumed_at=datetime.utcnow()
        )
        db.add(meal_consumption)

    await db.commit()
    await db.refresh(meal_consumption)

    return MarkMealConsumedResponse(
        success=True,
        message=f"{request.meal_type.capitalize()} marked as consumed",
        meal_consumption=meal_consumption
    )


@router.post("/unmark", response_model=MarkMealConsumedResponse)
async def unmark_meal_consumed(
    request: MarkMealConsumedRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unmark a meal as consumed (mark it as not consumed).

    Args:
        request: Request containing date and meal_type
        db: Database session
        current_user: Currently authenticated user

    Returns:
        MarkMealConsumedResponse with success status

    Raises:
        HTTPException 404: If meal consumption record not found
    """
    # Check if a record exists
    stmt = select(MealConsumption).where(
        and_(
            MealConsumption.user_id == current_user.id,
            MealConsumption.date == request.date,
            MealConsumption.meal_type == request.meal_type
        )
    )
    result = await db.execute(stmt)
    meal_consumption = result.scalar_one_or_none()

    if not meal_consumption:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal consumption record not found"
        )

    # Update record
    meal_consumption.consumed = False
    meal_consumption.consumed_at = None

    await db.commit()
    await db.refresh(meal_consumption)

    return MarkMealConsumedResponse(
        success=True,
        message=f"{request.meal_type.capitalize()} unmarked",
        meal_consumption=meal_consumption
    )


@router.get("/today", response_model=DailyMealStatus)
async def get_today_meal_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get meal consumption status for today for the authenticated user.

    Args:
        db: Database session
        current_user: Currently authenticated user

    Returns:
        DailyMealStatus with consumption status for all meals today
    """
    today = date.today()

    # Get all meal consumptions for today
    stmt = select(MealConsumption).where(
        and_(
            MealConsumption.user_id == current_user.id,
            MealConsumption.date == today
        )
    )
    result = await db.execute(stmt)
    meal_consumptions = result.scalars().all()

    # Build status response
    status_dict = {
        'breakfast': False,
        'lunch': False,
        'dinner': False
    }

    for mc in meal_consumptions:
        if mc.consumed:
            status_dict[mc.meal_type] = True

    total_consumed = sum(1 for consumed in status_dict.values() if consumed)

    return DailyMealStatus(
        date=today,
        breakfast=status_dict['breakfast'],
        lunch=status_dict['lunch'],
        dinner=status_dict['dinner'],
        total_consumed=total_consumed,
        total_meals=3
    )


@router.get("/date/{target_date}", response_model=DailyMealStatus)
async def get_meal_status_for_date(
    target_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get meal consumption status for a specific date for the authenticated user.

    Args:
        target_date: The date to get meal status for
        db: Database session
        current_user: Currently authenticated user

    Returns:
        DailyMealStatus with consumption status for all meals on that date
    """
    # Get all meal consumptions for the specified date
    stmt = select(MealConsumption).where(
        and_(
            MealConsumption.user_id == current_user.id,
            MealConsumption.date == target_date
        )
    )
    result = await db.execute(stmt)
    meal_consumptions = result.scalars().all()

    # Build status response
    status_dict = {
        'breakfast': False,
        'lunch': False,
        'dinner': False
    }

    for mc in meal_consumptions:
        if mc.consumed:
            status_dict[mc.meal_type] = True

    total_consumed = sum(1 for consumed in status_dict.values() if consumed)

    return DailyMealStatus(
        date=target_date,
        breakfast=status_dict['breakfast'],
        lunch=status_dict['lunch'],
        dinner=status_dict['dinner'],
        total_consumed=total_consumed,
        total_meals=3
    )


@router.get("/history", response_model=List[MealConsumptionHistory])
async def get_meal_consumption_history(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get meal consumption history for the authenticated user.
    Returns data for the last N days (default 7).

    Args:
        days: Number of days to look back (1-90, default 7)
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of MealConsumptionHistory with meals grouped by date
    """
    from datetime import timedelta

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # Get all meal consumptions for the date range
    stmt = select(MealConsumption).where(
        and_(
            MealConsumption.user_id == current_user.id,
            MealConsumption.date >= start_date,
            MealConsumption.date <= end_date
        )
    ).order_by(MealConsumption.date.desc(), MealConsumption.meal_type)

    result = await db.execute(stmt)
    meal_consumptions = result.scalars().all()

    # Group by date
    history_dict = {}
    for mc in meal_consumptions:
        if mc.date not in history_dict:
            history_dict[mc.date] = []
        history_dict[mc.date].append(mc)

    # Build response
    history = []
    for date_key in sorted(history_dict.keys(), reverse=True):
        meals = history_dict[date_key]
        total_consumed = sum(1 for meal in meals if meal.consumed)

        history.append(MealConsumptionHistory(
            date=date_key,
            meals=meals,
            total_consumed=total_consumed,
            total_meals=3
        ))

    return history


@router.get("/all", response_model=List[MealConsumptionResponse])
async def get_all_meal_consumptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all meal consumption records for the authenticated user.

    Args:
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of all MealConsumptionResponse records
    """
    stmt = select(MealConsumption).where(
        MealConsumption.user_id == current_user.id
    ).order_by(MealConsumption.date.desc(), MealConsumption.meal_type)

    result = await db.execute(stmt)
    meal_consumptions = result.scalars().all()

    return meal_consumptions
