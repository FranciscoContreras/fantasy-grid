import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface TeamStats {
  team_id: string;
  team_name: string;
  team_abbr: string;
  score: number;
  first_downs: number;
  total_yards: number;
  passing_yards: number;
  rushing_yards: number;
  turnovers: number;
  penalties: number;
  time_of_possession?: string;
}

interface GameStats {
  game_id: string;
  home_team: TeamStats;
  away_team: TeamStats;
  game_date: string;
  final: boolean;
}

interface GameStatsComparisonProps {
  gameId: string;
}

export function GameStatsComparison({ gameId }: GameStatsComparisonProps) {
  const [stats, setStats] = useState<GameStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGameStats();
  }, [gameId]);

  const fetchGameStats = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/advanced/games/${gameId}/stats`);
      const data = await response.json();
      setStats(data.data);
    } catch (error) {
      console.error('Failed to fetch game stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const getWinnerStyle = (homeScore: number, awayScore: number, isHome: boolean) => {
    if (!stats?.final) return '';
    const won = isHome ? homeScore > awayScore : awayScore > homeScore;
    return won ? 'bg-green-50 border-green-500' : 'bg-gray-50';
  };

  const StatRow = ({ label, homeValue, awayValue, unit = '' }: {
    label: string;
    homeValue: number | string;
    awayValue: number | string;
    unit?: string;
  }) => {
    const homeNum = typeof homeValue === 'number' ? homeValue : 0;
    const awayNum = typeof awayValue === 'number' ? awayValue : 0;
    const homeWinning = homeNum > awayNum;
    const awayWinning = awayNum > homeNum;

    return (
      <div className="grid grid-cols-3 items-center py-3 border-b last:border-b-0">
        <div className={`text-right font-bold ${homeWinning ? 'text-green-600' : ''}`}>
          {homeValue}{unit}
        </div>
        <div className="text-center text-xs text-gray-500 uppercase tracking-wider font-semibold">
          {label}
        </div>
        <div className={`text-left font-bold ${awayWinning ? 'text-green-600' : ''}`}>
          {awayValue}{unit}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-sm text-muted-foreground">Loading game stats...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="text-center">
            <p className="text-lg font-semibold text-gray-600">Game stats not available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between mb-4">
          <CardTitle className="text-2xl font-black">Game Statistics</CardTitle>
          {stats.final && (
            <Badge className="bg-black text-white font-bold">FINAL</Badge>
          )}
        </div>

        {/* Score Header */}
        <div className="grid grid-cols-3 items-center gap-4 pt-4 border-t">
          {/* Home Team */}
          <div className={`p-4 rounded-lg border-2 ${getWinnerStyle(stats.home_team.score, stats.away_team.score, true)}`}>
            <p className="text-sm text-gray-600 mb-1">{stats.home_team.team_name}</p>
            <p className="text-4xl font-black">{stats.home_team.score}</p>
          </div>

          {/* VS */}
          <div className="text-center">
            <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold">vs</p>
            <p className="text-xs text-gray-400 mt-1">
              {new Date(stats.game_date).toLocaleDateString()}
            </p>
          </div>

          {/* Away Team */}
          <div className={`p-4 rounded-lg border-2 ${getWinnerStyle(stats.home_team.score, stats.away_team.score, false)}`}>
            <p className="text-sm text-gray-600 mb-1">{stats.away_team.team_name}</p>
            <p className="text-4xl font-black">{stats.away_team.score}</p>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Team Headers */}
        <div className="grid grid-cols-3 items-center mb-4 pb-4 border-b-2">
          <div className="text-right">
            <p className="font-black text-lg">{stats.home_team.team_abbr}</p>
            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Home</p>
          </div>
          <div className="text-center text-xs text-gray-500 uppercase tracking-wider font-semibold">
            Statistics
          </div>
          <div className="text-left">
            <p className="font-black text-lg">{stats.away_team.team_abbr}</p>
            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Away</p>
          </div>
        </div>

        {/* Stats Comparison */}
        <div className="space-y-0">
          <StatRow
            label="First Downs"
            homeValue={stats.home_team.first_downs}
            awayValue={stats.away_team.first_downs}
          />
          <StatRow
            label="Total Yards"
            homeValue={stats.home_team.total_yards}
            awayValue={stats.away_team.total_yards}
          />
          <StatRow
            label="Passing Yards"
            homeValue={stats.home_team.passing_yards}
            awayValue={stats.away_team.passing_yards}
          />
          <StatRow
            label="Rushing Yards"
            homeValue={stats.home_team.rushing_yards}
            awayValue={stats.away_team.rushing_yards}
          />
          <StatRow
            label="Turnovers"
            homeValue={stats.home_team.turnovers}
            awayValue={stats.away_team.turnovers}
          />
          <StatRow
            label="Penalties"
            homeValue={stats.home_team.penalties}
            awayValue={stats.away_team.penalties}
          />
          {stats.home_team.time_of_possession && stats.away_team.time_of_possession && (
            <StatRow
              label="Time of Possession"
              homeValue={stats.home_team.time_of_possession}
              awayValue={stats.away_team.time_of_possession}
            />
          )}
        </div>

        {/* Key Insights */}
        <div className="mt-6 pt-6 border-t">
          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">Key Insights</p>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Yards Differential</p>
              <p className="text-lg font-black">
                {Math.abs(stats.home_team.total_yards - stats.away_team.total_yards)} yds
              </p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Turnover Battle</p>
              <p className="text-lg font-black">
                {stats.home_team.turnovers} - {stats.away_team.turnovers}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
