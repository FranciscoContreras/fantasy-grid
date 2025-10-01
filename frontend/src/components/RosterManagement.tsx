import { useState, useEffect } from 'react';
import { Roster, Matchup } from '../types';
import {
  getRosters,
  createRoster,
  deleteRoster,
  createMatchup,
  getMatchups,
  getCurrentWeek,
  getAvailableWeeks,
} from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { RosterBuilder } from './RosterBuilder';
import { MatchupAnalysis } from './MatchupAnalysis';
import { SeasonMatchups } from './SeasonMatchups';
import { Badge } from './ui/badge';

export function RosterManagement() {
  const [rosters, setRosters] = useState<Roster[]>([]);
  const [selectedRosterId, setSelectedRosterId] = useState<number | null>(null);
  const [selectedMatchupId, setSelectedMatchupId] = useState<number | null>(null);
  const [matchups, setMatchups] = useState<Matchup[]>([]);
  const [view, setView] = useState<'rosters' | 'matchup' | 'season'>('rosters');
  const [showNewRosterForm, setShowNewRosterForm] = useState(false);
  const [showNewMatchupForm, setShowNewMatchupForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // New roster form
  const [newRosterName, setNewRosterName] = useState('');
  const [newRosterLeague, setNewRosterLeague] = useState('');
  const [newRosterScoring, setNewRosterScoring] = useState('PPR');

  // New matchup form
  const [matchupWeek, setMatchupWeek] = useState(1);
  const [matchupSeason, setMatchupSeason] = useState(2025);
  const [matchupUserRoster, setMatchupUserRoster] = useState<number | null>(null);
  const [availableWeeks, setAvailableWeeks] = useState<number[]>([]);

  useEffect(() => {
    loadRosters();
    loadMatchups();
    loadCurrentWeek();
  }, []);

  const loadCurrentWeek = async () => {
    try {
      const response = await getCurrentWeek();
      if (response.data) {
        setMatchupWeek(response.data.week);
        setMatchupSeason(response.data.season);
        // Load available weeks for this season
        loadAvailableWeeks(response.data.season);
      }
    } catch (err) {
      console.error('Failed to load current week:', err);
    }
  };

  const loadAvailableWeeks = async (season: number) => {
    try {
      const response = await getAvailableWeeks(season);
      if (response.data) {
        setAvailableWeeks(response.data.available_weeks);
      }
    } catch (err) {
      console.error('Failed to load available weeks:', err);
    }
  };

  const loadRosters = async () => {
    try {
      setLoading(true);
      const response = await getRosters();
      setRosters(response.data || []);
      if (response.data && response.data.length > 0 && !selectedRosterId) {
        setSelectedRosterId(response.data[0].id);
      }
    } catch (err) {
      setError('Failed to load rosters');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadMatchups = async () => {
    try {
      const response = await getMatchups();
      setMatchups(response.data || []);
    } catch (err) {
      console.error('Failed to load matchups:', err);
    }
  };

  const handleCreateRoster = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRosterName) return;

    try {
      await createRoster({
        name: newRosterName,
        league_name: newRosterLeague,
        scoring_type: newRosterScoring,
      });
      setNewRosterName('');
      setNewRosterLeague('');
      setShowNewRosterForm(false);
      await loadRosters();
    } catch (err) {
      setError('Failed to create roster');
      console.error(err);
    }
  };

  const handleDeleteRoster = async (rosterId: number) => {
    if (!confirm('Are you sure you want to delete this roster?')) return;

    try {
      await deleteRoster(rosterId);
      if (selectedRosterId === rosterId) {
        setSelectedRosterId(null);
      }
      await loadRosters();
    } catch (err) {
      setError('Failed to delete roster');
      console.error(err);
    }
  };

  const handleCreateMatchup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!matchupUserRoster) {
      setError('Please select a roster');
      return;
    }

    // Validate week availability
    if (availableWeeks.length > 0 && !availableWeeks.includes(matchupWeek)) {
      setError(`Schedule not available for Week ${matchupWeek} yet. Please select a different week.`);
      return;
    }

    try {
      const response = await createMatchup({
        week: matchupWeek,
        season: matchupSeason,
        user_roster_id: matchupUserRoster,
      });
      setShowNewMatchupForm(false);
      setSelectedMatchupId(response.data.id);
      setView('matchup');
      await loadMatchups();
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || 'Failed to create matchup';
      setError(errorMessage);
      console.error(err);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl md:text-4xl font-bold mb-2">Roster Management</h1>
        <p className="text-sm md:text-base text-muted-foreground">
          Build your roster and analyze weekly matchups
        </p>
      </div>

      {/* View Toggle */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={view === 'rosters' ? 'default' : 'outline'}
          onClick={() => setView('rosters')}
        >
          My Rosters
        </Button>
        <Button
          variant={view === 'matchup' ? 'default' : 'outline'}
          onClick={() => setView('matchup')}
        >
          Weekly Matchup
        </Button>
        <Button
          variant={view === 'season' ? 'default' : 'outline'}
          onClick={() => setView('season')}
          disabled={!selectedRosterId}
        >
          Season Matchups
        </Button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-md text-sm">
          {error}
          <button
            onClick={() => setError('')}
            className="ml-2 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {view === 'rosters' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Roster List */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>My Rosters</CardTitle>
                  <Button
                    size="sm"
                    onClick={() => setShowNewRosterForm(true)}
                  >
                    + New
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p className="text-sm text-muted-foreground">Loading...</p>
                ) : rosters.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-sm text-muted-foreground mb-3">
                      No rosters yet
                    </p>
                    <Button onClick={() => setShowNewRosterForm(true)}>
                      Create Your First Roster
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {rosters.map((roster) => (
                      <div
                        key={roster.id}
                        className={`p-3 border rounded-md cursor-pointer hover:bg-accent ${
                          selectedRosterId === roster.id ? 'bg-accent' : ''
                        }`}
                        onClick={() => setSelectedRosterId(roster.id)}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="font-semibold">{roster.name}</p>
                            {roster.league_name && (
                              <p className="text-xs text-muted-foreground">
                                {roster.league_name}
                              </p>
                            )}
                            <Badge variant="outline" className="text-xs mt-1">
                              {roster.scoring_type}
                            </Badge>
                          </div>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteRoster(roster.id);
                            }}
                          >
                            🗑️
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Content - Roster Builder */}
          <div className="lg:col-span-2">
            {selectedRosterId ? (
              <RosterBuilder
                key={selectedRosterId}
                rosterId={selectedRosterId}
                onRosterUpdate={loadRosters}
              />
            ) : (
              <Card>
                <CardContent className="py-12">
                  <p className="text-center text-muted-foreground">
                    Select a roster to edit
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {view === 'matchup' && (
        <div>
          <div className="mb-6 flex justify-between items-center">
            <h2 className="text-2xl font-bold">Weekly Matchups</h2>
            <Button onClick={() => setShowNewMatchupForm(true)}>
              + New Matchup
            </Button>
          </div>

          {/* Matchup List */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {matchups.map((matchup) => (
              <Card
                key={matchup.id}
                className={`cursor-pointer hover:bg-accent ${
                  selectedMatchupId === matchup.id ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => setSelectedMatchupId(matchup.id)}
              >
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Week {matchup.week} • {matchup.season}
                      </p>
                      <p className="font-semibold">{matchup.user_roster_name}</p>
                      <p className="text-sm text-muted-foreground">vs NFL Defenses</p>
                    </div>
                    {matchup.analyzed && (
                      <Badge className="bg-green-600 text-white">Analyzed</Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Matchup Analysis */}
          {selectedMatchupId ? (
            <MatchupAnalysis matchupId={selectedMatchupId} />
          ) : (
            <Card>
              <CardContent className="py-12">
                <p className="text-center text-muted-foreground">
                  Select a matchup or create a new one to analyze
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {view === 'season' && selectedRosterId && (
        <div>
          <div className="mb-6">
            <h2 className="text-2xl font-bold">Season Matchups</h2>
            <p className="text-muted-foreground mt-1">
              View all future matchups for the selected roster
            </p>
          </div>
          <SeasonMatchups rosterId={selectedRosterId} />
        </div>
      )}

      {/* New Roster Modal */}
      {showNewRosterForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="max-w-md w-full mx-4">
            <CardHeader>
              <CardTitle>Create New Roster</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateRoster} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">
                    Roster Name <span className="text-red-500">*</span>
                  </label>
                  <Input
                    value={newRosterName}
                    onChange={(e) => setNewRosterName(e.target.value)}
                    placeholder="e.g., My Fantasy Team"
                    required
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">League Name (Optional)</label>
                  <Input
                    value={newRosterLeague}
                    onChange={(e) => setNewRosterLeague(e.target.value)}
                    placeholder="e.g., Friends League"
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Scoring Type</label>
                  <select
                    value={newRosterScoring}
                    onChange={(e) => setNewRosterScoring(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                  >
                    <option value="PPR">PPR (Point Per Reception)</option>
                    <option value="Half-PPR">Half PPR</option>
                    <option value="Standard">Standard</option>
                  </select>
                </div>
                <div className="flex gap-2">
                  <Button type="submit" className="flex-1">
                    Create
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowNewRosterForm(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* New Matchup Modal */}
      {showNewMatchupForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="max-w-md w-full mx-4">
            <CardHeader>
              <CardTitle>Create New Matchup</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateMatchup} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Week</label>
                    <Input
                      type="number"
                      min="1"
                      max="18"
                      value={matchupWeek}
                      onChange={(e) => setMatchupWeek(parseInt(e.target.value))}
                      className="mt-1"
                    />
                    {availableWeeks.length > 0 && !availableWeeks.includes(matchupWeek) && (
                      <p className="text-xs text-orange-600 mt-1">
                        Schedule not available for this week yet
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="text-sm font-medium">Season</label>
                    <Input
                      type="number"
                      min="2020"
                      max="2030"
                      value={matchupSeason}
                      onChange={(e) => {
                        const newSeason = parseInt(e.target.value);
                        setMatchupSeason(newSeason);
                        loadAvailableWeeks(newSeason);
                      }}
                      className="mt-1"
                    />
                  </div>
                </div>
                {availableWeeks.length > 0 && (
                  <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-md text-sm">
                    <p className="font-medium text-blue-900 dark:text-blue-100">
                      Available weeks: {availableWeeks.join(', ')}
                    </p>
                  </div>
                )}
                <div>
                  <label className="text-sm font-medium">
                    Select Roster <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={matchupUserRoster || ''}
                    onChange={(e) => setMatchupUserRoster(parseInt(e.target.value))}
                    required
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                  >
                    <option value="">Select roster...</option>
                    {rosters.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex gap-2">
                  <Button type="submit" className="flex-1">
                    Create
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowNewMatchupForm(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
