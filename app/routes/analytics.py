"""
Analytics routes for retrieving user analytics and progress data.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.analytics import AnalyticsResponse, ScoreResponse
from app.services.analytics_service import (
    get_user_with_data,
    get_progress_data,
    calculate_carbon_savings
)
from app.services.scoring import calculate_eco_score, calculate_wellness_score
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/score/{user_id}", response_model=ScoreResponse)
async def get_user_scores(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get eco and wellness scores for a specific user.

    **Authorization**: User can only access their own scores unless admin.

    Args:
        user_id: The ID of the user
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ScoreResponse with eco_score, wellness_score, and co2_saved

    Raises:
        HTTPException 403: If user tries to access another user's scores
        HTTPException 404: If user not found
    """
    # Check if user is accessing their own scores
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own analytics"
        )

    # Get user data
    user = await get_user_with_data(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Calculate scores
    eco_score = calculate_eco_score(user.lifestyle_data)
    wellness_score = calculate_wellness_score(user.health_data)
    co2_saved = calculate_carbon_savings(user.lifestyle_data)

    return ScoreResponse(
        eco_score=eco_score,
        wellness_score=wellness_score,
        co2_saved=co2_saved
    )


@router.get("/score", response_model=ScoreResponse)
async def get_my_scores(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get eco and wellness scores for the currently authenticated user.
    Convenience endpoint that doesn't require user_id parameter.

    Args:
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ScoreResponse with eco_score, wellness_score, and co2_saved

    Raises:
        HTTPException 404: If user not found
    """
    # Get user data
    user = await get_user_with_data(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Calculate scores
    eco_score = calculate_eco_score(user.lifestyle_data)
    wellness_score = calculate_wellness_score(user.health_data)
    co2_saved = calculate_carbon_savings(user.lifestyle_data)

    return ScoreResponse(
        eco_score=eco_score,
        wellness_score=wellness_score,
        co2_saved=co2_saved
    )


@router.get("/progress/{user_id}", response_model=AnalyticsResponse)
async def get_user_progress(
    user_id: int,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get progress tracking data for a specific user over time.
    Returns progress data points for the last N days (default 30).
    If insufficient activity data exists, returns mock data for demonstration.

    **Authorization**: User can only access their own progress unless admin.

    Args:
        user_id: The ID of the user
        days: Number of days to look back (1-365, default 30)
        db: Database session
        current_user: Currently authenticated user

    Returns:
        AnalyticsResponse with scores, CO2 saved, and progress data over time

    Raises:
        HTTPException 403: If user tries to access another user's progress
        HTTPException 404: If user not found
    """
    # Check if user is accessing their own progress
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own analytics"
        )

    # Get user data
    user = await get_user_with_data(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Calculate current scores
    eco_score = calculate_eco_score(user.lifestyle_data)
    wellness_score = calculate_wellness_score(user.health_data)
    co2_saved = calculate_carbon_savings(user.lifestyle_data)

    # Get progress data
    progress_data = await get_progress_data(db, user_id, days)

    return AnalyticsResponse(
        wellness_score=wellness_score,
        eco_score=eco_score,
        co2_saved=co2_saved,
        health_progress_over_time=progress_data
    )


@router.get("/progress", response_model=AnalyticsResponse)
async def get_my_progress(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get progress tracking data for the currently authenticated user over time.
    Convenience endpoint that doesn't require user_id parameter.
    Returns progress data points for the last N days (default 30).
    If insufficient activity data exists, returns mock data for demonstration.

    Args:
        days: Number of days to look back (1-365, default 30)
        db: Database session
        current_user: Currently authenticated user

    Returns:
        AnalyticsResponse with scores, CO2 saved, and progress data over time

    Raises:
        HTTPException 404: If user not found
    """
    # Get user data
    user = await get_user_with_data(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Calculate current scores
    eco_score = calculate_eco_score(user.lifestyle_data)
    wellness_score = calculate_wellness_score(user.health_data)
    co2_saved = calculate_carbon_savings(user.lifestyle_data)

    # Get progress data
    progress_data = await get_progress_data(db, current_user.id, days)

    return AnalyticsResponse(
        wellness_score=wellness_score,
        eco_score=eco_score,
        co2_saved=co2_saved,
        health_progress_over_time=progress_data
    )
