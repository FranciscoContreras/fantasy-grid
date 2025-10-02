import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';

interface Player {
  id: string;
  player_id?: string;
  name: string;
  position: string;
  team: string;
  status?: string;
  jersey_number?: number;
  height?: string;
  weight?: number;
  experience?: number;
}

interface PlayerListViewProps {
  onSelectPlayer: (player: Player) => void;
}

export function PlayerListView({ onSelectPlayer }: PlayerListViewProps) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPosition, setSelectedPosition] = useState<string>('ALL');
  const [selectedTeam, setSelectedTeam] = useState<string>('ALL');

  const positions = ['ALL', 'QB', 'RB', 'WR', 'TE', 'K', 'DEF'];

  const fetchPlayers = async () => {
    setLoading(true);
    try {
      // This will call the backend route once implemented
      // For now, using the existing search endpoint
      const response = await fetch(
        `/api/players/search?q=${searchQuery || 'a'}&position=${selectedPosition !== 'ALL' ? selectedPosition : ''}`
      );
      const data = await response.json();
      setPlayers(data.data || []);
    } catch (error) {
      console.error('Failed to fetch players:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlayers();
  }, [selectedPosition]);

  const filteredPlayers = players.filter(player => {
    const matchesSearch = player.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTeam = selectedTeam === 'ALL' || player.team === selectedTeam;
    return matchesSearch && matchesTeam;
  });

  const getPositionColor = (position: string) => {
    const colors: Record<string, string> = {
      QB: 'bg-red-500',
      RB: 'bg-blue-500',
      WR: 'bg-green-500',
      TE: 'bg-yellow-500',
      K: 'bg-purple-500',
      DEF: 'bg-gray-500',
    };
    return colors[position] || 'bg-gray-400';
  };

  const getStatusColor = (status?: string) => {
    if (!status) return 'bg-gray-200 text-gray-800';
    if (status.toLowerCase() === 'active') return 'bg-green-100 text-green-800';
    if (status.toLowerCase() === 'injured') return 'bg-red-100 text-red-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-2xl font-black">Player Browser</CardTitle>
        <p className="text-sm text-muted-foreground">
          Search and filter NFL players
        </p>
      </CardHeader>
      <CardContent>
        {/* Search and Filters */}
        <div className="space-y-4 mb-6">
          {/* Search Input */}
          <Input
            placeholder="Search by player name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full"
          />

          {/* Position Filter */}
          <div className="flex flex-wrap gap-2">
            {positions.map((pos) => (
              <Button
                key={pos}
                variant={selectedPosition === pos ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedPosition(pos)}
                className="font-bold"
              >
                {pos}
              </Button>
            ))}
          </div>
        </div>

        {/* Player Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-sm text-muted-foreground">Loading players...</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPlayers.map((player) => (
              <Card
                key={player.id || player.player_id}
                className="cursor-pointer hover:bg-gray-50 transition-all hover:shadow-md"
                onClick={() => onSelectPlayer(player)}
              >
                <CardContent className="p-4">
                  {/* Position Badge */}
                  <div className="flex items-start justify-between mb-3">
                    <Badge className={`${getPositionColor(player.position)} text-white font-bold`}>
                      {player.position}
                    </Badge>
                    {player.status && (
                      <Badge className={getStatusColor(player.status)}>
                        {player.status}
                      </Badge>
                    )}
                  </div>

                  {/* Player Name */}
                  <h3 className="text-lg font-black mb-1">{player.name}</h3>

                  {/* Team */}
                  <p className="text-sm text-gray-600 mb-2">{player.team}</p>

                  {/* Player Details */}
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-500 pt-2 border-t">
                    {player.jersey_number && (
                      <div>
                        <span className="font-semibold">Number:</span> #{player.jersey_number}
                      </div>
                    )}
                    {player.height && (
                      <div>
                        <span className="font-semibold">Height:</span> {player.height}
                      </div>
                    )}
                    {player.weight && (
                      <div>
                        <span className="font-semibold">Weight:</span> {player.weight} lbs
                      </div>
                    )}
                    {player.experience !== undefined && (
                      <div>
                        <span className="font-semibold">Exp:</span> {player.experience} yrs
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredPlayers.length === 0 && (
          <div className="text-center py-12">
            <p className="text-lg font-semibold text-gray-600 mb-2">No players found</p>
            <p className="text-sm text-gray-500">Try adjusting your search or filters</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
