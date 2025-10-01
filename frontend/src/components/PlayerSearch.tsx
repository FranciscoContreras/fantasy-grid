import { useState, useEffect, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { searchPlayers } from '@/lib/api';
import { Player } from '@/types';
import { getPlayerImageUrl, getTeamLogoUrl } from '@/lib/images';

interface PlayerSearchProps {
  onSelectPlayer: (player: Player) => void;
}

export function PlayerSearch({ onSelectPlayer }: PlayerSearchProps) {
  const [query, setQuery] = useState('');
  const [position, setPosition] = useState<string>('');
  const [results, setResults] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Debounced search
  const handleSearch = useCallback(async (searchQuery: string, searchPosition?: string) => {
    if (!searchQuery || searchQuery.length < 2) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await searchPlayers(searchQuery, searchPosition);
      setResults(response.data || []);
    } catch (err) {
      setError('Failed to search players. Please try again.');
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-search with minimal debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.length >= 2) {
        handleSearch(query, position);
      } else {
        setResults([]);
      }
    }, 150); // 150ms debounce - faster response

    return () => clearTimeout(timer);
  }, [query, position, handleSearch]);

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && query.length >= 2) {
      handleSearch(query, position);
    }
  };

  const highlightMatch = (text: string, query: string) => {
    if (!query) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return (
      <>
        {parts.map((part, index) =>
          part.toLowerCase() === query.toLowerCase() ? (
            <span key={index} className="bg-yellow-200 dark:bg-yellow-800 font-semibold">
              {part}
            </span>
          ) : (
            part
          )
        )}
      </>
    );
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="text-sm text-muted-foreground mb-2">
          💡 Tip: Select a position first for faster, more accurate results
        </div>
        <div className="flex gap-2">
          <select
            value={position}
            onChange={(e) => setPosition(e.target.value)}
            className="px-3 py-2 border rounded-md bg-background min-w-[120px]"
            disabled={loading}
          >
            <option value="">All Positions</option>
            <option value="QB">QB</option>
            <option value="RB">RB</option>
            <option value="WR">WR</option>
            <option value="TE">TE</option>
            <option value="K">K</option>
            <option value="DEF">DEF</option>
          </select>
          <Input
            placeholder="Search players by name (min 2 characters)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            className="flex-1"
          />
        </div>

        {query.length > 0 && query.length < 2 && (
          <p className="text-xs text-muted-foreground">
            Type at least 2 characters to search
          </p>
        )}

        {loading && (
          <p className="text-xs text-muted-foreground flex items-center gap-2">
            <span className="animate-spin">⏳</span> Searching...
          </p>
        )}
      </div>

      {error && (
        <div className="text-sm text-red-600 dark:text-red-400 p-3 bg-red-50 dark:bg-red-950 rounded-md">
          {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground">
            {results.length} player{results.length !== 1 ? 's' : ''} found
          </p>
          <div className="grid gap-2 max-h-96 overflow-y-auto">
            {results.map((player, index) => (
              <Card
                key={player.id || index}
                className="p-3 cursor-pointer hover:bg-accent transition-colors hover:shadow-md"
                onClick={() => {
                  onSelectPlayer(player);
                  setQuery('');
                  setResults([]);
                }}
              >
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-3 flex-1">
                    {/* Player Image */}
                    <img
                      src={getPlayerImageUrl(player.player_id || player.nfl_id)}
                      alt={player.name}
                      className="w-12 h-12 rounded-full object-cover border-2 border-gray-200 dark:border-gray-700"
                      onError={(e) => {
                        e.currentTarget.src = 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146';
                      }}
                    />
                    {/* Team Logo */}
                    {player.team && (
                      <img
                        src={getTeamLogoUrl(player.team)}
                        alt={player.team}
                        className="w-7 h-7 object-contain"
                        onError={(e) => e.currentTarget.style.display = 'none'}
                      />
                    )}
                    <div className="flex-1">
                      <p className="font-semibold">
                        {highlightMatch(player.name, query)}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-xs">
                          {player.position}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {player.team}
                        </Badge>
                        {player.status && player.status.toUpperCase() === 'ACTIVE' && (
                          <Badge className="text-xs bg-green-600 text-white">
                            Active
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  {player.jersey_number && (
                    <div className="text-xl font-bold text-muted-foreground ml-4">
                      #{player.jersey_number}
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {!loading && results.length === 0 && query.length >= 2 && (
        <div className="text-center py-8">
          <p className="text-sm text-muted-foreground mb-2">
            No players found for "{query}"
          </p>
          <p className="text-xs text-muted-foreground">
            Try:
          </p>
          <ul className="text-xs text-muted-foreground mt-1">
            <li>• Checking your spelling</li>
            <li>• Using a different name variation</li>
            <li>• Searching by first or last name only</li>
            <li>• Removing the position filter</li>
          </ul>
        </div>
      )}
    </div>
  );
}
