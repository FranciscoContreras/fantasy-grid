import { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';

interface FirstAnalysisProps {
  rosterId: number;
  playerCount: number;
  onComplete: () => void;
}

export function FirstAnalysis({ rosterId, playerCount, onComplete }: FirstAnalysisProps) {
  const [analyzing, setAnalyzing] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Simulate analysis progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setAnalyzing(false);
          return 100;
        }
        return prev + 10;
      });
    }, 300);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full mb-6">
          <span className="text-xs font-bold text-gray-900 uppercase tracking-wider">
            Step 3 of 3
          </span>
        </div>
        <h2 className="text-5xl font-black tracking-tight mb-4">
          {analyzing ? 'ANALYZING YOUR ROSTER' : 'YOU\'RE ALL SET!'}
        </h2>
        <p className="text-xl text-gray-600">
          {analyzing
            ? 'Our AI is analyzing your lineup for this week...'
            : 'Your roster is ready for start/sit recommendations'}
        </p>
      </div>

      <Card>
        <CardContent className="pt-12 pb-12">
          {analyzing ? (
            <div className="space-y-8">
              {/* Progress Circle */}
              <div className="flex justify-center">
                <div className="relative w-32 h-32">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="64"
                      cy="64"
                      r="60"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      className="text-gray-200"
                    />
                    <circle
                      cx="64"
                      cy="64"
                      r="60"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 60}`}
                      strokeDashoffset={`${2 * Math.PI * 60 * (1 - progress / 100)}`}
                      className="text-black transition-all duration-300"
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-3xl font-black">{progress}%</span>
                  </div>
                </div>
              </div>

              {/* Analysis Steps */}
              <div className="space-y-4">
                <AnalysisStep
                  label="Fetching player data"
                  completed={progress > 20}
                  active={progress <= 20}
                />
                <AnalysisStep
                  label="Analyzing matchups"
                  completed={progress > 40}
                  active={progress > 20 && progress <= 40}
                />
                <AnalysisStep
                  label="Checking weather conditions"
                  completed={progress > 60}
                  active={progress > 40 && progress <= 60}
                />
                <AnalysisStep
                  label="Calculating AI grades"
                  completed={progress > 80}
                  active={progress > 60 && progress <= 80}
                />
                <AnalysisStep
                  label="Generating recommendations"
                  completed={progress >= 100}
                  active={progress > 80 && progress < 100}
                />
              </div>
            </div>
          ) : (
            <div className="text-center space-y-8">
              {/* Success Icon */}
              <div className="flex justify-center">
                <div className="w-32 h-32 bg-black rounded-full flex items-center justify-center">
                  <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>

              {/* Success Message */}
              <div>
                <h3 className="text-3xl font-black mb-3">ANALYSIS COMPLETE!</h3>
                <p className="text-gray-600 text-lg">
                  Your roster with {playerCount} players is ready.
                  <br />
                  We've analyzed matchups, weather, and stats for Week 5.
                </p>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
                <div className="p-4 bg-gray-50 rounded-xl">
                  <div className="text-3xl font-black mb-1">{playerCount}</div>
                  <div className="text-xs text-gray-600 uppercase tracking-wider font-semibold">Players</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <div className="text-3xl font-black mb-1">5</div>
                  <div className="text-xs text-gray-600 uppercase tracking-wider font-semibold">Week</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <div className="text-3xl font-black mb-1">100%</div>
                  <div className="text-xs text-gray-600 uppercase tracking-wider font-semibold">Ready</div>
                </div>
              </div>

              {/* CTA Button */}
              <Button
                onClick={onComplete}
                className="bg-black text-white hover:bg-gray-900 px-12 py-7 text-lg font-black uppercase tracking-wider"
              >
                VIEW MY LINEUP
                <svg className="ml-2 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Button>

              <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold">
                You can add more players anytime
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

interface AnalysisStepProps {
  label: string;
  completed: boolean;
  active: boolean;
}

function AnalysisStep({ label, completed, active }: AnalysisStepProps) {
  return (
    <div className="flex items-center gap-3">
      {completed ? (
        <div className="w-6 h-6 bg-black rounded-full flex items-center justify-center flex-shrink-0">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      ) : active ? (
        <div className="w-6 h-6 border-4 border-black border-t-transparent rounded-full animate-spin flex-shrink-0" />
      ) : (
        <div className="w-6 h-6 border-2 border-gray-300 rounded-full flex-shrink-0" />
      )}
      <span className={`text-sm font-semibold uppercase tracking-wider ${
        completed ? 'text-black' : active ? 'text-gray-900' : 'text-gray-400'
      }`}>
        {label}
      </span>
    </div>
  );
}
