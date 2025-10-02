/**
 * TypeScript types for API v2 Advanced Stats
 * Next Gen Stats, EPA, CPOE, Play-by-Play data
 */

export interface NextGenStatsQB {
  time_to_throw: number;
  avg_air_yards: number;
  completion_above_expectation: number;
  avg_intended_air_yards: number;
  max_air_distance: number;
}

export interface NextGenStatsReceiver {
  avg_separation: number;
  avg_cushion: number;
  avg_yac: number;
  avg_target_separation: number;
  percent_share_of_routes: number;
}

export interface NextGenStatsRusher {
  rush_yards_over_expected: number;
  rush_yards_over_expected_per_att: number;
  avg_time_to_los: number;
  efficiency_rating: number;
  percent_attempts_gte_eight_defenders: number;
}

export interface EPAStats {
  epa_per_play: number;
  epa_total: number;
  epa_pass: number;
  epa_rush: number;
  success_rate: number;
}

export interface CPOEStats {
  cpoe: number;
  expected_completion_pct: number;
  actual_completion_pct: number;
}

export interface AdvancedPlayerStats {
  player_id: string;
  player_name: string;
  position: string;
  season: number;
  week?: number;

  // Next Gen Stats
  time_to_throw?: number;
  avg_air_yards?: number;
  completion_above_expectation?: number;
  avg_separation?: number;
  avg_yac?: number;
  rush_yards_over_expected_per_att?: number;

  // EPA
  epa_per_play?: number;
  epa_total?: number;
  success_rate?: number;

  // CPOE
  cpoe?: number;

  // Opportunity Metrics
  snap_count?: number;
  snap_share?: number;
  target_share?: number;
  air_yards_share?: number;
  wopr?: number; // Weighted Opportunity Rating
  racr?: number; // Receiver Air Conversion Ratio
}

export interface PlayByPlayData {
  id: number;
  game_id: string;
  play_id: string;
  season: number;
  week: number;

  // Game State
  quarter: number;
  time_remaining: string;
  down: number;
  yards_to_go: number;
  yard_line: number;
  possession_team: string;

  // Play Details
  play_type: string;
  play_description: string;
  yards_gained: number;
  is_touchdown: boolean;
  is_turnover: boolean;
  is_penalty: boolean;
  is_scoring_play: boolean;

  // Players
  passer_id?: string;
  passer_name?: string;
  rusher_id?: string;
  rusher_name?: string;
  receiver_id?: string;
  receiver_name?: string;

  // Advanced Metrics
  epa?: number;
  wpa?: number; // Win Probability Added
  air_yards?: number;
  yards_after_catch?: number;

  // Score
  home_score: number;
  away_score: number;
  score_differential: number;
}

export interface ScoringPlay {
  id: number;
  game_id: string;
  play_id: string;
  season: number;
  week: number;
  quarter: number;
  time_remaining: string;
  scoring_team: string;
  scoring_type: string; // TD, FG, SAFETY, 2PT
  points: number;
  player_id?: string;
  player_name?: string;
  play_description: string;
  home_score: number;
  away_score: number;
}

export interface DefenseAdvancedStats {
  team_id: string;
  team_abbr: string;
  season: number;
  week?: number;

  // Traditional Stats
  points_allowed: number;
  yards_allowed: number;
  pass_yards_allowed: number;
  rush_yards_allowed: number;
  sacks: number;
  interceptions: number;
  fumbles_recovered: number;
  forced_fumbles: number;

  // Advanced Metrics
  epa_per_play_allowed: number;
  success_rate_allowed: number;
  explosive_play_rate_allowed: number;
  stuff_rate: number;

  // Coverage Stats
  completion_pct_allowed: number;
  yards_per_attempt_allowed: number;
  passer_rating_allowed: number;
  pressure_rate: number;
  blitz_rate: number;

  // Situational Stats
  third_down_conversion_pct_allowed: number;
  red_zone_td_pct_allowed: number;
  goal_to_go_stop_rate: number;

  // Rankings
  overall_rank: number;
  pass_defense_rank: number;
  rush_defense_rank: number;
  scoring_defense_rank: number;
}

export interface InjuryReport {
  id: number;
  player_id: string;
  player_name: string;
  team: string;
  position: string;

  // Injury Details
  injury_status: 'OUT' | 'DOUBTFUL' | 'QUESTIONABLE' | 'PROBABLE' | 'IR' | 'HEALTHY';
  injury_type: string;
  body_part: string;
  description: string;

