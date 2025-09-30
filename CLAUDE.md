# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **fantasy football player recommendation application** that is currently in the planning phase. The project will integrate with the Grid Iron Mind NFL API to provide AI-powered player analysis, matchup ratings, weather impact assessments, and start/sit recommendations.

**Current Status:** Planning phase - no code has been implemented yet.

## Project Structure

The project is designed with a full-stack architecture:

- **Backend:** Python (Flask/FastAPI) with AI/ML models for player grading
- **Frontend:** React + TypeScript with shadcn UI components
- **Database:** PostgreSQL (Heroku add-on)
- **Deployment:** Heroku
- **External API:** Grid Iron Mind API (https://nfl.wearemachina.com/api/v1)

## Key Documentation Files

### BUILD.md
Contains complete step-by-step instructions for building the entire application from scratch. Follow this as the primary development guide. It includes:
- 36 sequential steps covering backend, frontend, database, and deployment
- Code examples for all major components
- Configuration files and environment setup
- Testing procedures and troubleshooting

### instructions.md
Complete API documentation for the Grid Iron Mind NFL API. Reference this when:
- Integrating player data endpoints
- Implementing weather data features
- Setting up AI-powered prediction endpoints
- Understanding data models and response formats

**Base API URL:** `https://nfl.wearemachina.com/api/v1`

**Important:** Most endpoints are public, but AI endpoints require an API key via `X-API-Key` header.

### AGENTS.md
Defines specialized agent roles if using multi-agent development approach:
- Backend Architect
- Frontend Developer
- Data Analysis Engineer
- AI/ML Specialist
- DevOps Engineer

## Core Features to Implement

1. **Player Search & Selection**
   - Search by name, position, team
   - Filter by status (active/injured)
   - Display player stats and info

2. **Matchup Analysis**
   - Defense rankings and stats
   - Opponent analysis
   - Historical performance against specific teams
   - Matchup scoring (0-100)

3. **Weather Impact Assessment**
   - Current weather conditions for game locations
   - Historical weather data
   - Position-specific weather impact calculations
   - Weather scoring (0-100)

4. **AI Grading System**
   - Machine learning model for player performance prediction
   - Letter grades (A+ to F)
   - Projected fantasy points
   - Confidence percentages

5. **Start/Sit Recommendations**
   - Combined analysis of matchup, weather, and AI grade
   - Status: START / CONSIDER / BENCH
   - Confidence levels

## API Integration Requirements

When implementing API calls to Grid Iron Mind:

### Public Endpoints (No Auth Required)
- `/api/v1/teams` - All NFL teams
- `/api/v1/players` - Player search and data
- `/api/v1/games` - Game schedules and results
- `/api/v1/stats/leaders` - League leaders by category
- `/api/v1/weather/*` - Weather data

### AI Endpoints (API Key Required)
- `/api/v1/ai/predict/game/{game_id}` - Game predictions
- `/api/v1/ai/predict/player/{player_id}` - Player performance predictions
- `/api/v1/ai/insights/player/{player_id}` - Player insights
- `/api/v1/ai/query` - Natural language queries

### Admin Endpoints (Data Sync)
- `/api/v1/admin/sync/teams` - Sync team data
- `/api/v1/admin/sync/rosters` - Sync rosters
- `/api/v1/admin/sync/injuries` - Sync injury reports
- `/api/v1/admin/sync/nflverse/*` - Sync NFLverse data

## Development Workflow

When starting development, follow BUILD.md in this order:

1. **Phase 1:** Project structure setup
2. **Phase 2:** Backend development (Steps 3-11)
   - Python environment, Flask setup, API client
   - Analysis services, AI grading, routes
3. **Phase 3:** Frontend development (Steps 12-21)
   - React + Vite setup, shadcn installation
   - Components, API client, type definitions
4. **Phase 4:** Database setup (Steps 22-23)
5. **Phase 5:** Deployment to Heroku (Steps 24-30)
6. **Phase 6:** Testing (Steps 31-33)
7. **Phase 7:** Enhancements (Steps 34-36)

## Key Implementation Details

### Backend Architecture

The backend should be structured as:
```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes/              # API endpoints
│   │   ├── players.py       # Player search, analysis
│   │   ├── analysis.py      # Comparison, calculations
│   │   └── predictions.py   # AI predictions
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   │   ├── api_client.py    # Grid Iron Mind API client
│   │   ├── analyzer.py      # Matchup/weather analysis
│   │   └── ai_grader.py     # ML grading model
│   └── utils/               # Helper functions
├── requirements.txt
├── Procfile                 # Heroku config
└── app.py                   # Entry point
```

### Frontend Architecture

The frontend should be structured as:
```
frontend/
├── src/
│   ├── components/          # UI components
│   │   ├── ui/             # shadcn components
│   │   ├── PlayerSearch.tsx
│   │   └── PlayerAnalysis.tsx
│   ├── pages/              # Page components
│   ├── lib/
│   │   └── api.ts          # Backend API client
│   ├── types/
│   │   └── index.ts        # TypeScript types
│   └── App.tsx
└── package.json
```

### Database Schema

Implement these tables:
- `players` - Player metadata and stats
- `player_stats` - Weekly performance history
- `user_preferences` - User settings and roster config

See BUILD.md Step 22 for complete SQL schema.

## Environment Variables

### Backend (.env)
```
SECRET_KEY=<random-secret-key>
DATABASE_URL=<postgres-connection-string>
API_BASE_URL=https://nfl.wearemachina.com/api/v1
API_KEY=<grid-iron-mind-api-key>
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:5000/api  # Development
```

### Frontend (.env.production)
```
VITE_API_URL=https://your-app.herokuapp.com/api
```

## Important Notes

- **API Key Management:** AI endpoints require an API key. Generate one using `/api/v1/admin/keys/generate` endpoint (see instructions.md)
- **Error Handling:** Implement robust error handling for API calls - the Grid Iron Mind API has clear error codes (see instructions.md)
- **Rate Limiting:** Public endpoints: 100 req/min, AI endpoints: 10 req/min (standard) or unlimited (with unlimited API key)
- **CORS:** Enable CORS in Flask for frontend communication
- **Caching:** Consider implementing Redis caching for frequently accessed data (BUILD.md Step 34)

## Testing

Before deployment, test:
1. Player search functionality
2. Matchup analysis with real team data
3. Weather data integration
4. AI grading accuracy
5. Full end-to-end flow: search → select → analyze → recommendation
6. Error states and loading states
7. Mobile responsiveness

## Next Steps for First-Time Setup

If you're starting fresh:
1. Read BUILD.md completely to understand the full architecture
2. Start with Phase 1 and work sequentially through Phase 5
3. Reference instructions.md whenever implementing Grid Iron Mind API calls
4. Test each phase before moving to the next
5. Deploy to Heroku and validate in production

If you're enhancing existing code:
1. Review the current implementation
2. Check which phase of BUILD.md has been completed
3. Continue from the next appropriate step
4. Ensure new features align with the overall architecture
