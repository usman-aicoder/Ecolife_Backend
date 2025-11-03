"""
Pydantic schemas for meal consumption tracking.
"""

from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional, List


class MealConsumptionBase(BaseModel):
    """Base meal consumption schema with common fields."""
    meal_plan_id: Optional[int] = None
    date: date
    meal_type: str = Field(..., description="Type of meal: 'breakfast', 'lunch', or 'dinner'")
    consumed: bool = False

    @validator('meal_type')
    def validate_meal_type(cls, v):
        """Validate that meal_type is one of the allowed values."""
        allowed_types = ['breakfast', 'lunch', 'dinner']
        if v.lower() not in allowed_types:
            raise ValueError(f"meal_type must be one of {allowed_types}")
        return v.lower()


class MealConsumptionCreate(BaseModel):
    """Schema for creating meal consumption record."""
    meal_plan_id: Optional[int] = None
    date: date
    meal_type: str = Field(..., description="Type of meal: 'breakfast', 'lunch', or 'dinner'")

    @validator('meal_type')
    def validate_meal_type(cls, v):
        """Validate that meal_type is one of the allowed values."""
        allowed_types = ['breakfast', 'lunch', 'dinner']
        if v.lower() not in allowed_types:
            raise ValueError(f"meal_type must be one of {allowed_types}")
        return v.lower()


class MealConsumptionUpdate(BaseModel):
    """Schema for updating meal consumption status."""
    consumed: bool


class MealConsumptionResponse(BaseModel):
    """Schema for returning meal consumption data."""
    id: int
    user_id: int
    meal_plan_id: Optional[int] = None
    date: date
    meal_type: str
    consumed: bool
    consumed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyMealStatus(BaseModel):
    """Schema for daily meal consumption status."""
    date: date
    breakfast: bool = False
    lunch: bool = False
    dinner: bool = False
    total_consumed: int = 0
    total_meals: int = 3


class MealConsumptionHistory(BaseModel):
    """Schema for meal consumption history."""
    date: date
    meals: List[MealConsumptionResponse]
    total_consumed: int
    total_meals: int


class MarkMealConsumedRequest(BaseModel):
    """Request schema for marking a meal as consumed."""
    date: date
    meal_type: str = Field(..., description="Type of meal: 'breakfast', 'lunch', or 'dinner'")
    meal_plan_id: Optional[int] = None

    @validator('meal_type')
    def validate_meal_type(cls, v):
        """Validate that meal_type is one of the allowed values."""
        allowed_types = ['breakfast', 'lunch', 'dinner']
        if v.lower() not in allowed_types:
            raise ValueError(f"meal_type must be one of {allowed_types}")
        return v.lower()


class MarkMealConsumedResponse(BaseModel):
    """Response schema for marking a meal as consumed."""
    success: bool
    message: str
    meal_consumption: MealConsumptionResponse
