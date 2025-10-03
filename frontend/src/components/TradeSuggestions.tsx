import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';

interface Player {
  id: string;
  name: string;
  position: string;
  team: string;
}

interface TradeSuggestion {
  player: Player;
  value: number;
  value_difference: number;
  fairness_score: number;
  trade_type: string;
  recommendation: string;
}

interface TradeSuggestionsData {
  trading_away: {
    player: Player;
    value: number;
  };
  suggestions: TradeSuggestion[];
  total_suggestions: number;
}

interface TradeSuggestionsProps {
  playerId?: string;
  playerName?: string;
}

export function TradeSuggestions({ playerId: initialPlayerId, playerName }: TradeSuggestionsProps) {
  const [playerId, setPlayerId] = useState<string>(initialPlayerId || '');
  const [selectedPositions, setSelectedPositions] = useState<string[]>([]);
  const [data, setData] = useState<TradeSuggestionsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF'];

  const fetchSuggestions = async () => {
    if (!playerId.trim()) {
      setError('Please enter a player ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        season: '2024',
      });

      if (selectedPositions.length > 0) {
        params.append('positions', selectedPositions.join(','));
      }

      const response = await fetch(`/api/trades/suggestions/${playerId}?${params}`);
      const result = await response.json();

      if (response.ok) {
        setData(result.data);
      } else {
        setError(result.error || 'Failed to get trade suggestions');
      }
    } catch (err) {
      console.error('Trade suggestions error:', err);
      setError('Failed to get trade suggestions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialPlayerId) {
      fetchSuggestions();
    }
  }, [initialPlayerId]);

  const togglePosition = (position: string) => {
    setSelectedPositions((prev) =>
      prev.includes(position)
        ? prev.filter((p) => p !== position)
        : [...prev, position]
    );
  };

  const getFairnessColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 75) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-gray-500';
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
          <CardTitle className="text-2xl font-black">Trade Suggestions</CardTitle>
          <p className="text-sm text-muted-foreground">
            Find fair trade targets for your player
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Player ID Input */}
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2 block">
                Player ID to Trade Away
              </label>
              <Input
                type="text"
                placeholder="e.g., player_123"
                value={playerId}
                onChange={(e) => setPlayerId(e.target.value)}
                className="font-mono"
                disabled={!!initialPlayerId}
              />
              {playerName && (
                <p className="text-xs text-gray-500 mt-1">
                  Trading: {playerName}
                </p>
              )}
            </div>

            {/* Position Filter */}
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2 block">
                Desired Positions (Optional)
              </label>
              <div className="flex flex-wrap gap-2">
                {positions.map((pos) => (
                  <Button
                    key={pos}
                    variant={selectedPositions.includes(pos) ? 'default' : 'outline'}
                    onClick={() => togglePosition(pos)}
                    size="sm"
                  >
                    {pos}
                  </Button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {selectedPositions.length > 0
                  ? `Looking for: ${selectedPositions.join(', ')}`
                  : 'Select positions or leave empty for all'}
              </p>
            </div>

            {/* Get Suggestions Button */}
            <Button
              onClick={fetchSuggestions}
              disabled={loading || !playerId.trim()}
              className="w-full font-bold"
            >
              {loading ? 'Finding Trades...' : 'Get Trade Suggestions'}
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

      {/* Results */}
      {data && (
        <>
          {/* Trading Away Player */}
          <Card className="w-full">
            <CardHeader>
              <CardTitle className="text-lg font-black">Trading Away</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-gray-300 rounded-lg p-4 bg-gray-50">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-xl font-black">{data.trading_away.player.name}</h3>
                    <p className="text-sm text-gray-600">{data.trading_away.player.team}</p>
                  </div>
                  <div className="text-right">
                    <Badge className={getPositionBadgeColor(data.trading_away.player.position)}>
                      {data.trading_away.player.position}
                    </Badge>
                    <p className="text-2xl font-black mt-2">{data.trading_away.value}</p>
                    <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                      Trade Value
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Suggestions List */}
          {data.suggestions.length > 0 ? (
            <Card className="w-full">
              <CardHeader>
                <CardTitle className="text-lg font-black">
                  Suggested Trade Targets ({data.total_suggestions})
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Ranked by fairness and value match
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.suggestions.map((suggestion, index) => (
                    <div
                      key={suggestion.player.id}
                      className="border-2 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <Badge className="bg-black text-white font-bold">
                            #{index + 1}
                          </Badge>
                          <div>
                            <h3 className="font-black text-lg">{suggestion.player.name}</h3>
                            <p className="text-sm text-gray-600">{suggestion.player.team}</p>
                          </div>
                        </div>
                        <Badge className={getPositionBadgeColor(suggestion.player.position)}>
                          {suggestion.player.position}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">
                            Trade Value
                          </p>
                          <p className="text-xl font-black">{suggestion.value}</p>
                        </div>

                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">
                            Value Diff
                          </p>
                          <p className="text-xl font-black">
                            {suggestion.value_difference > 0 ? '+' : ''}
                            {suggestion.value_difference}
                          </p>
                        </div>

                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">
                            Fairness
                          </p>
                          <div className="flex items-center gap-2">
                            <p className="text-xl font-black">{suggestion.fairness_score}</p>
                            <div
                              className={`w-3 h-3 rounded-full ${getFairnessColor(suggestion.fairness_score)}`}
                            ></div>
                          </div>
                        </div>

                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">
                            Type
                          </p>
                          <p className="text-sm font-black">{suggestion.trade_type}</p>
                        </div>
                      </div>

                      <div className="mt-3 pt-3 border-t">
                        <Badge
                          className={`${getFairnessColor(suggestion.fairness_score)} text-white font-bold`}
                        >
                          {suggestion.recommendation}
                        </Badge>
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
                    No trade suggestions found
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Try adjusting your position filters or check back later
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Loading State */}
      {loading && !data && (
        <Card className="w-full">
          <CardContent className="p-12">
            <div className="flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
                <p className="text-sm text-muted-foreground">Finding trade suggestions...</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
