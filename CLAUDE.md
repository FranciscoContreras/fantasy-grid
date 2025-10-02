# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fantasy Grid is a **production-ready fantasy football player recommendation application** featuring AI-powered player analysis, matchup ratings, weather impact assessments, and intelligent start/sit recommendations. The application integrates with the Grid Iron Mind NFL API and includes user authentication, roster management, and head-to-head matchup analysis.

## Architecture

**Full-stack monorepo structure:**
- **Backend:** Python 3.11 + Flask (serves both API and static frontend)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind + shadcn/ui
- **Database:** PostgreSQL with connection pooling
- **Cache:** Redis (optional, falls back to in-memory)
- **Deployment:** Heroku (Gunicorn WSGI server)
- **External API:** Grid Iron Mind NFL API **v2** (with Next Gen Stats, EPA, CPOE)

**Major v2 Upgrade:**
The application now integrates with Grid Iron Mind API v2, unlocking advanced capabilities:
- **Next Gen Stats**: Air yards, separation, YAC, time to throw, etc.
- **EPA/CPOE**: Expected Points Added, Completion Percentage Over Expected
- **Play-by-Play Data**: Detailed game analysis with every play
- **Enhanced Filtering**: Better query performance and filtering
- **AI-Powered Predictions**: Claude-powered game and player predictions
- **Sub-200ms Response Times**: Redis-backed caching on API side

**Key Pattern:** The Flask backend serves the built frontend as static files from `app/static/`, enabling single-deployment architecture on Heroku.

## API v2 Integration (Grid Iron Mind)

### What's New in v2

The application leverages Grid Iron Mind API v2, which provides transformative capabilities beyond basic player stats.

**Advanced Statistics:**
- **Next Gen Stats**: NFL's official advanced tracking data (player separation, air yards, time to throw, route efficiency)
- **EPA (Expected Points Added)**: Measures play efficiency and player impact (>0.2 per play = elite)
- **CPOE (Completion % Over Expected)**: QB accuracy metric accounting for throw difficulty
- **Success Rate**: Percentage of plays with positive EPA
- **WOPR (Weighted Opportunity Rating)**: Combines target/air yard share for WR/TE value

**Enhanced Capabilities:**
- **Play-by-Play Data**: Every play with EPA, WPA, player involvement
- **Scoring Plays**: Detailed touchdown and scoring summaries
- **Enhanced Injury Reports**: Practice participation, game status, timeline
- **Advanced Defense Stats**: Pressure rate, coverage metrics, EPA allowed, stuff rate
- **Claude AI Predictions**: Natural language queries and player/game predictions

**API Client Usage (`app/services/api_client.py`):**
```python
api_client = FantasyAPIClient()  # Auto-uses v2 by default

# Advanced stats
stats = api_client.get_player_advanced_stats(player_id, season=2024, week=5)

# Play-by-play
plays = api_client.get_game_play_by_play(game_id)

# AI predictions
prediction = api_client.ai_predict_player_v2(player_id)
insights = api_client.ai_player_insights_v2(player_id)

# Natural language
result = api_client.ai_query_v2("Top 5 rushing leaders this season?")
```

**New Advanced Routes (`app/routes/advanced_stats.py`):**
- `/api/advanced/players/:id/nextgen` - Next Gen Stats
- `/api/advanced/players/:id/enhanced-analysis` - Full analysis with Next Gen Stats
- `/api/advanced/games/:id/play-by-play` - Complete play-by-play
- `/api/advanced/defense/rankings` - Advanced defense metrics
- `/api/advanced/ai/query` - Natural language queries
- `/api/advanced/ai/predict/player/:id` - Claude player predictions
- `/api/advanced/standings` - NFL standings

**Database Schema v2 (`schema_v2_updates.sql`):**
New tables for advanced data:
- `player_advanced_stats` - Next Gen Stats, EPA, CPOE per week
- `play_by_play` - Detailed play data with EPA/WPA
- `scoring_plays` - Scoring summaries
- `injury_reports` - Enhanced injury tracking with practice status
- `defense_advanced_stats` - Advanced defensive metrics
- `game_weather` - Stadium weather with impact multipliers

