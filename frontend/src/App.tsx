import { useState, useEffect, lazy, Suspense } from 'react';
import { analyzePlayer, isAuthenticated, logout, getStoredUser } from './lib/api';
import { Player, Analysis } from './types';
import { Input } from './components/ui/input';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';

// Code splitting: Lazy load heavy components
const PlayerSearch = lazy(() => import('./components/PlayerSearch').then(m => ({ default: m.PlayerSearch })));
const PlayerAnalysis = lazy(() => import('./components/PlayerAnalysis').then(m => ({ default: m.PlayerAnalysis })));
const RosterManagement = lazy(() => import('./components/RosterManagement').then(m => ({ default: m.RosterManagement })));
const Auth = lazy(() => import('./components/Auth').then(m => ({ default: m.Auth })));
const LandingPage = lazy(() => import('./components/LandingPage').then(m => ({ default: m.LandingPage })));
const OnboardingWizard = lazy(() => import('./components/OnboardingWizard').then(m => ({ default: m.OnboardingWizard })));

// Loading fallback component
const LoadingFallback = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
      <p className="text-muted-foreground">Loading...</p>
    </div>
  </div>
);

function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [showAuth, setShowAuth] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [currentView, setCurrentView] = useState<'player-analysis' | 'roster-management'>('player-analysis');
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [opponent, setOpponent] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const checkAuth = () => {
      const authed = isAuthenticated();
      setAuthenticated(authed);
      if (authed) {
        setUser(getStoredUser());
      }
    };
    checkAuth();
  }, []);

  const handleAuthSuccess = (isNewUser = false) => {
    setAuthenticated(true);
    setUser(getStoredUser());
    setShowAuth(false);

    // Show onboarding for new users
    if (isNewUser) {
      setShowOnboarding(true);
    }
  };

  const handleOnboardingComplete = (rosterId: number) => {
    setShowOnboarding(false);
    // Switch to roster management view with the new roster
    setCurrentView('roster-management');
  };

  const handleLogout = () => {
    logout();
    setAuthenticated(false);
    setUser(null);
    setShowAuth(false);
  };

  const handleGetStarted = () => {
    setShowAuth(true);
  };

  const handleSignIn = () => {
    setShowAuth(true);
  };

  const handleBackToLanding = () => {
    setShowAuth(false);
  };

  // Show landing page if not authenticated and not on auth page
  if (!authenticated && !showAuth) {
    return (
      <Suspense fallback={<LoadingFallback />}>
        <LandingPage onGetStarted={handleGetStarted} onSignIn={handleSignIn} />
      </Suspense>
    );
  }

  // Show auth modal/page if triggered
  if (!authenticated && showAuth) {
    return (
      <Suspense fallback={<LoadingFallback />}>
        <div className="min-h-screen bg-white flex flex-col">
          {/* Back button */}
          <div className="p-4">
            <Button variant="outline" onClick={handleBackToLanding} className="gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Home
            </Button>
          </div>
          <div className="flex-1 flex items-center justify-center">
            <Auth onAuthSuccess={handleAuthSuccess} />
          </div>
        </div>
      </Suspense>
    );
  }

  // Show onboarding wizard for new users
  if (authenticated && showOnboarding) {
    return (
      <Suspense fallback={<LoadingFallback />}>
        <OnboardingWizard onComplete={handleOnboardingComplete} />
      </Suspense>
    );
  }

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
    <div className="min-h-screen bg-background safe-top safe-bottom">
      <div className="container mx-auto py-4 md:py-8 px-4 md:px-6">
        {/* Header */}
        <div className="mb-4 md:mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
            <div className="flex-1">
              <h1 className="text-2xl md:text-4xl font-bold mb-2">Pilon</h1>
              <p className="text-xs md:text-base text-muted-foreground">
                AI-powered fantasy football player analysis and recommendations
              </p>
            </div>
            <div className="flex items-center gap-2 md:gap-4 w-full sm:w-auto">
              {user && (
                <div className="text-left sm:text-right flex-1 sm:flex-none">
                  <p className="text-sm font-medium truncate max-w-[150px]">{user.username}</p>
                  <p className="text-xs text-muted-foreground truncate max-w-[150px] hidden sm:block">{user.email}</p>
                </div>
              )}
              <Button variant="outline" size="sm" onClick={handleLogout} className="shrink-0">
                Logout
              </Button>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mb-4 md:mb-6 flex gap-2 overflow-x-auto mobile-scroll pb-2">
          <Button
            variant={currentView === 'player-analysis' ? 'default' : 'outline'}
            onClick={() => setCurrentView('player-analysis')}
            className="whitespace-nowrap flex-1 sm:flex-none"
          >
            Player Analysis
          </Button>
          <Button
            variant={currentView === 'roster-management' ? 'default' : 'outline'}
            onClick={() => setCurrentView('roster-management')}
            className="whitespace-nowrap flex-1 sm:flex-none"
          >
            Roster & Matchups
          </Button>
        </div>

        {currentView === 'roster-management' ? (
          <Suspense fallback={<LoadingFallback />}>
            <RosterManagement />
          </Suspense>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8">
            {/* Left Column - Search & Input */}
            <div className="space-y-6">
            {/* Player Search */}
            <Card>
              <CardHeader>
                <CardTitle>Search Player</CardTitle>
              </CardHeader>
              <CardContent>
                <Suspense fallback={<div className="text-center py-4 text-muted-foreground">Loading search...</div>}>
                  <PlayerSearch onSelectPlayer={handleSelectPlayer} />
                </Suspense>
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
              <Suspense fallback={<div className="text-center py-12 text-muted-foreground">Loading analysis...</div>}>
                <PlayerAnalysis analysis={analysis} />
              </Suspense>
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
        )}

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
