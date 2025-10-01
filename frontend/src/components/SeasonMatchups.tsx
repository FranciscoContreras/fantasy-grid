import { useState, useEffect } from 'react';
import { getSeasonMatchups } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { getPlayerImageUrl, getTeamLogoUrl } from '../lib/images';

interface SeasonMatchupsProps {
  rosterId: number;
}

interface PlayerMatchup {
  player: {
    player_id?: string;
    player_name: string;
    position: string;
    team: string;
  };
  opponent_team: string | null;
  has_game: boolean;
  error?: string;
}

interface WeekMatchups {
  [week: number]: PlayerMatchup[];
}

interface SeasonData {
  roster_id: number;
  roster_name: string;
  season: number;
  total_weeks: number;
  matchups: WeekMatchups;
}

export function SeasonMatchups({ rosterId }: SeasonMatchupsProps) {
  const [data, setData] = useState<SeasonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSeasonMatchups();
  }, [rosterId]);

  const loadSeasonMatchups = async () => {
    try {
      setLoading(true);
      const response = await getSeasonMatchups(rosterId);
      setData(response.data);
    } catch (err) {
      setError('Failed to load season matchups');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">Loading season matchups...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-red-600">{error || 'No data available'}</p>
        </CardContent>
      </Card>
    );
  }

  const weeks = Object.keys(data.matchups).map(Number).sort((a, b) => a - b);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>
            {data.roster_name} - {data.season} Season Matchups
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            {data.total_weeks} weeks available
          </p>
        </CardHeader>
      </Card>

      <div className="space-y-4">
        {weeks.map((week) => (
          <Card key={week}>
            <CardHeader>
              <CardTitle className="text-lg">Week {week}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {data.matchups[week].map((matchup, idx) => (
                  <PlayerMatchupRow key={idx} matchup={matchup} />
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

function PlayerMatchupRow({ matchup }: { matchup: PlayerMatchup }) {
  const player = matchup.player;
  const isByeWeek = !matchup.has_game || matchup.opponent_team === null;

  return (
    <div className="flex items-center justify-between p-3 border rounded-lg">
      <div className="flex items-center gap-3">
        {/* Player Image */}
        <img
          src={getPlayerImageUrl(player.player_id)}
          alt={player.player_name}
          className="w-10 h-10 rounded-full object-cover border border-gray-200 dark:border-gray-700"
          onError={(e) => {
            e.currentTarget.src = 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146';
          }}
        />
        {/* Team Logo */}
        {player.team && (
          <img
            src={getTeamLogoUrl(player.team)}
            alt={player.team}
            className="w-6 h-6 object-contain"
            onError={(e) => e.currentTarget.style.display = 'none'}
          />
        )}
        <div>
          <p className="font-medium">{player.player_name}</p>
          <div className="flex gap-2 mt-1">
            <Badge variant="outline">{player.position}</Badge>
            <Badge variant="outline">{player.team}</Badge>
          </div>
        </div>
      </div>

      <div className="text-right">
        {isByeWeek ? (
          <Badge className="bg-gray-500 text-white">BYE</Badge>
        ) : (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">vs</span>
            {/* Opponent Team Logo */}
            {matchup.opponent_team && (
              <img
                src={getTeamLogoUrl(matchup.opponent_team)}
                alt={matchup.opponent_team}
                className="w-6 h-6 object-contain"
                onError={(e) => e.currentTarget.style.display = 'none'}
              />
            )}
            <Badge className="bg-blue-600 text-white">{matchup.opponent_team}</Badge>
          </div>
        )}
      </div>
    </div>
  );
}
