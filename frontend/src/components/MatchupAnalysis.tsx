import { useState, useEffect } from 'react';
import { Matchup, MatchupAnalysis as MatchupAnalysisType } from '../types';
import { getMatchup, analyzeMatchup } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

interface MatchupAnalysisProps {
  matchupId: number;
}

const GRADE_COLORS: Record<string, string> = {
  'A+': 'bg-green-600',
  A: 'bg-green-500',
  B: 'bg-blue-500',
  C: 'bg-yellow-500',
  D: 'bg-orange-500',
  F: 'bg-red-500',
};

const RECOMMENDATION_COLORS: Record<string, string> = {
  START: 'bg-green-600',
  CONSIDER: 'bg-yellow-600',
  SIT: 'bg-red-600',
};

export function MatchupAnalysis({ matchupId }: MatchupAnalysisProps) {
  const [matchup, setMatchup] = useState<Matchup | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadMatchup();
  }, [matchupId]);

  const loadMatchup = async () => {
    try {
      setLoading(true);
      const response = await getMatchup(matchupId);
      setMatchup(response.data);
    } catch (err) {
      setError('Failed to load matchup');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      setError('');
      await analyzeMatchup(matchupId);
      // Reload matchup to get updated analysis
      await loadMatchup();
    } catch (err) {
      setError('Failed to analyze matchup');
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">Loading matchup...</p>
        </CardContent>
      </Card>
    );
  }

  if (!matchup) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-red-600">Matchup not found</p>
        </CardContent>
      </Card>
    );
  }

  const userAnalysis = matchup.analysis?.filter((a) => a.is_user_player) || [];

  const startPlayers = userAnalysis.filter((a) => a.recommendation === 'START');
  const sitPlayers = userAnalysis.filter((a) => a.recommendation === 'SIT');
  const considerPlayers = userAnalysis.filter((a) => a.recommendation === 'CONSIDER');

  const avgProjectedPoints =
    userAnalysis.length > 0
      ? (
          userAnalysis.reduce((sum, a) => sum + a.projected_points, 0) /
          userAnalysis.length
        ).toFixed(2)
      : '0';

  return (
    <div className="space-y-6">
      {/* Matchup Header */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>
                Week {matchup.week} Analysis - {matchup.season}
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                {matchup.user_roster_name} vs Real NFL Defenses
              </p>
            </div>
            <Button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="min-w-32"
            >
              {analyzing ? 'Analyzing...' : matchup.analyzed ? 'Re-analyze' : 'Analyze'}
            </Button>
          </div>
        </CardHeader>
      </Card>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-md text-sm">
          {error}
        </div>
      )}

      {matchup.analyzed && matchup.analysis && matchup.analysis.length > 0 && (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">Avg Projected</p>
                <p className="text-2xl font-bold">{avgProjectedPoints} pts</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">Should Start</p>
                <p className="text-2xl font-bold text-green-600">{startPlayers.length}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">Monitor</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {considerPlayers.length}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">Should Sit</p>
                <p className="text-2xl font-bold text-red-600">{sitPlayers.length}</p>
              </CardContent>
            </Card>
          </div>

          {/* Your Players Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Your Players - Start/Sit Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {userAnalysis.map((player) => (
                  <PlayerAnalysisCard key={player.id} analysis={player} />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Note: Opponent roster analysis removed - fantasy matchups depend on
              your players' performance against real NFL defenses, not opponent's roster */}
        </>
      )}

      {!matchup.analyzed && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <p className="text-lg mb-2">No analysis yet</p>
              <p className="text-sm">Click "Analyze" to generate start/sit recommendations</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function PlayerAnalysisCard({ analysis }: { analysis: MatchupAnalysisType }) {
  const gradeColor = GRADE_COLORS[analysis.ai_grade] || 'bg-gray-500';
  const recColor = RECOMMENDATION_COLORS[analysis.recommendation] || 'bg-gray-500';

  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-lg">{analysis.player_name}</h3>
            <Badge variant="outline">{analysis.position}</Badge>
            <Badge variant="outline">{analysis.team}</Badge>
            {analysis.injury_status && analysis.injury_status !== 'HEALTHY' && (
              <Badge className="bg-orange-500 text-white">
                {analysis.injury_status}
              </Badge>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Badge className={`${gradeColor} text-white`}>{analysis.ai_grade}</Badge>
          <Badge className={`${recColor} text-white`}>
            {analysis.recommendation}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-3">
        <div>
          <p className="text-xs text-muted-foreground">Matchup Score</p>
          <p className="text-lg font-semibold">{analysis.matchup_score.toFixed(1)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Projected Points</p>
          <p className="text-lg font-semibold">{analysis.projected_points.toFixed(1)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Confidence</p>
          <p className="text-lg font-semibold">{analysis.confidence_score.toFixed(0)}%</p>
        </div>
      </div>

      <div className="text-sm">
        <p className="text-muted-foreground mb-1">Analysis:</p>
        <p>{analysis.reasoning}</p>
      </div>

      {analysis.injury_impact && analysis.injury_impact !== 'No impact' && (
        <div className="mt-2 p-2 bg-orange-50 dark:bg-orange-950 rounded text-sm">
          <span className="font-medium">Injury Impact:</span> {analysis.injury_impact}
        </div>
      )}
    </div>
  );
}
