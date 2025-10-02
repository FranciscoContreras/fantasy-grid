import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

interface TeamHistory {
  team_id: string;
  team_name: string;
  team_abbr: string;
  season_start: number;
  season_end?: number;
  games_played?: number;
  stats?: {
    touchdowns?: number;
    yards?: number;
    receptions?: number;
  };
}

interface PlayerTeamHistoryTimelineProps {
  playerId: string;
  playerName: string;
}

export function PlayerTeamHistoryTimeline({ playerId, playerName }: PlayerTeamHistoryTimelineProps) {
  const [history, setHistory] = useState<TeamHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTeamHistory();
  }, [playerId]);

  const fetchTeamHistory = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/advanced/players/${playerId}/history`);
      const data = await response.json();
      // Sort by most recent first
      const sortedHistory = (data.data || []).sort(
        (a: TeamHistory, b: TeamHistory) => b.season_start - a.season_start
      );
      setHistory(sortedHistory);
    } catch (error) {
      console.error('Failed to fetch team history:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentTeam = () => {
    return history.find(h => !h.season_end);
  };

  const getPastTeams = () => {
    return history.filter(h => h.season_end);
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardContent className="p-12">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-sm text-muted-foreground">Loading team history...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const currentTeam = getCurrentTeam();
  const pastTeams = getPastTeams();

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-2xl font-black">Team History</CardTitle>
        <p className="text-sm text-muted-foreground">{playerName}'s career timeline</p>
      </CardHeader>
      <CardContent>
        {history.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="font-semibold">No team history available</p>
            <p className="text-sm">This player's career history is not yet available</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Current Team */}
            {currentTeam && (
              <div className="relative">
                <Badge className="bg-green-500 text-white font-bold mb-4">Current Team</Badge>
                <div className="relative pl-8 pb-8 border-l-4 border-green-500">
                  <div className="absolute left-0 top-0 w-4 h-4 -ml-2 rounded-full bg-green-500 ring-4 ring-white"></div>
                  <div className="bg-green-50 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-xl font-black">{currentTeam.team_name}</h3>
                        <p className="text-sm text-gray-600">{currentTeam.team_abbr}</p>
                      </div>
                      <Badge variant="outline" className="font-bold">
                        {currentTeam.season_start} - Present
                      </Badge>
                    </div>
                    {currentTeam.games_played && (
                      <p className="text-sm text-gray-600 mb-2">
                        <span className="font-semibold">Games Played:</span> {currentTeam.games_played}
                      </p>
                    )}
                    {currentTeam.stats && (
                      <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                        {currentTeam.stats.touchdowns !== undefined && (
                          <div>
                            <p className="text-2xl font-black">{currentTeam.stats.touchdowns}</p>
                            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">TDs</p>
                          </div>
                        )}
                        {currentTeam.stats.yards !== undefined && (
                          <div>
                            <p className="text-2xl font-black">{currentTeam.stats.yards}</p>
                            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Yards</p>
                          </div>
                        )}
                        {currentTeam.stats.receptions !== undefined && (
                          <div>
                            <p className="text-2xl font-black">{currentTeam.stats.receptions}</p>
                            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Rec</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Past Teams */}
            {pastTeams.length > 0 && (
              <div>
                {pastTeams.length > 0 && currentTeam && (
                  <Badge className="bg-gray-500 text-white font-bold mb-4">Previous Teams</Badge>
                )}
                <div className="space-y-4">
                  {pastTeams.map((team, index) => (
                    <div key={team.team_id + team.season_start} className="relative pl-8 pb-4 border-l-4 border-gray-300">
                      <div className="absolute left-0 top-0 w-4 h-4 -ml-2 rounded-full bg-gray-300 ring-4 ring-white"></div>
                      <div className="bg-gray-50 rounded-lg p-6">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="text-lg font-black">{team.team_name}</h3>
                            <p className="text-sm text-gray-600">{team.team_abbr}</p>
                          </div>
                          <Badge variant="outline" className="font-bold">
                            {team.season_start}
                            {team.season_end && team.season_end !== team.season_start
                              ? ` - ${team.season_end}`
                              : ''}
                          </Badge>
                        </div>
                        {team.games_played && (
                          <p className="text-sm text-gray-600">
                            <span className="font-semibold">Games Played:</span> {team.games_played}
                          </p>
                        )}
                        {team.stats && (
                          <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                            {team.stats.touchdowns !== undefined && (
                              <div>
                                <p className="text-xl font-black">{team.stats.touchdowns}</p>
                                <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">TDs</p>
                              </div>
                            )}
                            {team.stats.yards !== undefined && (
                              <div>
                                <p className="text-xl font-black">{team.stats.yards}</p>
                                <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Yards</p>
                              </div>
                            )}
                            {team.stats.receptions !== undefined && (
                              <div>
                                <p className="text-xl font-black">{team.stats.receptions}</p>
                                <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Rec</p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
