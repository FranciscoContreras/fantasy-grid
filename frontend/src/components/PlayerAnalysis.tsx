import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Analysis } from '@/types';
import { AdvancedStatsPanel } from './AdvancedStatsPanel';
import { AdvancedPlayerStats } from '@/types/advancedStats';
import { useState, useEffect } from 'react';
import api from '@/lib/api';

interface PlayerAnalysisProps {
  analysis: Analysis;
}

export function PlayerAnalysis({ analysis }: PlayerAnalysisProps) {
  const [advancedStats, setAdvancedStats] = useState<AdvancedPlayerStats | null>(null);
  const [loadingAdvanced, setLoadingAdvanced] = useState(false);

  useEffect(() => {
    // Fetch advanced stats for the player
    const fetchAdvancedStats = async () => {
      if (!analysis.player?.id) return;

      try {
        setLoadingAdvanced(true);
        const response = await api.get(`/advanced/players/${analysis.player.id}/nextgen`, {
          params: { season: 2024 }
        });
        setAdvancedStats(response.data.data);
      } catch (error) {
        console.error('Failed to fetch advanced stats:', error);
        // Gracefully handle - advanced stats are optional
      } finally {
        setLoadingAdvanced(false);
      }
    };

    fetchAdvancedStats();
  }, [analysis.player?.id]);

  const getRecommendationColor = (status: string) => {
    switch (status) {
      case 'START':
        return 'bg-white text-black border-2 border-white font-display uppercase tracking-[0.2em] text-sm font-bold';
      case 'CONSIDER':
        return 'bg-gray-600 text-white border-2 border-gray-600 font-display uppercase tracking-[0.2em] text-sm font-bold';
      case 'BENCH':
        return 'bg-gray-800 text-gray-300 border-2 border-gray-600 font-display uppercase tracking-[0.2em] text-sm font-bold';
      default:
        return 'bg-gray-700 text-white border-2 border-gray-600 font-display uppercase tracking-[0.2em] text-sm font-bold';
    }
  };

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-white';
    if (grade.startsWith('B')) return 'text-gray-300';
    if (grade.startsWith('C')) return 'text-gray-400';
    return 'text-gray-500';
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-white';
    if (score >= 50) return 'text-gray-300';
    if (score >= 30) return 'text-gray-400';
    return 'text-gray-500';
  };

  return (
    <div className="space-y-8">
      {/* Main Analysis Card */}
      <Card className="bg-gray-900 text-white border-4 border-gray-700">
        <CardHeader className="border-b-2 border-gray-600 pb-6">
          <CardTitle className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="font-display text-2xl uppercase tracking-[0.1em] text-white">{analysis.player.name}</span>
              <p className="text-sm text-gray-400 uppercase tracking-[0.3em] mt-1 font-display">
                {analysis.player.position} · {analysis.player.team}
              </p>
            </div>
            <div className={`inline-flex items-center gap-2 px-6 py-3 ${getRecommendationColor(analysis.recommendation.status)}`}>
              {analysis.recommendation.status}
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-8 pt-6">
          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4 p-6 bg-black border-2 border-gray-600">
              <p className="text-sm text-gray-400 font-display uppercase tracking-[0.2em]">Matchup Score</p>
              <p className={`text-4xl font-display ${getScoreColor(analysis.matchup_score)}`}>
                {analysis.matchup_score}/100
              </p>
              <div className="w-full bg-gray-700 h-3 border border-gray-600">
                <div
                  className="bg-white h-full transition-all"
                  style={{ width: `${analysis.matchup_score}%` }}
                />
              </div>
            </div>
            <div className="space-y-4 p-6 bg-black border-2 border-gray-600">
              <p className="text-sm text-gray-400 font-display uppercase tracking-[0.2em]">Weather Impact</p>
              <p className={`text-4xl font-display ${getScoreColor(analysis.weather_impact)}`}>
                {analysis.weather_impact}/100
              </p>
              <div className="w-full bg-gray-700 h-3 border border-gray-600">
                <div
                  className="bg-white h-full transition-all"
                  style={{ width: `${analysis.weather_impact}%` }}
                />
              </div>
            </div>
          </div>

          {/* AI Grade & Projection */}
          <div className="border-t-2 border-gray-600 pt-6">
            <p className="text-sm text-gray-400 font-display uppercase tracking-[0.2em] mb-4">AI Championship Grade</p>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 p-6 bg-black border-2 border-gray-600">
              <div className="text-center">
                <p className={`text-6xl font-script ${getGradeColor(analysis.ai_grade.grade)}`}>
                  {analysis.ai_grade.grade}
                </p>
                <p className="text-xs text-gray-500 uppercase tracking-[0.3em] font-display mt-2">Grade</p>
              </div>
              <div className="flex-1 space-y-2">
                <p className="text-3xl font-display text-white">
                  {analysis.ai_grade.predicted_points} <span className="text-lg text-gray-400">PTS</span>
                </p>
                <p className="text-sm text-gray-400 uppercase tracking-[0.2em] font-display">
                  Projected Fantasy Points
                </p>
                <div className="mt-3">
                  <p className="text-sm font-body">
                    <span className="text-gray-400 uppercase tracking-wider">Confidence: </span>
                    <span className="font-display text-white uppercase tracking-wider">{analysis.ai_grade.confidence}%</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Championship Analysis */}
          {analysis.recommendation.reason && (
            <div className="border-t-2 border-gray-600 pt-6">
              <p className="text-sm text-gray-400 font-display uppercase tracking-[0.2em] mb-4">Championship Analysis</p>
              <div className="p-6 bg-gray-800 border-2 border-gray-600">
                <p className="text-sm font-body leading-relaxed text-gray-100">{analysis.recommendation.reason}</p>
              </div>
            </div>
          )}

          {/* Weather Conditions */}
          {analysis.weather_data && (
            <div className="border-t-2 border-gray-600 pt-6">
              <p className="text-sm text-gray-400 font-display uppercase tracking-[0.2em] mb-4">Field Conditions</p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {analysis.weather_data.temperature && (
                  <div className="p-4 bg-black border-2 border-gray-600 text-center">
                    <p className="text-xs text-gray-500 uppercase tracking-[0.3em] font-display">Temperature</p>
                    <p className="text-2xl font-display text-white mt-2">{analysis.weather_data.temperature}°F</p>
                  </div>
                )}
                {analysis.weather_data.wind_speed && (
                  <div className="p-4 bg-black border-2 border-gray-600 text-center">
                    <p className="text-xs text-gray-500 uppercase tracking-[0.3em] font-display">Wind Speed</p>
                    <p className="text-2xl font-display text-white mt-2">{analysis.weather_data.wind_speed} MPH</p>
                  </div>
                )}
                {analysis.weather_data.conditions && (
                  <div className="p-4 bg-black border-2 border-gray-600 text-center">
                    <p className="text-xs text-gray-500 uppercase tracking-[0.3em] font-display">Conditions</p>
                    <p className="text-lg font-display text-white mt-2 uppercase tracking-wider">{analysis.weather_data.conditions}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Advanced Stats Panel - API v2 Next Gen Stats */}
      <AdvancedStatsPanel stats={advancedStats} loading={loadingAdvanced} />
    </div>
  );
}
