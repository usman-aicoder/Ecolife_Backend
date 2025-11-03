"""
HealthData model for storing user's health and wellness information.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class HealthData(Base):
    """
    HealthData model for storing user's health metrics and wellness goals.
    """
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Basic Health fields
    gender = Column(String(20), nullable=True)  # "male", "female", "other"
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    activity_level = Column(String(50), nullable=True)  # e.g., "sedentary", "moderate", "active", "very_active"
    wellness_goal = Column(String(100), nullable=True)  # e.g., "weight_loss", "muscle_gain", "maintain"
    dietary_preference = Column(String(50), nullable=True)  # e.g., "none", "gluten_free", "lactose_free"

    # Medical Information (arrays stored as JSON)
    allergies = Column(JSON, nullable=True, default=list)  # e.g., ["dairy", "nuts", "shellfish"]
    medical_conditions = Column(JSON, nullable=True, default=list)  # e.g., ["diabetes", "hypertension"]

    # Meal Planning Preferences
    meal_frequency = Column(String(50), nullable=True)  # e.g., "2-meals", "3-meals", "4-5-meals"
    cooking_skill = Column(String(50), nullable=True)  # e.g., "beginner", "intermediate", "advanced"
    time_available = Column(String(50), nullable=True)  # e.g., "quick", "moderate", "flexible"
    budget = Column(String(50), nullable=True)  # e.g., "low", "medium", "high"

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    user = relationship("User", back_populates="health_data")

    def __repr__(self):
        return f"<HealthData(user_id={self.user_id}, age={self.age}, gender={self.gender}, activity={self.activity_level})>"
