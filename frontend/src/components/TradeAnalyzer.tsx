import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';

interface Player {
  id: string;
  name: string;
  position: string;
  team?: string;
  trade_value: number;
}

interface TradeEvaluation {
  team_a: {
    players: Player[];
    total_value: number;
    positions: { [key: string]: number };
    receiving: Player[];
  };
  team_b: {
    players: Player[];
    total_value: number;
    positions: { [key: string]: number };
    receiving: Player[];
  };
  analysis: {
    fairness_score: number;
    value_difference: number;
    winner: string | null;
    recommendation: string;
    trade_type: string;
  };
}

export function TradeAnalyzer() {
  const [teamAPlayerIds, setTeamAPlayerIds] = useState<string>('');
  const [teamBPlayerIds, setTeamBPlayerIds] = useState<string>('');
  const [evaluation, setEvaluation] = useState<TradeEvaluation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const evaluateTrade = async () => {
    setLoading(true);
    setError(null);

    try {
      // Parse comma-separated player IDs
      const teamAGives = teamAPlayerIds.split(',').map(id => id.trim()).filter(id => id);
      const teamBGives = teamBPlayerIds.split(',').map(id => id.trim()).filter(id => id);

      if (teamAGives.length === 0 || teamBGives.length === 0) {
        setError('Both teams must give at least one player');
        setLoading(false);
        return;
      }

      const response = await fetch('/api/trades/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          team_a_gives: teamAGives,
          team_b_gives: teamBGives,
          season: 2025,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        setEvaluation(result.data);
      } else {
        setError(result.error || 'Failed to evaluate trade');
      }
    } catch (err) {
      console.error('Trade evaluation error:', err);
      setError('Failed to evaluate trade');
    } finally {
      setLoading(false);
    }
  };

  const getFairnessColor = (score: number) => {
    if (score >= 85) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 50) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getFairnessLabel = (score: number) => {
    if (score >= 85) return 'FAIR';
    if (score >= 70) return 'SLIGHTLY UNBALANCED';
    if (score >= 50) return 'UNBALANCED';
    return 'VERY LOPSIDED';
  };

  const getPositionBadgeColor = (position: string) => {
    const colors: Record<string, string> = {
      QB: 'bg-purple-100 text-purple-800',
      RB: 'bg-blue-100 text-blue-800',
      WR: 'bg-green-100 text-green-800',
      TE: 'bg-yellow-100 text-yellow-800',
      K: 'bg-gray-100 text-gray-800',
      DEF: 'bg-red-100 text-red-800',
    };
    return colors[position] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-2xl font-black">Trade Analyzer</CardTitle>
          <p className="text-sm text-muted-foreground">
            Evaluate trade fairness and value for both teams
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Team A */}
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2 block">
                Team A Gives (Player IDs, comma-separated)
              </label>
              <Input
                type="text"
                placeholder="e.g., player_123, player_456"
                value={teamAPlayerIds}
                onChange={(e) => setTeamAPlayerIds(e.target.value)}
                className="font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter player IDs separated by commas
              </p>
            </div>

            {/* Team B */}
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2 block">
                Team B Gives (Player IDs, comma-separated)
              </label>
              <Input
                type="text"
                placeholder="e.g., player_789"
                value={teamBPlayerIds}
                onChange={(e) => setTeamBPlayerIds(e.target.value)}
                className="font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter player IDs separated by commas
              </p>
            </div>

            {/* Evaluate Button */}
            <Button
              onClick={evaluateTrade}
              disabled={loading}
              className="w-full font-bold"
            >
              {loading ? 'Evaluating...' : 'Evaluate Trade'}
            </Button>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-500 rounded-lg p-4">
                <p className="text-sm text-red-800 font-semibold">{error}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Evaluation Results */}
      {evaluation && (
        <>
          {/* Trade Summary */}
          <Card className="w-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl font-black">Trade Evaluation</CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    {evaluation.analysis.trade_type} Trade
                  </p>
                </div>
                <div className="text-right">
                  <Badge
                    className={`${getFairnessColor(evaluation.analysis.fairness_score)} text-white font-bold text-lg px-4 py-2`}
                  >
                    {getFairnessLabel(evaluation.analysis.fairness_score)}
                  </Badge>
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mt-2">
                    Fairness: {evaluation.analysis.fairness_score}/100
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="font-bold text-sm mb-2">Recommendation</p>
                <p className="text-sm">{evaluation.analysis.recommendation}</p>
                {evaluation.analysis.winner && (
                  <p className="text-sm mt-2">
                    <span className="font-bold">Winner:</span> {evaluation.analysis.winner}
                  </p>
                )}
                <p className="text-sm mt-2">
                  <span className="font-bold">Value Difference:</span>{' '}
                  {evaluation.analysis.value_difference} points
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Team Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Team A */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-black">Team A</CardTitle>
                <div className="flex items-center gap-2 mt-2">
                  <Badge className="bg-black text-white font-bold">
                    Value: {evaluation.team_a.total_value}
                  </Badge>
                  <Badge variant="outline" className="font-bold">
                    Giving {evaluation.team_a.players.length} player(s)
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Giving */}
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                      Giving Away
                    </p>
                    <div className="space-y-2">
                      {evaluation.team_a.players.map((player) => (
                        <div
                          key={player.id}
                          className="border rounded-lg p-3 bg-red-50"
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-black">{player.name}</p>
                              <p className="text-xs text-gray-600">{player.team}</p>
                            </div>
                            <div className="text-right">
                              <Badge className={getPositionBadgeColor(player.position)}>
                                {player.position}
                              </Badge>
                              <p className="text-sm font-bold mt-1">
                                Value: {player.trade_value}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Receiving */}
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                      Receiving
                    </p>
                    <div className="space-y-2">
                      {evaluation.team_a.receiving.map((player) => (
                        <div
                          key={player.id}
                          className="border rounded-lg p-3 bg-green-50"
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-black">{player.name}</p>
                              <p className="text-xs text-gray-600">{player.team}</p>
                            </div>
                            <div className="text-right">
                              <Badge className={getPositionBadgeColor(player.position)}>
                                {player.position}
                              </Badge>
                              <p className="text-sm font-bold mt-1">
                                Value: {player.trade_value}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Team B */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-black">Team B</CardTitle>
                <div className="flex items-center gap-2 mt-2">
                  <Badge className="bg-black text-white font-bold">
                    Value: {evaluation.team_b.total_value}
                  </Badge>
                  <Badge variant="outline" className="font-bold">
                    Giving {evaluation.team_b.players.length} player(s)
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Giving */}
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                      Giving Away
                    </p>
                    <div className="space-y-2">
                      {evaluation.team_b.players.map((player) => (
                        <div
                          key={player.id}
                          className="border rounded-lg p-3 bg-red-50"
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-black">{player.name}</p>
                              <p className="text-xs text-gray-600">{player.team}</p>
                            </div>
                            <div className="text-right">
                              <Badge className={getPositionBadgeColor(player.position)}>
                                {player.position}
                              </Badge>
                              <p className="text-sm font-bold mt-1">
                                Value: {player.trade_value}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Receiving */}
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                      Receiving
                    </p>
                    <div className="space-y-2">
                      {evaluation.team_b.receiving.map((player) => (
                        <div
                          key={player.id}
                          className="border rounded-lg p-3 bg-green-50"
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-black">{player.name}</p>
                              <p className="text-xs text-gray-600">{player.team}</p>
                            </div>
                            <div className="text-right">
                              <Badge className={getPositionBadgeColor(player.position)}>
                                {player.position}
                              </Badge>
                              <p className="text-sm font-bold mt-1">
                                Value: {player.trade_value}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Position Analysis */}
          <Card className="w-full">
            <CardHeader>
              <CardTitle className="text-lg font-black">Position Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                {/* Team A Positions */}
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">
                    Team A
                  </p>
                  <div className="space-y-2">
                    {Object.entries(evaluation.team_a.positions).map(([position, count]) => (
                      <div
                        key={position}
                        className="flex items-center justify-between bg-gray-50 rounded-lg p-3"
                      >
                        <Badge className={getPositionBadgeColor(position)}>
                          {position}
                        </Badge>
                        <p className="font-bold">{count} player(s)</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Team B Positions */}
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-3">
                    Team B
                  </p>
                  <div className="space-y-2">
                    {Object.entries(evaluation.team_b.positions).map(([position, count]) => (
                      <div
                        key={position}
                        className="flex items-center justify-between bg-gray-50 rounded-lg p-3"
                      >
                        <Badge className={getPositionBadgeColor(position)}>
                          {position}
                        </Badge>
                        <p className="font-bold">{count} player(s)</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
