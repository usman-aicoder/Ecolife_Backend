"""
Pydantic schemas for onboarding data (lifestyle and health).
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ========== Lifestyle Schemas ==========

class LifestyleBase(BaseModel):
    """Base lifestyle schema with common fields."""
    transportation_mode: Optional[str] = Field(None, max_length=50)
    diet_type: Optional[str] = Field(None, max_length=50)
    shopping_pattern: Optional[str] = Field(None, max_length=50)
    recycling_habits: Optional[str] = Field(None, max_length=50)
    reusable_items: Optional[bool] = False
    energy_source: Optional[str] = Field(None, max_length=50)
    travel_frequency: Optional[str] = Field(None, max_length=50)
    paper_preference: Optional[str] = Field(None, max_length=50)


class LifestyleCreate(LifestyleBase):
    """Schema for creating lifestyle data."""
    pass


class LifestyleUpdate(LifestyleBase):
    """Schema for updating lifestyle data."""
    pass


class LifestyleResponse(LifestyleBase):
    """Schema for returning lifestyle data."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Health Schemas ==========

class HealthBase(BaseModel):
    """Base health schema with common fields."""
    # Basic Health fields
    gender: Optional[str] = Field(None, max_length=20)
    age: Optional[int] = Field(None, ge=0, le=150)
    height: Optional[float] = Field(None, ge=0, le=300)  # in cm
    weight: Optional[float] = Field(None, ge=0, le=500)  # in kg
    activity_level: Optional[str] = Field(None, max_length=50)
    wellness_goal: Optional[str] = Field(None, max_length=100)
    dietary_preference: Optional[str] = Field(None, max_length=50)

    # Medical Information
    allergies: Optional[List[str]] = Field(default_factory=list)
    medical_conditions: Optional[List[str]] = Field(default_factory=list)

    # Meal Planning Preferences
    meal_frequency: Optional[str] = Field(None, max_length=50)
    cooking_skill: Optional[str] = Field(None, max_length=50)
    time_available: Optional[str] = Field(None, max_length=50)
    budget: Optional[str] = Field(None, max_length=50)


class HealthCreate(HealthBase):
    """Schema for creating health data."""
    pass


class HealthUpdate(HealthBase):
    """Schema for updating health data."""
    pass


class HealthResponse(HealthBase):
    """Schema for returning health data."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Combined Onboarding Summary ==========

class OnboardingSummary(BaseModel):
    """Combined onboarding summary with scores."""
    user_id: int
    lifestyle: Optional[LifestyleResponse] = None
    health: Optional[HealthResponse] = None
    eco_score: float
    wellness_score: float

    class Config:
        from_attributes = True
