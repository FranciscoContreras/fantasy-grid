import { Button } from '../ui/button';
import PilonLogo from '../../assets/logo.svg';

interface HeroProps {
  onGetStarted: () => void;
  onSignIn: () => void;
}

export function Hero({ onGetStarted, onSignIn }: HeroProps) {
  return (
    <div className="relative min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white overflow-hidden font-system">
      {/* Monochromatic Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-white/5 to-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-gradient-to-r from-white/3 to-white/8 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-white/30 rounded-full"></div>
      </div>

      {/* Glass Navigation */}
      <nav className="relative z-10 max-w-6xl mx-auto px-6 py-4">
        <div className="glass-card compact-padding">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <img src={PilonLogo} alt="Pilon" className="w-16 h-12 object-contain brightness-0 invert" />
            </div>
            <Button
              variant="outline"
              onClick={onSignIn}
              className="glass border-white/30 text-white hover:bg-white/10 font-medium text-sm px-6 py-2 rounded-xl transition-all"
            >
              Sign In
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-center">
          {/* Left Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Badge */}
            <div className="glass-card inline-flex items-center gap-3 px-4 py-2 text-xs font-medium text-white/80">
              <div className="w-2 h-2 bg-white/60 rounded-full"></div>
              <span>EST. 2024 • NFL ANALYTICS</span>
              <div className="w-2 h-2 bg-white/60 rounded-full"></div>
            </div>

            {/* Main Headline */}
            <div className="space-y-4">
              <h1 className="font-logo text-6xl sm:text-7xl md:text-8xl leading-none text-white">
                Pilon
              </h1>
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-light text-white/90 leading-tight">
                Intelligent Fantasy Football
                <br />
                <span className="font-semibold">Analytics Platform</span>
              </h2>
            </div>

            {/* Value Proposition */}
            <p className="text-lg text-white/70 font-light max-w-lg leading-relaxed">
              AI-powered start/sit decisions with real-time analytics.
              Make championship-winning moves with zero guesswork.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4">
              <Button
                size="lg"
                onClick={onGetStarted}
                className="glass bg-white/20 text-white hover:bg-white/30 font-medium px-8 py-3 rounded-xl border-0 transition-all"
              >
                Get Started
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={onSignIn}
                className="glass border-white/20 text-white hover:bg-white/10 font-medium px-8 py-3 rounded-xl transition-all"
              >
                View Demo
              </Button>
            </div>
          </div>

          {/* Right Stats Grid */}
          <div className="lg:col-span-2 grid grid-cols-2 gap-4">
            <div className="glass-card compact-padding text-center">
              <div className="text-3xl font-bold text-white mb-1">10K+</div>
              <div className="text-xs text-white/60 font-medium">Users</div>
            </div>
            <div className="glass-card compact-padding text-center">
              <div className="text-3xl font-bold text-white mb-1">73%</div>
              <div className="text-xs text-white/60 font-medium">Win Rate</div>
            </div>
            <div className="glass-card compact-padding text-center">
              <div className="text-3xl font-bold text-white mb-1">4.9★</div>
              <div className="text-xs text-white/60 font-medium">Rating</div>
            </div>
            <div className="glass-card compact-padding text-center">
              <div className="text-3xl font-bold text-white mb-1">24/7</div>
              <div className="text-xs text-white/60 font-medium">Analysis</div>
            </div>
          </div>
        </div>
      </div>

      {/* Preview Cards */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h3 className="text-2xl font-semibold text-white mb-2">Live Player Analysis</h3>
          <p className="text-white/60">See how our AI grades your players in real-time</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* START Card */}
          <div className="glass-card p-6 hover:scale-105 transition-all group">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <span className="text-gray-900 font-bold text-sm">A+</span>
              </div>
              <div className="px-3 py-1 bg-white/20 text-white text-xs font-medium rounded-full">
                START
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-white">P. Mahomes</h4>
              <p className="text-sm text-white/60">QB • Kansas City</p>
              <div className="text-2xl font-bold text-white">24.8 pts</div>
            </div>
          </div>

          {/* CONSIDER Card */}
          <div className="glass-card p-6 hover:scale-105 transition-all group">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-white/80 rounded-full flex items-center justify-center">
                <span className="text-gray-900 font-bold text-sm">B+</span>
              </div>
              <div className="px-3 py-1 bg-white/15 text-white/90 text-xs font-medium rounded-full">
                CONSIDER
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-white">S. Barkley</h4>
              <p className="text-sm text-white/60">RB • New York</p>
              <div className="text-2xl font-bold text-white/90">18.3 pts</div>
            </div>
          </div>

          {/* BENCH Card */}
          <div className="glass-card p-6 hover:scale-105 transition-all group opacity-60">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-white/40 rounded-full flex items-center justify-center">
                <span className="text-gray-700 font-bold text-sm">C</span>
              </div>
              <div className="px-3 py-1 bg-white/10 text-white/70 text-xs font-medium rounded-full">
                BENCH
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-white/80">D. Hopkins</h4>
              <p className="text-sm text-white/50">WR • Tennessee</p>
              <div className="text-2xl font-bold text-white/70">12.1 pts</div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10">
        <div className="glass-card compact-padding">
          <div className="flex flex-col items-center gap-2 text-white/60">
            <span className="text-xs font-medium">Explore</span>
            <svg className="w-4 h-4 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}
