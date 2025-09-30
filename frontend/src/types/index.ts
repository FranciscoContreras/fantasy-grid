export interface Player {
  id?: string;
  player_id?: string;
  name: string;
  position: string;
  team: string;
  jersey_number?: string;
  avg_points?: number;
  height?: string;
  weight?: number;
  age?: number;
  experience?: number;
  college?: string;
  status?: string;
}

export interface Analysis {
  player: Player;
  matchup_score: number;
  weather_impact: number;
  weather_data?: WeatherData;
  ai_grade: {
    grade: string;
    predicted_points: number;
    confidence: number;
  };
  recommendation: {
    status: 'START' | 'CONSIDER' | 'BENCH';
    confidence: string;
    reason?: string;
  };
}

export interface WeatherData {
  temperature?: number;
  wind_speed?: number;
  precipitation?: number;
  conditions?: string;
}
