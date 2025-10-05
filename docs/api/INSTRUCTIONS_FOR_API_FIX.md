# Instructions for Fixing Grid Iron Mind API Player Search

**Context:** You are working on the Grid Iron Mind NFL API codebase. The player search functionality is critically broken and needs to be fixed.

---

## Problem Statement

The `/api/v2/players` endpoint's `search` parameter returns completely wrong results:

**Current Behavior (BROKEN):**
```bash
# Searching for "mahomes" should return Patrick Mahomes
GET /api/v2/players?search=mahomes&status=active

# Returns: Aaron Banks, Aaron Brewer, Aaron Jones
# Missing: Patrick Mahomes (the target player!)
```

**Root Cause:**
The search is matching against ALL database columns (IDs, metadata, etc.) instead of just the player name field.

---

## Required Fix

### Step 1: Locate the Search Implementation

Find the code that handles the `search` parameter in the players endpoint. It's likely in one of these locations:

```
/api/routes/players.go          (if Go)
/api/routes/players.py           (if Python)
/api/routes/players.js           (if Node.js)
/api/handlers/players.go         (if Go)
/api/controllers/players_controller.rb  (if Rails)
```

Look for code like:
```go
// Current broken implementation (example in Go)
query := r.URL.Query().Get("search")
if query != "" {
    // This is probably matching all fields - WRONG
    db.Where("LOWER(CONCAT(name, team, id, ...)) LIKE ?", "%"+strings.ToLower(query)+"%")
}
```

### Step 2: Implement Name-Only Search

Replace the broken search with name-field-only matching:

**Option A: Simple PostgreSQL (Recommended Start)**

```go
// If using Go with GORM/database/sql
if searchQuery != "" {
    searchQuery = strings.ToLower(searchQuery)
    db = db.Where("LOWER(name) LIKE ?", "%"+searchQuery+"%")
}
```

```python
# If using Python with SQLAlchemy
if search_query:
    search_query = search_query.lower()
    query = query.filter(func.lower(Player.name).like(f"%{search_query}%"))
```

```javascript
// If using Node.js with Sequelize
if (searchQuery) {
    where.name = {
        [Op.iLike]: `%${searchQuery}%`
    };
}
```

**Option B: Full-Text Search (Better - Implement After Option A Works)**

```sql
-- PostgreSQL Full-Text Search
SELECT *,
  ts_rank(
    to_tsvector('english', name),
    plainto_tsquery('english', $1)
  ) AS search_rank
FROM players
WHERE to_tsvector('english', name) @@ plainto_tsquery('english', $1)
  AND status = $2
ORDER BY search_rank DESC, name ASC
LIMIT $3;
```

### Step 3: Add Relevance Scoring

Implement this scoring logic (in order of priority):

```go
// Pseudo-code for relevance scoring
func calculateRelevanceScore(playerName string, searchQuery string) float64 {
    name := strings.ToLower(playerName)
    query := strings.ToLower(searchQuery)

    // 1. Exact match - highest score
    if name == query {
        return 100.0
    }

    // 2. Name starts with query
    if strings.HasPrefix(name, query) {
        return 80.0
    }

    // 3. Name contains query
    if strings.Contains(name, query) {
        return 60.0
    }

    // 4. Word boundary match (any word starts with query)
    words := strings.Split(name, " ")
    for _, word := range words {
        if strings.HasPrefix(word, query) {
            return 50.0
        }
    }

    // 5. Fuzzy match with Levenshtein distance
    distance := levenshteinDistance(name, query)
    if distance <= 2 && len(query) > 4 {
        return 40.0 - float64(distance*5)
    }

    return 0.0
}
```

### Step 4: Order Results by Relevance

Make sure results are sorted by relevance score, NOT alphabetically:

```sql
-- WRONG (current):
ORDER BY name ASC

-- RIGHT (fixed):
ORDER BY search_rank DESC, name ASC
```

---

## Implementation Checklist

