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
    <div className="min-h-screen bg-black text-white safe-top safe-bottom font-body">
      <div className="container mx-auto py-6 md:py-12 px-4 md:px-6">
        {/* Neo-Vintage Header */}
        <div className="mb-8 md:mb-12 border-b-4 border-white pb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start gap-6">
            <div className="flex-1">
              <h1 className="text-4xl md:text-6xl font-script mb-4 text-white">Pilon</h1>
              <p className="text-sm md:text-lg text-gray-300 font-body max-w-2xl uppercase tracking-[0.2em]">
                AI-Powered Fantasy Football Analytics • Championship Performance
              </p>
            </div>
            <div className="flex items-center gap-4 md:gap-6 w-full sm:w-auto">
              {user && (
                <div className="text-left sm:text-right flex-1 sm:flex-none">
                  <p className="text-lg font-display uppercase tracking-wider text-white truncate max-w-[150px]">{user.username}</p>
                  <p className="text-xs text-gray-400 uppercase tracking-[0.2em] truncate max-w-[150px] hidden sm:block">{user.email}</p>
                </div>
              )}
              <Button
                variant="outline"
                size="lg"
                onClick={handleLogout}
                className="shrink-0 border-2 border-white text-white hover:bg-white hover:text-black font-display uppercase tracking-wider px-6 py-3"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>

        {/* Neo-Vintage Navigation */}
        <div className="mb-8 md:mb-12 flex gap-4 overflow-x-auto mobile-scroll pb-4">
          <Button
            variant={currentView === 'player-analysis' ? 'default' : 'outline'}
            onClick={() => setCurrentView('player-analysis')}
            className={`whitespace-nowrap flex-1 sm:flex-none font-display uppercase tracking-[0.2em] text-lg px-8 py-4 border-2 ${
              currentView === 'player-analysis'
                ? 'bg-white text-black border-white'
                : 'border-white text-white hover:bg-white hover:text-black'
            } transition-all`}
          >
            Player Analysis
          </Button>
          <Button
            variant={currentView === 'roster-management' ? 'default' : 'outline'}
            onClick={() => setCurrentView('roster-management')}
            className={`whitespace-nowrap flex-1 sm:flex-none font-display uppercase tracking-[0.2em] text-lg px-8 py-4 border-2 ${
              currentView === 'roster-management'
                ? 'bg-white text-black border-white'
                : 'border-white text-white hover:bg-white hover:text-black'
            } transition-all`}
          >
            Roster & Matchups
          </Button>
        </div>

        {currentView === 'roster-management' ? (
          <Suspense fallback={<LoadingFallback />}>
            <RosterManagement />
          </Suspense>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-12">
            {/* Left Column - Search & Input */}
            <div className="space-y-8">
            {/* Neo-Vintage Player Search */}
            <Card className="bg-white text-black border-4 border-white">
              <CardHeader className="border-b-2 border-black pb-4">
                <CardTitle className="font-display text-2xl uppercase tracking-[0.1em] text-black">Search Player</CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <Suspense fallback={<div className="text-center py-6 text-gray-600 font-display uppercase tracking-wider">Loading search...</div>}>
                  <PlayerSearch onSelectPlayer={handleSelectPlayer} />
                </Suspense>
              </CardContent>
            </Card>

            {/* Neo-Vintage Analysis Inputs */}
            {selectedPlayer && (
              <Card className="bg-gray-900 text-white border-4 border-gray-700">
                <CardHeader className="border-b-2 border-gray-600 pb-4">
                  <CardTitle className="font-display text-2xl uppercase tracking-[0.1em] text-white">Analyze Matchup</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6 pt-6">
                  <div>
                    <p className="text-sm text-gray-400 mb-3 font-display uppercase tracking-[0.2em]">Selected Player</p>
                    <div className="p-4 bg-black border-2 border-gray-600">
                      <p className="font-display text-xl uppercase tracking-wider text-white">{selectedPlayer.name}</p>
                      <p className="text-sm text-gray-400 uppercase tracking-[0.3em] mt-1">
                        {selectedPlayer.position} · {selectedPlayer.team}
                      </p>
                    </div>
                  </div>

                  <div>
                    <label className="text-sm text-gray-400 font-display uppercase tracking-[0.2em] mb-2 block">
                      Opponent Team ID <span className="text-red-400">*</span>
                    </label>
                    <Input
                      placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000"
                      value={opponent}
                      onChange={(e) => setOpponent(e.target.value)}
                      className="mt-1 bg-black border-2 border-gray-600 text-white font-body p-3 focus:border-white"
                    />
                    <p className="text-xs text-gray-500 mt-2 uppercase tracking-wider">
                      Enter the opponent team's UUID
                    </p>
                  </div>

                  <div>
                    <label className="text-sm text-gray-400 font-display uppercase tracking-[0.2em] mb-2 block">
                      Game Location (Optional)
                    </label>
                    <Input
                      placeholder="e.g., Buffalo,NY"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      className="mt-1 bg-black border-2 border-gray-600 text-white font-body p-3 focus:border-white"
                    />
                    <p className="text-xs text-gray-500 mt-2 uppercase tracking-wider">
                      Add location for weather impact analysis
                    </p>
                  </div>

                  {error && (
                    <div className="text-sm text-red-400 p-4 bg-red-900 border-2 border-red-700 font-display uppercase tracking-wider">
                      {error}
                    </div>
                  )}

                  <Button
                    onClick={handleAnalyze}
                    disabled={loading || !opponent}
                    className="w-full bg-white text-black hover:bg-gray-100 font-display uppercase tracking-[0.2em] text-lg py-6 border-2 border-white disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {loading ? 'ANALYZING...' : 'ANALYZE MATCHUP'}
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Neo-Vintage Analysis Results */}
          <div>
            {analysis ? (
              <Suspense fallback={<div className="text-center py-12 text-gray-400 font-display uppercase tracking-[0.2em]">Loading analysis...</div>}>
                <PlayerAnalysis analysis={analysis} />
              </Suspense>
            ) : (
              <Card className="bg-gray-800 text-white border-4 border-gray-600">
                <CardContent className="py-16">
                  <div className="text-center">
                    <div className="w-24 h-24 mx-auto mb-8 border-4 border-gray-600 flex items-center justify-center">
                      <div className="w-12 h-12 bg-gray-600"></div>
                    </div>
                    <p className="text-2xl mb-4 font-display uppercase tracking-[0.1em] text-white">No Analysis Yet</p>
                    <p className="text-sm text-gray-400 uppercase tracking-[0.2em] font-body max-w-md mx-auto">
                      Search for a player and enter opponent details to get started
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
          </div>
        )}

        {/* Neo-Vintage Footer */}
        <div className="mt-20 text-center border-t-4 border-white pt-12">
          <p className="text-sm text-gray-400 uppercase tracking-[0.3em] font-display">
            Powered by Grid Iron Mind NFL API • Championship Analytics Since 2024
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
