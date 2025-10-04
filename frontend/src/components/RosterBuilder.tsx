import { useState, useEffect } from 'react';
import { Roster, RosterPlayer, Player } from '../types';
import { getRoster, addPlayerToRoster, removePlayerFromRoster, updateRosterPlayer } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { PlayerSearch } from './PlayerSearch';
import { Badge } from './ui/badge';
import { getPlayerImageUrl, getTeamLogoUrl } from '../lib/images';

interface RosterBuilderProps {
  rosterId: number;
  onRosterUpdate?: () => void;
}

const ROSTER_SLOTS = [
  { slot: 'QB', label: 'Quarterback', count: 1 },
  { slot: 'RB1', label: 'Running Back 1', count: 1 },
  { slot: 'RB2', label: 'Running Back 2', count: 1 },
  { slot: 'WR1', label: 'Wide Receiver 1', count: 1 },
  { slot: 'WR2', label: 'Wide Receiver 2', count: 1 },
  { slot: 'WR3', label: 'Wide Receiver 3', count: 1 },
  { slot: 'TE', label: 'Tight End', count: 1 },
  { slot: 'FLEX', label: 'Flex (RB/WR/TE)', count: 1 },
  { slot: 'K', label: 'Kicker', count: 1 },
  { slot: 'DEF', label: 'Defense', count: 1 },
];

const INJURY_STATUS_COLORS: Record<string, string> = {
  HEALTHY: 'bg-green-500',
  PROBABLE: 'bg-blue-500',
  QUESTIONABLE: 'bg-yellow-500',
  DOUBTFUL: 'bg-orange-500',
  OUT: 'bg-red-500',
};