- [ ] **Find the search implementation** in the players endpoint handler
- [ ] **Identify the query builder** (GORM, SQLAlchemy, Sequelize, raw SQL, etc.)
- [ ] **Change search to match name field only** (not all columns)
- [ ] **Add relevance scoring** (exact > starts with > contains)
- [ ] **Sort by relevance** (DESC), then name (ASC) as tiebreaker
- [ ] **Test with these queries:**
  - `?search=mahomes` → Should return Patrick Mahomes first
  - `?search=saquon` → Should return Saquon Barkley first
  - `?search=justin jefferson` → Should return Justin Jefferson first
- [ ] **Preserve existing filters** (status, position, team, etc.)

---

## Test Cases (Copy-Paste for Validation)

After making changes, run these tests:

```bash
BASE_URL="http://localhost:8080/api/v2"  # Adjust port as needed

# Test 1: Patrick Mahomes (should be #1 result)
curl "${BASE_URL}/players?search=mahomes&status=active&limit=5" | jq '.data[0].name'
# Expected output: "Patrick Mahomes"

# Test 2: Saquon Barkley (should be #1 result)
curl "${BASE_URL}/players?search=saquon&status=active&limit=5" | jq '.data[0].name'
# Expected output: "Saquon Barkley"

# Test 3: Justin Jefferson (should be in top 3)
curl "${BASE_URL}/players?search=jefferson&status=active&limit=5" | jq '.data[] | .name'
# Expected: Justin Jefferson in results

# Test 4: Partial match
curl "${BASE_URL}/players?search=jef&status=active&limit=5" | jq '.data[] | .name'
# Expected: Players with "Jef" in name (Jefferson, etc.)

# Test 5: With position filter (ensure compatibility)
curl "${BASE_URL}/players?search=mahomes&status=active&position=QB&limit=5" | jq '.data[0].name'
# Expected output: "Patrick Mahomes"
```

**Success Criteria:**
- ✅ All 5 tests return the expected player in top result or top 3
- ✅ No irrelevant players in results (e.g., "Aaron Banks" for "mahomes")
- ✅ Results ordered by relevance, not alphabetically

---

## Code Examples by Framework

### Example 1: Go + GORM

**Before (Broken):**
```go
func GetPlayers(c *gin.Context) {
    searchQuery := c.Query("search")

    db := database.DB

    // BROKEN: Matches all fields
    if searchQuery != "" {
        db = db.Where("LOWER(CAST(id AS TEXT)) LIKE ? OR LOWER(name) LIKE ?",
            "%"+strings.ToLower(searchQuery)+"%",
            "%"+strings.ToLower(searchQuery)+"%")
    }

    db.Order("name ASC").Find(&players)  // Wrong order
}
```

**After (Fixed):**
```go
func GetPlayers(c *gin.Context) {
    searchQuery := c.Query("search")
    status := c.Query("status")
    position := c.Query("position")

    db := database.DB.Model(&Player{})

    // Apply filters
    if status != "" {
        db = db.Where("status = ?", status)
    }
    if position != "" {
        db = db.Where("position = ?", position)
    }

    var players []Player

    // FIXED: Search name field only
    if searchQuery != "" {
        searchQuery = strings.ToLower(searchQuery)

        // Use raw SQL for relevance scoring
        db = db.Select(`*,
            CASE
                WHEN LOWER(name) = ? THEN 100
                WHEN LOWER(name) LIKE ? THEN 80
                WHEN LOWER(name) LIKE ? THEN 60
                ELSE 0
            END as relevance_score`,
            searchQuery,
            searchQuery+"%",
            "%"+searchQuery+"%",
        ).Where("LOWER(name) LIKE ?", "%"+searchQuery+"%")

        // Order by relevance, then name
        db = db.Order("relevance_score DESC, name ASC")
    } else {
        db = db.Order("name ASC")
    }

    db.Limit(20).Find(&players)

    c.JSON(200, gin.H{"data": players})
}
```

### Example 2: Python + SQLAlchemy

