# BUILD.md

## Complete Build Instructions

This guide walks you through building the fantasy football player recommendation app from scratch.

---

## Prerequisites

Install these tools before starting:

- Python 3.9+
- Node.js 18+
- PostgreSQL
- Git
- Heroku CLI

---

## Phase 1: Project Setup

### Step 1: Create Project Structure

```
fantasy-football-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   ├── Procfile
│   └── runtime.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── lib/
│   └── package.json
├── instructions.md
├── agents.md
└── BUILD.md
```

### Step 2: Initialize Git Repository

```bash
git init
echo "node_modules/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
```

---

## Phase 2: Backend Development

### Step 3: Set Up Python Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 4: Install Backend Dependencies

Create `requirements.txt`:

```
flask==3.0.0
flask-cors==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
gunicorn==21.2.0
numpy==1.26.0
pandas==2.1.0
scikit-learn==1.3.0
```

Install:

```bash
pip install -r requirements.txt
```

### Step 5: Create Flask Application

Create `backend/app/__init__.py`:

```python
from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
  
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
  
    from app.routes import players, analysis, predictions
    app.register_blueprint(players.bp)
    app.register_blueprint(analysis.bp)
    app.register_blueprint(predictions.bp)
  
    return app
```

### Step 6: Build API Integration Service

Create `backend/app/services/api_client.py`:

Read your `instructions.md` file and build the client based on those specs. Structure it like this:

```python
import requests
import os

class FantasyAPIClient:
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL')
        self.api_key = os.getenv('API_KEY')
      
    def get_player_data(self, player_id):
        # Implement based on instructions.md
        pass
      
    def get_defense_stats(self, team):
        # Implement based on instructions.md
        pass
      
    def get_weather_data(self, location):
        # Implement based on instructions.md
        pass
```

### Step 7: Create Database Models

Create `backend/app/models/player.py`:

```python
from datetime import datetime

class Player:
    def __init__(self, player_id, name, position, team):
        self.player_id = player_id
        self.name = name
        self.position = position
        self.team = team
        self.created_at = datetime.utcnow()
      
    def to_dict(self):
        return {
            'player_id': self.player_id,
            'name': self.name,
            'position': self.position,
            'team': self.team
        }
```

### Step 8: Build Analysis Services

Create `backend/app/services/analyzer.py`:

```python
import numpy as np
from sklearn.preprocessing import StandardScaler

class PlayerAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
      
    def calculate_matchup_score(self, player_stats, defense_stats):
        # Implement scoring logic
        # Consider: yards allowed, TDs allowed, sacks, etc.
        matchup_factors = {
            'yards_allowed': defense_stats.get('yards_allowed', 0),
            'tds_allowed': defense_stats.get('tds_allowed', 0),
            'rank': defense_stats.get('rank', 16)
        }
      
        # Score from 0-100
        score = self._compute_score(matchup_factors)
        return score
      
    def calculate_weather_impact(self, weather_data, player_position):
        # Different positions affected differently by weather
        wind_speed = weather_data.get('wind_speed', 0)
        precipitation = weather_data.get('precipitation', 0)
        temperature = weather_data.get('temperature', 70)
      
        impact_score = 100
      
        # QBs and WRs affected by wind
        if player_position in ['QB', 'WR']:
            if wind_speed > 15:
                impact_score -= (wind_speed - 15) * 2
              
        # All positions affected by heavy rain/snow
        if precipitation > 0.5:
            impact_score -= precipitation * 20
          
        return max(0, min(100, impact_score))
      
    def _compute_score(self, factors):
        # Implement your scoring algorithm
        pass
```

### Step 9: Build AI Grading System

Create `backend/app/services/ai_grader.py`:

```python
import numpy as np
from sklearn.ensemble import RandomForestRegressor

class AIGrader:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.is_trained = False
      
    def train(self, training_data, labels):
        # Training_data: historical player stats
        # Labels: actual fantasy points scored
        self.model.fit(training_data, labels)
        self.is_trained = True
      
    def grade_player(self, player_features):
        if not self.is_trained:
            return self._fallback_grading(player_features)
          
        prediction = self.model.predict([player_features])[0]
      
        # Convert prediction to grade (A+ to F)
        grade = self._score_to_grade(prediction)
        confidence = self._calculate_confidence(player_features)
      
        return {
            'grade': grade,
            'predicted_points': round(prediction, 2),
            'confidence': confidence
        }
      
    def _score_to_grade(self, score):
        if score >= 20: return 'A+'
        elif score >= 17: return 'A'
        elif score >= 14: return 'B+'
        elif score >= 11: return 'B'
        elif score >= 8: return 'C'
        else: return 'D'
      
    def _calculate_confidence(self, features):
        # Return confidence percentage
        return 85.0
      
    def _fallback_grading(self, features):
        # Simple rule-based grading when model not trained
        return {'grade': 'B', 'predicted_points': 12.0, 'confidence': 60.0}
```

