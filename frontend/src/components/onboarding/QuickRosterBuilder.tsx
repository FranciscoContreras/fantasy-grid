import { useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { PlayerSearch } from '../PlayerSearch';
import { Player } from '@/types';
import { Badge } from '../ui/badge';

interface QuickRosterBuilderProps {
  onNext: (players: Player[]) => void;
  onSkip: () => void;
}

export function QuickRosterBuilder({ onNext, onSkip }: QuickRosterBuilderProps) {
  const [players, setPlayers] = useState<Player[]>([]);

  const handleAddPlayer = (player: Player) => {
    if (!players.find(p => p.id === player.id)) {
      setPlayers([...players, player]);
    }
  };

  const handleRemovePlayer = (playerId: string) => {
    setPlayers(players.filter(p => p.id !== playerId));
  };

  const handleContinue = () => {
    onNext(players);
  };

  const getPositionColor = (position: string) => {
    const colors: Record<string, string> = {
      QB: 'bg-blue-100 text-blue-800',
      RB: 'bg-green-100 text-green-800',
      WR: 'bg-purple-100 text-purple-800',
      TE: 'bg-orange-100 text-orange-800',
      K: 'bg-gray-100 text-gray-800',
      DEF: 'bg-red-100 text-red-800',
    };
    return colors[position] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full mb-6">
          <span className="text-xs font-bold text-gray-900 uppercase tracking-wider">
            Step 2 of 3
          </span>
        </div>
        <h2 className="text-5xl font-black tracking-tight mb-4">
          ADD YOUR PLAYERS
        </h2>
        <p className="text-xl text-gray-600">
          Search and add players to your roster (you can add more later)
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Player Search */}
        <Card>
          <CardContent className="pt-8">
            <h3 className="text-lg font-black uppercase tracking-tight mb-4">SEARCH PLAYERS</h3>
            <PlayerSearch onSelectPlayer={handleAddPlayer} />
            <p className="text-xs text-gray-500 mt-4 uppercase tracking-wider font-semibold">
              Type player name and select to add
            </p>
          </CardContent>
        </Card>

        {/* Added Players */}
        <Card>
          <CardContent className="pt-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-black uppercase tracking-tight">
                YOUR ROSTER ({players.length})
              </h3>
              {players.length > 0 && (
                <div className="text-sm font-semibold text-gray-600">
                  {players.length}/15 RECOMMENDED
                </div>
              )}
            </div>

            {players.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <div className="text-6xl mb-4">=e</div>
                <p className="text-sm font-semibold uppercase tracking-wider">
                  No players added yet
                </p>
                <p className="text-xs mt-2">Search and select players to add them here</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {players.map((player) => (
                  <div
                    key={player.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="font-bold text-sm">{player.name}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={`text-xs ${getPositionColor(player.position)}`}>
                          {player.position}
                        </Badge>
                        <span className="text-xs text-gray-500">{player.team}</span>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemovePlayer(player.id)}
                      className="ml-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {/* Progress bar */}
            {players.length > 0 && (
              <div className="mt-6">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-black h-full rounded-full transition-all"
                    style={{ width: `${Math.min((players.length / 15) * 100, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-center text-gray-500 mt-2 uppercase tracking-wider font-semibold">
                  {players.length >= 8 ? 'Great progress!' : 'Add at least 5-8 players to start'}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mt-8 justify-center">
        <Button
          variant="outline"
          onClick={onSkip}
          className="px-8 py-6 font-bold uppercase tracking-wider"
        >
          SKIP FOR NOW
        </Button>
        <Button
          onClick={handleContinue}
          disabled={players.length === 0}
          className="bg-black text-white hover:bg-gray-900 px-8 py-6 font-black uppercase tracking-wider"
        >
          {players.length === 0 ? 'ADD PLAYERS TO CONTINUE' : `CONTINUE WITH ${players.length} PLAYERS`}
          <svg className="ml-2 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Button>
      </div>
    </div>
  );
}
