# Fantasy Grid AI Analysis Improvement Plan

## Current State Analysis

### What Data We Currently Have:
1. **Player Data**: Name, position, team, injury status
2. **Opponent Team**: Team abbreviation only (e.g., "WSH", "DEN")
3. **Partial Context**: Defensive coordinator, 2 key defenders, historical stats
4. **Matchup Score**: Calculated algorithmic score (0-100)
5. **Weather**: Basic weather data (if configured)

### What's Missing for Optimal Grok Analysis:
1. **Complete Schedule Context**: Who is playing whom, home/away, date/time
2. **Opponent Roster Details**: Key offensive players Patrick Mahomes will face
3. **Game-Specific Context**: Is it a division game? Rivalry? Prime time?
4. **Complete Defensive Stats**: Full defensive rankings, not just coordinator
5. **Cached Analysis**: No DB storage, only in-memory Redis cache

### Current Pain Points:
- **Week 8 2025**: Schedule API returns null (no data yet), so we analyze "vs Unknown"
- **Grok gets incomplete context**: "Patrick Mahomes vs Unknown defense"
- **No persistent cache**: If user re-analyzes, we call Grok again (wastes money)
- **Sequential processing**: 14 players × 10 seconds = 140 seconds per matchup

---

## Improvement Plan (Step-by-Step)

### Phase 1: Ensure Complete Schedule Data (CRITICAL)
**Goal**: Make sure we always know opponents before calling Grok

#### Changes Needed:
1. **Validate Schedule Availability**
   - File: `app/services/season_service.py`
   - Add method: `is_schedule_available(season, week)`
   - Check if API returns actual game data, not null

2. **Better Error Handling in matchup_data_service.py**
   - File: `app/services/matchup_data_service.py`
   - Lines 52-71
   - Instead of setting `opponent_team=None`, log warning and skip week
   - Don't allow analysis of weeks without schedule data

3. **Frontend Validation**
   - File: `frontend/src/components/RosterManagement.tsx`
   - Disable matchup creation for future weeks without schedule
   - Show message: "Schedule not available for Week 8 2025 yet"

**Example Context Before:**
```
Patrick Mahomes vs Unknown defense
Matchup score: 72/100
```

**Example Context After:**
```
Patrick Mahomes (KC) vs Washington Commanders (WSH)
Home game at Arrowhead Stadium
Matchup score: 72/100
Washington allows 25 PPG (rank #28)
```

---

### Phase 2: Add Opponent Roster Context
**Goal**: Tell Grok about key players on the opposing team

#### New Data to Fetch:
1. **Get Opposing Roster** (New API calls)
   - Fetch Washington Commanders roster when analyzing Chiefs
   - Get their top defensive players by position
   - Get their offensive weapons (QB, RB, WR for defensive matchup)

2. **New Method in api_client.py**
```python
def get_team_roster(self, team_abbr, season):
    """Get complete roster for a team"""
    # Call /teams/{team}/players endpoint
    # Return top players by fantasy points
    pass

def get_team_defensive_rankings(self, team_abbr, season):
    """Get complete defensive stats"""
    # Points allowed, yards allowed, sacks, INT, etc.
    # Return comprehensive defensive profile
    pass
```

3. **Add to matchup_data_service.py**
```python
# In get_comprehensive_matchup_data():
opponent_roster = self.api_client.get_team_roster(opponent_team, season)
opponent_defense_stats = self.api_client.get_team_defensive_rankings(opponent_team, season)

data['opponent_roster'] = opponent_roster
data['opponent_defense_stats'] = opponent_defense_stats
```

**Example Grok Prompt Enhancement:**
```
Analyze Patrick Mahomes (KC QB) vs Washington Commanders:

Game Context:
- Week 8, 2025 at Arrowhead Stadium (KC home)
- Matchup score: 82/100 (favorable)

Washington Defense:
- DC: Vic Fangio
- Key defenders: Chase Young (DE), Bobby Wagner (LB)
- Rank: #28 in PPG allowed (25.3)
- Pass defense rank: #30 (280 yards/game)
- Sacks: 15 total (rank #22)

Patrick Mahomes History vs WSH:
- 3 games, avg 310 yards, 2.7 TDs
- Last game: 28/35, 320 yards, 3 TDs (2024)

Provide 1-2 sentence analysis on whether to start him.
```