### Step 10: Create API Routes

Create `backend/app/routes/players.py`:

```python
from flask import Blueprint, jsonify, request
from app.services.api_client import FantasyAPIClient
from app.services.analyzer import PlayerAnalyzer
from app.services.ai_grader import AIGrader

bp = Blueprint('players', __name__, url_prefix='/api/players')

api_client = FantasyAPIClient()
analyzer = PlayerAnalyzer()
grader = AIGrader()

@bp.route('/search', methods=['GET'])
def search_players():
    query = request.args.get('q', '')
    position = request.args.get('position', None)
  
    # Call your API from instructions.md
    players = api_client.search_players(query, position)
  
    return jsonify(players)

@bp.route('/<player_id>/analysis', methods=['GET'])
def analyze_player(player_id):
    # Get player data
    player = api_client.get_player_data(player_id)
    opponent = request.args.get('opponent')
  
    # Get opponent defense stats
    defense_stats = api_client.get_defense_stats(opponent)
  
    # Get weather if game location provided
    location = request.args.get('location')
    weather = api_client.get_weather_data(location) if location else {}
  
    # Calculate scores
    matchup_score = analyzer.calculate_matchup_score(player, defense_stats)
    weather_impact = analyzer.calculate_weather_impact(weather, player['position'])
  
    # AI grading
    features = [
        player.get('avg_points', 0),
        matchup_score,
        weather_impact,
        player.get('consistency_rating', 0)
    ]
    ai_grade = grader.grade_player(features)
  
    return jsonify({
        'player': player,
        'matchup_score': matchup_score,
        'weather_impact': weather_impact,
        'ai_grade': ai_grade,
        'recommendation': _generate_recommendation(matchup_score, weather_impact, ai_grade)
    })

def _generate_recommendation(matchup, weather, ai_grade):
    overall_score = (matchup * 0.4 + weather * 0.2 + ai_grade['predicted_points'] * 3) / 4
  
    if overall_score >= 16:
        return {'status': 'START', 'confidence': 'HIGH'}
    elif overall_score >= 10:
        return {'status': 'CONSIDER', 'confidence': 'MEDIUM'}
    else:
        return {'status': 'BENCH', 'confidence': 'MEDIUM'}
```

Create `backend/app/routes/analysis.py`:

```python
from flask import Blueprint, jsonify, request
from app.services.analyzer import PlayerAnalyzer

bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

analyzer = PlayerAnalyzer()

@bp.route('/compare', methods=['POST'])
def compare_players():
    data = request.json
    player_ids = data.get('player_ids', [])
  
    # Get analysis for each player
    comparisons = []
    for player_id in player_ids:
        # Fetch and analyze each player
        # Return comparison data
        pass
      
    return jsonify(comparisons)

@bp.route('/percentage-calculator', methods=['POST'])
def calculate_percentages():
    data = request.json
  
    # Calculate success probability based on factors
    factors = data.get('factors', {})
  
    probability = _calculate_probability(factors)
  
    return jsonify({'probability': probability})

def _calculate_probability(factors):
    # Implement probability calculation
    base_probability = 50.0
  
    # Adjust based on factors
    if factors.get('matchup_score', 0) > 70:
        base_probability += 15
    if factors.get('weather_impact', 0) < 50:
        base_probability -= 10
      
    return min(95, max(5, base_probability))
```

### Step 11: Create Heroku Configuration

Create `backend/Procfile`:

```
web: gunicorn app:app
```

Create `backend/runtime.txt`:

```
python-3.11.0
```

Create `backend/app.py`:

```python
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

---

## Phase 3: Frontend Development

### Step 12: Create React App with Vite

```bash
cd ../
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

### Step 13: Install Dependencies

```bash
npm install @radix-ui/react-slot class-variance-authority clsx tailwindcss-animate
npm install axios react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 14: Install shadcn

```bash
npx shadcn-ui@latest init
```

When prompted:

- Style: Default
- Base color: Slate
- CSS variables: Yes

Install components:

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add select
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add table
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add dialog
```

### Step 15: Configure Tailwind

Update `tailwind.config.js`:

```javascript
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("tailwindcss-animate")],
}
```

### Step 16: Create API Client

Create `frontend/src/lib/api.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchPlayers = async (query: string, position?: string) => {
  const response = await api.get('/players/search', {
    params: { q: query, position },
  });
  return response.data;
};

export const analyzePlayer = async (
  playerId: string,
  opponent: string,
  location?: string
) => {
  const response = await api.get(`/players/${playerId}/analysis`, {
    params: { opponent, location },
  });
  return response.data;
};

export const comparePlayers = async (playerIds: string[]) => {
  const response = await api.post('/analysis/compare', { player_ids: playerIds });
  return response.data;
};

export default api;
```

