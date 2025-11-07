"""
Health Insights API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.schemas.health_insights import (
    DailyInsightsResponse,
    WeeklyInsightsResponse
)
from app.services.health_insights_service import (
    get_daily_insights,
    get_weekly_insights
)


router = APIRouter(prefix="/health-insights", tags=["Health Insights"])


@router.get("/daily", response_model=DailyInsightsResponse)
async def get_daily_health_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get today's health insights including:
    - Activity progress (steps, calories burned)
    - Meal consumption status
    - Calorie tracking vs target
    - Personalized recommendations
    """
    try:
        insights = await get_daily_insights(db, current_user.id)
        return insights
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get daily insights: {str(e)}"
        )


@router.get("/weekly", response_model=WeeklyInsightsResponse)
async def get_weekly_health_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get this week's health insights including:
    - Weekly activity summary
    - Weekly meal tracking summary
    - Activity streak
    - Consistency score
    """
    try:
        insights = await get_weekly_insights(db, current_user.id)
        return insights
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get weekly insights: {str(e)}"
        )
