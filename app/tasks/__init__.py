"""
Celery tasks package for async operations.
"""

from app.tasks.meal_plan import generate_meal_plan_task

__all__ = ['generate_meal_plan_task']
