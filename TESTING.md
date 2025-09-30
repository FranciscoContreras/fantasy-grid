# Testing Guide - Fantasy Grid

This document outlines all testing procedures for the Fantasy Grid application.

## Quick Test

Run the automated test suite:

```bash
./test-endpoints.sh
```

## Manual Testing

### 1. Backend API Tests

#### Health Check
```bash
curl https://fantasy-grid-8e65f9ca9754.herokuapp.com/health
```

Expected: `{"status":"healthy","service":"Fantasy Grid API","version":"1.0.0"}`

#### Player Search
```bash
curl "https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/players/search?q=aaron"
```

Expected: JSON array of players with names containing "aaron"

#### Player Details
```bash
curl "https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/players/b31ee0b9-858d-455f-b504-4e00479b0110"
```

Expected: Detailed player information for Aaron Rodgers

#### Player Career Stats
```bash
curl "https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/players/b31ee0b9-858d-455f-b504-4e00479b0110/career"
```

Expected: Career statistics data

#### Analysis History
```bash
curl "https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/players/b31ee0b9-858d-455f-b504-4e00479b0110/history"
```

Expected: Array of past analyses for the player

### 2. Frontend Tests

#### Local Development
```bash
cd frontend
npm run dev
```

Open http://localhost:5173

**Test checklist:**
- [ ] Page loads with "Fantasy Grid - Player Analysis" title
- [ ] Search input is visible
- [ ] Can type in search box
- [ ] Search button is clickable
- [ ] Tailwind styles are applied correctly
- [ ] Dark mode toggle works (if implemented)

#### Production Frontend
Visit: https://fantasy-grid-8e65f9ca9754.herokuapp.com/

**Test checklist:**
- [ ] Page loads without errors
- [ ] All assets (CSS, JS) load successfully
- [ ] UI matches local development version
- [ ] No console errors in browser DevTools

### 3. Full Integration Test

Complete user workflow:

1. **Open the app**: https://fantasy-grid-8e65f9ca9754.herokuapp.com/

2. **Search for a player**:
   - Type "aaron" in the search box
   - Click "Search"
   - Verify players appear in results

3. **Select a player**:
   - Click on a player card (e.g., Aaron Rodgers)
   - Verify player name appears in "Selected Player" section

4. **Enter opponent**:
   - Type a team ID in the opponent field
   - Note: Team abbreviations may not work; use full team names or IDs from the API

5. **Analyze matchup**:
   - Click "Analyze Matchup"
   - Verify analysis results appear:
     - Matchup score (0-100)
     - Weather impact (0-100)
     - AI grade (A+ to D)
     - Recommendation badge (START/CONSIDER/BENCH)

6. **Verify database logging**:
   - Make the analysis request
   - Check analysis history endpoint to confirm it was saved

### 4. Database Tests

#### Check Database Connection
```bash
heroku pg:info
```

Expected: Database details and connection stats

#### View Analysis History
```bash
heroku run 'python -c "from app.database import execute_query; results = execute_query(\"SELECT COUNT(*) as count FROM analysis_history\", fetch_one=True); print(f\"Total analyses: {results[\"count\"]}\")"'
```

Expected: Count of analysis records

#### Manual Database Query
```bash
heroku pg:psql
```

Then run:
```sql
SELECT player_id, opponent, ai_grade, recommendation, analyzed_at
FROM analysis_history
ORDER BY analyzed_at DESC
LIMIT 10;
```

### 5. Performance Tests

#### Response Time
```bash
time curl "https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/players/search?q=aaron"
```

Expected: < 2 seconds

#### Frontend Load Time
Use browser DevTools Network tab:
- Total page load: < 3 seconds
- Time to interactive: < 2 seconds

### 6. Error Handling Tests

#### Invalid Player ID
```bash
curl "https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/players/invalid-id-12345"
```

Expected: Proper error message

#### Missing Query Parameter
```bash
curl "https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/players/search"
```

Expected: `{"error":"Query parameter \"q\" is required"}` (HTTP 400)

#### Missing Opponent Parameter
```bash
curl "https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/players/b31ee0b9-858d-455f-b504-4e00479b0110/analysis"
```

Expected: `{"error":"Query parameter \"opponent\" is required"}` (HTTP 400)

## Test Results

### Phase 6 Testing Completed

Date: 2025-09-30

**Backend API**: ✅ All endpoints responding correctly
- Health check: ✅
- Player search: ✅
- Player details: ✅
- Career stats: ✅
- Analysis history: ✅

**Frontend**: ✅ Deployed and accessible
- Production site: ✅
- Static assets: ✅
- Local development: ✅

**Database**: ✅ PostgreSQL configured and operational
- Schema initialized: ✅
- Connection working: ✅
- Analysis logging: ✅

**Integration**: ✅ Full workflow functional
- Search → Select → Analyze: ✅
- Database persistence: ✅

## Known Issues

1. **Team opponent parameter**: The analysis endpoint expects team IDs from the Grid Iron Mind API, not simple abbreviations like "KC" or "DAL". This is an API limitation.

2. **Player search**: Currently returns partial matches. Search for "patrick" may not return Patrick Mahomes if the API doesn't index by first name.

## Next Steps

See BUILD.md Phase 7 for enhancement opportunities:
- Add caching with Redis
- Implement authentication
- Add monitoring and logging
- Performance optimization