### Step 17: Create Type Definitions

Create `frontend/src/types/index.ts`:

```typescript
export interface Player {
  player_id: string;
  name: string;
  position: string;
  team: string;
  avg_points: number;
}

export interface Analysis {
  player: Player;
  matchup_score: number;
  weather_impact: number;
  ai_grade: {
    grade: string;
    predicted_points: number;
    confidence: number;
  };
  recommendation: {
    status: 'START' | 'CONSIDER' | 'BENCH';
    confidence: string;
  };
}

export interface WeatherData {
  temperature: number;
  wind_speed: number;
  precipitation: number;
  conditions: string;
}
```

### Step 18: Build Player Search Component

Create `frontend/src/components/PlayerSearch.tsx`:

```typescript
import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { searchPlayers } from '@/lib/api';
import { Player } from '@/types';

export function PlayerSearch({ onSelectPlayer }: { onSelectPlayer: (player: Player) => void }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query) return;
  
    setLoading(true);
    try {
      const players = await searchPlayers(query);
      setResults(players);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Search players..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <Button onClick={handleSearch} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </div>
    
      <div className="grid gap-2">
        {results.map((player) => (
          <Card
            key={player.player_id}
            className="p-4 cursor-pointer hover:bg-accent"
            onClick={() => onSelectPlayer(player)}
          >
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold">{player.name}</p>
                <p className="text-sm text-muted-foreground">
                  {player.position} - {player.team}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium">{player.avg_points} PPG</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

### Step 19: Build Analysis Display Component

Create `frontend/src/components/PlayerAnalysis.tsx`:

```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Analysis } from '@/types';

