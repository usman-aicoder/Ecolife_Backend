"""
MealConsumption model for tracking whether users have consumed their meals.
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class MealConsumption(Base):
    """
    MealConsumption model for tracking user's meal consumption status.
    Tracks whether breakfast, lunch, and dinner have been consumed each day.
    """
    __tablename__ = "meal_consumptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Optional reference to meal plan (if user is following a plan)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id", ondelete="SET NULL"), nullable=True)

    # Meal tracking fields
    date = Column(Date, nullable=False, index=True)  # Date of the meal
    meal_type = Column(String(20), nullable=False)  # 'breakfast', 'lunch', or 'dinner'
    consumed = Column(Boolean, default=False, nullable=False)  # Whether meal was consumed
    consumed_at = Column(DateTime(timezone=True), nullable=True)  # When it was marked as consumed

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="meal_consumptions")
    meal_plan = relationship("MealPlan", back_populates="meal_consumptions")

    def __repr__(self):
        return f"<MealConsumption(user_id={self.user_id}, date={self.date}, type={self.meal_type}, consumed={self.consumed})>"
