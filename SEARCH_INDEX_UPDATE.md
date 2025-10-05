# Search Index Update Job

This document explains how to keep the search index up-to-date with the latest player and team data.

## Overview

The search index needs to be updated periodically to include:
- New players added to the NFL
- Player roster changes (team transfers)
- Updated player information (status, injuries, etc.)
- New teams or team information changes

## Update Methods

### Option 1: Heroku Scheduler (Recommended for Free/Hobby Tier)

Heroku Scheduler is a free add-on that runs jobs at specified intervals.

**Setup:**
```bash
# Add Heroku Scheduler add-on (free)
heroku addons:create scheduler:standard

# Open scheduler dashboard
heroku addons:open scheduler
```

**Configure Job:**
1. Click "Add Job"
2. Command: `python update_search_index.py`
3. Frequency: Daily (recommended) or Every hour (for real-time updates)
4. Save

**Benefits:**
- Free (no additional dyno cost)
- Simple setup
- Good for daily/hourly updates

**Limitations:**
- Minimum interval is 10 minutes
- No real-time monitoring
- Jobs run on one-off dynos

### Option 2: Dedicated Worker Dyno (For Production)

Run a continuous background worker for real-time index updates.

**Setup:**
```bash
# Scale up the search-worker dyno
heroku ps:scale search-worker=1
```

**Configure Update Interval:**
```bash
# Set custom interval (default: 1 hour / 3600 seconds)
heroku config:set INDEX_UPDATE_INTERVAL=1800  # 30 minutes
```

**Monitor:**
```bash
# View worker logs
heroku logs --tail --dyno search-worker
```

**Stop Worker:**
```bash
# Scale down to save dyno hours
heroku ps:scale search-worker=0
```

**Benefits:**
- Continuous updates
- Configurable interval (down to seconds)
- Real-time monitoring
- Better for high-traffic applications

**Cost:**
- Uses 1 dyno (Hobby: $7/month, Basic: $25/month)

### Option 3: Manual Update

Run index updates manually when needed.

**Locally:**
```bash
python update_search_index.py
```

**On Heroku:**
```bash
heroku run python update_search_index.py
```

## Update Intervals Recommendation

| Scenario | Recommended Interval | Method |
|----------|---------------------|--------|
| Development | As needed (manual) | Manual |
| Low traffic app | Daily | Heroku Scheduler |
| Medium traffic | Every 6 hours | Heroku Scheduler |
| High traffic | Every 1-2 hours | Worker Dyno |
| Real-time updates | Every 15-30 minutes | Worker Dyno |

## Monitoring

### View Update Logs

**Heroku Scheduler:**
```bash
# View all logs
heroku logs --tail

# Filter for index updates
heroku logs --tail | grep "Search Index Update"
```

**Worker Dyno:**
```bash
# View worker-specific logs
heroku logs --tail --dyno search-worker
```

### Check Index Stats

After an update, you can check index statistics via the API:

```bash
curl https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/search/stats
```

## Troubleshooting

### Update Job Failing

1. Check logs for errors:
   ```bash
   heroku logs --tail | grep ERROR
   ```

2. Verify database connection:
   ```bash
   heroku config:get DATABASE_URL
   ```

3. Test locally:
   ```bash
   python update_search_index.py
   ```

### Index Not Updating

1. Check if job is scheduled:
   ```bash
   heroku addons:open scheduler  # View scheduled jobs
   ```

2. Verify worker is running:
   ```bash
   heroku ps  # Check dyno status
   ```

3. Manually trigger update:
   ```bash
   heroku run python update_search_index.py
   ```

### High API Rate Limits

If you hit Grid Iron Mind API rate limits:

1. Increase update interval:
   ```bash
   heroku config:set INDEX_UPDATE_INTERVAL=7200  # 2 hours
   ```

2. Use Heroku Scheduler instead of worker (less frequent updates)

3. Implement rate limiting in indexer (add delays between API calls)

## Best Practices

1. **Start Conservative**: Begin with daily updates, increase frequency as needed

2. **Monitor Costs**: Worker dynos cost money - only use if necessary

3. **Cache Invalidation**: Index updates automatically happen, but you may want to invalidate Redis cache:
   ```bash
   curl -X POST https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/cache/cleanup
   ```

4. **Seasonal Adjustments**:
   - Pre-season: Daily updates (roster changes frequent)
   - Regular season: Every 6 hours (injuries, status changes)
   - Off-season: Weekly updates (minimal changes)

5. **Error Handling**: The update job logs errors but continues running. Check logs regularly during initial setup.

## Technical Details

### What Gets Updated

- **Players**: All active NFL players from Grid Iron Mind API
- **Teams**: All NFL teams with current information
- **Metadata**: Position, team, status, jersey number, college, etc.

### Update Process

1. Fetch latest data from Grid Iron Mind API
2. Process and tokenize text (name, team, position, etc.)
3. Update inverted index in PostgreSQL
4. Update document metadata (JSONB)
5. Calculate term frequencies for ranking

### Database Impact

- Updates use `ON CONFLICT` (upsert) - existing records updated, new ones inserted
- Minimal performance impact (typically <5 seconds for full update)
- No downtime - searches work during updates
- Atomic operations ensure consistency

## Cost Analysis

### Heroku Scheduler (Free Tier)
- **Cost**: $0/month
- **Updates**: Daily recommended
- **Good for**: Low-medium traffic apps

### Worker Dyno
- **Hobby**: $7/month (1 worker @ 1 hour intervals)
- **Basic**: $25/month (1 worker @ 15 min intervals)
- **Updates**: Continuous
- **Good for**: Production apps with frequent data changes
