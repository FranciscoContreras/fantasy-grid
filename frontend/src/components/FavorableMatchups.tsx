import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface FavorableMatchup {
  team_facing_weak_defense: string;
  weak_defense_team: string;
  game_id: string;
  matchup_score: number;
}

interface WeakDefense {
  team_id: string;
  team_name: string;
  rank: number;
  points_allowed?: number;
  yards_allowed?: number;
}

interface FavorableMatchupsData {
  players: FavorableMatchup[];
  weak_defenses: WeakDefense[];
  week: number;
  season: number;
}

export function FavorableMatchups() {
  const [data, setData] = useState<FavorableMatchupsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState<string>('ALL');
  const [selectedWeek, setSelectedWeek] = useState<number>(1);

  const positions = ['ALL', 'QB', 'RB', 'WR', 'TE'];

  useEffect(() => {
    fetchFavorableMatchups();
  }, [selectedPosition, selectedWeek]);

  const fetchFavorableMatchups = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        week: selectedWeek.toString(),
        season: '2024',
      });

      if (selectedPosition !== 'ALL') {
        params.append('position', selectedPosition);
      }

      const response = await fetch(`/api/analysis/favorable-matchups?${params}`);
      const result = await response.json();
      setData(result.data);
    } catch (error) {
      console.error('Failed to fetch favorable matchups:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMatchupScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-gray-500';
  };

  const getMatchupScoreLabel = (score: number) => {
    if (score >= 80) return 'EXCELLENT';
    if (score >= 60) return 'GOOD';
    return 'AVERAGE';
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-sm text-muted-foreground">Finding favorable matchups...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-2xl font-black">Favorable Matchups</CardTitle>
          <p className="text-sm text-muted-foreground">
            Players facing weak defenses - perfect for waiver wire pickups
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Position Filter */}
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                Position
              </p>
              <div className="flex flex-wrap gap-2">
                {positions.map((pos) => (
                  <Button
                    key={pos}
                    variant={selectedPosition === pos ? 'default' : 'outline'}
                    onClick={() => setSelectedPosition(pos)}
                    className="font-bold"
                  >
                    {pos}
                  </Button>
                ))}
              </div>
            </div>

            {/* Week Selector */}
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                Week
              </p>
              <div className="flex flex-wrap gap-2">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18].map((week) => (
                  <Button
                    key={week}
                    variant={selectedWeek === week ? 'default' : 'outline'}
                    onClick={() => setSelectedWeek(week)}
                    size="sm"
                  >
                    {week}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Weak Defenses */}
      {data && data.weak_defenses.length > 0 && (
        <Card className="w-full">
          <CardHeader>
            <CardTitle className="text-xl font-black">Weak Defenses (Bottom 10)</CardTitle>
            <p className="text-sm text-muted-foreground">
              Target players facing these defenses
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {data.weak_defenses.map((defense) => (
                <div
                  key={defense.team_id}
                  className="border rounded-lg p-4 bg-red-50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-black">{defense.team_name}</h3>
                      <p className="text-xs text-gray-600">Team ID: {defense.team_id}</p>
                    </div>
                    <Badge className="bg-red-500 text-white font-bold">
                      Rank #{defense.rank}
                    </Badge>
                  </div>
                  {defense.points_allowed && (
                    <div className="text-sm text-gray-600 mt-2">
                      <p>Points Allowed: {defense.points_allowed}</p>
                      {defense.yards_allowed && (
                        <p>Yards Allowed: {defense.yards_allowed}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Favorable Matchups */}
      {data && data.players.length > 0 ? (
        <Card className="w-full">
          <CardHeader>
            <CardTitle className="text-xl font-black">
              Top Favorable Matchups - Week {data.week}
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              {data.players.length} matchups found
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.players.map((matchup, index) => (
                <div
                  key={matchup.game_id + index}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Badge className="bg-black text-white font-bold">
                          #{index + 1}
                        </Badge>
                        <div>
                          <p className="font-black text-lg">
                            Team: {matchup.team_facing_weak_defense}
                          </p>
                          <p className="text-sm text-gray-600">
                            vs {matchup.weak_defense_team}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500">
                        Game ID: {matchup.game_id}
                      </p>
                    </div>
                    <div className="text-right">
                      <Badge
                        className={`${getMatchupScoreColor(matchup.matchup_score)} text-white font-bold mb-2`}
                      >
                        {getMatchupScoreLabel(matchup.matchup_score)}
                      </Badge>
                      <p className="text-2xl font-black">{matchup.matchup_score}</p>
                      <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                        Matchup Score
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="w-full">
          <CardContent className="p-12">
            <div className="text-center">
              <p className="text-lg font-semibold text-gray-600">
                No favorable matchups found
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Try adjusting your filters or selecting a different week
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
