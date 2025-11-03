"""
Onboarding routes for collecting lifestyle and health data.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.lifestyle import LifestyleData
from app.models.health import HealthData
from app.schemas.onboarding import (
    LifestyleCreate,
    LifestyleResponse,
    HealthCreate,
    HealthResponse,
    OnboardingSummary
)
from app.utils.dependencies import get_current_user
from app.services.scoring import calculate_combined_score
from app.services.meal_plan_generator import auto_generate_meal_plan_for_user

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post("/lifestyle", response_model=LifestyleResponse, status_code=status.HTTP_201_CREATED)
async def submit_lifestyle_data(
    lifestyle_data: LifestyleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit or update lifestyle data for the current user.

    Args:
        lifestyle_data: Lifestyle information
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created or updated lifestyle data
    """
    # Check if user already has lifestyle data
    result = await db.execute(
        select(LifestyleData).where(LifestyleData.user_id == current_user.id)
    )
    existing_lifestyle = result.scalar_one_or_none()

    if existing_lifestyle:
        # Update existing data
        for key, value in lifestyle_data.model_dump(exclude_unset=True).items():
            setattr(existing_lifestyle, key, value)

        await db.commit()
        await db.refresh(existing_lifestyle)
        return existing_lifestyle
    else:
        # Create new lifestyle data
        new_lifestyle = LifestyleData(
            user_id=current_user.id,
            **lifestyle_data.model_dump()
        )
        db.add(new_lifestyle)
        await db.commit()
        await db.refresh(new_lifestyle)
        return new_lifestyle


@router.post("/health", response_model=HealthResponse, status_code=status.HTTP_201_CREATED)
async def submit_health_data(
    health_data: HealthCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit or update health data for the current user.
    Automatically generates a 7-day meal plan after health data is saved.

    Args:
        health_data: Health information
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created or updated health data
    """
    # Check if user already has health data
    result = await db.execute(
        select(HealthData).where(HealthData.user_id == current_user.id)
    )
    existing_health = result.scalar_one_or_none()

    if existing_health:
        # Update existing data
        for key, value in health_data.model_dump(exclude_unset=True).items():
            setattr(existing_health, key, value)

        await db.commit()
        await db.refresh(existing_health)
        health_record = existing_health
    else:
        # Create new health data
        new_health = HealthData(
            user_id=current_user.id,
            **health_data.model_dump()
        )
        db.add(new_health)
        await db.commit()
        await db.refresh(new_health)
        health_record = new_health

    # Get user's diet type from lifestyle data (if exists)
    lifestyle_result = await db.execute(
        select(LifestyleData).where(LifestyleData.user_id == current_user.id)
    )
    lifestyle = lifestyle_result.scalar_one_or_none()
    diet_type = lifestyle.diet_type if lifestyle else None

    # Auto-generate 7-day meal plan (uses fresh DB session internally)
    try:
        await auto_generate_meal_plan_for_user(
            user_id=current_user.id,
            dietary_preference=health_data.dietary_preference,
            calorie_target=2000,  # Default calorie target
            diet_type=diet_type
        )
    except Exception as e:
        # Log the error but don't fail the health data submission
        print(f"Warning: Failed to auto-generate meal plan: {e}")
        import traceback
        traceback.print_exc()
        # Continue anyway - meal plan can be generated later

    return health_record


@router.get("/summary/{user_id}", response_model=OnboardingSummary)
async def get_onboarding_summary(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get combined onboarding summary with scores for a specific user.

    Args:
        user_id: User ID to get summary for
        current_user: Current authenticated user
        db: Database session

    Returns:
        Onboarding summary with lifestyle, health data, and computed scores

    Raises:
        HTTPException: If user is not authorized to view this data
    """
    # Only allow users to view their own data (for now)
    # In the future, you might allow admins to view any user's data
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's data"
        )

    # Fetch lifestyle data
    lifestyle_result = await db.execute(
        select(LifestyleData).where(LifestyleData.user_id == user_id)
    )
    lifestyle = lifestyle_result.scalar_one_or_none()

    # Fetch health data
    health_result = await db.execute(
        select(HealthData).where(HealthData.user_id == user_id)
    )
    health = health_result.scalar_one_or_none()

    # Calculate scores
    eco_score, wellness_score = calculate_combined_score(lifestyle, health)

    return OnboardingSummary(
        user_id=user_id,
        lifestyle=lifestyle,
        health=health,
        eco_score=eco_score,
        wellness_score=wellness_score
    )


@router.get("/summary", response_model=OnboardingSummary)
async def get_my_onboarding_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get combined onboarding summary with scores for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Onboarding summary with lifestyle, health data, and computed scores
    """
    # Fetch lifestyle data
    lifestyle_result = await db.execute(
        select(LifestyleData).where(LifestyleData.user_id == current_user.id)
    )
    lifestyle = lifestyle_result.scalar_one_or_none()

    # Fetch health data
    health_result = await db.execute(
        select(HealthData).where(HealthData.user_id == current_user.id)
    )
    health = health_result.scalar_one_or_none()

    # Calculate scores
    eco_score, wellness_score = calculate_combined_score(lifestyle, health)

    return OnboardingSummary(
        user_id=current_user.id,
        lifestyle=lifestyle,
        health=health,
        eco_score=eco_score,
        wellness_score=wellness_score
    )
