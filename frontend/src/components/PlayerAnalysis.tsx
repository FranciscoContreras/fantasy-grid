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

  const getRecommendationStyle = (status: string) => {
    switch (status) {
      case 'START':
        return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
      case 'CONSIDER':
        return 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
      case 'BENCH':
        return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-emerald-400';
    if (grade.startsWith('B')) return 'text-amber-400';
    if (grade.startsWith('C')) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-emerald-400';
    if (score >= 50) return 'text-amber-400';
    if (score >= 30) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-6 font-system">
      {/* Main Analysis Card */}
      <div className="glass-card p-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-semibold text-white mb-1">{analysis.player.name}</h2>
            <p className="text-sm text-white/60 font-medium">
              {analysis.player.position} • {analysis.player.team}
            </p>
          </div>
          <div className={`px-4 py-2 rounded-full text-sm font-medium ${getRecommendationStyle(analysis.recommendation.status)}`}>
            {analysis.recommendation.status}
          </div>
        </div>
        {/* Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="glass compact-padding">
            <p className="text-sm text-white/60 font-medium mb-2">Matchup Score</p>
            <p className={`text-3xl font-bold ${getScoreColor(analysis.matchup_score)} mb-3`}>
              {analysis.matchup_score}/100
            </p>
            <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all rounded-full ${analysis.matchup_score >= 70 ? 'bg-emerald-400' : analysis.matchup_score >= 50 ? 'bg-amber-400' : 'bg-red-400'}`}
                style={{ width: `${analysis.matchup_score}%` }}
              />
            </div>
          </div>
          <div className="glass compact-padding">
            <p className="text-sm text-white/60 font-medium mb-2">Weather Impact</p>
            <p className={`text-3xl font-bold ${getScoreColor(analysis.weather_impact)} mb-3`}>
              {analysis.weather_impact}/100
            </p>
            <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all rounded-full ${analysis.weather_impact >= 70 ? 'bg-emerald-400' : analysis.weather_impact >= 50 ? 'bg-amber-400' : 'bg-red-400'}`}
                style={{ width: `${analysis.weather_impact}%` }}
              />
            </div>
          </div>
        </div>

        {/* AI Grade & Projection */}
        <div className="glass compact-padding mt-6">
          <p className="text-sm text-white/60 font-medium mb-4">AI Analysis</p>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
            <div className="text-center">
              <div className={`text-5xl font-bold ${getGradeColor(analysis.ai_grade.grade)} mb-2`}>
                {analysis.ai_grade.grade}
              </div>
              <p className="text-xs text-white/50 font-medium">Grade</p>
            </div>
            <div className="flex-1 space-y-3">
              <div>
                <p className="text-2xl font-bold text-white">
                  {analysis.ai_grade.predicted_points} <span className="text-sm text-white/60 font-medium">pts</span>
                </p>
                <p className="text-sm text-white/60">Projected Fantasy Points</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-white/60">Confidence:</span>
                <span className="text-sm font-semibold text-white">{analysis.ai_grade.confidence}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Reasoning */}
        {analysis.recommendation.reason && (
          <div className="glass compact-padding mt-6">
            <p className="text-sm text-white/60 font-medium mb-3">Analysis</p>
            <p className="text-sm text-white/80 leading-relaxed">{analysis.recommendation.reason}</p>
          </div>
        )}

        {/* Weather Conditions */}
        {analysis.weather_data && (
          <div className="glass compact-padding mt-6">
            <p className="text-sm text-white/60 font-medium mb-4">Weather Conditions</p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {analysis.weather_data.temperature && (
                <div className="text-center">
                  <p className="text-xs text-white/50 font-medium mb-1">Temperature</p>
                  <p className="text-xl font-bold text-white">{analysis.weather_data.temperature}°F</p>
                </div>
              )}
              {analysis.weather_data.wind_speed && (
                <div className="text-center">
                  <p className="text-xs text-white/50 font-medium mb-1">Wind Speed</p>
                  <p className="text-xl font-bold text-white">{analysis.weather_data.wind_speed} MPH</p>
                </div>
              )}
              {analysis.weather_data.conditions && (
                <div className="text-center">
                  <p className="text-xs text-white/50 font-medium mb-1">Conditions</p>
                  <p className="text-lg font-bold text-white">{analysis.weather_data.conditions}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Advanced Stats Panel - API v2 Next Gen Stats */}
      <AdvancedStatsPanel stats={advancedStats} loading={loadingAdvanced} />
    </div>
  );
}
