"""
Celery Configuration for Ecolife Application
Handles asynchronous task processing with Redis as broker and backend
"""

from celery import Celery
from app.config import settings

# Initialize Celery app
celery_app = Celery(
    'ecolife_tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max task time
    result_expires=3600,  # Results expire after 1 hour
    task_routes={
        'app.tasks.meal_plan.*': {'queue': 'mealplan'},
        'app.tasks.analytics.*': {'queue': 'analytics'},
    },
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
)

# Auto-discover tasks in the app.tasks module
celery_app.autodiscover_tasks(['app.tasks'])
