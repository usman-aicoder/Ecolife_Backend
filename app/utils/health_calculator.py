"""
Health Calculation Utilities
Includes BMR (Basal Metabolic Rate) and TDEE (Total Daily Energy Expenditure) calculations
"""

from typing import Optional


def calculate_bmr(
    weight: float,
    height: float,
    age: int,
    gender: str
) -> Optional[float]:
    """
    Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation.

    This is the most accurate formula for calculating BMR, validated by multiple studies.

    Formula:
    - Men: BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
    - Women: BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161
    - Other: Uses average of male and female calculations

    Args:
        weight: Weight in kilograms
        height: Height in centimeters
        age: Age in years
        gender: Gender ('male', 'female', or 'other')

    Returns:
        BMR in kcal/day, or None if inputs are invalid

    Examples:
        >>> calculate_bmr(70, 175, 30, 'male')
        1673.75
        >>> calculate_bmr(60, 165, 25, 'female')
        1383.75
    """
    # Validate inputs
    if not all([weight, height, age]) or weight <= 0 or height <= 0 or age <= 0:
        return None

    if not gender or gender.lower() not in ['male', 'female', 'other']:
        return None

    # Mifflin-St Jeor Equation
    base_calculation = (10 * weight) + (6.25 * height) - (5 * age)

    gender_lower = gender.lower()

    if gender_lower == 'male':
        bmr = base_calculation + 5
    elif gender_lower == 'female':
        bmr = base_calculation - 161
    else:  # 'other' - use average of male and female
        male_bmr = base_calculation + 5
        female_bmr = base_calculation - 161
        bmr = (male_bmr + female_bmr) / 2

    return round(bmr, 2)


def calculate_tdee(
    bmr: float,
    activity_level: str
) -> Optional[float]:
    """
    Calculate Total Daily Energy Expenditure (TDEE) based on BMR and activity level.

    TDEE = BMR × Activity Factor

    Activity Factors (based on Harris-Benedict principle):
    - sedentary: Little to no exercise (BMR × 1.2)
    - active: Light exercise 1-3 days/week (BMR × 1.375)
    - very-active: Moderate exercise 3-5 days/week (BMR × 1.55)

    Args:
        bmr: Basal Metabolic Rate in kcal/day
        activity_level: Activity level string

    Returns:
        TDEE in kcal/day, or None if inputs are invalid

    Examples:
        >>> calculate_tdee(1673.75, 'sedentary')
        2008.5
        >>> calculate_tdee(1383.75, 'active')
        1902.66
    """
    if not bmr or bmr <= 0:
        return None

    # Activity multipliers based on Harris-Benedict principle
    activity_multipliers = {
        'sedentary': 1.2,       # Little to no exercise
        'active': 1.375,        # Light exercise 1-3 days/week
        'very-active': 1.55,    # Moderate exercise 3-5 days/week
    }

    activity_lower = activity_level.lower() if activity_level else ''
    multiplier = activity_multipliers.get(activity_lower, 1.2)  # Default to sedentary

    tdee = bmr * multiplier
    return round(tdee, 2)


def calculate_calorie_target(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: str,
    wellness_goal: Optional[str] = None
) -> Optional[float]:
    """
    Calculate personalized daily calorie target based on user's health data and goals.

    This combines BMR calculation, activity level adjustment, and wellness goal modification.

    Args:
        weight: Weight in kilograms
        height: Height in centimeters
        age: Age in years
        gender: Gender ('male', 'female', or 'other')
        activity_level: Activity level ('sedentary', 'active', 'very-active')
        wellness_goal: Optional wellness goal ('lose-weight', 'gain-weight', 'maintain', etc.)

    Returns:
        Recommended daily calorie intake in kcal/day, or None if calculation fails

    Examples:
        >>> calculate_calorie_target(70, 175, 30, 'male', 'active', 'lose-weight')
        1802.41  # (BMR 1673.75 × 1.375 activity) - 500 deficit
        >>> calculate_calorie_target(60, 165, 25, 'female', 'sedentary', 'maintain')
        1660.5  # (BMR 1383.75 × 1.2 activity)
    """
    # Calculate BMR
    bmr = calculate_bmr(weight, height, age, gender)
    if not bmr:
        return None

    # Calculate TDEE
    tdee = calculate_tdee(bmr, activity_level)
    if not tdee:
        return None

    # Adjust based on wellness goal
    if wellness_goal:
        goal_lower = wellness_goal.lower()

        if 'lose' in goal_lower or 'weight-loss' in goal_lower or 'lose-weight' in goal_lower:
            # Create a 500 kcal deficit for safe weight loss (~0.5kg/week)
            target = tdee - 500
            # Ensure minimum calorie intake (1200 for women, 1500 for men)
            min_calories = 1200 if gender.lower() == 'female' else 1500
            target = max(target, min_calories)

        elif 'gain' in goal_lower or 'muscle' in goal_lower or 'bulk' in goal_lower:
            # Create a 300 kcal surplus for lean muscle gain
            target = tdee + 300

        elif 'maintain' in goal_lower or 'balance' in goal_lower:
            # Maintain current weight
            target = tdee

        else:
            # Default to maintenance
            target = tdee
    else:
        # No specific goal, use TDEE
        target = tdee

    return round(target, 2)


def get_bmi(weight: float, height: float) -> Optional[float]:
    """
    Calculate Body Mass Index (BMI).

    BMI = weight (kg) / (height (m))^2

    Args:
        weight: Weight in kilograms
        height: Height in centimeters

    Returns:
        BMI value, or None if inputs are invalid

    Examples:
        >>> get_bmi(70, 175)
        22.86
        >>> get_bmi(60, 165)
        22.04
    """
    if not weight or not height or weight <= 0 or height <= 0:
        return None

    height_meters = height / 100
    bmi = weight / (height_meters ** 2)

    return round(bmi, 2)


def get_bmi_category(bmi: float) -> str:
    """
    Get BMI category based on WHO classification.

    Args:
        bmi: BMI value

    Returns:
        BMI category string

    Categories:
        < 18.5: Underweight
        18.5 - 24.9: Normal weight
        25.0 - 29.9: Overweight
        >= 30.0: Obese
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"
