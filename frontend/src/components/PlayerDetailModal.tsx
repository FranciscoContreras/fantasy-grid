import { useState, useEffect } from 'react';
import { getPlayerDetails } from '../lib/api';
import { getPlayerImageUrl, getTeamLogoUrl } from '../lib/images';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface PlayerDetailModalProps {
  playerId: string;
  playerName: string;
  onClose: () => void;
}

export function PlayerDetailModal({ playerId, playerName, onClose }: PlayerDetailModalProps) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPlayerDetails();
  }, [playerId]);

  const loadPlayerDetails = async () => {
    try {
      setLoading(true);
      const response = await getPlayerDetails(playerId);
      setData(response.data);
    } catch (err) {
      setError('Failed to load player details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const player = data?.player?.data || data?.player;
  const recentGames = data?.recent_games || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="bg-background rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="sticky top-0 bg-background border-b p-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold">{playerName}</h2>
          <Button variant="outline" size="sm" onClick={onClose}>Close</Button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Loading player details...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 p-4 rounded-md">
              {error}
            </div>
          )}

          {!loading && !error && player && (
            <>
              {/* Player Info Card */}
              <Card className="mb-6">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-6">
                    {/* Player Image */}
                    <div className="flex-shrink-0">
                      <img
                        src={getPlayerImageUrl(player.nfl_id)}
                        alt={playerName}
                        className="w-32 h-32 object-cover rounded-lg border-2 border-gray-200 dark:border-gray-700"
                        onError={(e) => {
                          e.currentTarget.src = 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146';
                        }}
                      />
                    </div>

                    {/* Player Details */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-4">
                        <Badge variant="outline" className="text-lg">{player.position}</Badge>
                        {player.jersey_number && (
                          <Badge variant="outline" className="text-lg">#{player.jersey_number}</Badge>
                        )}
                        {player.team_id && (
                          <img
                            src={getTeamLogoUrl(player.team)}
                            alt={player.team}
                            className="w-8 h-8 object-contain"
                            onError={(e) => e.currentTarget.style.display = 'none'}
                          />
                        )}
                        <Badge className={player.status === 'active' ? 'bg-green-600' : 'bg-gray-600'}>
                          {player.status}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        {player.height_inches && (
                          <div>
                            <p className="text-muted-foreground">Height</p>
                            <p className="font-semibold">{Math.floor(player.height_inches / 12)}'{player.height_inches % 12}"</p>
                          </div>
                        )}
                        {player.weight_pounds && (
                          <div>
                            <p className="text-muted-foreground">Weight</p>
                            <p className="font-semibold">{player.weight_pounds} lbs</p>
                          </div>
                        )}
                        {player.team && (
                          <div>
                            <p className="text-muted-foreground">Team</p>
                            <p className="font-semibold">{player.team}</p>
                          </div>
                        )}
                        {player.nfl_id && (
                          <div>
                            <p className="text-muted-foreground">NFL ID</p>
                            <p className="font-semibold">{player.nfl_id}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Games Performance */}
              <Card>
                <CardHeader>
                  <CardTitle>Last {recentGames.length} Games</CardTitle>
                </CardHeader>
                <CardContent>
                  {recentGames.length === 0 ? (
                    <p className="text-center text-muted-foreground py-4">No recent game data available</p>
                  ) : (
                    <div className="space-y-2">
                      <div className="grid grid-cols-6 gap-2 text-sm font-semibold text-muted-foreground pb-2 border-b">
                        <div>Week</div>
                        <div>Opp</div>
                        <div className="text-right">Yds</div>
                        <div className="text-right">TD</div>
                        <div className="text-right">Rec</div>
                        <div className="text-right">Pts</div>
                      </div>

                      {recentGames.map((game: any, index: number) => (
                        <div key={index} className="grid grid-cols-6 gap-2 text-sm py-2 border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900">
                          <div>{game.week || game.game_week || '-'}</div>
                          <div className="font-semibold">{game.opponent_team || game.opponent || '-'}</div>
                          <div className="text-right">{game.yards || game.passing_yards || game.rushing_yards || game.receiving_yards || 0}</div>
                          <div className="text-right">{game.touchdowns || game.passing_tds || game.rushing_tds || game.receiving_tds || 0}</div>
                          <div className="text-right">{game.receptions || game.targets || '-'}</div>
                          <div className="text-right font-semibold">{game.fantasy_points ? game.fantasy_points.toFixed(1) : '-'}</div>
                        </div>
                      ))}

                      {recentGames.length > 0 && (
                        <div className="grid grid-cols-6 gap-2 text-sm py-2 font-bold bg-gray-50 dark:bg-gray-900">
                          <div className="col-span-2">Average</div>
                          <div className="text-right">
                            {(recentGames.reduce((sum: number, g: any) =>
                              sum + (g.yards || g.passing_yards || g.rushing_yards || g.receiving_yards || 0), 0) / recentGames.length).toFixed(1)}
                          </div>
                          <div className="text-right">
                            {(recentGames.reduce((sum: number, g: any) =>
                              sum + (g.touchdowns || g.passing_tds || g.rushing_tds || g.receiving_tds || 0), 0) / recentGames.length).toFixed(1)}
                          </div>
                          <div className="text-right">-</div>
                          <div className="text-right">
                            {recentGames.some((g: any) => g.fantasy_points !== undefined) ?
                              (recentGames.reduce((sum: number, g: any) => sum + (g.fantasy_points || 0), 0) / recentGames.length).toFixed(1) :
                              '-'
                            }
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
