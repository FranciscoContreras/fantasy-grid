"""
Celery task queue configuration for Fantasy Grid
"""
from celery import Celery
import os


def make_celery():
    """Create and configure Celery instance"""
    celery = Celery(
        'fantasy_grid',
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )

    celery.conf.update(
        # Task configuration
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,

        # Task execution
        task_track_started=True,
        task_time_limit=300,  # 5 minutes max
        task_soft_time_limit=240,  # 4 minutes soft limit
        task_acks_late=True,
        task_reject_on_worker_lost=True,

        # Task routing
        task_routes={
            'app.tasks.matchup_tasks.*': {'queue': 'matchups'},
            'app.tasks.analysis_tasks.*': {'queue': 'analysis'},
            'app.tasks.ai_tasks.*': {'queue': 'ai'},
        },

        # Result backend
        result_expires=3600,  # Results expire after 1 hour
        result_extended=True,

        # Worker configuration
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )

    return celery


# Create celery instance
celery_app = make_celery()
