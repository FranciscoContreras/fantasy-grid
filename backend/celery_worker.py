#!/usr/bin/env python
"""
Celery worker entry point for Fantasy Grid

Start worker with:
    celery -A celery_worker worker --loglevel=info

Start with multiple queues:
    celery -A celery_worker worker --loglevel=info -Q matchups,analysis,ai

Start flower (monitoring):
    celery -A celery_worker flower
"""
from app.tasks import celery_app

if __name__ == '__main__':
    celery_app.start()
