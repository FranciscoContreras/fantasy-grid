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
