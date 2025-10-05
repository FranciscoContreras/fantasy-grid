web: gunicorn wsgi:app --timeout 300
worker: cd backend && celery -A celery_worker worker --loglevel=info --concurrency=2
search-worker: python update_search_index.py --continuous
