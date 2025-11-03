"""
ActivityData model for tracking user's daily activities and exercise.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class ActivityData(Base):
    """
    ActivityData model for storing user's physical activities and exercise data.
    """
    __tablename__ = "activity_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Activity fields
    steps = Column(Integer, nullable=True, default=0)  # Daily step count
    duration_minutes = Column(Float, nullable=True, default=0.0)  # Activity duration
    activity_type = Column(String(100), nullable=True)  # e.g., "running", "cycling", "yoga"
    calories_burned = Column(Float, nullable=True, default=0.0)  # Estimated calories
    date = Column(Date, nullable=False)  # Activity date

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<ActivityData(user_id={self.user_id}, type={self.activity_type}, date={self.date})>"
