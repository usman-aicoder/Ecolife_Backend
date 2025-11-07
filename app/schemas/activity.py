"""
Pydantic schemas for Activity Data.
"""

from pydantic import BaseModel, Field
from datetime import date as date_type, datetime
from typing import Optional


class ActivityDataBase(BaseModel):
    """Base schema for activity data."""
    steps: Optional[int] = Field(None, ge=0, description="Daily step count")
    duration_minutes: Optional[float] = Field(None, ge=0, description="Activity duration in minutes")
    activity_type: Optional[str] = Field(None, max_length=100, description="Type of activity")
    calories_burned: Optional[float] = Field(None, ge=0, description="Calories burned")
    date: date_type = Field(..., description="Date of activity")


class ActivityDataCreate(ActivityDataBase):
    """Schema for creating activity data."""
    pass


class ActivityDataUpdate(BaseModel):
    """Schema for updating activity data."""
    steps: Optional[int] = Field(None, ge=0)
    duration_minutes: Optional[float] = Field(None, ge=0)
    activity_type: Optional[str] = Field(None, max_length=100)
    calories_burned: Optional[float] = Field(None, ge=0)


class ActivityDataResponse(ActivityDataBase):
    """Schema for activity data response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddStepsRequest(BaseModel):
    """Schema for adding daily steps or activity duration."""
    date: date_type = Field(..., description="Date of the activity")
    steps: int = Field(..., ge=0, le=100000, description="Number of steps")
    activity_type: str = Field(default="walking", description="Type of activity")
    duration_minutes: Optional[float] = Field(None, ge=0, description="Duration in minutes for time-based activities")


class AddStepsResponse(BaseModel):
    """Schema for add steps response."""
    success: bool
    message: str
    activity: ActivityDataResponse
