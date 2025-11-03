"""
Scoring service for calculating eco and wellness scores based on user data.
"""

from typing import Optional
from app.models.lifestyle import LifestyleData
from app.models.health import HealthData


def calculate_eco_score(lifestyle: Optional[LifestyleData]) -> float:
    """
    Calculate eco score based on lifestyle choices.
    Score range: 0-100 (higher is better for environment)

    Args:
        lifestyle: LifestyleData object

    Returns:
        Eco score (0-100)
    """
    if not lifestyle:
        return 50.0  # Default neutral score

    score = 50.0  # Start with neutral

    # Transportation mode scoring
    transport_scores = {
        "bike": 15,
        "walk": 15,
        "public_transport": 12,
        "electric_car": 8,
        "carpool": 5,
        "car": -10,
        "motorcycle": -5
    }
    if lifestyle.transportation_mode:
        score += transport_scores.get(lifestyle.transportation_mode.lower(), 0)

    # Diet type scoring
    diet_scores = {
        "vegan": 15,
        "vegetarian": 10,
        "pescatarian": 5,
        "flexitarian": 3,
        "omnivore": -5
    }
    if lifestyle.diet_type:
        score += diet_scores.get(lifestyle.diet_type.lower(), 0)

    # Recycling habits
    recycling_scores = {
        "always": 10,
        "often": 7,
        "sometimes": 3,
        "rarely": -3,
        "never": -8
    }
    if lifestyle.recycling_habits:
        score += recycling_scores.get(lifestyle.recycling_habits.lower(), 0)

    # Reusable items
    if lifestyle.reusable_items:
        score += 8

    # Energy source
    energy_scores = {
        "renewable": 10,
        "mostly_renewable": 7,
        "mixed": 3,
        "mostly_non_renewable": -3,
        "non_renewable": -8
    }
    if lifestyle.energy_source:
        score += energy_scores.get(lifestyle.energy_source.lower(), 0)

    # Travel frequency
    travel_scores = {
        "rarely": 8,
        "occasionally": 3,
        "monthly": -2,
        "weekly": -8,
        "daily": -12
    }
    if lifestyle.travel_frequency:
        score += travel_scores.get(lifestyle.travel_frequency.lower(), 0)

    # Paper preference
    paper_scores = {
        "digital": 5,
        "mostly_digital": 3,
        "both": 0,
        "mostly_paper": -3,
        "paper": -5
    }
    if lifestyle.paper_preference:
        score += paper_scores.get(lifestyle.paper_preference.lower(), 0)

    # Clamp score between 0 and 100
    return max(0.0, min(100.0, score))


def calculate_wellness_score(health: Optional[HealthData]) -> float:
    """
    Calculate wellness score based on health data and goals.
    Score range: 0-100 (higher is better for health)

    Args:
        health: HealthData object

    Returns:
        Wellness score (0-100)
    """
    if not health:
        return 50.0  # Default neutral score

    score = 50.0  # Start with neutral

    # Activity level scoring
    activity_scores = {
        "very_active": 20,
        "active": 15,
        "moderately_active": 10,
        "lightly_active": 5,
        "sedentary": -10
    }
    if health.activity_level:
        score += activity_scores.get(health.activity_level.lower(), 0)

    # BMI calculation and scoring (if height and weight provided)
    if health.height and health.weight and health.height > 0:
        height_m = health.height / 100  # convert cm to m
        bmi = health.weight / (height_m ** 2)

        if 18.5 <= bmi <= 24.9:
            score += 15  # Healthy BMI
        elif 25 <= bmi <= 29.9:
            score += 5  # Overweight
        elif 17 <= bmi < 18.5:
            score += 5  # Slightly underweight
        else:
            score -= 5  # Outside healthy range

    # Age consideration (general health awareness)
    if health.age:
        if 18 <= health.age <= 65:
            score += 5  # Active age range
        elif health.age > 65:
            score += 10  # Extra points for maintaining health in older age

    # Wellness goal (shows motivation)
    goal_scores = {
        "weight_loss": 5,
        "muscle_gain": 5,
        "maintain_health": 8,
        "improve_fitness": 7,
        "stress_reduction": 5,
        "better_sleep": 5
    }
    if health.wellness_goal:
        score += goal_scores.get(health.wellness_goal.lower(), 3)

    # Dietary preference (health consciousness)
    if health.dietary_preference and health.dietary_preference.lower() != "none":
        score += 3  # Being mindful of dietary needs

    # Clamp score between 0 and 100
    return max(0.0, min(100.0, score))


def calculate_combined_score(
    lifestyle: Optional[LifestyleData],
    health: Optional[HealthData]
) -> tuple[float, float]:
    """
    Calculate both eco and wellness scores.

    Args:
        lifestyle: LifestyleData object
        health: HealthData object

    Returns:
        Tuple of (eco_score, wellness_score)
    """
    eco_score = calculate_eco_score(lifestyle)
    wellness_score = calculate_wellness_score(health)

    return eco_score, wellness_score