**Before (Broken):**
```python
def get_players():
    search_query = request.args.get('search', '')

    query = Player.query

    # BROKEN: Matches all fields
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Player.name.ilike(search_pattern),
                Player.id.ilike(search_pattern),  # WRONG
                Player.team.ilike(search_pattern)  # WRONG
            )
        )

    players = query.order_by(Player.name).limit(20).all()  # Wrong order
```

**After (Fixed):**
```python
from sqlalchemy import case, func

def get_players():
    search_query = request.args.get('search', '')
    status = request.args.get('status', '')
    position = request.args.get('position', '')

    query = Player.query

    # Apply filters
    if status:
        query = query.filter(Player.status == status)
    if position:
        query = query.filter(Player.position == position)

    # FIXED: Search name only with relevance scoring
    if search_query:
        search_lower = search_query.lower()

        # Add relevance score column
        relevance = case(
            (func.lower(Player.name) == search_lower, 100),
            (func.lower(Player.name).startswith(search_lower), 80),
            (func.lower(Player.name).contains(search_lower), 60),
            else_=0
        )

        query = query.add_columns(relevance.label('relevance_score'))
        query = query.filter(func.lower(Player.name).like(f"%{search_lower}%"))
        query = query.order_by(relevance.desc(), Player.name.asc())
    else:
        query = query.order_by(Player.name.asc())

    players = query.limit(20).all()

    return jsonify({"data": [p.to_dict() for p in players]})
```

### Example 3: Node.js + Sequelize

**Before (Broken):**
```javascript
async function getPlayers(req, res) {
    const { search, status, position } = req.query;

    const where = {};

    // BROKEN: Matches all fields
    if (search) {
        where[Op.or] = [
            { name: { [Op.iLike]: `%${search}%` } },
            { id: { [Op.iLike]: `%${search}%` } },  // WRONG
            { team: { [Op.iLike]: `%${search}%` } }  // WRONG
        ];
    }

    const players = await Player.findAll({
        where,
        order: [['name', 'ASC']],  // Wrong order
        limit: 20
    });
}
```

**After (Fixed):**
```javascript
const { Op, Sequelize } = require('sequelize');

async function getPlayers(req, res) {
    const { search, status, position } = req.query;

    const where = {};

    // Apply filters
    if (status) where.status = status;
    if (position) where.position = position;

    // FIXED: Search name only with relevance scoring
    if (search) {
        const searchLower = search.toLowerCase();

        where.name = { [Op.iLike]: `%${searchLower}%` };

        const players = await Player.findAll({
            where,
            attributes: {
                include: [
                    [
                        Sequelize.literal(`
                            CASE
                                WHEN LOWER(name) = '${searchLower}' THEN 100
                                WHEN LOWER(name) LIKE '${searchLower}%' THEN 80
                                WHEN LOWER(name) LIKE '%${searchLower}%' THEN 60
                                ELSE 0
                            END
                        `),
                        'relevance_score'
                    ]
                ]
            },
            order: [
                [Sequelize.literal('relevance_score'), 'DESC'],
                ['name', 'ASC']
            ],
            limit: 20
        });

        return res.json({ data: players });
    }

    // No search - just return ordered by name
    const players = await Player.findAll({
        where,
        order: [['name', 'ASC']],
        limit: 20
    });

    return res.json({ data: players });
}
```

---

## Validation Steps

1. **Make the code changes** based on your framework (see examples above)

2. **Restart the API server**
   ```bash
   # Go
   go run main.go

   # Python
   python app.py
   # or
   flask run

   # Node.js
   npm start
   # or
   node server.js
   ```

3. **Run the test commands** (see "Test Cases" section above)

4. **Verify all tests pass:**
   - Patrick Mahomes is #1 for "mahomes" search
   - Saquon Barkley is #1 for "saquon" search
   - Justin Jefferson appears in top 3 for "jefferson" search
   - No random/irrelevant players in results

