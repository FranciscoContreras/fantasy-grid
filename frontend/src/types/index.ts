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

export interface Roster {
  id: number;
  user_id: string;
  name: string;
  league_name?: string;
  scoring_type: string;
  is_active: boolean;
  created_at: string;
  players?: RosterPlayer[];
}

export interface RosterPlayer {
  id: number;
  player_id?: string;
  player_name: string;
  position: string;
  team: string;
  roster_slot: string;
  is_starter: boolean;
  injury_status: 'HEALTHY' | 'PROBABLE' | 'QUESTIONABLE' | 'DOUBTFUL' | 'OUT';
  added_at: string;
}

export interface Matchup {
  id: number;
  week: number;
  season: number;
  user_roster_id: number;
  opponent_roster_id: number;
  user_roster_name?: string;
  opponent_roster_name?: string;
  analyzed: boolean;
  analyzed_at?: string;
  created_at: string;
  analysis?: MatchupAnalysis[];
}

export interface MatchupAnalysis {
  id: number;
  player_id?: string;
  player_name: string;
  position: string;
  team: string;
  is_user_player: boolean;
  opponent_team: string;
  matchup_score: number;
  projected_points: number;
  ai_grade: string;
  recommendation: 'START' | 'SIT' | 'CONSIDER';
  injury_status?: string;
  injury_impact: string;
  confidence_score: number;
  reasoning: string;
  analyzed_at: string;
}
