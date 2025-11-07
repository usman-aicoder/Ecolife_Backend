"""
Meal Plan Generation Service
Generates personalized 7-day meal plans based on dietary preferences.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


# Meal database by dietary preference
MEAL_DATABASE = {
    "vegan": {
        "breakfast": [
            {
                "name": "Overnight Oats with Berries",
                "description": "Creamy oats with fresh berries and chia seeds",
                "calories": 350,
                "protein": 12,
                "carbs": 58,
                "fats": 8,
                "carbon_footprint": 0.3,
                "ingredients": ["oats", "almond milk", "berries", "chia seeds", "maple syrup"],
                "cooking_time": 5
            },
            {
                "name": "Tofu Scramble with Spinach",
                "description": "Scrambled tofu with spinach and nutritional yeast",
                "calories": 320,
                "protein": 18,
                "carbs": 15,
                "fats": 20,
                "carbon_footprint": 0.4,
                "ingredients": ["tofu", "spinach", "nutritional yeast", "turmeric", "olive oil"],
                "cooking_time": 15
            },
            {
                "name": "Avocado Toast with Tomatoes",
                "description": "Whole grain toast with mashed avocado and cherry tomatoes",
                "calories": 380,
                "protein": 10,
                "carbs": 42,
                "fats": 18,
                "carbon_footprint": 0.5,
                "ingredients": ["whole grain bread", "avocado", "cherry tomatoes", "lemon", "red pepper flakes"],
                "cooking_time": 10
            }
        ],
        "lunch": [
            {
                "name": "Quinoa Buddha Bowl",
                "description": "Quinoa with roasted vegetables and tahini dressing",
                "calories": 480,
                "protein": 16,
                "carbs": 68,
                "fats": 16,
                "carbon_footprint": 0.6,
                "ingredients": ["quinoa", "chickpeas", "sweet potato", "kale", "tahini", "lemon"],
                "cooking_time": 30
            },
            {
                "name": "Lentil Soup with Vegetables",
                "description": "Hearty lentil soup with seasonal vegetables",
                "calories": 420,
                "protein": 20,
                "carbs": 62,
                "fats": 8,
                "carbon_footprint": 0.5,
                "ingredients": ["red lentils", "carrots", "celery", "tomatoes", "vegetable broth"],
                "cooking_time": 35
            },
            {
                "name": "Falafel Wrap with Hummus",
                "description": "Crispy falafel in whole wheat wrap with hummus",
                "calories": 520,
                "protein": 18,
                "carbs": 72,
                "fats": 16,
                "carbon_footprint": 0.7,
                "ingredients": ["chickpeas", "whole wheat wrap", "lettuce", "tomato", "hummus", "cucumber"],
                "cooking_time": 25
            }
        ],
        "dinner": [
            {
                "name": "Vegetable Stir-Fry with Tofu",
                "description": "Colorful vegetables stir-fried with crispy tofu",
                "calories": 480,
                "protein": 24,
                "carbs": 48,
                "fats": 20,
                "carbon_footprint": 0.6,
                "ingredients": ["tofu", "broccoli", "bell peppers", "brown rice", "soy sauce", "ginger"],
                "cooking_time": 25
            },
            {
                "name": "Chickpea Curry with Rice",
                "description": "Spiced chickpea curry served over basmati rice",
                "calories": 520,
                "protein": 18,
                "carbs": 82,
                "fats": 12,
                "carbon_footprint": 0.5,
                "ingredients": ["chickpeas", "coconut milk", "tomatoes", "basmati rice", "curry spices"],
                "cooking_time": 35
            },
            {
                "name": "Mushroom and Spinach Pasta",
                "description": "Whole wheat pasta with garlic mushrooms and spinach",
                "calories": 500,
                "protein": 16,
                "carbs": 78,
                "fats": 14,
                "carbon_footprint": 0.4,
                "ingredients": ["whole wheat pasta", "mushrooms", "spinach", "garlic", "olive oil"],
                "cooking_time": 20
            }
        ]
    },
    "vegetarian": {
        "breakfast": [
            {
                "name": "Greek Yogurt with Granola",
                "description": "Protein-rich Greek yogurt with homemade granola and honey",
                "calories": 380,
                "protein": 18,
                "carbs": 52,
                "fats": 10,
                "carbon_footprint": 0.8,
                "ingredients": ["Greek yogurt", "granola", "honey", "blueberries", "almonds"],
                "cooking_time": 5
            },
            {
                "name": "Vegetable Omelette",
                "description": "Fluffy omelette with bell peppers, onions, and cheese",
                "calories": 340,
                "protein": 22,
                "carbs": 12,
                "fats": 22,
                "carbon_footprint": 1.2,
                "ingredients": ["eggs", "bell peppers", "onions", "cheese", "butter"],
                "cooking_time": 15
            }
        ],
        "lunch": [
            {
                "name": "Caprese Salad with Mozzarella",
                "description": "Fresh tomatoes, mozzarella, and basil with balsamic",
                "calories": 420,
                "protein": 20,
                "carbs": 18,
                "fats": 28,
                "carbon_footprint": 1.5,
                "ingredients": ["tomatoes", "mozzarella", "basil", "olive oil", "balsamic vinegar"],
                "cooking_time": 10
            },
            {
                "name": "Vegetarian Burrito Bowl",
                "description": "Rice bowl with black beans, cheese, and guacamole",
                "calories": 550,
                "protein": 22,
                "carbs": 68,
                "fats": 20,
                "carbon_footprint": 1.0,
                "ingredients": ["brown rice", "black beans", "cheese", "avocado", "sour cream", "salsa"],
                "cooking_time": 20
            }
        ],
        "dinner": [
            {
                "name": "Eggplant Parmesan",
                "description": "Breaded eggplant baked with marinara and mozzarella",
                "calories": 520,
                "protein": 20,
                "carbs": 58,
                "fats": 22,
                "carbon_footprint": 1.1,
                "ingredients": ["eggplant", "marinara sauce", "mozzarella", "parmesan", "breadcrumbs"],
                "cooking_time": 45
            },
            {
                "name": "Spinach and Ricotta Stuffed Shells",
                "description": "Pasta shells filled with ricotta and spinach",
                "calories": 580,
                "protein": 26,
                "carbs": 72,
                "fats": 18,
                "carbon_footprint": 0.9,
                "ingredients": ["pasta shells", "ricotta", "spinach", "marinara", "parmesan"],
                "cooking_time": 40
            }
        ]
    },
    "omnivore": {
        "breakfast": [
            {
                "name": "Scrambled Eggs with Bacon",
                "description": "Classic scrambled eggs with crispy bacon strips",
                "calories": 420,
                "protein": 28,
                "carbs": 8,
                "fats": 30,
                "carbon_footprint": 2.5,
                "ingredients": ["eggs", "bacon", "butter", "cheese", "toast"],
                "cooking_time": 15
            },
            {
                "name": "Pancakes with Sausage",
                "description": "Fluffy pancakes served with maple syrup and sausage",
                "calories": 520,
                "protein": 18,
                "carbs": 68,
                "fats": 18,
                "carbon_footprint": 2.0,
                "ingredients": ["flour", "eggs", "milk", "sausage", "maple syrup"],
                "cooking_time": 20
            }
        ],
        "lunch": [
            {
                "name": "Grilled Chicken Caesar Salad",
                "description": "Grilled chicken breast over romaine with Caesar dressing",
                "calories": 480,
                "protein": 42,
                "carbs": 22,
                "fats": 22,
                "carbon_footprint": 3.2,
                "ingredients": ["chicken breast", "romaine lettuce", "parmesan", "croutons", "Caesar dressing"],
                "cooking_time": 20
            },
            {
                "name": "Turkey and Avocado Sandwich",
                "description": "Whole grain sandwich with turkey, avocado, and vegetables",
                "calories": 520,
                "protein": 32,
                "carbs": 48,
                "fats": 20,
                "carbon_footprint": 2.8,
                "ingredients": ["turkey", "whole grain bread", "avocado", "lettuce", "tomato", "mayo"],
                "cooking_time": 10
            }
        ],
        "dinner": [
            {
                "name": "Grilled Salmon with Vegetables",
                "description": "Herb-crusted salmon with roasted seasonal vegetables",
                "calories": 540,
                "protein": 42,
                "carbs": 32,
                "fats": 24,
                "carbon_footprint": 4.5,
                "ingredients": ["salmon", "broccoli", "carrots", "olive oil", "herbs", "lemon"],
                "cooking_time": 30
            },
            {
                "name": "Chicken Stir-Fry",
                "description": "Chicken breast with mixed vegetables in teriyaki sauce",
                "calories": 520,
                "protein": 38,
                "carbs": 58,
                "fats": 14,
                "carbon_footprint": 3.8,
                "ingredients": ["chicken breast", "bell peppers", "snap peas", "rice", "teriyaki sauce"],
                "cooking_time": 25
            },
            {
                "name": "Beef Tacos with Toppings",
                "description": "Seasoned ground beef tacos with fresh toppings",
                "calories": 580,
                "protein": 32,
                "carbs": 52,
                "fats": 26,
                "carbon_footprint": 5.2,
                "ingredients": ["ground beef", "taco shells", "lettuce", "cheese", "sour cream", "salsa"],
                "cooking_time": 20
            }
        ]
    }
}

# Add balanced diet (mix of all)
MEAL_DATABASE["balanced"] = {
    "breakfast": MEAL_DATABASE["vegetarian"]["breakfast"] + MEAL_DATABASE["vegan"]["breakfast"][:1],
    "lunch": MEAL_DATABASE["vegetarian"]["lunch"] + MEAL_DATABASE["omnivore"]["lunch"][:1],
    "dinner": MEAL_DATABASE["vegetarian"]["dinner"] + MEAL_DATABASE["omnivore"]["dinner"][:2]
}

# Map other diet types
MEAL_DATABASE["pescatarian"] = MEAL_DATABASE["vegetarian"]  # Can be enhanced with fish meals
MEAL_DATABASE["flexitarian"] = MEAL_DATABASE["balanced"]


async def generate_7_day_meal_plan(
    dietary_preference: str = "balanced",
    calorie_target: int = 2000,
    exclude_ingredients: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Generate a 7-day meal plan based on dietary preferences.

    Args:
        dietary_preference: Type of diet (vegan, vegetarian, omnivore, balanced)
        calorie_target: Daily calorie target
        exclude_ingredients: List of ingredients to exclude

    Returns:
        List of 7 days of meals
    """

    exclude_ingredients = exclude_ingredients or []
    dietary_preference = dietary_preference.lower()

    # Get meal options for the diet type
    if dietary_preference not in MEAL_DATABASE:
        dietary_preference = "balanced"

    meal_options = MEAL_DATABASE[dietary_preference]

    # Generate 7 days of meals
    meal_plan = []
    start_date = datetime.now().date()

    for day in range(1, 8):
        current_date = start_date + timedelta(days=day - 1)

        # Select meals (try to avoid repetition)
        breakfast = random.choice(meal_options["breakfast"])
        lunch = random.choice(meal_options["lunch"])
        dinner = random.choice(meal_options["dinner"])

        # Filter out excluded ingredients
        if exclude_ingredients:
            # Skip meals with excluded ingredients (simple check)
            breakfast_valid = not any(ing.lower() in " ".join(breakfast["ingredients"]).lower() for ing in exclude_ingredients)
            lunch_valid = not any(ing.lower() in " ".join(lunch["ingredients"]).lower() for ing in exclude_ingredients)
            dinner_valid = not any(ing.lower() in " ".join(dinner["ingredients"]).lower() for ing in exclude_ingredients)

            # If any meal has excluded ingredients, try to find an alternative
            attempts = 0
            while (not breakfast_valid or not lunch_valid or not dinner_valid) and attempts < 10:
                if not breakfast_valid:
                    breakfast = random.choice(meal_options["breakfast"])
                    breakfast_valid = not any(ing.lower() in " ".join(breakfast["ingredients"]).lower() for ing in exclude_ingredients)
                if not lunch_valid:
                    lunch = random.choice(meal_options["lunch"])
                    lunch_valid = not any(ing.lower() in " ".join(lunch["ingredients"]).lower() for ing in exclude_ingredients)
                if not dinner_valid:
                    dinner = random.choice(meal_options["dinner"])
                    dinner_valid = not any(ing.lower() in " ".join(dinner["ingredients"]).lower() for ing in exclude_ingredients)
                attempts += 1

        # Calculate totals
        total_calories = breakfast["calories"] + lunch["calories"] + dinner["calories"]
        total_carbon = breakfast["carbon_footprint"] + lunch["carbon_footprint"] + dinner["carbon_footprint"]

        day_meals = {
            "day": day,
            "date": current_date.strftime("%Y-%m-%d"),
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
            "total_calories": total_calories,
            "total_carbon": round(total_carbon, 2)
        }

        meal_plan.append(day_meals)

    return meal_plan


def get_alternative_meals(
    meal_type: str,
    dietary_preference: str = "balanced",
    exclude_names: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Get alternative meals for swapping.

    Args:
        meal_type: Type of meal (breakfast, lunch, dinner)
        dietary_preference: User's dietary preference
        exclude_names: List of meal names to exclude

    Returns:
        List of alternative meal options
    """
    exclude_names = exclude_names or []
    dietary_preference = dietary_preference.lower()

    # Get meal options for the diet type
    if dietary_preference not in MEAL_DATABASE:
        dietary_preference = "balanced"

    meal_options = MEAL_DATABASE[dietary_preference]

    # Filter by meal type and exclude specified meals
    if meal_type not in meal_options:
        return []

    alternatives = [
        meal for meal in meal_options[meal_type]
        if meal["name"] not in exclude_names
    ]

    return alternatives
