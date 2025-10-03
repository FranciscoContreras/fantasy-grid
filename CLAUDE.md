# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fantasy Grid is a **production-ready fantasy football player recommendation application** featuring AI-powered player analysis, matchup ratings, weather impact assessments, and intelligent start/sit recommendations. The application integrates with the Grid Iron Mind NFL API and includes user authentication, roster management, and head-to-head matchup analysis.

## 🚀 Production Status & Critical Information

### Current Status: ✅ PRODUCTION READY & DEPLOYED
- **Live URL**: https://fantasy-grid-8e65f9ca9754.herokuapp.com/
- **Deployment**: Heroku (Hobby dyno + PostgreSQL Essential-0 + Redis Mini)
- **API Version**: Grid Iron Mind API v2 (95% endpoint coverage, unlimited tier active)
- **Last Deploy**: v127 (October 2, 2025)
- **Monthly Cost**: ~$15/month

### Completed Features (8 Phases + Extensions)
✅ User authentication (JWT with 24-hour tokens)
✅ Roster management (multi-roster, position-based)
✅ Matchup analysis with AI grading
✅ Advanced statistics (Next Gen Stats, EPA, CPOE)
✅ Landing page (Nike-inspired dark theme)
✅ Onboarding wizard (3-step, <3min to value)
✅ Weekly lineup UI (START/CONSIDER/BENCH centerpiece)
✅ Trade analyzer
✅ Matchup exploiter
✅ League intelligence
✅ PWA (installable, offline support)

### Critical Constraints & Known Issues

**⚠️ P0 BLOCKERS (Must Address Before Scale)**:
1. **Unsafe background threading** (`app/routes/matchups.py:335-377`)
   - Uses daemon threads without error handling
   - **Impact**: Lost analysis on restart, crashes under load
   - **Fix Required**: Implement Celery or RQ with Redis

2. **Hardcoded business logic** (season-sensitive data)
   - Defensive rankings: `matchups.py:724-728`
   - Defensive coordinators: `api_client.py:452-464`
   - Stadium locations: `weather_service.py:21-54`
   - **Impact**: Requires code deployment for data updates
   - **Fix Required**: Use Grid Iron Mind API for dynamic data

3. **No input validation** (security risk)
   - Missing Marshmallow schemas for request validation
   - No sanitization before DB insertion
   - **Impact**: SQL injection risk, data corruption
   - **Fix Required**: Add validation decorators

**⚠️ P1 High Priority**:
- No automated tests (0% unit test coverage)
- No CSRF protection
- JWT tokens in localStorage (should use httpOnly cookies)
- No HTTPS enforcement
- Performance bottlenecks (N+1 queries in matchup routes)

### Database Strategy: OPTIONAL
**The app works WITHOUT a database** for basic features:
- ✅ Player search, analysis, weather, AI grading, advanced stats
- ❌ User accounts, rosters, matchups, caching, history

**If DATABASE_URL missing**: App logs warning and runs in API-only mode. All code must handle gracefully:
```python
if not connection_pool:
    logger.warning("DATABASE_URL not configured - running in API-only mode")
    return None
```

### API Integration: CRITICAL PATTERNS

**ALWAYS use timeouts** (all API calls have 10-second timeout):
```python
response = requests.get(url, timeout=10)
```

**NEVER hardcode NFL data** - use Grid Iron Mind API:
```python
# ❌ AVOID
DEFENSIVE_RANKINGS = {"NYJ": 92, "BUF": 88, ...}

# ✅ CORRECT
rankings = api_client.get_defense_stats(season=2024)
```

**NEVER add background jobs with threading** - use Celery when available:
```python
# ❌ AVOID
thread = Thread(target=analyze_matchup, daemon=True)
thread.start()

# ✅ CORRECT (when Celery implemented)
analyze_matchup.delay(matchup_id)
```

### Product Mission & UX Principles

**Core Mission**: *"The key focus is to see which players you should start in fantasy to win the week"*

**Time to Value**: < 3 minutes from signup to first recommendation
**Visual Hierarchy**: START/CONSIDER/BENCH front and center
**Color System**: Green (START), Yellow (CONSIDER), Red (BENCH)
**Mobile-First**: Cards stack, large touch targets, swipe gestures

**Target Metrics**:
- Landing → Sign Up: >15% conversion
- Sign Up → First Roster: >80% completion
- Weekly Lineup View: Primary for 90% of users

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
See docs/guides/development/TESTING.md for comprehensive test cases
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
└── docs/                         # All documentation (organized)
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
- Full API docs in `docs/api/grid-iron-mind-api.md`

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

### Quick Links
- **[Documentation Hub](docs/README.md)** - Master index of all documentation
- **[Getting Started](docs/guides/getting-started/START_HERE.md)** - First-time setup
- **[Quick Start](docs/guides/getting-started/QUICKSTART.md)** - Get running quickly
- **[Complete Build Guide](docs/guides/getting-started/BUILD.md)** - Step-by-step setup (36 phases)

