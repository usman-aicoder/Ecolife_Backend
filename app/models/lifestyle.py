"""
LifestyleData model for storing user's eco-friendly lifestyle choices.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class LifestyleData(Base):
    """
    LifestyleData model for storing user's lifestyle and environmental choices.
    """
    __tablename__ = "lifestyle_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Lifestyle fields
    transportation_mode = Column(String(50), nullable=True)  # e.g., "public_transport", "bike", "car"
    diet_type = Column(String(50), nullable=True)  # e.g., "vegan", "vegetarian", "omnivore"
    shopping_pattern = Column(String(50), nullable=True)  # e.g., "local", "online", "mixed"
    recycling_habits = Column(String(50), nullable=True)  # e.g., "always", "sometimes", "never"
    reusable_items = Column(Boolean, default=False)  # Uses reusable bags, bottles, etc.
    energy_source = Column(String(50), nullable=True)  # e.g., "renewable", "mixed", "non_renewable"
    travel_frequency = Column(String(50), nullable=True)  # e.g., "rarely", "monthly", "weekly"
    paper_preference = Column(String(50), nullable=True)  # e.g., "digital", "paper", "both"

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    user = relationship("User", back_populates="lifestyle_data")

    def __repr__(self):
        return f"<LifestyleData(user_id={self.user_id}, diet={self.diet_type})>"
