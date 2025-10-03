import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface UpcomingMatchup {
  week: number;
  opponent: string;
  opponent_name: string;
  defense_rank: number | null;
  difficulty: string;
  matchup_score: number;
}

interface ScheduleLookaheadData {
  player: {
    id: string;
    name: string;
    position: string;
    team: string;
  };
  upcoming_matchups: UpcomingMatchup[];
  difficulty_score: number;
  difficulty_rating: string;
  weeks_analyzed: number;
}

interface ScheduleLookaheadProps {
  playerId: string;
  playerName?: string;
}

export function ScheduleLookahead({ playerId, playerName }: ScheduleLookaheadProps) {
  const [data, setData] = useState<ScheduleLookaheadData | null>(null);
  const [loading, setLoading] = useState(true);
  const [weeksAhead, setWeeksAhead] = useState<number>(4);

  useEffect(() => {
    fetchScheduleLookahead();
  }, [playerId, weeksAhead]);

  const fetchScheduleLookahead = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        weeks_ahead: weeksAhead.toString(),
        season: '2024',
      });

      const response = await fetch(`/api/analysis/schedule-lookahead/${playerId}?${params}`);
      const result = await response.json();
      setData(result.data);
    } catch (error) {
      console.error('Failed to fetch schedule lookahead:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800 border-green-500';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-500';
      case 'hard':
        return 'bg-red-100 text-red-800 border-red-500';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-500';
    }
  };

  const getDifficultyRatingColor = (rating: string) => {
    switch (rating.toLowerCase()) {
      case 'easy':
        return 'bg-green-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'hard':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getMatchupScoreBg = (score: number) => {
    if (score >= 75) return 'bg-green-50';
    if (score >= 50) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-sm text-muted-foreground">Loading schedule...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="text-center">
            <p className="text-lg font-semibold text-gray-600">Schedule not available</p>
            <p className="text-sm text-gray-500 mt-2">
              Unable to load schedule lookahead for this player
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Player Header */}
      <Card className="w-full">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl font-black">
                {data.player.name || playerName}
              </CardTitle>
              <div className="flex items-center gap-2 mt-2">
                <Badge variant="outline" className="font-bold">
                  {data.player.position}
                </Badge>
                <Badge variant="outline" className="font-bold">
                  {data.player.team}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <Badge
                className={`${getDifficultyRatingColor(data.difficulty_rating)} text-white font-bold text-lg px-4 py-2`}
              >
                {data.difficulty_rating.toUpperCase()}
              </Badge>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mt-2">
                Schedule Difficulty
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
            <div>
              <p className="text-sm text-gray-600 mb-1">Overall Difficulty Score</p>
              <p className="text-3xl font-black">{data.difficulty_score}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600 mb-1">Weeks Analyzed</p>
              <p className="text-3xl font-black">{data.weeks_analyzed}</p>
            </div>
          </div>

          {/* Weeks Selector */}
          <div className="mt-4">
            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
              Look Ahead
            </p>
            <div className="flex gap-2">
              {[3, 4, 5, 6].map((weeks) => (
                <Button
                  key={weeks}
                  variant={weeksAhead === weeks ? 'default' : 'outline'}
                  onClick={() => setWeeksAhead(weeks)}
                  size="sm"
                >
                  {weeks} weeks
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Upcoming Matchups */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-xl font-black">Upcoming Matchups</CardTitle>
          <p className="text-sm text-muted-foreground">
            Next {data.upcoming_matchups.length} weeks
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.upcoming_matchups.map((matchup, index) => (
              <div
                key={matchup.week}
                className={`border-2 rounded-lg p-4 ${getMatchupScoreBg(matchup.matchup_score)}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-center">
                      <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                        Week
                      </p>
                      <p className="text-2xl font-black">{matchup.week}</p>
                    </div>
                    <div className="border-l pl-4">
                      <p className="font-black text-lg">vs {matchup.opponent_name}</p>
                      <p className="text-sm text-gray-600">Team: {matchup.opponent}</p>
                      {matchup.defense_rank && (
                        <p className="text-xs text-gray-500 mt-1">
                          Defense Rank: #{matchup.defense_rank}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge
                      className={`${getDifficultyColor(matchup.difficulty)} font-bold mb-2 border-2`}
                    >
                      {matchup.difficulty.toUpperCase()}
                    </Badge>
                    <p className="text-2xl font-black">{matchup.matchup_score}</p>
                    <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                      Score
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Schedule Summary */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-xl font-black">Schedule Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-black">
                {data.upcoming_matchups.filter((m) => m.difficulty.toLowerCase() === 'easy').length}
              </p>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                Easy Matchups
              </p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-black">
                {data.upcoming_matchups.filter((m) => m.difficulty.toLowerCase() === 'medium').length}
              </p>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                Medium Matchups
              </p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-black">
                {data.upcoming_matchups.filter((m) => m.difficulty.toLowerCase() === 'hard').length}
              </p>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                Hard Matchups
              </p>
            </div>
          </div>

          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-semibold mb-2">Recommendation</p>
            <p className="text-sm text-gray-700">
              {data.difficulty_rating.toLowerCase() === 'easy' && (
                <>
                  <span className="font-black text-green-600">EXCELLENT SCHEDULE.</span> This player
                  faces favorable matchups in the coming weeks. Great time to start or trade for them.
                </>
              )}
              {data.difficulty_rating.toLowerCase() === 'medium' && (
                <>
                  <span className="font-black text-yellow-600">MODERATE SCHEDULE.</span> Mixed bag of
                  matchups ahead. Evaluate week-by-week based on opponent strength.
                </>
              )}
              {data.difficulty_rating.toLowerCase() === 'hard' && (
                <>
                  <span className="font-black text-red-600">TOUGH SCHEDULE.</span> Difficult matchups
                  ahead. Consider benching or looking for better options unless this player is elite.
                </>
              )}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