export function RosterBuilder({ rosterId, onRosterUpdate }: RosterBuilderProps) {
  const [roster, setRoster] = useState<Roster | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [addingToSlot, setAddingToSlot] = useState<string | null>(null);
  const [updatingInjury, setUpdatingInjury] = useState<number | null>(null);

  useEffect(() => {
    loadRoster();
  }, [rosterId]);

  const loadRoster = async () => {
    try {
      setLoading(true);
      const response = await getRoster(rosterId);
      setRoster(response.data);
    } catch (err) {
      setError('Failed to load roster');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPlayer = async (player: Player, slot: string) => {
    try {
      // CRITICAL DEBUG - Multiple logging methods
      console.error('🔥 handleAddPlayer CALLED!', { player, slot });
      window.alert?.(`handleAddPlayer called! Player: ${player.name}, Slot: ${slot}`);
      console.log('handleAddPlayer called with:', { player, slot });

      // Validate player has required fields
      if (!player.name || !player.position || !player.team) {
        console.error('Player missing required fields:', player);
        alert(`ERROR: Player missing fields - ${!player.name ? 'name ' : ''}${!player.position ? 'position ' : ''}${!player.team ? 'team' : ''}`);
        setError(`Invalid player data. Missing: ${!player.name ? 'name ' : ''}${!player.position ? 'position ' : ''}${!player.team ? 'team' : ''}`);
        return;
      }

      const playerData = {
        player_id: player.id || player.player_id || player.nfl_id,
        player_name: player.name,
        position: player.position,
        team: player.team,
        roster_slot: slot,
        is_starter: true,
        injury_status: 'HEALTHY',
      };

      console.log('Sending player data to API:', playerData);

      await addPlayerToRoster(rosterId, playerData);

      await loadRoster();
      setAddingToSlot(null);
      setError(''); // Clear any previous errors
      onRosterUpdate?.();
    } catch (err: any) {
      console.error('Failed to add player:', err);
      const errorMessage = err?.response?.data?.error || err?.message || 'Failed to add player to roster';
      setError(errorMessage);
    }
  };

  const handleRemovePlayer = async (playerRosterId: number) => {
    try {
      await removePlayerFromRoster(rosterId, playerRosterId);
      await loadRoster();
      onRosterUpdate?.();
    } catch (err) {
      console.error('Failed to remove player:', err);
      setError('Failed to remove player');
    }
  };

  const handleUpdateInjuryStatus = async (
    playerRosterId: number,
    newStatus: string
  ) => {
    try {
      await updateRosterPlayer(rosterId, playerRosterId, {
        injury_status: newStatus,
      });
      await loadRoster();
      setUpdatingInjury(null);
      onRosterUpdate?.();
    } catch (err) {
      console.error('Failed to update injury status:', err);
      setError('Failed to update injury status');
    }
  };

  const getPlayerInSlot = (slot: string): RosterPlayer | undefined => {
    return roster?.players?.find((p) => p.roster_slot === slot);
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">Loading roster...</p>
        </CardContent>
      </Card>
    );
  }

  if (!roster) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-red-600">Failed to load roster</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>{roster.name}</CardTitle>
            {roster.league_name && (
              <p className="text-sm text-muted-foreground mt-1">
                {roster.league_name} • {roster.scoring_type}
              </p>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-md text-sm">
            {error}
          </div>
        )}

        <div className="space-y-3">
          {ROSTER_SLOTS.map((slotInfo) => {
            const player = getPlayerInSlot(slotInfo.slot);

            return (
              <div
                key={slotInfo.slot}
                className="flex items-center justify-between p-3 border rounded-md"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted-foreground">
                    {slotInfo.label}
                  </p>
                  {player ? (
                    <div className="flex items-center gap-3 mt-1">
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
                      <div className="flex items-center gap-2">
                        <p className="font-semibold">{player.player_name}</p>
                        <Badge variant="outline" className="text-xs">
                          {player.position}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {player.team}
                        </Badge>
                        {player.injury_status !== 'HEALTHY' && (
                          <Badge
                            className={`text-xs text-white ${
                              INJURY_STATUS_COLORS[player.injury_status]
                            }`}
                          >
                            {player.injury_status}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground mt-1">Empty</p>
                  )}
                </div>

                <div className="flex gap-2">
                  {player ? (
                    <>
                      {updatingInjury === player.id ? (
                        <select
                          className="text-xs border rounded px-2 py-1"
                          onChange={(e) =>
                            handleUpdateInjuryStatus(player.id, e.target.value)
                          }
                          defaultValue={player.injury_status}
                        >
                          <option value="HEALTHY">Healthy</option>
                          <option value="PROBABLE">Probable</option>
                          <option value="QUESTIONABLE">Questionable</option>
                          <option value="DOUBTFUL">Doubtful</option>
                          <option value="OUT">Out</option>
                        </select>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setUpdatingInjury(player.id)}
                        >
                          Injury Status
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleRemovePlayer(player.id)}
                      >
                        Remove
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => setAddingToSlot(slotInfo.slot)}
                    >
                      Add Player
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Bench Players */}
        <div className="mt-6">
          <h3 className="text-sm font-semibold mb-3">Bench</h3>
          <div className="space-y-2">
            {roster.players
              ?.filter((p) => p.roster_slot === 'BENCH')
              .map((player) => (
                <div
                  key={player.id}
                  className="flex items-center justify-between p-2 border rounded-md"
                >
                  <div className="flex items-center gap-3">
                    {/* Player Image */}
                    <img
                      src={getPlayerImageUrl(player.player_id)}
                      alt={player.player_name}
                      className="w-8 h-8 rounded-full object-cover border border-gray-200 dark:border-gray-700"
                      onError={(e) => {
                        e.currentTarget.src = 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146';
                      }}
                    />
                    {/* Team Logo */}
                    {player.team && (
                      <img
                        src={getTeamLogoUrl(player.team)}
                        alt={player.team}
                        className="w-5 h-5 object-contain"
                        onError={(e) => e.currentTarget.style.display = 'none'}
                      />
                    )}
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-sm">{player.player_name}</p>
                      <Badge variant="outline" className="text-xs">
                        {player.position}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {player.team}
                      </Badge>
                      {player.injury_status !== 'HEALTHY' && (
                        <Badge
                          className={`text-xs text-white ${
                            INJURY_STATUS_COLORS[player.injury_status]
                          }`}
                        >
                          {player.injury_status}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleRemovePlayer(player.id)}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            <Button
              size="sm"
              variant="outline"
              className="w-full"
              onClick={() => setAddingToSlot('BENCH')}
            >
              Add Bench Player
            </Button>
          </div>
        </div>

        {/* Player Search Modal */}
        {addingToSlot && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 p-6 rounded-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">
                  Add Player to {addingToSlot}
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setAddingToSlot(null)}
                >
                  ✕
                </Button>
              </div>
              <PlayerSearch
                onSelectPlayer={(player) => {
                  console.error('🎯 Arrow function executing in RosterBuilder!', { player, addingToSlot });
                  window.alert?.(`Arrow function called! About to call handleAddPlayer with slot: ${addingToSlot}`);
                  handleAddPlayer(player, addingToSlot);
                }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
