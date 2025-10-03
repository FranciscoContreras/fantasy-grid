import { Button } from '../ui/button';

interface PlayerCardProps {
  player: {
    name: string;
    position: string;
    team: string;
    injury_status?: string;
  };
  recommendation: 'START' | 'CONSIDER' | 'BENCH';
  grade: string;
  confidence: number;
  matchup_score: number;
  weather_score: number;
  injury_score: number;
  advanced_stats_score: number;
  projected_points: number;
  projected_range: [number, number];
  reasons: string[];
}

export function PlayerCard({
  player,
  recommendation,
  grade,
  confidence,
  matchup_score,
  weather_score,
  injury_score,
  advanced_stats_score,
  projected_points,
  projected_range,
  reasons,
}: PlayerCardProps) {
  const getRecommendationStyles = () => {
    if (recommendation === 'START') {
      return {
        container: 'bg-black text-white border-black',
        badge: 'bg-white text-black',
        icon: '',
      };
    }
    if (recommendation === 'CONSIDER') {
      return {
        container: 'bg-gray-200 text-black border-gray-300',
        badge: 'bg-gray-600 text-white',
        icon: '?',
      };
    }
    return {
      container: 'bg-gray-100 text-gray-500 border-gray-200 opacity-60',
      badge: 'bg-gray-400 text-white',
      icon: '×',
    };
  };

  const styles = getRecommendationStyles();

  return (
    <div className={`relative border rounded-2xl p-6 hover:scale-105 transition-transform ${styles.container}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1">
          <div className="text-xl font-black tracking-tight mb-1">{player.name}</div>
          <div className="text-sm uppercase tracking-wider font-semibold opacity-70">
            {player.position} · {player.team}
          </div>
        </div>
        <div className="text-5xl font-black opacity-50">{grade}</div>
      </div>

      {/* Recommendation Badge */}
      <div className={`inline-flex items-center gap-2 px-5 py-2 rounded-full font-black text-sm uppercase tracking-wider mb-6 ${styles.badge}`}>
        <span className="text-lg">{styles.icon}</span>
        {recommendation}
      </div>

      {/* Projected Points */}
      <div className="mb-6 pb-6 border-b border-current opacity-30">
        <div className="text-xs uppercase tracking-wider font-semibold opacity-70 mb-1">
          Projected Points
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-black">{projected_points.toFixed(1)}</span>
          <span className="text-sm opacity-50">
            ({projected_range[0].toFixed(1)} - {projected_range[1].toFixed(1)})
          </span>
        </div>
      </div>

      {/* Key Factors */}
      <div className="space-y-3 mb-6">
        <FactorBar label="Matchup" score={matchup_score} />
        <FactorBar label="Weather" score={weather_score} />
        <FactorBar label="Health" score={injury_score} />
        <FactorBar label="Stats" score={advanced_stats_score} />
      </div>

      {/* Confidence */}
      <div className="mb-4">
        <div className="text-xs uppercase tracking-wider font-semibold opacity-70 mb-2">
          Confidence: {confidence}%
        </div>
        <div className="w-full bg-current opacity-20 rounded-full h-2">
          <div
            className="bg-current opacity-100 h-full rounded-full transition-all"
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Reasons */}
      {reasons.length > 0 && (
        <div className="text-xs opacity-70 space-y-1">
          {reasons.map((reason, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span>"</span>
              <span>{reason}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface FactorBarProps {
  label: string;
  score: number;
}

function FactorBar({ label, score }: FactorBarProps) {
  return (
    <div>
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs uppercase tracking-wider font-semibold opacity-70">{label}</span>
        <span className="text-xs font-bold">{score}/100</span>
      </div>
      <div className="w-full bg-current opacity-20 rounded-full h-1.5">
        <div
          className="bg-current opacity-100 h-full rounded-full transition-all"
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}
