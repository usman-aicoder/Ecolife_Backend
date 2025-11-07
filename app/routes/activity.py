"""
Activity routes for tracking user's daily activities and steps.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime
from typing import List

from app.db.session import get_db
from app.schemas.activity import (
    ActivityDataCreate,
    ActivityDataUpdate,
    ActivityDataResponse,
    AddStepsRequest,
    AddStepsResponse
)
from app.models.activity import ActivityData
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.post("/steps", response_model=AddStepsResponse)
async def add_steps(
    request: AddStepsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add or update daily steps for the authenticated user.

    If an activity record already exists for this date, it will be updated.
    Otherwise, a new record will be created.

    Args:
        request: Request containing date, steps, and activity type
        db: Database session
        current_user: Currently authenticated user

    Returns:
        AddStepsResponse with success status and activity data
    """
    # Check if a record already exists for this date
    stmt = select(ActivityData).where(
        and_(
            ActivityData.user_id == current_user.id,
            ActivityData.date == request.date
        )
    )
    result = await db.execute(stmt)
    activity = result.scalar_one_or_none()

    # Determine if this is a time-based activity
    time_based_activities = ["cycling", "gym", "swimming", "football", "other_sports"]
    is_time_based = request.activity_type in time_based_activities

    if activity:
        # Update existing record
        activity.steps = request.steps if not is_time_based else 0
        activity.activity_type = request.activity_type
        activity.duration_minutes = request.duration_minutes if request.duration_minutes else 0.0
        activity.updated_at = datetime.utcnow()

        # Estimate calories burned
        if is_time_based and request.duration_minutes:
            # Rough estimate: 5-10 calories per minute depending on activity
            activity.calories_burned = round(request.duration_minutes * 7, 2)
            message = f"Activity updated: {request.duration_minutes} minutes of {request.activity_type}"
        else:
            # For step-based: 0.04 calories per step
            activity.calories_burned = round(request.steps * 0.04, 2)
            message = f"Steps updated to {request.steps}"
    else:
        # Create new record
        if is_time_based and request.duration_minutes:
            calories = round(request.duration_minutes * 7, 2)
            duration = request.duration_minutes
            steps = 0
            message = f"Added {duration} minutes of {request.activity_type}"
        else:
            calories = round(request.steps * 0.04, 2)
            duration = 0.0
            steps = request.steps
            message = f"Added {steps} steps"

        activity = ActivityData(
            user_id=current_user.id,
            date=request.date,
            steps=steps,
            activity_type=request.activity_type,
            calories_burned=calories,
            duration_minutes=duration
        )
        db.add(activity)

    await db.commit()
    await db.refresh(activity)

    return AddStepsResponse(
        success=True,
        message=message,
        activity=activity
    )


@router.get("/today", response_model=ActivityDataResponse)
async def get_today_activity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get today's activity data for the authenticated user.

    Args:
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ActivityDataResponse or 404 if no activity for today
    """
    today = date.today()

    stmt = select(ActivityData).where(
        and_(
            ActivityData.user_id == current_user.id,
            ActivityData.date == today
        )
    )
    result = await db.execute(stmt)
    activity = result.scalar_one_or_none()

    if not activity:
        # Return default empty activity
        return ActivityDataResponse(
            id=0,
            user_id=current_user.id,
            steps=0,
            duration_minutes=0.0,
            activity_type="walking",
            calories_burned=0.0,
            date=today,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    return activity


@router.get("/date/{target_date}", response_model=ActivityDataResponse)
async def get_activity_by_date(
    target_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get activity data for a specific date.

    Args:
        target_date: The date to get activity for
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ActivityDataResponse or 404 if no activity for that date
    """
    stmt = select(ActivityData).where(
        and_(
            ActivityData.user_id == current_user.id,
            ActivityData.date == target_date
        )
    )
    result = await db.execute(stmt)
    activity = result.scalar_one_or_none()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No activity found for {target_date}"
        )

    return activity


@router.get("/history", response_model=List[ActivityDataResponse])
async def get_activity_history(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get activity history for the authenticated user.

    Args:
        days: Number of days to look back (default 7)
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of ActivityDataResponse
    """
    from datetime import timedelta

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    stmt = select(ActivityData).where(
        and_(
            ActivityData.user_id == current_user.id,
            ActivityData.date >= start_date,
            ActivityData.date <= end_date
        )
    ).order_by(ActivityData.date.desc())

    result = await db.execute(stmt)
    activities = result.scalars().all()

    return activities


@router.post("/", response_model=ActivityDataResponse)
async def create_activity(
    activity_data: ActivityDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new activity record.

    Args:
        activity_data: Activity data to create
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ActivityDataResponse with created activity
    """
    # Check if activity already exists for this date
    stmt = select(ActivityData).where(
        and_(
            ActivityData.user_id == current_user.id,
            ActivityData.date == activity_data.date
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Activity already exists for {activity_data.date}. Use PUT to update."
        )

    activity = ActivityData(
        user_id=current_user.id,
        **activity_data.model_dump()
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    return activity


@router.put("/{activity_id}", response_model=ActivityDataResponse)
async def update_activity(
    activity_id: int,
    activity_data: ActivityDataUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing activity record.

    Args:
        activity_id: ID of the activity to update
        activity_data: Updated activity data
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ActivityDataResponse with updated activity
    """
    stmt = select(ActivityData).where(
        and_(
            ActivityData.id == activity_id,
            ActivityData.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    activity = result.scalar_one_or_none()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    # Update fields
    update_data = activity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)

    activity.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(activity)

    return activity


@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an activity record.

    Args:
        activity_id: ID of the activity to delete
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Success message
    """
    stmt = select(ActivityData).where(
        and_(
            ActivityData.id == activity_id,
            ActivityData.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    activity = result.scalar_one_or_none()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    await db.delete(activity)
    await db.commit()

    return {"success": True, "message": "Activity deleted"}
