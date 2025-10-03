import { useState, useEffect } from 'react';
import { Roster, RosterPlayer } from '../types';
import { getRoster, analyzeRoster } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { getPlayerImageUrl, getTeamLogoUrl } from '../lib/images';
import { PlayerSearch } from './PlayerSearch';
import { WeeklyLineup } from './WeeklyLineup';
import {
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowUpDown,
  Zap
} from 'lucide-react';

interface RosterDashboardProps {
  rosterId: number;
  onRosterUpdate?: () => void;
}

interface PlayerWithAnalysis extends RosterPlayer {
  projected_points?: number;
  matchup_score?: number;
  ai_grade?: string;
  recommendation?: 'START' | 'SIT' | 'CONSIDER';
  confidence_score?: number;
  opponent_team?: string;
}

const ROSTER_SLOTS = [
  { slot: 'QB', label: 'QB', isStarter: true },
  { slot: 'RB1', label: 'RB', isStarter: true },
  { slot: 'RB2', label: 'RB', isStarter: true },
  { slot: 'WR1', label: 'WR', isStarter: true },
  { slot: 'WR2', label: 'WR', isStarter: true },
  { slot: 'WR3', label: 'WR', isStarter: true },
  { slot: 'TE', label: 'TE', isStarter: true },
  { slot: 'FLEX', label: 'FLEX', isStarter: true },
  { slot: 'K', label: 'K', isStarter: true },
  { slot: 'DEF', label: 'DEF', isStarter: true },
];

const INJURY_STATUS_COLORS: Record<string, string> = {
  HEALTHY: 'bg-green-500',
  PROBABLE: 'bg-blue-500',
  QUESTIONABLE: 'bg-yellow-500',
  DOUBTFUL: 'bg-orange-500',
  OUT: 'bg-red-500',
};

const RECOMMENDATION_COLORS: Record<string, { border: string; bg: string; text: string }> = {
  START: { border: 'border-green-500', bg: 'bg-green-50 dark:bg-green-950/20', text: 'text-green-700 dark:text-green-400' },
  SIT: { border: 'border-red-500', bg: 'bg-red-50 dark:bg-red-950/20', text: 'text-red-700 dark:text-red-400' },
  CONSIDER: { border: 'border-yellow-500', bg: 'bg-yellow-50 dark:bg-yellow-950/20', text: 'text-yellow-700 dark:text-yellow-400' },
};