export function PlayerAnalysis({ analysis }: { analysis: Analysis }) {
  const getRecommendationColor = (status: string) => {
    switch (status) {
      case 'START': return 'bg-green-500';
      case 'CONSIDER': return 'bg-yellow-500';
      case 'BENCH': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-green-600';
    if (grade.startsWith('B')) return 'text-blue-600';
    if (grade.startsWith('C')) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span>{analysis.player.name}</span>
            <Badge className={getRecommendationColor(analysis.recommendation.status)}>
              {analysis.recommendation.status}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Matchup Score</p>
              <p className="text-2xl font-bold">{analysis.matchup_score}/100</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Weather Impact</p>
              <p className="text-2xl font-bold">{analysis.weather_impact}/100</p>
            </div>
          </div>
        
          <div className="border-t pt-4">
            <p className="text-sm text-muted-foreground">AI Grade</p>
            <div className="flex items-baseline gap-2">
              <p className={`text-4xl font-bold ${getGradeColor(analysis.ai_grade.grade)}`}>
                {analysis.ai_grade.grade}
              </p>
              <p className="text-muted-foreground">
                {analysis.ai_grade.predicted_points} projected points
              </p>
            </div>
            <p className="text-sm mt-2">
              Confidence: {analysis.ai_grade.confidence}%
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

### Step 20: Build Main App Component

Create `frontend/src/App.tsx`:

```typescript
import { useState } from 'react';
import { PlayerSearch } from './components/PlayerSearch';
import { PlayerAnalysis } from './components/PlayerAnalysis';
import { analyzePlayer } from './lib/api';
import { Player, Analysis } from './types';
import { Input } from './components/ui/input';
import { Button } from './components/ui/button';

function App() {
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [opponent, setOpponent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!selectedPlayer || !opponent) return;
  
    setLoading(true);
    try {
      const result = await analyzePlayer(selectedPlayer.player_id, opponent);
      setAnalysis(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8 px-4">
        <h1 className="text-4xl font-bold mb-8">Fantasy Football Analyzer</h1>
      
        <div className="grid md:grid-cols-2 gap-8">
          <div className="space-y-6">
            <PlayerSearch onSelectPlayer={setSelectedPlayer} />
          
            {selectedPlayer && (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Selected Player</p>
                  <p className="text-xl font-semibold">{selectedPlayer.name}</p>
                </div>
              
                <Input
                  placeholder="Opponent team (e.g., KC, DAL)"
                  value={opponent}
                  onChange={(e) => setOpponent(e.target.value.toUpperCase())}
                />
              
                <Button 
                  onClick={handleAnalyze} 
                  disabled={loading || !opponent}
                  className="w-full"
                >
                  {loading ? 'Analyzing...' : 'Analyze Matchup'}
                </Button>
              </div>
            )}
          </div>
        
          <div>
            {analysis && <PlayerAnalysis analysis={analysis} />}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
```

### Step 21: Configure Environment Variables

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:5000/api
```

Create `frontend/.env.production`:

```
VITE_API_URL=https://your-app.herokuapp.com/api
```

---

## Phase 4: Database Setup

### Step 22: Create Database Schema

Create `backend/schema.sql`:

```sql
CREATE TABLE players (
    player_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    team VARCHAR(10) NOT NULL,
    avg_points DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE player_stats (
    id SERIAL PRIMARY KEY,
    player_id VARCHAR(50) REFERENCES players(player_id),
    week INT NOT NULL,
    season INT NOT NULL,
    points DECIMAL(5,2),
    opponent VARCHAR(10),
    weather_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    scoring_type VARCHAR(20),
    roster_slots JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_player_stats_player ON player_stats(player_id);
CREATE INDEX idx_player_stats_week ON player_stats(week, season);
```

### Step 23: Add Database Connection

Create `backend/app/database.py`:

```python
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    conn = psycopg2.connect(
        os.getenv('DATABASE_URL'),
        cursor_factory=RealDictCursor
    )
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
  
    with open('schema.sql', 'r') as f:
        cursor.execute(f.read())
  
    conn.commit()
    cursor.close()
    conn.close()
```

---

## Phase 5: Deployment

### Step 24: Create Heroku App

```bash
heroku login
heroku create your-app-name
```

### Step 25: Add PostgreSQL

```bash
heroku addons:create heroku-postgresql:mini
```

### Step 26: Set Environment Variables

```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set API_KEY=your-api-key
heroku config:set API_BASE_URL=your-api-base-url
```

### Step 27: Deploy Backend

```bash
cd backend
git add .
git commit -m "Initial backend"
git push heroku main
```

### Step 28: Initialize Database

```bash
heroku run python -c "from app.database import init_db; init_db()"
```

### Step 29: Build Frontend

```bash
cd ../frontend
npm run build
```

### Step 30: Deploy Frontend

Option 1: Serve from Flask

Move build files to backend:

```bash
cp -r dist ../backend/static
```

Update Flask to serve static files.

Option 2: Deploy to Vercel/Netlify

```bash
npm install -g vercel
vercel --prod
```

Update API URL in production env.

---

## Phase 6: Testing

### Step 31: Test Backend Endpoints

```bash
curl http://localhost:5000/api/players/search?q=mahomes
curl http://localhost:5000/api/players/123/analysis?opponent=KC
```

### Step 32: Test Frontend Locally

```bash
cd frontend
npm run dev
```

Open browser to http://localhost:5173

### Step 33: Test Full Integration

1. Search for a player
2. Select opponent team
3. Click analyze
4. Verify all scores display
5. Check recommendation badge
6. Test multiple players

---

## Phase 7: Enhancements

### Step 34: Add Caching

Install Redis:

```bash
heroku addons:create heroku-redis:mini
```

Add caching to API calls:

```python
import redis
import json

cache = redis.from_url(os.getenv('REDIS_URL'))

def get_cached_or_fetch(key, fetch_func, expiry=3600):
    cached = cache.get(key)
    if cached:
        return json.loads(cached)
  
    data = fetch_func()
    cache.setex(key, expiry, json.dumps(data))
    return data
```

### Step 35: Add Authentication (Optional)

Install dependencies:

```bash
pip install flask-login
npm install @clerk/clerk-react
```

Implement auth flows in both frontend and backend.

### Step 36: Add Monitoring

```bash
heroku addons:create papertrail:choklad
heroku addons:create newrelic:wayne
```

Add logging throughout your code.

---

## Troubleshooting

### Common Issues

**Port binding error on Heroku**:
Ensure you use `PORT` environment variable in app.py

**CORS errors**:
Verify CORS is enabled in Flask and origin is whitelisted

**Database connection fails**:
Check DATABASE_URL is set correctly
Run `heroku pg:info` to verify database exists

**API calls fail**:
Verify instructions.md API endpoints are correct
Check API keys are set in environment
Add error handling and logging

**Build fails**:
Check all dependencies are in requirements.txt
Verify Python version in runtime.txt

---

## Maintenance

### Regular Updates

1. Update dependencies monthly
2. Monitor Heroku logs daily
3. Backup database weekly
4. Review API usage and costs
5. Test all features after updates

### Scaling

When traffic increases:

```bash
heroku ps:scale web=2
heroku addons:upgrade heroku-postgresql:standard-0
```

---

## Next Steps

After completing build:

1. Train AI model with historical data
2. Add more positions and statistics
3. Build mobile responsive design
4. Add user accounts and saved lineups
5. Implement real-time updates
6. Add export to CSV feature
7. Build comparison tool for multiple players
8. Add weekly recap and insights
