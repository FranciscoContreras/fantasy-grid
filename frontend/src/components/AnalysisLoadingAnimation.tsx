import { useEffect, useState } from 'react';

interface AnalysisLoadingAnimationProps {
  /** Total number of players being analyzed */
  totalPlayers: number;
  /** Number of players completed */
  completedPlayers: number;
}

const ANALYSIS_STAGES = [
  { label: 'Gathering player data...', icon: '📊' },
  { label: 'Analyzing matchups...', icon: '⚔️' },
  { label: 'Evaluating defenses...', icon: '🛡️' },
  { label: 'AI generating insights...', icon: '🤖' },
  { label: 'Finalizing recommendations...', icon: '✨' },
];

export function AnalysisLoadingAnimation({ totalPlayers, completedPlayers }: AnalysisLoadingAnimationProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const progressPercentage = totalPlayers > 0 ? (completedPlayers / totalPlayers) * 100 : 0;

  // Cycle through stages based on progress
  useEffect(() => {
    const stageIndex = Math.floor((progressPercentage / 100) * ANALYSIS_STAGES.length);
    setCurrentStage(Math.min(stageIndex, ANALYSIS_STAGES.length - 1));
  }, [progressPercentage]);

  // Calculate football position (moves along a parabolic arc)
  const footballX = progressPercentage;
  const footballY = Math.sin((progressPercentage / 100) * Math.PI) * 30; // Arc height

  return (
    <div className="w-full py-8 px-6 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 rounded-lg border border-green-200 dark:border-green-800">
      {/* Stadium Field */}
      <div className="relative w-full h-32 mb-6 bg-gradient-to-b from-green-600 to-green-700 rounded-lg overflow-hidden shadow-inner">
        {/* Yard lines */}
        {[0, 20, 40, 60, 80, 100].map((yard) => (
          <div
            key={yard}
            className="absolute top-0 bottom-0 w-0.5 bg-white/30"
            style={{ left: `${yard}%` }}
          />
        ))}

        {/* End zones */}
        <div className="absolute left-0 top-0 bottom-0 w-[10%] bg-blue-600/40" />
        <div className="absolute right-0 top-0 bottom-0 w-[10%] bg-red-600/40" />

        {/* Football animation */}
        <div
          className="absolute transition-all duration-300 ease-out"
          style={{
            left: `${footballX}%`,
            bottom: `${50 + footballY}%`,
            transform: `translateX(-50%) rotate(${footballX * 3.6}deg)`,
          }}
        >
          <div className="relative">
            {/* Football */}
            <div className="text-4xl animate-bounce" style={{ animationDuration: '0.6s' }}>
              🏈
            </div>
            {/* Motion trail */}
            {progressPercentage > 0 && (
              <div className="absolute top-1/2 -right-8 flex gap-1">
                <div className="w-1 h-1 rounded-full bg-white/40 animate-pulse" />
                <div className="w-1 h-1 rounded-full bg-white/30 animate-pulse" style={{ animationDelay: '0.1s' }} />
                <div className="w-1 h-1 rounded-full bg-white/20 animate-pulse" style={{ animationDelay: '0.2s' }} />
              </div>
            )}
          </div>
        </div>

        {/* Start & End markers */}
        <div className="absolute left-[5%] top-1/2 -translate-y-1/2 text-2xl">🏁</div>
        <div className="absolute right-[5%] top-1/2 -translate-y-1/2 text-2xl">🎯</div>
      </div>

      {/* Progress Bar */}
      <div className="relative w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-4 shadow-inner">
        <div
          className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 via-green-500 to-emerald-500 transition-all duration-500 ease-out rounded-full shadow-lg"
          style={{ width: `${progressPercentage}%` }}
        >
          {/* Shimmer effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
        </div>
      </div>

      {/* Stage indicator */}
      <div className="text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <span className="text-2xl animate-pulse">{ANALYSIS_STAGES[currentStage].icon}</span>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {ANALYSIS_STAGES[currentStage].label}
          </p>
        </div>
        <p className="text-xs text-gray-600 dark:text-gray-400">
          Analyzing {completedPlayers} of {totalPlayers} players ({Math.round(progressPercentage)}%)
        </p>
      </div>

      {/* Stage dots */}
      <div className="flex justify-center gap-2 mt-4">
        {ANALYSIS_STAGES.map((stage, index) => (
          <div
            key={index}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              index <= currentStage
                ? 'bg-green-600 dark:bg-green-400 scale-110'
                : 'bg-gray-300 dark:bg-gray-600'
            }`}
            title={stage.label}
          />
        ))}
      </div>
    </div>
  );
}
