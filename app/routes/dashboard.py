"""
Dashboard routes for retrieving user dashboard metrics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.analytics_service import get_dashboard_data
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{user_id}", response_model=DashboardResponse)
async def get_user_dashboard(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard summary for a specific user.
    Returns eco score, wellness score, CO2 savings, calories burned, and activity streak.

    **Authorization**: User can only access their own dashboard unless admin.

    Args:
        user_id: The ID of the user
        db: Database session
        current_user: Currently authenticated user

    Returns:
        DashboardResponse with all metrics

    Raises:
        HTTPException 403: If user tries to access another user's dashboard
    """
    # Check if user is accessing their own dashboard
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own dashboard"
        )

    # Get dashboard data
    eco_score, wellness_score, co2_saved, calories_burned, streak_days, last_updated = (
        await get_dashboard_data(db, user_id)
    )

    return DashboardResponse(
        eco_score=eco_score,
        wellness_score=wellness_score,
        total_carbon_savings=co2_saved,
        total_calories_burned=calories_burned,
        streak_days=streak_days,
        last_updated=last_updated
    )


@router.get("", response_model=DashboardResponse)
async def get_my_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard summary for the currently authenticated user.
    Convenience endpoint that doesn't require user_id parameter.

    Args:
        db: Database session
        current_user: Currently authenticated user

    Returns:
        DashboardResponse with all metrics
    """
    # Get dashboard data for current user
    eco_score, wellness_score, co2_saved, calories_burned, streak_days, last_updated = (
        await get_dashboard_data(db, current_user.id)
    )

    return DashboardResponse(
        eco_score=eco_score,
        wellness_score=wellness_score,
        total_carbon_savings=co2_saved,
        total_calories_burned=calories_burned,
        streak_days=streak_days,
        last_updated=last_updated
    )