  // Timeline
  injury_date?: string;
  report_date: string;
  expected_return_date?: string;
  weeks_out?: number;

  // Practice Participation
  wednesday_practice?: 'FULL' | 'LIMITED' | 'DNP';
  thursday_practice?: 'FULL' | 'LIMITED' | 'DNP';
  friday_practice?: 'FULL' | 'LIMITED' | 'DNP';
  game_status?: 'OUT' | 'DOUBTFUL' | 'QUESTIONABLE' | 'ACTIVE';

  season: number;
  week: number;
  is_current: boolean;
}

export interface InjuryRiskAssessment {
  risk: 'none' | 'low' | 'moderate' | 'high' | 'extreme';
  impact: number; // 0-100
  status: string;
  injury_type: string;
  details: string[];
}

export interface AdvancedMatchupAnalysis {
  score: number; // 0-100
  confidence: 'low' | 'medium' | 'high';
  factors: string[];
  advanced_analysis: boolean;
}

export interface PlayerTrendAnalysis {
  trend: 'improving' | 'declining' | 'stable' | 'unknown';
  momentum: 'hot' | 'cold' | 'neutral';
  insights: string[];
}

export interface AIGradeWithAdvancedStats {
  grade: string; // A+, A, B+, B, C, D, F
  predicted_points: number;
  confidence: number;
  insights: string[];
  advanced_stats_used: boolean;
}

export interface EnhancedPlayerAnalysis {
  player: {
    id: string;
    name: string;
    position: string;
    team: string;
  };
  opponent: string;
  matchup_analysis: AdvancedMatchupAnalysis;
  ai_grade: AIGradeWithAdvancedStats;
  advanced_stats: AdvancedPlayerStats | null;
  trend_analysis?: PlayerTrendAnalysis;
  injury_risk?: InjuryRiskAssessment;
  season: number;
  week?: number;
}

export interface GameWeather {
  game_id: string;
  stadium_name: string;
  city: string;
  state: string;
  is_dome: boolean;
  surface_type: string;

  // Weather Conditions
  temperature: number;
  feels_like: number;
  humidity: number;
  wind_speed: number;
  wind_direction: string;
  precipitation_chance: number;
  precipitation_amount: number;
  weather_condition: string;

  // Impact
  weather_severity: 'NONE' | 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREME';
  impact_on_passing: number; // 0-1 multiplier
  impact_on_kicking: number;
}

export interface AIGamePrediction {
  game_id: string;
  home_team: string;
  away_team: string;

  // Predictions
  home_win_probability: number;
  away_win_probability: number;
  predicted_home_score: number;
  predicted_away_score: number;
  confidence: number;

  // Analysis
  key_factors: string[];
  player_impacts: {
    player_name: string;
    projected_impact: string;
  }[];
  narrative: string;
}

export interface AIPlayerPrediction {
  player_id: string;
  player_name: string;
  position: string;

  // Projections
  projected_fantasy_points: number;
  projected_passing_yards?: number;
  projected_passing_tds?: number;
  projected_rushing_yards?: number;
  projected_rushing_tds?: number;
  projected_receptions?: number;
  projected_receiving_yards?: number;
  projected_receiving_tds?: number;

  // Analysis
  confidence: number;
  risk_factors: string[];
  opportunities: string[];
  narrative: string;
}

export interface AIPlayerInsights {
  player_id: string;
  player_name: string;

  // Insights
  performance_trends: string[];
  strengths: string[];
  weaknesses: string[];
  matchup_advantages: string[];
  season_outlook: string;
  trade_value_assessment: string;
  narrative: string;
}

export interface NFLStandings {
  team_id: string;
  team_abbr: string;
  team_name: string;
  division: string;
  conference: string;

  // Record
  wins: number;
  losses: number;
  ties: number;
  win_pct: number;

  // Division/Conference
  division_rank: number;
  conference_rank: number;
  playoff_seed?: number;

  // Additional
  points_for: number;
  points_against: number;
  point_differential: number;
  streak: string; // W3, L2, etc.
}

// API Response wrappers
export interface APIv2Response<T> {
  data: T;
  meta?: {
    total?: number;
    limit?: number;
    offset?: number;
    timestamp?: string;
    [key: string]: any;
  };
}

export interface APIv2Error {
  error: string;
  details?: string;
  timestamp?: string;
}
