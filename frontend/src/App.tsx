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
  <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white font-system">
    <div className="glass-card compact-padding text-center">
      <div className="animate-spin h-12 w-12 border-2 border-white/20 border-t-white mx-auto mb-4"></div>
      <p className="text-white/80 font-medium">Loading...</p>
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

    // Check for Yahoo OAuth success
    const params = new URLSearchParams(window.location.search);
    if (params.get('yahoo_auth') === 'success') {
      // Show success notification
      alert('Yahoo Fantasy account connected successfully! You can now import your rosters.');
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
      // Switch to roster management view
      setCurrentView('roster-management');
    }
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
        <div className="min-h-screen bg-gray-50 flex flex-col font-system">
          {/* Back button */}
          <div className="p-6">
            <Button variant="outline" onClick={handleBackToLanding} className="border-gray-300 text-gray-700 hover:bg-gray-100 hover:border-gray-400 gap-2 rounded-lg">
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white safe-top safe-bottom font-system">
      {/* Monochromatic Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-white/5 to-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-gradient-to-r from-white/3 to-white/8 rounded-full blur-3xl"></div>
      </div>

      <div className="relative container mx-auto py-6 px-6 max-w-7xl">
        {/* Header */}
        <div className="glass-card compact-padding mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex-1">
              <h1 className="text-3xl font-logo mb-2 text-white">Pilon</h1>
              <p className="text-sm text-white/70 font-medium">
                AI-Powered Fantasy Football Analytics
              </p>
            </div>
            <div className="flex items-center gap-4">
              {user && (
                <div className="text-right">
                  <p className="text-sm font-semibold text-white">{user.username}</p>
                  <p className="text-xs text-white/60">{user.email}</p>
                </div>
              )}
              <Button
                variant="outline"
                onClick={handleLogout}
                className="glass border-white/20 text-white hover:bg-white/10 font-medium px-4 py-2 rounded-xl"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex gap-3 mb-8">
          <Button
            variant={currentView === 'player-analysis' ? 'default' : 'outline'}
            onClick={() => setCurrentView('player-analysis')}
            className={`flex-1 sm:flex-none font-medium px-6 py-3 rounded-xl transition-all ${
              currentView === 'player-analysis'
                ? 'glass bg-white/20 text-white border-0'
                : 'glass border-white/20 text-white hover:bg-white/10'
            }`}
          >
            Player Analysis
          </Button>
          <Button
            variant={currentView === 'roster-management' ? 'default' : 'outline'}
            onClick={() => setCurrentView('roster-management')}
            className={`flex-1 sm:flex-none font-medium px-6 py-3 rounded-xl transition-all ${
              currentView === 'roster-management'
                ? 'glass bg-white/20 text-white border-0'
                : 'glass border-white/20 text-white hover:bg-white/10'
            }`}
          >
            Roster & Matchups
          </Button>
        </div>

        {currentView === 'roster-management' ? (
          <Suspense fallback={<LoadingFallback />}>
            <RosterManagement />
          </Suspense>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Search & Input */}
            <div className="space-y-6">
              {/* Player Search */}
              <div className="glass-card p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Search Player</h2>
                <Suspense fallback={<div className="text-center py-6 text-white/60 font-medium">Loading search...</div>}>
                  <PlayerSearch onSelectPlayer={handleSelectPlayer} />
                </Suspense>
              </div>

              {/* Analysis Inputs */}
              {selectedPlayer && (
                <div className="glass-card p-6">
                  <h2 className="text-xl font-semibold text-white mb-4">Analyze Matchup</h2>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-white/60 font-medium mb-3">Selected Player</p>
                      <div className="glass compact-padding">
                        <p className="text-lg font-semibold text-white">{selectedPlayer.name}</p>
                        <p className="text-sm text-white/60">
                          {selectedPlayer.position} • {selectedPlayer.team}
                        </p>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-white/80 mb-2 block">
                        Opponent Team ID <span className="text-red-400">*</span>
                      </label>
                      <Input
                        placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000"
                        value={opponent}
                        onChange={(e) => setOpponent(e.target.value)}
                        className="glass border-white/20 text-white font-medium p-3 focus:border-white/40 placeholder:text-white/40"
                      />
                      <p className="text-xs text-white/50 mt-2">
                        Enter the opponent team's UUID
                      </p>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-white/80 mb-2 block">
                        Game Location (Optional)
                      </label>
                      <Input
                        placeholder="e.g., Buffalo,NY"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        className="glass border-white/20 text-white font-medium p-3 focus:border-white/40 placeholder:text-white/40"
                      />
                      <p className="text-xs text-white/50 mt-2">
                        Add location for weather impact analysis
                      </p>
                    </div>

                    {error && (
                      <div className="glass-dark p-4 rounded-xl text-center">
                        <p className="text-sm text-red-300 font-medium">{error}</p>
                      </div>
                    )}

                    <Button
                      onClick={handleAnalyze}
                      disabled={loading || !opponent}
                      className="w-full glass bg-white/20 text-white hover:bg-white/30 font-semibold py-3 rounded-xl border-0 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                      {loading ? 'Analyzing...' : 'Analyze Matchup'}
                    </Button>
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Analysis Results */}
            <div>
              {analysis ? (
                <Suspense fallback={<div className="glass-card compact-padding text-center"><p className="text-white/60 font-medium">Loading analysis...</p></div>}>
                  <PlayerAnalysis analysis={analysis} />
                </Suspense>
              ) : (
                <div className="glass-card p-12">
                  <div className="text-center">
                    <div className="w-16 h-16 mx-auto mb-6 rounded-full glass flex items-center justify-center">
                      <div className="w-8 h-8 bg-white/20 rounded-full"></div>
                    </div>
                    <p className="text-xl font-semibold text-white mb-2">No Analysis Yet</p>
                    <p className="text-sm text-white/60 max-w-md mx-auto">
                      Search for a player and enter opponent details to get started
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-16 text-center">
          <p className="text-sm text-white/50 font-medium">
            Powered by Grid Iron Mind NFL API • Analytics Since 2025
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
