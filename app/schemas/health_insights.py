"""
Pydantic schemas for Health Insights API
"""

from pydantic import BaseModel
from typing import List, Optional


class ActivityInsight(BaseModel):
    """Today's activity insights"""
    steps: int
    steps_goal: int
    percentage: int
    calories_burned: int
    activity_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    goal_achieved: bool
    message: str


class MealInsight(BaseModel):
    """Today's meal insights"""
    meals_consumed: int
    total_meals: int
    percentage: int
    breakfast: bool
    lunch: bool
    dinner: bool
    message: str


class CalorieInsight(BaseModel):
    """Today's calorie insights"""
    consumed: int
    target: int
    difference: int
    percentage: int
    status: str
    message: str


class DailyInsightsResponse(BaseModel):
    """Daily health insights response"""
    date: str
    activity: ActivityInsight
    meals: MealInsight
    calories: CalorieInsight
    recommendations: List[str]


class ActivitySummary(BaseModel):
    """Weekly activity summary"""
    total_steps: int
    avg_steps: int
    total_calories: int
    days_active: int
    goal_days: int
    message: str


class MealSummary(BaseModel):
    """Weekly meal summary"""
    meals_logged: int
    total_possible: int
    percentage: int
    breakfast_count: int
    lunch_count: int
    dinner_count: int
    message: str


class WeeklyInsightsResponse(BaseModel):
    """Weekly health insights response"""
    week_start: str
    week_end: str
    activity_summary: ActivitySummary
    meal_summary: MealSummary
    streak: int
    consistency_score: int
