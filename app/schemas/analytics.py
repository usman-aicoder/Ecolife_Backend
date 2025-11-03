"""
Pydantic schemas for analytics endpoints.
"""

from typing import List, Optional
from datetime import datetime
import datetime as dt
from pydantic import BaseModel, Field


class ProgressDataPoint(BaseModel):
    """Single data point for progress tracking over time."""
    date: dt.date = Field(..., description="Date of the data point")
    eco_score: float = Field(..., ge=0, le=100, description="Eco score on this date")
    wellness_score: float = Field(..., ge=0, le=100, description="Wellness score on this date")
    steps: Optional[int] = Field(default=0, description="Steps count on this date")
    calories_burned: Optional[float] = Field(default=0.0, description="Calories burned on this date")


class AnalyticsResponse(BaseModel):
    """
    Analytics response with scores and progress tracking.
    """
    wellness_score: float = Field(..., ge=0, le=100, description="Current wellness score (0-100)")
    eco_score: float = Field(..., ge=0, le=100, description="Current eco score (0-100)")
    co2_saved: float = Field(..., ge=0, description="Total CO2 saved in kg")
    health_progress_over_time: List[ProgressDataPoint] = Field(
        default_factory=list,
        description="Progress data over time (last 30 days or mock data)"
    )

    class Config:
        from_attributes = True


class ScoreResponse(BaseModel):
    """Simple response for score endpoints."""
    eco_score: float = Field(..., ge=0, le=100, description="Environmental impact score")
    wellness_score: float = Field(..., ge=0, le=100, description="Health and wellness score")
    co2_saved: float = Field(..., ge=0, description="Total CO2 saved in kg")

    class Config:
        from_attributes = True