---

### Phase 3: Improve Caching Strategy
**Goal**: Never call Grok twice for the same analysis

#### Current Problem:
```python
# ai_service.py line 42-45
prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
cached = get_cached_ai_response(prompt_hash)
```
- Caches by prompt text only
- If prompt wording changes slightly, cache misses
- Redis cache expires, no persistent storage

#### Solution:
1. **Cache Key by Data, Not Prompt**
```python
def get_analysis_cache_key(player_id, opponent_team, week, season):
    """Generate consistent cache key"""
    return f"analysis:{player_id}:{opponent_team}:{week}:{season}"
```

2. **Two-Tier Caching**
   - **Tier 1**: Redis (fast, temporary) - 7 days
   - **Tier 2**: PostgreSQL (persistent, forever)

3. **New Database Table**
```sql
CREATE TABLE ai_analysis_cache (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50),
    player_name VARCHAR(100),
    opponent_team VARCHAR(10),
    week INT,
    season INT,
    analysis_text TEXT,
    matchup_score DECIMAL(5,2),
    recommendation VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(player_id, opponent_team, week, season)
);
```

4. **Cache Lookup Flow**
```python
def get_cached_analysis(player_id, opponent, week, season):
    # 1. Check Redis first (fastest)
    redis_key = get_analysis_cache_key(player_id, opponent, week, season)
    cached = redis_client.get(redis_key)
    if cached:
        return json.loads(cached)

    # 2. Check database (persistent)
    db_result = query_one(
        "SELECT analysis_text FROM ai_analysis_cache WHERE player_id=%s AND opponent_team=%s AND week=%s AND season=%s",
        (player_id, opponent, week, season)
    )
    if db_result:
        # Store back in Redis for next time
        redis_client.setex(redis_key, 604800, json.dumps(db_result))  # 7 days
        return db_result

    return None
```

---

### Phase 4: Enhance Grok Prompts with Full Context
**Goal**: Give Grok everything it needs to make the best recommendation

#### New Prompt Structure:
```python
def generate_comprehensive_prompt(player, opponent_data, game_context):
    """Build rich context prompt for Grok"""

    prompt = f"""Analyze {player['name']} ({player['team']} {player['position']}) for Week {game_context['week']}, {game_context['season']}

GAME CONTEXT:
- Opponent: {opponent_data['team']} {opponent_data['mascot']}
- Location: {'Home' if game_context['is_home'] else 'Away'} at {game_context['stadium']}
- Game time: {game_context['date_time']}
{'- Division rival game' if game_context['is_division'] else ''}
{'- Prime time game' if game_context['is_primetime'] else ''}

OPPONENT DEFENSE:
- Overall rank: #{opponent_data['def_rank']} ({opponent_data['ppg_allowed']} PPG)
- {player['position']}-specific rank: #{opponent_data['position_rank']}
- Defensive coordinator: {opponent_data['dc_name']}
- Key defenders: {', '.join(opponent_data['key_defenders'])}
- Recent form: {opponent_data['last_3_games_summary']}

PLAYER HISTORY:
- vs {opponent_data['team']}: {player['history']['games']} games, avg {player['history']['avg_points']} pts
- Last meeting: {player['history']['last_game']}
- Season avg: {player['season_avg']} pts/game
- Last 3 games: {player['recent_form']}

INJURY STATUS: {player['injury_status']}
WEATHER: {game_context['weather']}

Provide a concise 2-3 sentence analysis with clear START/SIT/CONSIDER recommendation.
Focus on the most impactful factors: matchup strength, recent form, and game context."""

    return prompt
```

---

### Phase 5: Optimize API Calls & Performance
**Goal**: Reduce time to analyze full roster

#### Current: Sequential (140 seconds for 14 players)
```python
for player in players:
    analysis = analyze_player(player)  # 10 seconds each
```

