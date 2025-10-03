import { useState, useEffect } from 'react';
import { WeekSelector } from './weekly/WeekSelector';
import { ConfidenceBar } from './weekly/ConfidenceBar';
import { StartSitGrid } from './weekly/StartSitGrid';
import { Button } from './ui/button';

interface WeeklyLineupProps {
  rosterId: number;
}

interface WeeklyLineupData {
  starters: any[];
  bench: any[];
  overall_confidence: number;
  week: number;
  season: number;
}

export function WeeklyLineup({ rosterId }: WeeklyLineupProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lineupData, setLineupData] = useState<WeeklyLineupData | null>(null);
  const [week, setWeek] = useState(5); // Default to week 5
  const [season] = useState(2024);

  useEffect(() => {
    loadWeeklyLineup();
  }, [rosterId, week]);

  const loadWeeklyLineup = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `/api/rosters/${rosterId}/weekly-lineup?week=${week}&season=${season}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to load weekly lineup');
      }

      const result = await response.json();
      setLineupData(result.data);
    } catch (err) {
      console.error('Error loading weekly lineup:', err);
      setError('Failed to load weekly lineup. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleWeekChange = (newWeek: number) => {
    setWeek(newWeek);
  };

  const handleAnalyzeAll = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`/api/rosters/${rosterId}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ week, season }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze roster');
      }

      // Reload lineup data after analysis
      await loadWeeklyLineup();
    } catch (err) {
      console.error('Error analyzing roster:', err);
      setError('Failed to analyze roster. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !lineupData) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-black border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg font-semibold text-gray-600">Loading weekly lineup...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <p className="text-red-600 font-semibold mb-4">{error}</p>
        <Button onClick={loadWeeklyLineup} variant="outline">
          Try Again
        </Button>
      </div>
    );
  }

  if (!lineupData) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Week Selector */}
      <WeekSelector week={lineupData.week} season={lineupData.season} onWeekChange={handleWeekChange} />

      {/* Confidence Bar */}
      <ConfidenceBar score={lineupData.overall_confidence} />

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-3">
        <Button
          onClick={handleAnalyzeAll}
          disabled={loading}
          className="bg-black text-white hover:bg-gray-900 font-bold"
        >
          {loading ? 'ANALYZING...' : 'ANALYZE ALL PLAYERS'}
        </Button>
        <Button variant="outline" className="font-bold">
          COMPARE PLAYERS
        </Button>
        <Button variant="outline" className="font-bold">
          TRADE ANALYZER
        </Button>
      </div>

      {/* Start/Sit Grid */}
      <StartSitGrid starters={lineupData.starters} bench={lineupData.bench} />

      {/* Empty State */}
      {lineupData.starters.length === 0 && lineupData.bench.length === 0 && (
        <div className="text-center py-20 bg-gray-50 rounded-xl border border-gray-200">
          <div className="max-w-md mx-auto">
            <div className="text-6xl mb-6">=�</div>
            <h3 className="text-2xl font-black mb-3">NO PLAYERS IN ROSTER</h3>
            <p className="text-gray-600 mb-6">
              Add players to your roster to see weekly start/sit recommendations.
            </p>
            <Button className="bg-black text-white hover:bg-gray-900 font-bold">
              ADD PLAYERS
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