5. **Check that existing filters still work:**
   ```bash
   # Position filter
   curl "${BASE_URL}/players?position=QB&limit=10" | jq '.data[].position'
   # All should be "QB"

   # Status filter
   curl "${BASE_URL}/players?status=active&limit=10" | jq '.data[].status'
   # All should be "active"

   # Combined filters
   curl "${BASE_URL}/players?search=smith&position=WR&status=active&limit=10"
   # Should return active WR players named Smith
   ```

---

## Performance Optimization (Do After Basic Fix Works)

### Add Database Index

```sql
-- PostgreSQL
CREATE INDEX idx_players_name_lower ON players (LOWER(name));
CREATE INDEX idx_players_status ON players (status);
CREATE INDEX idx_players_position ON players (position);

-- For full-text search (advanced)
CREATE INDEX idx_players_name_fts ON players USING GIN (to_tsvector('english', name));
```

### Add Caching for Common Searches

```go
// Example: Cache top 20 results for each search query
var searchCache = make(map[string][]Player)

func GetPlayers(c *gin.Context) {
    searchQuery := c.Query("search")
    cacheKey := fmt.Sprintf("search:%s", searchQuery)

    // Check cache first
    if cached, ok := searchCache[cacheKey]; ok {
        c.JSON(200, gin.H{"data": cached, "cached": true})
        return
    }

    // ... execute search query ...

    // Store in cache
    searchCache[cacheKey] = players

    c.JSON(200, gin.H{"data": players, "cached": false})
}
```

---

## Common Issues & Solutions

### Issue 1: "Column 'relevance_score' not found"

**Solution:** Make sure relevance_score is added as a computed column, not selected from database:

```sql
-- Use CASE statement or calculated field
SELECT *,
  CASE
    WHEN LOWER(name) = 'mahomes' THEN 100
    ...
  END as relevance_score
FROM players
```

### Issue 2: Results still ordered alphabetically

**Solution:** Check ORDER BY clause - relevance must come BEFORE name:

```sql
-- WRONG
ORDER BY name ASC, relevance_score DESC

-- RIGHT
ORDER BY relevance_score DESC, name ASC
```

### Issue 3: Search is case-sensitive

**Solution:** Convert both search query and name to lowercase:

```go
// Go
db.Where("LOWER(name) LIKE ?", "%"+strings.ToLower(searchQuery)+"%")

// SQL
WHERE LOWER(name) LIKE LOWER($1)
```

### Issue 4: Special characters breaking search

**Solution:** Sanitize input and escape SQL wildcards:

```go
// Escape SQL wildcards
searchQuery = strings.ReplaceAll(searchQuery, "%", "\\%")
searchQuery = strings.ReplaceAll(searchQuery, "_", "\\_")
```

---

## Final Checklist

Before considering the fix complete:

- [ ] Code only searches the `name` field
- [ ] Results are ordered by relevance score (DESC)
- [ ] All 5 test cases pass
- [ ] Existing filters (status, position, team) still work
- [ ] No performance regression (response time < 200ms)
- [ ] Database indexes added for `name` column
- [ ] Code is committed with clear commit message
- [ ] API documentation updated with search behavior

---

## Questions to Ask Me

If you run into issues:

1. **"What framework/ORM is the API using?"**
   - Look for imports: gorm, sqlalchemy, sequelize, etc.
   - Share the player handler code with me

2. **"Where is the search logic located?"**
   - Search codebase for `"search"` parameter
   - Look in routes/handlers/controllers for players endpoint

3. **"How do I add a computed column for relevance score?"**
   - Share your current query builder code
   - I'll show you the syntax for your specific ORM

4. **"Tests are failing - what am I missing?"**
   - Share the test output
   - Share your modified code
   - I'll help debug

---

## Success Indicators

You'll know the fix worked when:

✅ Searching "mahomes" returns **Patrick Mahomes** as the first result
✅ Searching "saquon" returns **Saquon Barkley** as the first result
✅ Searching "jefferson" returns **Justin Jefferson** in top 3
✅ No irrelevant players appear in search results
✅ Position and status filters still work correctly
✅ API response time stays under 200ms

Good luck! This fix will make player search actually usable for all applications using the Grid Iron Mind API.
