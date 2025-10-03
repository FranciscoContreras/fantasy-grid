# Celery Background Tasks

Fantasy Grid uses Celery for background task processing to handle long-running analysis operations asynchronously.

## Prerequisites

- Redis server running (for broker and result backend)
- All Python dependencies installed (`pip install -r requirements.txt`)

## Starting Redis (Local Development)

### macOS (via Homebrew)
```bash
brew install redis
brew services start redis
```

### Docker
```bash
docker run -d -p 6379:6379 redis:alpine
```

## Starting Celery Worker

### Basic worker
```bash
cd backend
source venv/bin/activate
celery -A celery_worker worker --loglevel=info
```

### Worker with specific queues
```bash
celery -A celery_worker worker --loglevel=info -Q matchups,analysis,ai
```

### Worker with concurrency
```bash
celery -A celery_worker worker --loglevel=info --concurrency=4
```

## Monitoring with Flower

Flower is a web-based tool for monitoring Celery tasks and workers.

```bash
celery -A celery_worker flower
```

Then visit: http://localhost:5555

## Task Queues

- **matchups**: Player matchup analysis tasks
- **analysis**: Player comparison and analysis tasks
- **ai**: AI grading and prediction tasks

## Available Tasks

### 1. Analyze Player Matchup
**Endpoint**: `POST /api/tasks/analyze-player`
```json
{
  "player_id": "12345",
  "opponent_id": "SF",
  "location": "Santa Clara, CA"
}
```

**Response**:
```json
{
  "task_id": "abc-123-def-456",
  "status": "queued"
}
```

### 2. Compare Players
**Endpoint**: `POST /api/tasks/compare-players`
```json
{
  "player_ids": ["123", "456", "789"],
  "opponent_ids": ["SF", "LAR", "SEA"]
}
```

### 3. Check Task Status
**Endpoint**: `GET /api/tasks/status/{task_id}`

**Response**:
```json
{
  "task_id": "abc-123-def-456",
  "status": "SUCCESS",
  "ready": true,
  "successful": true,
  "result": {
    "player": {...},
    "matchup_score": 75,
    "recommendation": {...}
  }
}
```

## Task States

- `PENDING`: Task is waiting to be executed
- `STARTED`: Task has been started
- `SUCCESS`: Task completed successfully
- `FAILURE`: Task failed with an error
- `RETRY`: Task is being retried after failure

## Production Deployment

### Heroku

1. Add Redis addon:
```bash
heroku addons:create heroku-redis:mini
```

2. Add worker dyno to Procfile:
```
web: gunicorn app:app
worker: celery -A celery_worker worker --loglevel=info
```

3. Scale worker:
```bash
heroku ps:scale worker=1
```

### Environment Variables

```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0
```

## Troubleshooting

### Connection refused to Redis
- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check REDIS_URL environment variable

### Tasks not executing
- Check worker is running: `celery -A celery_worker inspect active`
- Check queue exists: `celery -A celery_worker inspect registered`

### Memory issues
- Set max tasks per worker: `--max-tasks-per-child=1000`
- Reduce concurrency: `--concurrency=2`
