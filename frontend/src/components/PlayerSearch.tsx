import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { searchPlayers } from '@/lib/api';
import { Player } from '@/types';

interface PlayerSearchProps {
  onSelectPlayer: (player: Player) => void;
}

export function PlayerSearch({ onSelectPlayer }: PlayerSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!query) return;

    setLoading(true);
    setError('');

    try {
      const response = await searchPlayers(query);
      setResults(response.data || []);
    } catch (err) {
      setError('Failed to search players. Please try again.');
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Search players by name..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <Button onClick={handleSearch} disabled={loading || !query}>
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </div>

      {error && (
        <div className="text-sm text-red-600 dark:text-red-400">
          {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="grid gap-2">
          {results.map((player) => (
            <Card
              key={player.id}
              className="p-4 cursor-pointer hover:bg-accent transition-colors"
              onClick={() => onSelectPlayer(player)}
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-semibold">{player.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {player.position} - {player.team}
                  </p>
                </div>
                {player.jersey_number && (
                  <div className="text-2xl font-bold text-muted-foreground">
                    #{player.jersey_number}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {!loading && results.length === 0 && query && (
        <p className="text-sm text-muted-foreground text-center py-4">
          No players found. Try a different search.
        </p>
      )}
    </div>
  );
}
