import { useState } from 'react';
import { PlayerSearch } from './components/PlayerSearch';
import { PlayerAnalysis } from './components/PlayerAnalysis';
import { analyzePlayer } from './lib/api';
import { Player, Analysis } from './types';
import { Input } from './components/ui/input';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';

function App() {
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [opponent, setOpponent] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!selectedPlayer || !opponent) return;

    setLoading(true);
    setError('');

    try {
      const playerId = selectedPlayer.id || selectedPlayer.player_id || '';
      const result = await analyzePlayer(playerId, opponent, location || undefined);
      setAnalysis(result.data);
    } catch (err) {
      setError('Failed to analyze player. Please check the opponent team ID and try again.');
      console.error('Analysis failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlayer = (player: Player) => {
    setSelectedPlayer(player);
    setAnalysis(null); // Clear previous analysis
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Fantasy Grid</h1>
          <p className="text-muted-foreground">
            AI-powered fantasy football player analysis and recommendations
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Left Column - Search & Input */}
          <div className="space-y-6">
            {/* Player Search */}
            <Card>
              <CardHeader>
                <CardTitle>Search Player</CardTitle>
              </CardHeader>
              <CardContent>
                <PlayerSearch onSelectPlayer={handleSelectPlayer} />
              </CardContent>
            </Card>

            {/* Analysis Inputs */}
            {selectedPlayer && (
              <Card>
                <CardHeader>
                  <CardTitle>Analyze Matchup</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Selected Player</p>
                    <div className="p-3 bg-accent rounded-md">
                      <p className="font-semibold">{selectedPlayer.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {selectedPlayer.position} - {selectedPlayer.team}
                      </p>
                    </div>
                  </div>

                  <div>
                    <label className="text-sm text-muted-foreground">
                      Opponent Team ID <span className="text-red-500">*</span>
                    </label>
                    <Input
                      placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000"
                      value={opponent}
                      onChange={(e) => setOpponent(e.target.value)}
                      className="mt-1"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Enter the opponent team's UUID
                    </p>
                  </div>

                  <div>
                    <label className="text-sm text-muted-foreground">
                      Game Location (Optional)
                    </label>
                    <Input
                      placeholder="e.g., Buffalo,NY"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      className="mt-1"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Add location for weather impact analysis
                    </p>
                  </div>

                  {error && (
                    <div className="text-sm text-red-600 dark:text-red-400 p-3 bg-red-50 dark:bg-red-950 rounded-md">
                      {error}
                    </div>
                  )}

                  <Button
                    onClick={handleAnalyze}
                    disabled={loading || !opponent}
                    className="w-full"
                  >
                    {loading ? 'Analyzing...' : 'Analyze Matchup'}
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Analysis Results */}
          <div>
            {analysis ? (
              <PlayerAnalysis analysis={analysis} />
            ) : (
              <Card>
                <CardContent className="py-12">
                  <div className="text-center text-muted-foreground">
                    <p className="text-lg mb-2">No analysis yet</p>
                    <p className="text-sm">
                      Search for a player and enter opponent details to get started
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-muted-foreground border-t pt-6">
          <p>
            Powered by Grid Iron Mind NFL API • AI-driven insights for smarter fantasy decisions
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
