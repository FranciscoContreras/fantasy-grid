# Fantasy Grid - Player Analysis

AI-powered fantasy football player recommendation app with matchup analysis, weather impact assessment, and intelligent start/sit recommendations.

## Features

- **Player Search & Analysis** - Search NFL players and get detailed performance insights
- **Matchup Ratings** - Analyze player matchups against opposing defenses
- **Weather Impact** - Factor in weather conditions for game-day performance
- **AI Grading** - Machine learning-powered player performance predictions
- **Start/Sit Recommendations** - Get actionable recommendations for your lineup

## Tech Stack

**Backend:**
- Python 3.11
- Flask
- PostgreSQL
- scikit-learn (AI/ML)

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS + shadcn/ui

**Data Source:**
- Grid Iron Mind NFL API

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL
- Grid Iron Mind API key

### Installation

See [Complete Build Guide](docs/guides/getting-started/BUILD.md) for complete step-by-step setup instructions.

**Quick Start:**

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd fantasy-grid
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your credentials
   python app.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit .env if needed
   npm run dev
   ```

4. **Access the app**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

## Documentation

**📚 [Complete Documentation Hub](docs/README.md)** - Organized documentation index with 27 guides and references

### Quick Links
- **[Getting Started](docs/guides/getting-started/START_HERE.md)** - First-time setup
- **[Quick Start Guide](docs/guides/getting-started/QUICKSTART.md)** - Get running in minutes
- **[Complete Build Guide](docs/guides/getting-started/BUILD.md)** - Step-by-step build (36 phases)
- **[Grid Iron Mind API](docs/api/grid-iron-mind-api.md)** - External NFL API documentation
- **[Fantasy Grid API](docs/api/fantasy-grid-api.md)** - Internal API reference
- **[Testing Guide](docs/guides/development/TESTING.md)** - Test procedures
- **[Product Roadmap](docs/planning/product-roadmap.md)** - Product vision and phases
- **[CLAUDE.md](./CLAUDE.md)** - Guidance for Claude Code (stays in root)

## API Integration

This app integrates with the Grid Iron Mind NFL API for:
- Player statistics and career data
- Team information and defense stats
- Game schedules and results
- Weather data
- AI-powered predictions and insights

API Base URL: `https://nfl.wearemachina.com/api/v1`

## Development

```bash
# Backend
cd backend
source venv/bin/activate
python app.py

# Frontend
cd frontend
npm run dev

# Build for production
npm run build
```

## Deployment

Configured for Heroku deployment. See [Build Guide - Phase 5](docs/guides/getting-started/BUILD.md) for deployment instructions.

## License

MIT