#### Solution 1: Batch Prompting (Preferred)
```python
def analyze_roster_batch(players, opponent_data):
    """Send all players in ONE Grok request"""

    prompt = f"""Analyze all {len(players)} players for this matchup:

{format_all_players_context(players, opponent_data)}

Provide START/SIT/CONSIDER recommendation + 1-2 sentence reasoning for EACH player.
Format as JSON array."""

    response = grok_api.call(prompt)
    return parse_batch_response(response)
```
**Time**: 1 request × 15 seconds = **15 seconds total** (9x faster!)

#### Solution 2: Parallel Requests (Alternative)
```python
import concurrent.futures

def analyze_roster_parallel(players):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(analyze_player, p) for p in players]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    return results
```
**Time**: 14 players / 5 workers = 3 batches × 10 seconds = **30 seconds** (4.6x faster)

---

## Implementation Priority

### Must-Have (Week 1):
1. ✅ Fix schedule validation - don't analyze weeks without data
2. ✅ Add database caching table
3. ✅ Implement two-tier cache lookup
4. ✅ Enhanced Grok prompts with full context

### Should-Have (Week 2):
5. ⏳ Add opponent roster data fetching
6. ⏳ Add opponent defensive rankings
7. ⏳ Batch Grok API calls for performance

### Nice-to-Have (Week 3):
8. ⏳ Division/rivalry game detection
9. ⏳ Prime time game flags
10. ⏳ Stadium/weather integration

---

## Expected Improvements

### Before:
- ❌ Analyzes "Patrick Mahomes vs Unknown"
- ❌ Takes 140 seconds for 14 players
- ❌ Re-runs same analysis if user clicks twice
- ❌ Generic context, weak recommendations

### After:
- ✅ "Patrick Mahomes (KC) vs Washington Commanders at Arrowhead"
- ✅ Takes 15 seconds for 14 players (9x faster)
- ✅ Instant results on repeat analysis (cached in DB)
- ✅ Rich context with defensive rankings, key players, historical data
- ✅ Grok can make informed, specific recommendations

### Cost Savings:
- **Current**: ~$0.015 per roster analysis × repeat analyses
- **After**: ~$0.015 first time, $0.00 every time after (cached)
- **Estimated savings**: 80%+ for repeat users

---

## Files to Modify

### Backend:
1. `app/services/api_client.py` - Add roster/defense fetching methods
2. `app/services/matchup_data_service.py` - Fetch opponent data
3. `app/services/season_service.py` - Schedule validation
4. `app/services/ai_service.py` - Caching refactor + batch API
5. `app/routes/matchups.py` - Use enhanced context
6. `app/database/schema.sql` - New cache table
7. `app/services/cache_service.py` - Two-tier caching

### Frontend:
8. `frontend/src/components/RosterManagement.tsx` - Disable unavailable weeks
9. `frontend/src/components/MatchupAnalysis.tsx` - Show richer data

### Database:
10. Migration: `migrations/008_ai_analysis_cache.sql`

---

## Testing Plan

1. **Unit Tests**: Cache lookup, API fetching
2. **Integration Tests**: Full analysis pipeline with mocked APIs
3. **Performance Tests**: Time 14-player analysis before/after
4. **Cost Tests**: Verify no duplicate Grok calls
5. **User Testing**: Verify UI shows complete context

---

## Rollout Plan

1. **Phase 1** (Day 1-2): Database + caching infrastructure
2. **Phase 2** (Day 3-4): Enhanced data fetching (opponent info)
3. **Phase 3** (Day 5): Improved prompts
4. **Phase 4** (Day 6): Batch API optimization
5. **Phase 5** (Day 7): Testing + deployment

---

## Success Metrics

- ✅ Analysis time: < 20 seconds for full roster
- ✅ Cache hit rate: > 80% for repeat analyses
- ✅ Grok quality: Users rate recommendations 4+ stars
- ✅ Cost per analysis: < $0.003 average (with caching)
- ✅ No "Unknown opponent" analyses in production
