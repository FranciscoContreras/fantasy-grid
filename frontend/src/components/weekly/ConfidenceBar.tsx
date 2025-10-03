interface ConfidenceBarProps {
  score: number;
}

export function ConfidenceBar({ score }: ConfidenceBarProps) {
  const getConfidenceColor = () => {
    if (score >= 85) return 'bg-black';
    if (score >= 70) return 'bg-gray-600';
    return 'bg-gray-400';
  };

  const getConfidenceLabel = () => {
    if (score >= 85) return 'EXCELLENT';
    if (score >= 70) return 'GOOD';
    if (score >= 50) return 'FAIR';
    return 'WEAK';
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-sm text-gray-500 uppercase tracking-wider font-semibold mb-1">
            Lineup Confidence
          </div>
          <div className="text-5xl font-black tracking-tight">{score}%</div>
        </div>
        <div className={`px-6 py-3 rounded-full text-white font-black text-sm uppercase tracking-wider ${getConfidenceColor()}`}>
          {getConfidenceLabel()}
        </div>
      </div>

      {/* Progress bar */}
      <div className="relative w-full h-4 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full ${getConfidenceColor()} transition-all duration-500`}
          style={{ width: `${score}%` }}
        />
      </div>

      <p className="text-xs text-gray-500 mt-3 text-center uppercase tracking-wider font-semibold">
        Based on matchups, injuries, and analytics
      </p>
    </div>
  );
}
