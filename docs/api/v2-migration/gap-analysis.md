# API v2 Gap Analysis & Implementation Plan

**Date:** October 2, 2025
**Status:** Analysis Complete

---

## 📊 Current State

**Our Implementation:** 34 API client methods
**Documented v2 Endpoints:** 25+ endpoints
**Overlap:** ~70%
**Missing:** ~30% of documented features

---

## 🔍 Detailed Comparison

### ✅ IMPLEMENTED & WORKING

#### Players Endpoints
- ✅ `get_player_data` - Get player details
- ✅ `get_player_career_stats` - Career statistics
- ✅ `get_player_injuries_v2` - Injury information
- ✅ `get_player_advanced_stats` - Next Gen Stats
- ✅ `get_player_stats_vs_team` - Performance vs opponent
- ✅ `search_players` - Player search

#### Teams Endpoints
- ✅ `get_team_roster_v2` - Team roster
- ✅ `get_team_injuries_v2` - Team injury report
- ✅ `get_team_schedule_v2` - Team schedule

#### Games Endpoints
- ✅ `get_games_v2` - List games
- ✅ `get_game_details_v2` - Game information
- ✅ `get_game_play_by_play` - Play-by-play data
- ✅ `get_game_scoring_plays` - Scoring plays

#### Stats Endpoints
- ✅ `get_standings_v2` - NFL standings
- ✅ `get_stat_leaders` - Statistical leaders

#### AI Endpoints
- ✅ `ai_query_v2` - Natural language queries
- ✅ `ai_predict_game_v2` - Game predictions
- ✅ `ai_predict_player_v2` - Player predictions

---

## ❌ MISSING / NEEDS UPDATE

### 1. Players Endpoints

#### Missing: List Players with Filters
**Documented:** `GET /api/v2/players`
**Parameters:**
- `position` - Filter by position
- `status` - Filter by status
- `team` - Filter by team ID
- `limit` - Pagination limit
- `offset` - Pagination offset

**Current:** We have `search_players` but it only searches by name
**Need:** `get_players_list_v2(position=None, status=None, team=None, limit=50, offset=0)`

#### Missing: Player by ID
**Documented:** `GET /api/v2/players/:id`
**Current:** We use `get_player_data` which may be v1
**Need:** Verify `get_player_data` uses v2 endpoint or create `get_player_by_id_v2`

#### Missing: Player Team History
**Documented:** `GET /api/v2/players/:id/history`
**Returns:** All teams a player has played for
**Need:** `get_player_team_history_v2(player_id)`

#### Missing: Player vs Specific Defense
**Documented:** `GET /api/v2/players/:id/vs-defense/:teamId`
**Current:** We have `get_player_stats_vs_team` but may not use v2 format
**Need:** `get_player_vs_defense_v2(player_id, defense_team_id, season=None, limit=None)`

---

### 2. Teams Endpoints

#### Missing: Get Team by ID
**Documented:** `GET /api/v2/teams/:id`
**Returns:** Detailed team information (stadium, colors, etc.)
**Need:** `get_team_by_id_v2(team_id)`

#### Missing: List All Teams
**Documented:** `GET /api/v2/teams`
**Returns:** All 32 NFL teams
**Current:** We verified this works via direct HTTP, but no method
**Need:** `get_teams_list_v2()`

---

### 3. Games Endpoints

#### Missing: Get Game by ID
**Documented:** `GET /api/v2/games/:id`
**Current:** We have `get_game_details_v2` - verify it's correct
**Need:** Verify or update

#### Missing: Game Team Statistics
**Documented:** `GET /api/v2/games/:id/stats`
**Returns:** Team-level stats for a specific game
**Current:** We have `get_game_stats` but may be v1
**Need:** `get_game_team_stats_v2(game_id)`

---

### 4. Parameter Naming Discrepancies

Several methods may not match v2 parameter names:

| Our Method | Parameter Issue | v2 Standard |
|------------|----------------|-------------|
| `get_games_v2` | Uses `week` | Should support `status`, `limit` |
| `get_team_roster_v2` | Uses team abbr | v2 uses team UUID |
| `search_players` | Name only | v2 supports multiple filters |

---

## 🎯 Priority Implementation Plan

### Phase 1: Critical Missing Methods (HIGH PRIORITY)

These are essential for full app functionality:

1. **`get_players_list_v2`** - List/filter players
   ```python
   def get_players_list_v2(self, position=None, status=None, team=None, limit=50, offset=0):
       """List players with flexible filtering"""
   ```

2. **`get_teams_list_v2`** - List all teams
   ```python
   def get_teams_list_v2(self):
       """Get all 32 NFL teams"""
   ```

3. **`get_team_by_id_v2`** - Team details
   ```python
   def get_team_by_id_v2(self, team_id):
       """Get detailed team information"""
   ```

4. **`get_player_team_history_v2`** - Player's team history
   ```python
   def get_player_team_history_v2(self, player_id):
       """Get player's team history"""
   ```

---

### Phase 2: Enhanced Methods (MEDIUM PRIORITY)

Improve existing methods to match v2 specs:

1. **Update `get_games_v2`**
   - Add `status` parameter (scheduled, live, final)
   - Add `limit` parameter
   - Support team filtering

2. **Update `get_player_vs_defense_v2`**
   - Ensure using v2 endpoint
   - Add all documented parameters

