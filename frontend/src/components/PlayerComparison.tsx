import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Player } from '@/types';
import { getPlayerImageUrl, getTeamLogoUrl, getPlayerInitials, handleImageError, teamColors } from '@/lib/images';

interface ComparisonPlayer extends Player {
  matchup_score?: number;
  projected_points?: number;
  grade?: string;
  opponent?: string;
}

interface PlayerComparisonProps {
  players: ComparisonPlayer[];
}

export function PlayerComparison({ players }: PlayerComparisonProps) {
  if (players.length === 0) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">
            No players to compare yet.
          </p>
        </CardContent>
      </Card>
    );
  }

  const getGradeColor = (grade?: string) => {
    if (!grade) return 'text-gray-600';
    if (grade.startsWith('A')) return 'text-green-600 dark:text-green-400';
    if (grade.startsWith('B')) return 'text-blue-600 dark:text-blue-400';
    if (grade.startsWith('C')) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Player Comparison ({players.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-2"></th>
                  <th className="text-left py-2 px-2">Player</th>
                  <th className="text-left py-2 px-2">Position</th>
                  <th className="text-left py-2 px-2">Team</th>
                  <th className="text-left py-2 px-2">vs</th>
                  <th className="text-right py-2 px-2">Matchup</th>
                  <th className="text-right py-2 px-2">Grade</th>
                  <th className="text-right py-2 px-2">Projected</th>
                </tr>
              </thead>
              <tbody>
                {players.map((player, idx) => (
                  <tr key={player.id || idx} className="border-b last:border-0">
                    <td className="py-3 px-2">
                      <div className="flex items-center gap-2">
                        {/* Player Image with Fallback */}
                        <div className="relative">
                          <img
                            src={getPlayerImageUrl(player.player_id || player.nfl_id)}
                            alt={player.name}
                            className="w-10 h-10 rounded-full object-cover border border-gray-200 dark:border-gray-700"
                            onError={(e) => handleImageError(e)}
                          />
                          <div
                            className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-xs border border-gray-200 dark:border-gray-700 absolute top-0 left-0"
                            style={{ backgroundColor: teamColors[player.team]?.primary || '#6B7280', display: 'none' }}
                          >
                            {getPlayerInitials(player.name)}
                          </div>
                        </div>
                        {/* Team Logo */}
                        {player.team && (
                          <img
                            src={getTeamLogoUrl(player.team)}
                            alt={player.team}
                            className="w-6 h-6 object-contain"
                            onError={(e) => e.currentTarget.style.display = 'none'}
                          />
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-2 font-semibold">{player.name}</td>
                    <td className="py-3 px-2">
                      <Badge variant="outline">{player.position}</Badge>
                    </td>
                    <td className="py-3 px-2">{player.team}</td>
                    <td className="py-3 px-2 text-sm text-muted-foreground">
                      {player.opponent || '-'}
                    </td>
                    <td className="py-3 px-2 text-right">
                      {player.matchup_score !== undefined ? (
                        <span className="font-semibold">{player.matchup_score}</span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="py-3 px-2 text-right">
                      {player.grade ? (
                        <span className={`text-xl font-bold ${getGradeColor(player.grade)}`}>
                          {player.grade}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
                    <td className="py-3 px-2 text-right">
                      {player.projected_points !== undefined ? (
                        <span className="font-semibold">{player.projected_points} pts</span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Top Ranked */}
      {players.length > 0 && players[0].projected_points && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Top Ranked</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {/* Player Image */}
                <img
                  src={getPlayerImageUrl(players[0].player_id || players[0].nfl_id)}
                  alt={players[0].name}
                  className="w-16 h-16 rounded-full object-cover border-2 border-gray-200 dark:border-gray-700"
                  onError={(e) => {
                    e.currentTarget.src = 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146';
                  }}
                />
                {/* Team Logo */}
                {players[0].team && (
                  <img
                    src={getTeamLogoUrl(players[0].team)}
                    alt={players[0].team}
                    className="w-10 h-10 object-contain"
                    onError={(e) => e.currentTarget.style.display = 'none'}
                  />
                )}
                <div>
                  <p className="text-2xl font-bold">{players[0].name}</p>
                  <p className="text-sm text-muted-foreground">
                    {players[0].position} - {players[0].team}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-4xl font-bold ${getGradeColor(players[0].grade)}`}>
                  {players[0].grade || '-'}
                </p>
                <p className="text-sm text-muted-foreground">
                  {players[0].projected_points} projected points
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
