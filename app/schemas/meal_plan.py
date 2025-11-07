"""
Pydantic schemas for Meal Plan API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Individual Meal Schema
class MealDetail(BaseModel):
    """Individual meal details"""
    name: str
    description: str
    calories: int
    protein: int  # grams
    carbs: int  # grams
    fats: int  # grams
    carbon_footprint: float  # kg CO2
    ingredients: List[str]
    cooking_time: int  # minutes
    recipe_url: Optional[str] = None


# Day's Meals Schema
class DayMeals(BaseModel):
    """Meals for a single day"""
    day: int  # 1-7
    date: str  # YYYY-MM-DD
    breakfast: MealDetail
    lunch: MealDetail
    dinner: MealDetail
    total_calories: int
    total_carbon: float


# Request Schemas
class MealPlanGenerateRequest(BaseModel):
    """Request to generate a new meal plan"""
    dietary_preference: Optional[str] = Field(
        default="balanced",
        description="Diet type: vegan, vegetarian, pescatarian, flexitarian, omnivore, balanced"
    )
    calorie_target: Optional[int] = Field(
        default=2000,
        ge=1200,
        le=3500,
        description="Daily calorie target"
    )
    exclude_ingredients: Optional[List[str]] = Field(
        default=[],
        description="Ingredients to exclude from meals"
    )


# Response Schemas
class MealPlanStatusResponse(BaseModel):
    """Response for meal plan status check"""
    id: int
    task_id: str
    status: str  # pending, processing, completed, failed
    message: str
    progress: Optional[int] = None  # 0-100


class MealPlanResponse(BaseModel):
    """Complete meal plan response"""
    id: int
    user_id: int
    status: str
    task_id: Optional[str] = None
    meals: Optional[List[DayMeals]] = None
    dietary_preference: Optional[str] = None
    calorie_target: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    # Summary statistics
    total_calories_week: Optional[int] = None
    total_carbon_week: Optional[float] = None
    avg_calories_day: Optional[int] = None

    class Config:
        from_attributes = True


class MealPlanListResponse(BaseModel):
    """List of meal plans for a user"""
    meal_plans: List[MealPlanResponse]
    total: int


# Meal Editing Schemas
class UpdateMealPlanRequest(BaseModel):
    """Request to update an existing meal plan"""
    meals: List[DayMeals]


class SwapMealRequest(BaseModel):
    """Request to swap a single meal in the plan"""
    day_index: int = Field(ge=0, le=6, description="Day index (0-6)")
    meal_type: str = Field(description="Meal type: breakfast, lunch, or dinner")
    new_meal: MealDetail


class MealAlternativeResponse(BaseModel):
    """Response with alternative meals for swapping"""
    alternatives: List[MealDetail]
    meal_type: str
    count: int