### API Documentation
- **[Fantasy Grid API](docs/api/fantasy-grid-api.md)** - Internal API reference with examples
- **[Grid Iron Mind API](docs/api/grid-iron-mind-api.md)** - External NFL API documentation
- **[API V2 Migration](docs/api/v2-migration/)** - v2 upgrade documentation

### Development Guides
- **[Testing Guide](docs/guides/development/TESTING.md)** - Manual test procedures
- **[Agent Roles](docs/guides/development/AGENTS.md)** - Multi-agent development approach
- **[Database Setup](docs/guides/setup/DATABASE_SETUP.md)** - PostgreSQL configuration

### Planning & Reports
- **[Product Roadmap](docs/planning/product-roadmap.md)** - Long-term product vision
- **[Landing Page Strategy](docs/planning/landing-page-strategy.md)** - UX and conversion strategy
- **[Production Readiness](docs/reports/production-readiness.md)** - Production status report

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

## 🔜 Next Steps & Roadmap

### Immediate Priority (Week 1-2) - Critical Fixes

**🔴 P0: Replace Background Threading with Celery**
- **Location**: `app/routes/matchups.py:335-377`
- **Problem**: Daemon threads without error handling = lost analysis + crashes
- **Solution**:
  ```bash
  pip install celery redis
  # Create app/tasks/celery_app.py
  # Create app/tasks/matchup_tasks.py
  # Update matchups.py to use task.delay()
  ```
- **Impact**: Production-grade job processing with retries and status tracking

**🔴 P0: Add Input Validation**
- **Problem**: No Marshmallow schemas = SQL injection risk
- **Solution**:
  ```python
  from marshmallow import Schema, fields, validate
  from app.validation import validate_json

  class RosterSchema(Schema):
      name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
      league_name = fields.Str(validate=validate.Length(max=100))
      scoring_type = fields.Str(validate=validate.OneOf(['PPR', 'HALF_PPR', 'STANDARD']))

  @bp.route('/rosters', methods=['POST'])
  @validate_json(RosterSchema)
  def create_roster(validated_data):
      # validated_data is sanitized and validated
  ```
- **Files to Update**: All routes in `app/routes/`

**🔴 P0: Remove Hardcoded Data**
- **Locations**:
  - `matchups.py:724-728` - Defensive rankings
  - `api_client.py:452-464` - Defensive coordinators
  - `weather_service.py:21-54` - Stadium locations
- **Solution**: Use Grid Iron Mind API endpoints
  ```python
  # Replace hardcoded rankings
  rankings = api_client.get_defense_stats(season=2024, week=current_week)

  # Get key players dynamically
  team_players = api_client.get_team_players(team_id)
  ```

### Short-term (Week 3-4) - Production Hardening

**🟡 Security Hardening**
1. Add CSRF protection:
   ```bash
   pip install flask-wtf
   ```
2. Move JWT to httpOnly cookies (currently in localStorage)
3. Add HTTPS enforcement in Flask config
4. Implement rate limiting:
   ```bash
   pip install flask-limiter
   ```
5. Add input sanitization for all text fields

**🟡 Monitoring & Observability**
1. Set up Sentry for error tracking:
   ```bash
   pip install sentry-sdk[flask]
   ```
2. Add structured logging (JSON format):
   ```python
   import structlog
   logger = structlog.get_logger()
   logger.info("user_registered", user_id=user.id, email=user.email)
   ```
3. Implement uptime monitoring (UptimeRobot or similar)
4. Add performance monitoring (New Relic or Datadog)

**🟡 Testing Suite**
1. Set up pytest:
   ```bash
   pip install pytest pytest-cov pytest-flask
   ```
2. Target 70%+ unit test coverage
3. Add integration tests for API flows
4. E2E tests with Playwright (frontend)

### Medium-term (Month 2) - Scalability

**🟢 Database Migrations**
- Set up Alembic for schema versioning:
  ```bash
  pip install alembic
  alembic init migrations
  ```
- Create migration for schema v2 updates
- Automate migrations in Heroku release phase

**🟢 Performance Optimization**
- Fix N+1 queries in matchup routes (use JOIN or batch queries)
- Implement async API calls with `aiohttp`:
  ```python
  import aiohttp
  async def fetch_all_players(player_ids):
      async with aiohttp.ClientSession() as session:
          tasks = [fetch_player(session, pid) for pid in player_ids]
          return await asyncio.gather(*tasks)
  ```
- Add database read replicas for query scaling
- Implement CDN for static assets (CloudFlare)

**🟢 API Documentation**
- Generate OpenAPI/Swagger spec:
  ```bash
  pip install flask-swagger-ui
  ```
- Add interactive API docs at `/api/docs`
- Include example requests/responses

### Long-term (Quarter 2) - Growth Features

**🔵 Real-time Features**
- WebSocket support for live updates:
  ```bash
  pip install flask-socketio
  ```
- Push notifications (Web Push API)
- Live injury alerts
- Game-day score tracking

**🔵 Advanced Analytics**
- User behavior tracking (Mixpanel/Amplitude)
- A/B testing framework (Optimizely)
- Conversion funnel analysis
- Feature usage heatmaps

