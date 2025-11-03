"""
Pydantic schemas for dashboard endpoints.
"""

from typing import Optional
from datetime import datetime
import datetime as dt
from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    """Schema for creating an activity entry."""
    steps: Optional[int] = Field(default=0, ge=0, description="Daily step count")
    duration_minutes: Optional[float] = Field(default=0.0, ge=0, description="Activity duration in minutes")
    activity_type: Optional[str] = Field(default=None, max_length=100, description="Type of activity (e.g., running, cycling)")
    calories_burned: Optional[float] = Field(default=0.0, ge=0, description="Estimated calories burned")
    date: dt.date = Field(..., description="Date of the activity")


class ActivityResponse(BaseModel):
    """Schema for activity response."""
    id: int
    user_id: int
    steps: Optional[int]
    duration_minutes: Optional[float]
    activity_type: Optional[str]
    calories_burned: Optional[float]
    date: dt.date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    """
    Combined dashboard response with eco and wellness metrics.
    """
    eco_score: float = Field(..., ge=0, le=100, description="Environmental impact score (0-100)")
    wellness_score: float = Field(..., ge=0, le=100, description="Health and wellness score (0-100)")
    total_carbon_savings: float = Field(..., ge=0, description="Total CO2 saved in kg")
    total_calories_burned: float = Field(..., ge=0, description="Total calories burned from activities")
    streak_days: int = Field(..., ge=0, description="Number of consecutive days with activity")
    last_updated: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        from_attributes = True
