import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';

interface Game {
  week: number;
  opponent: string;
  win_probability: number;
}

interface PlayoffSimulation {
  playoff_odds: number;
  current_record: {
    wins: number;
    losses: number;
  };
  projected_final_wins: number;
  win_distribution: { [wins: number]: number };
  must_win_weeks: number[];
  remaining_games: number;
  strategy_recommendation: string;
  simulations_run: number;
}

export function PlayoffOdds() {
  const [wins, setWins] = useState<number>(6);
  const [losses, setLosses] = useState<number>(3);
  const [remainingGames, setRemainingGames] = useState<Game[]>([
    { week: 11, opponent: 'Team A', win_probability: 65 },
    { week: 12, opponent: 'Team B', win_probability: 45 },
    { week: 13, opponent: 'Team C', win_probability: 55 },
    { week: 14, opponent: 'Team D', win_probability: 70 },
  ]);
  const [simulation, setSimulation] = useState<PlayoffSimulation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/league/playoffs/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_record: { wins, losses },
          remaining_schedule: remainingGames,
          num_simulations: 1000,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        setSimulation(result.data);
      } else {
        setError(result.error || 'Failed to simulate playoffs');
      }
    } catch (err) {
      console.error('Playoff simulation error:', err);
      setError('Failed to simulate playoffs');
    } finally {
      setLoading(false);
    }
  };

  const getOddsColor = (odds: number) => {
    if (odds >= 80) return 'bg-green-500';
    if (odds >= 60) return 'bg-yellow-500';
    if (odds >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getOddsLabel = (odds: number) => {
    if (odds >= 80) return 'LOCK';
    if (odds >= 60) return 'LIKELY';
    if (odds >= 40) return 'TOSS-UP';
    return 'LONGSHOT';
  };

  const getStrategyColor = (strategy: string) => {
    if (strategy.includes('COAST')) return 'bg-green-100 text-green-800';
    if (strategy.includes('MAINTAIN')) return 'bg-blue-100 text-blue-800';
    if (strategy.includes('PUSH')) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-2xl font-black">Playoff Odds Calculator</CardTitle>
          <p className="text-sm text-muted-foreground">
            Monte Carlo simulation of your playoff chances
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Current Record */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2 block">
                  Wins
                </label>
                <Input
                  type="number"
                  value={wins}
                  onChange={(e) => setWins(parseInt(e.target.value) || 0)}
                  min="0"
                  max="17"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2 block">
                  Losses
                </label>
                <Input
                  type="number"
                  value={losses}
                  onChange={(e) => setLosses(parseInt(e.target.value) || 0)}
                  min="0"
                  max="17"
                />
              </div>
            </div>

            {/* Current Record Display */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm font-semibold mb-1">Current Record</p>
              <p className="text-3xl font-black">
                {wins}-{losses}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {remainingGames.length} games remaining
              </p>
            </div>

            {/* Run Simulation Button */}
            <Button
              onClick={runSimulation}
              disabled={loading}
              className="w-full font-bold"
            >
              {loading ? 'Simulating...' : 'Run 1,000 Simulations'}
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

      {/* Simulation Results */}
      {simulation && (
        <>
          {/* Playoff Odds */}
          <Card className="w-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl font-black">Playoff Probability</CardTitle>
                <Badge
                  className={`${getOddsColor(simulation.playoff_odds)} text-white font-bold text-lg px-4 py-2`}
                >
                  {getOddsLabel(simulation.playoff_odds)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center mb-6">
                <p className="text-6xl font-black mb-2">{simulation.playoff_odds}%</p>
                <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold">
                  Chance to Make Playoffs
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                    Current Record
                  </p>
                  <p className="text-3xl font-black">
                    {simulation.current_record.wins}-{simulation.current_record.losses}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                    Projected Final Wins
                  </p>
                  <p className="text-3xl font-black">{simulation.projected_final_wins}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-2">
                    Games Remaining
                  </p>
                  <p className="text-3xl font-black">{simulation.remaining_games}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Strategy Recommendation */}
          <Card className="w-full">
            <CardHeader>
              <CardTitle className="text-xl font-black">Recommended Strategy</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 rounded-lg p-6">
                <Badge className={`${getStrategyColor(simulation.strategy_recommendation)} font-bold text-lg px-4 py-2 mb-4`}>
                  {simulation.strategy_recommendation}
                </Badge>
                <p className="text-sm mt-3">
                  {simulation.strategy_recommendation.includes('COAST') &&
                    "You're in excellent playoff position. Focus on avoiding injuries and don't make risky moves."}
                  {simulation.strategy_recommendation.includes('MAINTAIN') &&
                    "Stay the course with your current roster. Make only minor improvements if opportunities arise."}
                  {simulation.strategy_recommendation.includes('PUSH') &&
                    "Every game matters now. Look for upgrades on waivers and consider strategic trades to improve your roster."}
                  {simulation.strategy_recommendation.includes('ALL-IN') &&
                    "You need wins NOW. Be aggressive with trades, waivers, and lineup decisions. Take calculated risks."}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Must-Win Weeks */}
          {simulation.must_win_weeks.length > 0 && (
            <Card className="w-full">
              <CardHeader>
                <CardTitle className="text-xl font-black">Must-Win Weeks</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Critical games for your playoff push
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {simulation.must_win_weeks.map((week) => (
                    <div key={week} className="bg-red-50 border border-red-500 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-black text-lg">Week {week}</p>
                          <p className="text-sm text-gray-600">Critical matchup</p>
                        </div>
                        <Badge className="bg-red-500 text-white font-bold">MUST WIN</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Win Distribution */}
          <Card className="w-full">
            <CardHeader>
              <CardTitle className="text-xl font-black">Win Distribution</CardTitle>
              <p className="text-sm text-muted-foreground">
                Likelihood of final win totals (based on {simulation.simulations_run.toLocaleString()} simulations)
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(simulation.win_distribution)
                  .sort((a, b) => parseInt(b[0]) - parseInt(a[0]))
                  .map(([winTotal, percentage]) => (
                    <div key={winTotal} className="flex items-center gap-3">
                      <div className="w-16 font-black">{winTotal} wins</div>
                      <div className="flex-1 bg-gray-200 rounded-full h-6 overflow-hidden">
                        <div
                          className="bg-black h-full flex items-center justify-end pr-2"
                          style={{ width: `${percentage}%` }}
                        >
                          <span className="text-white text-xs font-bold">
                            {percentage > 5 ? `${percentage}%` : ''}
                          </span>
                        </div>
                      </div>
                      <div className="w-12 text-right text-sm font-bold">{percentage}%</div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>

          {/* Simulation Details */}
          <Card className="w-full">
            <CardHeader>
              <CardTitle className="text-lg font-black">Remaining Schedule</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {remainingGames.map((game) => (
                  <div key={game.week} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                    <div>
                      <p className="font-bold">Week {game.week}</p>
                      <p className="text-sm text-gray-600">vs {game.opponent}</p>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className="font-bold">
                        {game.win_probability}% win chance
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Loading State */}
      {loading && !simulation && (
        <Card className="w-full">
          <CardContent className="p-12">
            <div className="flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
                <p className="text-sm text-muted-foreground">
                  Running Monte Carlo simulation...
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