3. **Update `get_game_team_stats_v2`**
   - Create or update to use v2 endpoint
   - Return proper v2 format

---

### Phase 3: Parameter Standardization (LOW PRIORITY)

Ensure all methods use v2-standard parameter names and types:

1. Convert team abbreviations to UUIDs where needed
2. Standardize pagination parameters
3. Add missing optional parameters

---

## 📋 Detailed Implementation Tasks

### Task 1: Add Missing Player Methods

**File:** `app/services/api_client.py`

```python
def get_players_list_v2(self, position=None, status=None, team=None, limit=50, offset=0):
    """
    List players with flexible filtering (API v2).

    Args:
        position: Filter by position (QB, RB, WR, TE, etc.)
        status: Filter by status (active, injured, etc.)
        team: Filter by team UUID
        limit: Results per page (default: 50)
        offset: Pagination offset (default: 0)

    Returns:
        List of players matching filters
    """
    params = {'limit': limit, 'offset': offset}
    if position:
        params['position'] = position
    if status:
        params['status'] = status
    if team:
        params['team'] = team

    response = requests.get(
        f'{self.base_url}/players',
        params=params,
        headers=self._get_headers(),
        timeout=self.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json().get('data', [])

def get_player_team_history_v2(self, player_id):
    """
    Get player's team history (API v2).

    Args:
        player_id: Player UUID

    Returns:
        List of teams player has been on
    """
    response = requests.get(
        f'{self.base_url}/players/{player_id}/history',
        headers=self._get_headers(),
        timeout=self.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json().get('data', [])
```

### Task 2: Add Missing Team Methods

```python
def get_teams_list_v2(self):
    """
    Get all 32 NFL teams (API v2).

    Returns:
        List of all NFL teams with details
    """
    response = requests.get(
        f'{self.base_url}/teams',
        headers=self._get_headers(),
        timeout=self.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json().get('data', [])

def get_team_by_id_v2(self, team_id):
    """
    Get detailed team information (API v2).

    Args:
        team_id: Team UUID

    Returns:
        Detailed team information
    """
    response = requests.get(
        f'{self.base_url}/teams/{team_id}',
        headers=self._get_headers(),
        timeout=self.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json().get('data', {})
```

### Task 3: Add Missing Game Methods

```python
def get_game_team_stats_v2(self, game_id):
    """
    Get team statistics for a specific game (API v2).

    Args:
        game_id: Game UUID

    Returns:
        Team statistics for the game
    """
    response = requests.get(
        f'{self.base_url}/games/{game_id}/stats',
        headers=self._get_headers(),
        timeout=self.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json().get('data', {})
```

---

## 🔧 Backend Routes to Add/Update

### New Routes Needed

**File:** `app/routes/advanced_stats.py`

1. **List Players with Filters**
   ```python
   @bp.route('/players', methods=['GET'])
   def list_players_filtered():
       """GET /api/advanced/players - List players with filters"""
   ```

2. **Player Team History**
   ```python
   @bp.route('/players/<player_id>/history', methods=['GET'])
   def get_player_history(player_id):
       """GET /api/advanced/players/:id/history"""
   ```

3. **All Teams**
   ```python
   @bp.route('/teams', methods=['GET'])
   def list_all_teams():
       """GET /api/advanced/teams"""
   ```

4. **Team Details**
   ```python
   @bp.route('/teams/<team_id>', methods=['GET'])
   def get_team_details(team_id):
       """GET /api/advanced/teams/:id"""
   ```

5. **Game Team Stats**
   ```python
   @bp.route('/games/<game_id>/stats', methods=['GET'])
   def get_game_statistics(game_id):
       """GET /api/advanced/games/:id/stats"""
   ```

---

## 🎨 Frontend Updates Needed

### New UI Components

1. **Player List View** - Browse/filter players
2. **Team Details Card** - Show stadium, colors, etc.
3. **Player History Timeline** - Show team changes
4. **Game Statistics Comparison** - Side-by-side team stats

### Updated Components

1. **PlayerSearch** - Add position/status filters
2. **TeamView** - Show all team details
3. **GameView** - Add team statistics section

---

## 📊 Expected Impact

### After Full Implementation:

- **API Coverage:** 100% (from 70%)
- **New Features:** 8+ new endpoints
- **Updated Features:** 5+ enhanced methods
- **Frontend Features:** 4+ new UI components
- **User Experience:** Significantly enhanced filtering and data access

---

## ✅ Success Criteria

Implementation will be considered complete when:

1. ✅ All documented v2 endpoints have corresponding methods
2. ✅ All methods use correct v2 parameter names
3. ✅ All methods tested and returning data
4. ✅ Backend routes expose all features
5. ✅ Frontend can access and display all data
6. ✅ Documentation updated
7. ✅ Test coverage ≥80%

---

## 🚀 Recommended Execution Order

1. **Today:** Implement missing API client methods (Phase 1)
2. **Today:** Add backend routes for new methods
3. **Today:** Test all new endpoints
4. **Next:** Update frontend components
5. **Next:** Enhance existing features (Phase 2)
6. **Future:** Parameter standardization (Phase 3)

---

## 📝 Notes

- Some endpoints may require authentication (check docs)
- UUIDs vs abbreviations need careful handling
- Pagination should be consistent across all list methods
- Error handling must be robust for all new methods

---

**Ready to implement?** Let's start with Phase 1 critical methods!
