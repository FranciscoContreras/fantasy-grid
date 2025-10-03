import { PlayerCard } from './PlayerCard';

interface Player {
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

interface StartSitGridProps {
  starters: Player[];
  bench: Player[];
}

export function StartSitGrid({ starters, bench }: StartSitGridProps) {
  // Separate starters into START and CONSIDER
  const startPlayers = starters.filter(p => p.recommendation === 'START');
  const considerPlayers = starters.filter(p => p.recommendation === 'CONSIDER');

  return (
    <div className="space-y-8">
      {/* STARTERS Section */}
      <div>
        <div className="mb-6">
          <h2 className="text-3xl font-black tracking-tight mb-2">STARTERS</h2>
          <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold">
            Recommended for your lineup
          </p>
        </div>

        {/* START Players */}
        {startPlayers.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 bg-black rounded-full"></div>
              <h3 className="text-lg font-black uppercase tracking-tight">
                START ({startPlayers.length})
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {startPlayers.map((player, idx) => (
                <PlayerCard key={idx} {...player} />
              ))}
            </div>
          </div>
        )}

        {/* CONSIDER Players */}
        {considerPlayers.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 bg-gray-600 rounded-full"></div>
              <h3 className="text-lg font-black uppercase tracking-tight">
                CONSIDER ({considerPlayers.length})
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {considerPlayers.map((player, idx) => (
                <PlayerCard key={idx} {...player} />
              ))}
            </div>
          </div>
        )}

        {starters.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <p className="text-lg font-semibold">No starters recommended</p>
            <p className="text-sm mt-2">Add players to your roster to see recommendations</p>
          </div>
        )}
      </div>

      {/* BENCH Section */}
      {bench.length > 0 && (
        <div>
          <div className="mb-6">
            <h2 className="text-3xl font-black tracking-tight mb-2">BENCH</h2>
            <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold">
              Sit these players this week
            </p>
          </div>

          <div className="flex items-center gap-2 mb-4">
            <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
            <h3 className="text-lg font-black uppercase tracking-tight">
              BENCH ({bench.length})
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {bench.map((player, idx) => (
              <PlayerCard key={idx} {...player} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