**🔵 Monetization**
- Implement Stripe payment integration
- Create subscription tiers (Free/Pro/Premium)
- Tiered feature gating
- Annual vs monthly pricing

**🔵 Mobile App**
- React Native mobile app
- Native push notifications
- Offline-first architecture
- App Store + Play Store deployment

### API v2 Pending Items

**⏳ Waiting on Provider** (no code changes needed):
1. `/api/v2/games/{id}/stats` - Returns 404 (not deployed by provider)
2. `/api/v2/teams/{id}/schedule?season=2024` - Returns 400 (validation issue)

**Once available**, automatically work without code changes due to existing client methods.

### Future Enhancements (Backlog)

**Features from Roadmap**:
- Waiver wire assistant (AI-powered pickup recommendations)
- Injury impact predictor (ML model for replacement value)
- Trade finder (scan league for mutual benefit trades)
- Draft assistant (real-time draft recommendations)
- League sync (ESPN/Yahoo/Sleeper integration)
- Multi-league aggregation (manage 10+ leagues in one view)
- Expert consensus integration (FantasyPros, etc.)
- Custom scoring rules (support non-standard leagues)

**Infrastructure**:
- Horizontal scaling (multiple Heroku dynos + load balancer)
- Database sharding (if user base >100k)
- Multi-region deployment (US West + US East)
- Kubernetes migration (for cost optimization at scale)

## 📊 Success Metrics & Monitoring

### Key Performance Indicators
**User Growth**:
- Weekly Active Users (WAU): Target 1,000 by end of season
- Sign-up conversion: >15% (currently tracking baseline)
- Retention (Week 2): >60%

**Technical**:
- P99 API latency: <500ms (currently ~300ms avg)
- Error rate: <0.1% (currently <0.01%)
- Cache hit rate: >50% (currently 50-85% depending on endpoint)
- Uptime: 99.9% (currently 100% over 30 days)

**Product**:
- Time to first recommendation: <3 minutes (Target: <2 minutes)
- Weekly lineup view adoption: >90% of active users
- "Analyze All" feature usage: >70% weekly
- Average session duration: >5 minutes

### Monitoring Dashboard
Track these metrics in production:
1. Request rate (requests/min)
2. Error rate by endpoint
3. Cache hit/miss ratio
4. Database query time (P50, P95, P99)
5. External API latency (Grid Iron Mind)
6. Background job queue length (once Celery implemented)
7. User sign-ups per day
8. Active rosters per user

## 💡 Development Best Practices

### Before Making Changes

**ALWAYS**:
1. ✅ Check if `DATABASE_URL` is optional for the feature
2. ✅ Add timeout to any new API calls (10 seconds)
3. ✅ Consider caching strategy (Redis + PostgreSQL)
4. ✅ Test with and without database configured
5. ✅ Verify API v2 endpoints are available (check docs first)
6. ✅ Use Grid Iron Mind API for dynamic data (no hardcoding)
7. ✅ Add logging with context (user_id, request_id, etc.)
8. ✅ Handle errors gracefully (return None or empty dict)

**NEVER**:
1. ❌ Add background jobs with `threading.Thread` (use Celery when available)
2. ❌ Hardcode NFL data (teams, defenses, stadiums, coordinators)
3. ❌ Make API calls without timeout
4. ❌ Use `any` type in TypeScript (be explicit)
5. ❌ Assume database is always available
6. ❌ Commit sensitive data (API keys, tokens, etc.)
7. ❌ Skip validation on user inputs
8. ❌ Return raw error messages to users (log internally, show generic message)

### Code Review Checklist

Before committing:
- [ ] All API calls have timeout (10s)
- [ ] Database-dependent code has null checks
- [ ] User inputs are validated (Marshmallow schema)
- [ ] Errors are logged with context
- [ ] TypeScript types are explicit (no `any`)
- [ ] New routes are added to API documentation
- [ ] Cache invalidation is considered
- [ ] Tests are added (when testing framework exists)
- [ ] No hardcoded NFL data
- [ ] No background threading (use Celery when available)

### Quick Commands for Development

```bash
# Start everything
./launch-v2.sh                    # Backend (API v2)
./launch-frontend.sh              # Frontend dev server

# Test endpoints
curl http://localhost:5000/health                           # Health check
curl http://localhost:5000/api/cache/stats                  # Cache stats
curl "http://localhost:5000/api/advanced/standings?season=2024"  # Advanced endpoint

# Database
psql $DATABASE_URL < schema.sql                            # Fresh install
psql $DATABASE_URL < schema_v2_updates.sql                 # Apply v2 schema
python -c "from app.database import init_db; init_db()"    # Initialize from code

# Frontend build
cd frontend
npm run build                     # Build for production
cp -r dist/* ../app/static/      # Copy to Flask

# Heroku
heroku logs --tail               # View logs
heroku run python -c "..."       # Run Python commands
heroku ps                        # Check dyno status
```

---

**Last Updated**: October 2, 2025
**Version**: v127 (Production)
**Status**: ✅ Deployed and Operational
**Next Milestone**: Celery implementation + Input validation + Remove hardcoded data