**Frontend Types (`frontend/src/types/advancedStats.ts`):**
TypeScript interfaces for all v2 data structures:
- `AdvancedPlayerStats`, `NextGenStatsQB/Receiver/Rusher`
- `PlayByPlayData`, `ScoringPlay`
- `InjuryReport`, `DefenseAdvancedStats`
- `AIGamePrediction`, `AIPlayerPrediction`, `AIPlayerInsights`

**Key Metrics Explained:**
- **EPA**: Positive = good, >0.2/play = elite QB/RB, <-0.1 = struggling
- **CPOE**: >+3% = exceptional accuracy, <-3% = below expected
- **Separation (WR)**: >3.5 yd = excellent route running
- **Time to Throw (QB)**: <2.3s = quick release, >2.8s = holds ball
- **Yards Over Expected (RB)**: >+0.5/att = elite vision/elusiveness
- **WOPR (WR/TE)**: >0.7 = dominant opportunity

### Migration from v1 to v2

**Environment Variable:**
```bash
API_VERSION=v2  # Default, can override to v1
```

**Backward Compatibility:**
All v1 methods still work. New v2-specific methods have `_v2` suffix. Gradual migration supported.

**To Fully Adopt v2:**
1. Apply schema: `psql $DATABASE_URL < schema_v2_updates.sql`
2. Update frontend to display advanced stats using `AdvancedStatsPanel` component
3. Leverage AI prediction endpoints for enhanced recommendations
4. Use advanced matchup scoring in analyzer

## Development Commands

### Backend Development

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run dev server (port 5000)
python wsgi.py

# Initialize database schema
python -c "from app.database import init_db; init_db()"

# Run with Gunicorn (production-like)
gunicorn wsgi:app --timeout 300
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Development server with hot reload (port 5173)
npm run dev

# Build for production (outputs to frontend/dist/, then copied to app/static/)
npm run build

# Type check + build
npm run build:check

# Lint
npm run lint

# Preview production build locally
npm run preview
```

### Testing

```bash
# Test API endpoints
./test-endpoints.sh

