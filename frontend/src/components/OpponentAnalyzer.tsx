import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface Player {
  id: string;
  name: string;
  position: string;
  team?: string;
}

interface RosterAnalysis {
  total_strength: number;
  position_breakdown: {
    [position: string]: {
      count: number;
      strength: number;
      projected_points: number;
    };
  };
  weak_positions: string[];
  strengths: string[];
  projected_points: number;
}

interface OpponentAnalysis {
  opponent: RosterAnalysis & { weak_positions: string[] };
  your_team: RosterAnalysis;
  matchup: {
    win_probability: number;
    strategy: string;
    game_plan: string[];
    point_differential: number;
  };
  week?: number;
  season: number;
}

export function OpponentAnalyzer() {
  const [opponentRoster, setOpponentRoster] = useState<Player[]>([
    { id: 'opp1', name: 'Opponent QB', position: 'QB', team: 'Team A' },
    { id: 'opp2', name: 'Opponent RB1', position: 'RB', team: 'Team B' },
    { id: 'opp3', name: 'Opponent RB2', position: 'RB', team: 'Team C' },
  ]);
  const [yourRoster, setYourRoster] = useState<Player[]>([
    { id: 'you1', name: 'Your QB', position: 'QB', team: 'Team D' },
    { id: 'you2', name: 'Your RB1', position: 'RB', team: 'Team E' },
    { id: 'you3', name: 'Your RB2', position: 'RB', team: 'Team F' },
  ]);
  const [analysis, setAnalysis] = useState<OpponentAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeMatchup = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/league/opponent/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          opponent_roster: opponentRoster,
          your_roster: yourRoster,
          week: 10,
          season: 2025,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        setAnalysis(result.data);
      } else {
        setError(result.error || 'Failed to analyze opponent');
      }
    } catch (err) {
      console.error('Opponent analysis error:', err);
      setError('Failed to analyze opponent');
    } finally {
      setLoading(false);
    }
  };

  const getWinProbColor = (prob: number) => {
    if (prob >= 65) return 'bg-green-500';
    if (prob >= 45) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStrategyIcon = (strategy: string) => {
    if (strategy === 'BOOM_BUST') return '🎯';
    if (strategy === 'SAFE_FLOOR') return '🛡️';
    return '⚖️';
  };

  const getStrategyColor = (strategy: string) => {
    if (strategy === 'BOOM_BUST') return 'bg-orange-100 text-orange-800';
    if (strategy === 'SAFE_FLOOR') return 'bg-green-100 text-green-800';
    return 'bg-blue-100 text-blue-800';
  };

  return (
    <div className="space-y-6">
      {/* Mock Roster Display & Analyze Button */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-2xl font-black">Opponent Analyzer</CardTitle>
          <p className="text-sm text-muted-foreground">
            Analyze matchup and get strategic recommendations
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Using mock rosters for demonstration. In production, you would input actual player data.
            </p>

            <Button
              onClick={analyzeMatchup}
              disabled={loading}
              className="w-full font-bold"
            >
              {loading ? 'Analyzing...' : 'Analyze Matchup'}
            </Button>

            {error && (
              <div className="bg-red-50 border border-red-500 rounded-lg p-4">
                <p className="text-sm text-red-800 font-semibold">{error}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <>
          {/* Win Probability */}
          <Card className="w-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl font-black">Matchup Overview</CardTitle>
                <Badge
                  className={`${getWinProbColor(analysis.matchup.win_probability)} text-white font-bold text-lg px-4 py-2`}
                >
                  {analysis.matchup.win_probability}% Win Probability
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                    Your Projected Points
                  </p>
                  <p className="text-3xl font-black">{analysis.your_team.projected_points}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                    Point Differential
                  </p>
                  <p className={`text-3xl font-black ${analysis.matchup.point_differential > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {analysis.matchup.point_differential > 0 ? '+' : ''}
                    {analysis.matchup.point_differential}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                    Opponent Projected
                  </p>
                  <p className="text-3xl font-black">{analysis.opponent.projected_points}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Strategy Recommendation */}
          <Card className="w-full">
            <CardHeader>
              <CardTitle className="text-xl font-black">
                {getStrategyIcon(analysis.matchup.strategy)} Recommended Strategy
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Badge className={`${getStrategyColor(analysis.matchup.strategy)} font-bold text-lg px-4 py-2`}>
                    {analysis.matchup.strategy.replace('_', ' ')}
                  </Badge>
                  <p className="text-sm text-gray-600">
                    {analysis.matchup.strategy === 'BOOM_BUST' && 'Target high-ceiling players'}
                    {analysis.matchup.strategy === 'SAFE_FLOOR' && 'Play consistent, safe options'}
                    {analysis.matchup.strategy === 'BALANCED' && 'Mix safe players with upside'}
                  </p>
                </div>

                {/* Game Plan */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="font-bold text-sm mb-3">Game Plan:</p>
                  <ul className="space-y-2">
                    {analysis.matchup.game_plan.map((item, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-black font-bold">•</span>
                        <span className="text-sm">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Roster Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Your Team */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-black">Your Team</CardTitle>
                <div className="flex items-center gap-2 mt-2">
                  <Badge className="bg-black text-white font-bold">
                    Strength: {analysis.your_team.total_strength}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                      Position Breakdown
                    </p>
                    {Object.entries(analysis.your_team.position_breakdown).map(([pos, data]) => (
                      <div key={pos} className="flex items-center justify-between bg-gray-50 rounded-lg p-3 mb-2">
                        <div>
                          <Badge variant="outline" className="font-bold">{pos}</Badge>
                          <p className="text-xs text-gray-600 mt-1">{data.count} player(s)</p>
                        </div>
                        <div className="text-right">
                          <p className="font-black">{data.projected_points.toFixed(1)}</p>
                          <p className="text-xs text-gray-500">pts</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {analysis.your_team.strengths.length > 0 && (
                    <div className="bg-green-50 border border-green-500 rounded-lg p-3">
                      <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                        Your Strengths
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {analysis.your_team.strengths.map((pos) => (
                          <Badge key={pos} className="bg-green-500 text-white font-bold">
                            {pos}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Opponent Team */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-black">Opponent</CardTitle>
                <div className="flex items-center gap-2 mt-2">
                  <Badge className="bg-black text-white font-bold">
                    Strength: {analysis.opponent.total_strength}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                      Position Breakdown
                    </p>
                    {Object.entries(analysis.opponent.position_breakdown).map(([pos, data]) => (
                      <div key={pos} className="flex items-center justify-between bg-gray-50 rounded-lg p-3 mb-2">
                        <div>
                          <Badge variant="outline" className="font-bold">{pos}</Badge>
                          <p className="text-xs text-gray-600 mt-1">{data.count} player(s)</p>
                        </div>
                        <div className="text-right">
                          <p className="font-black">{data.projected_points.toFixed(1)}</p>
                          <p className="text-xs text-gray-500">pts</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {analysis.opponent.weak_positions.length > 0 && (
                    <div className="bg-red-50 border border-red-500 rounded-lg p-3">
                      <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                        Opponent Weaknesses
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {analysis.opponent.weak_positions.map((pos) => (
                          <Badge key={pos} className="bg-red-500 text-white font-bold">
                            {pos}
                          </Badge>
                        ))}
                      </div>
                      <p className="text-xs text-gray-600 mt-2">
                        Target these positions in your lineup
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* Loading State */}
      {loading && !analysis && (
        <Card className="w-full">
          <CardContent className="p-12">
            <div className="flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
                <p className="text-sm text-muted-foreground">Analyzing opponent...</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
