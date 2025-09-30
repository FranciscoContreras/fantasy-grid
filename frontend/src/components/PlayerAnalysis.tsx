import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Analysis } from '@/types';

interface PlayerAnalysisProps {
  analysis: Analysis;
}

export function PlayerAnalysis({ analysis }: PlayerAnalysisProps) {
  const getRecommendationColor = (status: string) => {
    switch (status) {
      case 'START':
        return 'bg-green-600 hover:bg-green-700';
      case 'CONSIDER':
        return 'bg-yellow-600 hover:bg-yellow-700';
      case 'BENCH':
        return 'bg-red-600 hover:bg-red-700';
      default:
        return 'bg-gray-600 hover:bg-gray-700';
    }
  };

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-green-600 dark:text-green-400';
    if (grade.startsWith('B')) return 'text-blue-600 dark:text-blue-400';
    if (grade.startsWith('C')) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600 dark:text-green-400';
    if (score >= 50) return 'text-blue-600 dark:text-blue-400';
    if (score >= 30) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span>{analysis.player.name}</span>
            <Badge className={getRecommendationColor(analysis.recommendation.status)}>
              {analysis.recommendation.status}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Matchup & Weather Scores */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Matchup Score</p>
              <p className={`text-3xl font-bold ${getScoreColor(analysis.matchup_score)}`}>
                {analysis.matchup_score}/100
              </p>
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all"
                  style={{ width: `${analysis.matchup_score}%` }}
                />
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Weather Impact</p>
              <p className={`text-3xl font-bold ${getScoreColor(analysis.weather_impact)}`}>
                {analysis.weather_impact}/100
              </p>
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all"
                  style={{ width: `${analysis.weather_impact}%` }}
                />
              </div>
            </div>
          </div>

          {/* AI Grade */}
          <div className="border-t pt-4">
            <p className="text-sm text-muted-foreground mb-2">AI Grade</p>
            <div className="flex items-baseline gap-4">
              <p className={`text-5xl font-bold ${getGradeColor(analysis.ai_grade.grade)}`}>
                {analysis.ai_grade.grade}
              </p>
              <div className="flex-1">
                <p className="text-2xl font-semibold">
                  {analysis.ai_grade.predicted_points} pts
                </p>
                <p className="text-sm text-muted-foreground">
                  Projected fantasy points
                </p>
              </div>
            </div>
            <div className="mt-2">
              <p className="text-sm">
                <span className="text-muted-foreground">Confidence: </span>
                <span className="font-semibold">{analysis.ai_grade.confidence}%</span>
              </p>
            </div>
          </div>

          {/* Recommendation Reasoning */}
          {analysis.recommendation.reason && (
            <div className="border-t pt-4">
              <p className="text-sm text-muted-foreground mb-1">Analysis</p>
              <p className="text-sm">{analysis.recommendation.reason}</p>
            </div>
          )}

          {/* Weather Data Details */}
          {analysis.weather_data && (
            <div className="border-t pt-4">
              <p className="text-sm text-muted-foreground mb-2">Weather Conditions</p>
              <div className="grid grid-cols-3 gap-2 text-sm">
                {analysis.weather_data.temperature && (
                  <div>
                    <p className="text-muted-foreground">Temp</p>
                    <p className="font-semibold">{analysis.weather_data.temperature}°F</p>
                  </div>
                )}
                {analysis.weather_data.wind_speed && (
                  <div>
                    <p className="text-muted-foreground">Wind</p>
                    <p className="font-semibold">{analysis.weather_data.wind_speed} mph</p>
                  </div>
                )}
                {analysis.weather_data.conditions && (
                  <div>
                    <p className="text-muted-foreground">Conditions</p>
                    <p className="font-semibold">{analysis.weather_data.conditions}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