# Manual testing reference
See TESTING.md for comprehensive test cases
```

## Project Structure

```
fantasy-grid/
├── app/                          # Flask application (main backend)
│   ├── __init__.py              # Flask factory, blueprint registration
│   ├── database.py              # PostgreSQL connection pool
│   ├── routes/                  # API endpoints (blueprints)
│   │   ├── auth.py             # JWT authentication
│   │   ├── players.py          # Player search/details
│   │   ├── analysis.py         # Player analysis + comparison
│   │   ├── predictions.py      # AI predictions
│   │   ├── rosters.py          # Roster CRUD
│   │   └── matchups.py         # Matchup analysis
│   ├── services/                # Business logic layer
│   │   ├── api_client.py       # Grid Iron Mind API wrapper
│   │   ├── analyzer.py         # Matchup/weather analysis
│   │   ├── ai_grader.py        # ML-based player grading
│   │   ├── ai_service.py       # LLM integrations (Groq/Anthropic/Gemini)
│   │   ├── weather_service.py  # Weather data processing
│   │   ├── auth_service.py     # User auth + JWT
│   │   └── cache_service.py    # Caching helpers
│   ├── models/                  # Data models (Marshmallow schemas)
│   ├── utils/                   # Utilities
│   │   └── cache.py            # Redis cache decorator + helpers
│   ├── validation/              # Request validation
│   └── static/                  # Built frontend files (from frontend/dist/)
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ui/            # shadcn components
│   │   │   ├── Auth.tsx       # Login/register
│   │   │   ├── PlayerSearch.tsx
│   │   │   ├── RosterBuilder.tsx
│   │   │   ├── MatchupAnalysis.tsx
│   │   │   └── ...
│   │   ├── pages/             # Page-level components
│   │   ├── lib/
│   │   │   └── api.ts         # Axios client for backend API
│   │   ├── types/             # TypeScript type definitions
│   │   └── hooks/             # React custom hooks
│   ├── package.json
│   └── vite.config.ts
├── wsgi.py                      # Entry point (creates Flask app)
├── Procfile                     # Heroku deployment config
├── requirements.txt             # Python dependencies
├── schema.sql                   # Database schema
└── API_DOCUMENTATION.md         # Complete API reference
```

## Key Implementation Details

### Backend Architecture

**Flask App Factory (`app/__init__.py`):**
- Connection pool initialization on startup
- Request ID middleware for log tracing
- Health check endpoint at `/health` (checks DB + Redis)
- Cache management endpoints at `/api/cache/*`
- Serves frontend from `/` and `/<path>` (SPA fallback routing)

**Database Layer (`app/database.py`):**
- Uses `psycopg2.pool.SimpleConnectionPool` for connection management
- `execute_query()` handles transactions automatically
- RealDictCursor returns rows as dicts
- Auto-commit for INSERT/UPDATE/DELETE, auto-rollback on errors

**Caching Strategy (`app/utils/cache.py`):**
- Redis primary, graceful fallback to function execution if unavailable
- Decorator pattern: `@cached_route(expiry=3600, key_prefix='players')`
- Pattern-based invalidation: `invalidate_cache('players:*')`
- Hybrid caching: Redis for fast access, PostgreSQL for AI analysis persistence

**Authentication (`app/services/auth_service.py`):**
- JWT tokens with 24-hour expiration
- Bcrypt password hashing
- Protected routes use `@login_required` decorator
- Token in `Authorization: Bearer <token>` header

**AI Analysis (`app/services/ai_grader.py` + `ai_service.py`):**
- Multi-provider support: Groq (default), Anthropic Claude, Google Gemini
- Structured output with matchup scores (0-100), grades (A+ to F), recommendations
- PostgreSQL cache table (`ai_analysis_cache`) prevents redundant LLM calls

### Frontend Architecture

**API Client (`frontend/src/lib/api.ts`):**
- Axios instance with base URL from env vars
- Request interceptor adds JWT token to headers
- Response interceptor handles 401 (redirect to login)

**State Management:**
- Local state with React hooks
- Auth state persisted in localStorage
- No global state library (intentionally simple)

**Routing:**
- React Router with protected routes
- Auth guard checks token validity
- SPA with Flask fallback for refresh handling

### Database Schema Highlights

**Core Tables:**
- `users` - Authentication (email, username, hashed password)
- `rosters` - User fantasy teams
- `roster_players` - Players in rosters (with positions/slots)
- `matchups` - Head-to-head matchup definitions
- `matchup_analysis` - AI analysis results per player per matchup
- `ai_analysis_cache` - Cached AI analysis (prevents redundant API calls)
- `player_stats` - Historical player performance (populated from Grid Iron Mind)

See `schema.sql` for complete schema with indexes.

## Environment Variables

### Backend (.env)
```bash
SECRET_KEY=<random-secret-key>           # Flask + JWT signing
DATABASE_URL=<postgres-url>              # PostgreSQL connection string
API_BASE_URL=https://nfl.wearemachina.com/api/v1  # Grid Iron Mind API
API_KEY=<grid-iron-mind-api-key>        # Optional, for AI endpoints
REDIS_URL=<redis-url>                    # Optional, for caching
AI_PROVIDER=groq                         # groq|anthropic|gemini
GROQ_API_KEY=<groq-key>                 # For AI analysis
ANTHROPIC_API_KEY=<anthropic-key>       # Alternative AI provider
GEMINI_API_KEY=<gemini-key>             # Alternative AI provider
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:5000/api  # Development
```

### Frontend (.env.production)
```bash
VITE_API_URL=/api                        # Production (same origin)
```

## Common Development Tasks

### Building and Deploying Frontend

The frontend must be built and copied to `app/static/` for Flask to serve it:

```bash
cd frontend
npm run build

# Copy built files to Flask static directory
rm -rf ../app/static/*
cp -r dist/* ../app/static/
```

For Heroku deployment, this happens automatically via the `build` script in the main Procfile.

### Adding New API Endpoints

1. Create route function in appropriate blueprint (`app/routes/*.py`)
2. Add validation decorator if needed (`@validate_json(MySchema)`)
3. Use `@login_required` for protected endpoints
4. Register blueprint in `app/__init__.py` if new file
5. Document in `API_DOCUMENTATION.md`

### Adding New Frontend Components

1. Create component in `frontend/src/components/`
2. Define TypeScript types in `frontend/src/types/`
3. Use shadcn/ui components from `frontend/src/components/ui/`
4. Add API calls via `frontend/src/lib/api.ts`
5. Import and use in pages or other components

### Cache Management

**Invalidate cache after data changes:**
```python
from app.utils.cache import invalidate_player_cache, invalidate_matchup_cache

# After updating player data
invalidate_player_cache(player_id)

# After matchup analysis
invalidate_matchup_cache(matchup_id=123)

# Clear all cache
from app.utils.cache import clear_all_cache
clear_all_cache()
```

**Check cache stats:**
```bash
curl http://localhost:5000/api/cache/stats
```

### Database Migrations

No formal migration system (Alembic) is used. To update schema:

1. Edit `schema.sql`
2. Create migration SQL in `schema_updates.sql` (if needed)
3. Apply manually:
   ```bash
   psql $DATABASE_URL < schema_updates.sql
   ```

For fresh installs, use `init_db()` to apply full schema.

## Testing

**Manual API Testing:**
```bash
# Health check
curl http://localhost:5000/health

# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"test1234"}'

# Search players
curl "http://localhost:5000/api/players/search?query=mahomes"

# Run all endpoint tests
./test-endpoints.sh
```

See `TESTING.md` for comprehensive manual test cases covering all features.

## Deployment

**Heroku Deployment:**
```bash
# Initial setup
heroku create fantasy-grid-app
heroku addons:create heroku-postgresql:essential-0
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set SECRET_KEY=$(python -c 'import os; print(os.urandom(24).hex())')
heroku config:set API_KEY=your-grid-iron-mind-key
heroku config:set GROQ_API_KEY=your-groq-key

# Deploy
git push heroku main

# Initialize database
heroku run python -c "from app.database import init_db; init_db()"
```

**Post-Deployment:**
- Access app at `https://fantasy-grid-app.herokuapp.com`
- Check health: `https://fantasy-grid-app.herokuapp.com/health`
- View logs: `heroku logs --tail`

## Important Notes

**Grid Iron Mind API Integration:**
- Public endpoints (players, teams, weather) don't require API key
- AI endpoints require API key in `X-API-Key` header
- Rate limits: 100 req/min (public), 10 req/min (AI standard tier)
- Full API docs in `instructions.md`

**Authentication Flow:**
- JWT tokens expire after 24 hours
- Frontend auto-redirects to login on 401
- Tokens stored in localStorage (consider httpOnly cookies for production hardening)

**AI Analysis:**
- Groq is default provider (fast, cost-effective)
- Can switch to Anthropic Claude or Google Gemini via `AI_PROVIDER` env var
- Results cached in PostgreSQL to avoid redundant LLM calls
- Analysis runs async for matchups (status polling pattern)

**Caching:**
- Player data: 30 minutes
- Roster data: 1 hour
- AI analysis: Stored in DB, invalidated manually
- Weather data: 15 minutes

**Frontend Build Process:**
- Vite builds to `frontend/dist/`
- Must be copied to `app/static/` before Flask deployment
- Heroku buildpack handles this automatically

## Reference Documentation

- **BUILD.md** - Step-by-step setup guide (36 phases)
- **API_DOCUMENTATION.md** - Complete API reference with examples
- **instructions.md** - Grid Iron Mind API documentation
- **TESTING.md** - Manual test procedures
- **AGENTS.md** - Multi-agent development approach (if applicable)

## Common Issues

**Database connection errors:**
- Verify `DATABASE_URL` env var
- Check connection pool settings in `app/database.py`
- Heroku: Ensure `heroku-postgresql` addon is attached

**Frontend not loading:**
- Ensure frontend was built: `cd frontend && npm run build`
- Verify files copied to `app/static/`
- Check Flask serves static files from correct path

**Cache not working:**
- Redis is optional; app works without it
- Check `REDIS_URL` env var if Redis expected
- View cache status at `/api/cache/stats`

**AI analysis failing:**
- Verify AI provider API key is set (GROQ_API_KEY, etc.)
- Check `AI_PROVIDER` env var matches available key
- Review Heroku logs for LLM API errors

## Code Style

- Python: PEP 8 (Flask conventions)
- TypeScript: ESLint rules in `frontend/.eslintrc`
- Use type hints in Python where beneficial
- Frontend components use functional components + hooks
- API responses follow consistent JSON structure: `{ "data": {...}, "message": "..." }` or `{ "error": "..." }`
