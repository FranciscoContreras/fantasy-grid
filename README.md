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

See [BUILD.md](./BUILD.md) for complete step-by-step setup instructions.

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

- **[BUILD.md](./BUILD.md)** - Complete build and deployment guide
- **[instructions.md](./instructions.md)** - Grid Iron Mind API documentation
- **[AGENTS.md](./AGENTS.md)** - Multi-agent development approach
- **[CLAUDE.md](./CLAUDE.md)** - Guidance for Claude Code

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

Configured for Heroku deployment. See BUILD.md Phase 5 for deployment instructions.

## License

MIT