export function RosterDashboard({ rosterId, onRosterUpdate }: RosterDashboardProps) {
  const [roster, setRoster] = useState<Roster | null>(null);
  const [playersWithAnalysis, setPlayersWithAnalysis] = useState<Map<number, PlayerWithAnalysis>>(new Map());
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [addingToSlot, setAddingToSlot] = useState<string | null>(null);
  const [view, setView] = useState<'weekly' | 'classic'>('weekly');

  useEffect(() => {
    loadRoster();
  }, [rosterId]);

  const loadRoster = async () => {
    try {
      setLoading(true);
      const response = await getRoster(rosterId);
      setRoster(response.data);
    } catch (err) {
      setError('Failed to load roster');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeRoster = async () => {
    try {
      setAnalyzing(true);
      setError('');
      // This will trigger analysis for the current week
      await analyzeRoster(rosterId);
      // Reload to get updated analysis
      await loadRoster();
    } catch (err) {
      setError('Failed to analyze roster');
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const getPlayerInSlot = (slot: string): PlayerWithAnalysis | undefined => {
    return roster?.players?.find((p) => p.roster_slot === slot) as PlayerWithAnalysis;
  };

  const calculateRosterStrength = (): number => {
    const starters = roster?.players?.filter(p =>
      ROSTER_SLOTS.some(s => s.isStarter && s.slot === p.roster_slot)
    ) || [];

    if (starters.length === 0) return 0;

    const totalProjected = starters.reduce((sum, p) => {
      const analysis = playersWithAnalysis.get(p.id);
      return sum + (analysis?.projected_points || 0);
    }, 0);

    return Math.round((totalProjected / starters.length) * 5); // Scale to 0-100
  };

  const getTotalProjectedPoints = (): number => {
    const starters = roster?.players?.filter(p =>
      ROSTER_SLOTS.some(s => s.isStarter && s.slot === p.roster_slot)
    ) || [];

    return starters.reduce((sum, p) => {
      const analysis = playersWithAnalysis.get(p.id);
      return sum + (analysis?.projected_points || 0);
    }, 0);
  };

  const getRecommendationCounts = () => {
    const starters = roster?.players?.filter(p =>
      ROSTER_SLOTS.some(s => s.isStarter && s.slot === p.roster_slot)
    ) || [];

    return {
      start: starters.filter(p => {
        const analysis = playersWithAnalysis.get(p.id);
        return analysis?.recommendation === 'START';
      }).length,
      sit: starters.filter(p => {
        const analysis = playersWithAnalysis.get(p.id);
        return analysis?.recommendation === 'SIT';
      }).length,
      consider: starters.filter(p => {
        const analysis = playersWithAnalysis.get(p.id);
        return analysis?.recommendation === 'CONSIDER';
      }).length,
    };
  };

  const getInjuryCount = (): number => {
    return roster?.players?.filter(p => p.injury_status !== 'HEALTHY').length || 0;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">Loading roster...</p>
        </CardContent>
      </Card>
    );
  }

  if (!roster) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-red-600">Failed to load roster</p>
        </CardContent>
      </Card>
    );
  }

  const rosterStrength = calculateRosterStrength();
  const totalPoints = getTotalProjectedPoints();
  const recommendations = getRecommendationCounts();
  const injuryCount = getInjuryCount();
  const benchPlayers = roster.players?.filter(p => p.roster_slot === 'BENCH') || [];

  return (
    <div className="space-y-6">
      {/* Header with Quick Stats */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-2xl">{roster.name}</CardTitle>
              {roster.league_name && (
                <p className="text-sm text-muted-foreground mt-1">
                  {roster.league_name} • {roster.scoring_type}
                </p>
              )}
            </div>
            <div className="flex items-center gap-3">
              {/* View Switcher */}
              <div className="flex gap-2 border rounded-lg p-1">
                <Button
                  variant={view === 'weekly' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setView('weekly')}
                  className="px-4 font-bold"
                >
                  WEEKLY
                </Button>
                <Button
                  variant={view === 'classic' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setView('classic')}
                  className="px-4 font-bold"
                >
                  CLASSIC
                </Button>
              </div>
              <Button
                onClick={handleAnalyzeRoster}
                disabled={analyzing}
                size="lg"
                className="min-w-40"
              >
                {analyzing ? (
                  <>
                    <Clock className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="mr-2 h-4 w-4" />
                    Analyze Roster
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>

        {/* Quick Stats Dashboard */}
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Roster Strength */}
            <div className="p-4 border rounded-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/20 dark:to-blue-900/20">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-muted-foreground">Roster Strength</p>
                <TrendingUp className="h-4 w-4 text-blue-600" />
              </div>
              <p className="text-3xl font-bold text-blue-700 dark:text-blue-400">
                {rosterStrength}
                <span className="text-lg text-muted-foreground">/100</span>
              </p>
            </div>

            {/* Projected Points */}
            <div className="p-4 border rounded-lg bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/20 dark:to-green-900/20">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-muted-foreground">Projected Points</p>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </div>
              <p className="text-3xl font-bold text-green-700 dark:text-green-400">
                {totalPoints.toFixed(1)}
              </p>
            </div>

            {/* Start/Sit Breakdown */}
            <div className="p-4 border rounded-lg">
              <p className="text-xs font-medium text-muted-foreground mb-2">Recommendations</p>
              <div className="flex gap-2">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{recommendations.start}</p>
                  <p className="text-xs text-muted-foreground">Start</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-600">{recommendations.consider}</p>
                  <p className="text-xs text-muted-foreground">Consider</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">{recommendations.sit}</p>
                  <p className="text-xs text-muted-foreground">Sit</p>
                </div>
              </div>
            </div>

            {/* Health Status */}
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-muted-foreground">Injury Report</p>
                <AlertCircle className="h-4 w-4 text-orange-600" />
              </div>
              {injuryCount > 0 ? (
                <>
                  <p className="text-3xl font-bold text-orange-700 dark:text-orange-400">{injuryCount}</p>
                  <p className="text-xs text-muted-foreground">Players injured</p>
                </>
              ) : (
                <>
                  <p className="text-2xl font-bold text-green-700 dark:text-green-400">All Healthy</p>
                  <p className="text-xs text-muted-foreground">✓ No concerns</p>
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-md text-sm">
          {error}
        </div>
      )}

      {/* Weekly Lineup View */}
      {view === 'weekly' ? (
        <WeeklyLineup rosterId={rosterId} />
      ) : (
        <>
      {/* Starting Lineup */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Starting Lineup
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {ROSTER_SLOTS.map((slotInfo) => {
              const player = getPlayerInSlot(slotInfo.slot);
              const analysis = player ? playersWithAnalysis.get(player.id) : undefined;
              const recStyle = analysis?.recommendation
                ? RECOMMENDATION_COLORS[analysis.recommendation]
                : { border: 'border-gray-200', bg: '', text: '' };

              return (
                <div
                  key={slotInfo.slot}
                  className={`flex items-center justify-between p-4 border-2 rounded-lg transition-all ${recStyle.border} ${recStyle.bg}`}
                >
                  <div className="flex items-center gap-3 flex-1">
                    {/* Position Label */}
                    <div className="w-16 text-center">
                      <Badge variant="outline" className="font-bold">
                        {slotInfo.label}
                      </Badge>
                    </div>

                    {player ? (
                      <>
                        {/* Player Image */}
                        <img
                          src={getPlayerImageUrl(player.player_id)}
                          alt={player.player_name}
                          className="w-12 h-12 rounded-full object-cover border-2 border-gray-200 dark:border-gray-700"
                          onError={(e) => {
                            e.currentTarget.src = 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146';
                          }}
                        />

                        {/* Team Logo */}
                        {player.team && (
                          <img
                            src={getTeamLogoUrl(player.team)}
                            alt={player.team}
                            className="w-8 h-8 object-contain"
                            onError={(e) => e.currentTarget.style.display = 'none'}
                          />
                        )}

                        {/* Player Info */}
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <p className="font-semibold">{player.player_name}</p>
                            <Badge variant="outline" className="text-xs">
                              {player.position}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {player.team}
                            </Badge>
                            {player.injury_status !== 'HEALTHY' && (
                              <Badge className={`text-xs text-white ${INJURY_STATUS_COLORS[player.injury_status]}`}>
                                {player.injury_status}
                              </Badge>
                            )}
                          </div>

                          {/* Analysis Info */}
                          {analysis && (
                            <div className="flex items-center gap-3 mt-1 text-sm">
                              {analysis.opponent_team && (
                                <span className="text-muted-foreground">
                                  vs {analysis.opponent_team}
                                </span>
                              )}
                              {analysis.projected_points !== undefined && (
                                <span className="font-semibold text-green-700 dark:text-green-400">
                                  {analysis.projected_points.toFixed(1)} pts
                                </span>
                              )}
                              {analysis.matchup_score !== undefined && (
                                <span className="text-muted-foreground">
                                  Matchup: {analysis.matchup_score}/100
                                </span>
                              )}
                              {analysis.ai_grade && (
                                <Badge variant="outline" className="text-xs">
                                  Grade: {analysis.ai_grade}
                                </Badge>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Recommendation Badge */}
                        {analysis?.recommendation && (
                          <Badge className={`${RECOMMENDATION_COLORS[analysis.recommendation].text} font-bold`}>
                            {analysis.recommendation}
                          </Badge>
                        )}

                        {/* Action Buttons */}
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline">
                            <ArrowUpDown className="h-4 w-4" />
                          </Button>
                        </div>
                      </>
                    ) : (
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">Empty slot</p>
                        <Button size="sm" onClick={() => setAddingToSlot(slotInfo.slot)} className="mt-2">
                          Add Player
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Bench */}
      {benchPlayers.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5" />
              Bench ({benchPlayers.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {benchPlayers.map((player) => {
                const analysis = playersWithAnalysis.get(player.id);
                return (
                  <div
                    key={player.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent transition-colors"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <img
                        src={getPlayerImageUrl(player.player_id)}
                        alt={player.player_name}
                        className="w-10 h-10 rounded-full object-cover border border-gray-200 dark:border-gray-700"
                        onError={(e) => {
                          e.currentTarget.src = 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146';
                        }}
                      />
                      {player.team && (
                        <img
                          src={getTeamLogoUrl(player.team)}
                          alt={player.team}
                          className="w-6 h-6 object-contain"
                          onError={(e) => e.currentTarget.style.display = 'none'}
                        />
                      )}
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-sm">{player.player_name}</p>
                          <Badge variant="outline" className="text-xs">
                            {player.position}
                          </Badge>
                          {player.injury_status !== 'HEALTHY' && (
                            <Badge className={`text-xs text-white ${INJURY_STATUS_COLORS[player.injury_status]}`}>
                              {player.injury_status}
                            </Badge>
                          )}
                        </div>
                        {analysis && analysis.projected_points !== undefined && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Projected: {analysis.projected_points.toFixed(1)} pts
                          </p>
                        )}
                      </div>
                    </div>
                    <Button size="sm" variant="ghost">
                      <ArrowUpDown className="h-4 w-4" />
                    </Button>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Player Search Modal */}
      {addingToSlot && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 p-6 rounded-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                Add Player to {addingToSlot}
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setAddingToSlot(null)}
              >
                ✕
              </Button>
            </div>
            <PlayerSearch
              onSelectPlayer={(player) => {
                // TODO: Implement add player logic
                setAddingToSlot(null);
              }}
            />
          </div>
        </div>
      )}
      </>
      )}
    </div>
  );
}
