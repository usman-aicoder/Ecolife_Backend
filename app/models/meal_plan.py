"""
MealPlan model for storing user meal plans.
Each meal plan contains 7 days of meals (breakfast, lunch, dinner).
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Task tracking
    task_id = Column(String(255), unique=True, index=True, nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed

    # Meal plan data (stored as JSON)
    meals = Column(JSON, nullable=True)  # 7-day meal plan structure

    # Generation parameters
    dietary_preference = Column(String(100), nullable=True)
    calorie_target = Column(Integer, nullable=True)

    # Editing fields
    customized = Column(Boolean, default=False, nullable=False)  # User has edited this plan
    original_meals = Column(JSON, nullable=True)  # Backup of original meals before edits
    edited_at = Column(DateTime(timezone=True), nullable=True)  # Last edit timestamp

    # Error handling
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="meal_plans")
    meal_consumptions = relationship("MealConsumption", back_populates="meal_plan", cascade="all, delete-orphan")
