"""
Celery Worker Startup Script
Run this to start the Celery worker for processing meal plan generation tasks.

Usage:
    python start_worker.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.celery_app import celery_app

if __name__ == '__main__':
    # Start Celery worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',  # Use solo pool for Windows compatibility
        '--concurrency=1',
        '--queues=default,mealplan,analytics'
    ])
