import { Button } from '../ui/button';
import PilonLogo from '../../assets/logo.svg';

interface HeroProps {
  onGetStarted: () => void;
  onSignIn: () => void;
}

export function Hero({ onGetStarted, onSignIn }: HeroProps) {
  return (
    <div className="relative min-h-screen bg-white text-gray-900 overflow-hidden font-system">
      {/* Subtle Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-gray-100/50 to-gray-200/50 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-gradient-to-r from-gray-50/50 to-gray-100/50 rounded-full blur-3xl"></div>
      </div>

      {/* Clean Navigation */}
      <nav className="relative z-10 max-w-6xl mx-auto px-6 py-6">
        <div className="bg-white border border-gray-200 rounded-xl px-6 py-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <img src={PilonLogo} alt="Pilon" className="w-16 h-12 object-contain" />
            </div>
            <Button
              variant="outline"
              onClick={onSignIn}
              className="border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 font-medium text-sm px-6 py-2 rounded-lg transition-all"
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
          <div className="lg:col-span-3 space-y-8">
            {/* Badge */}
            <div className="bg-gray-100 border border-gray-200 inline-flex items-center gap-3 px-4 py-2 rounded-full text-xs font-medium text-gray-600">
              <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
              <span>EST. 2024 • NFL ANALYTICS</span>
              <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
            </div>

            {/* Main Headline */}
            <div className="space-y-6">
              <div className="flex items-center">
                <img src={PilonLogo} alt="Pilon" className="w-24 h-18 object-contain mr-4" />
                <h1 className="font-system text-6xl sm:text-7xl md:text-8xl leading-none text-gray-900 font-black">
                  Pilon
                </h1>
              </div>
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-light text-gray-700 leading-tight">
                Intelligent Fantasy Football
                <br />
                <span className="font-semibold text-gray-900">Analytics Platform</span>
              </h2>
            </div>

            {/* Value Proposition */}
            <p className="text-lg text-gray-600 max-w-lg leading-relaxed">
              AI-powered start/sit decisions with real-time analytics.
              Make championship-winning moves with zero guesswork.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Button
                size="lg"
                onClick={onGetStarted}
                className="bg-gray-900 text-white hover:bg-gray-800 font-medium px-8 py-3 rounded-lg border-0 transition-all shadow-sm"
              >
                Get Started
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={onSignIn}
                className="border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 font-medium px-8 py-3 rounded-lg transition-all"
              >
                View Demo
              </Button>
            </div>
          </div>

          {/* Right Stats Grid */}
          <div className="lg:col-span-2 grid grid-cols-2 gap-4">
            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center shadow-sm">
              <div className="text-3xl font-bold text-gray-900 mb-1">10K+</div>
              <div className="text-xs text-gray-500 font-medium">Users</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center shadow-sm">
              <div className="text-3xl font-bold text-gray-900 mb-1">73%</div>
              <div className="text-xs text-gray-500 font-medium">Win Rate</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center shadow-sm">
              <div className="text-3xl font-bold text-gray-900 mb-1">4.9★</div>
              <div className="text-xs text-gray-500 font-medium">Rating</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center shadow-sm">
              <div className="text-3xl font-bold text-gray-900 mb-1">24/7</div>
              <div className="text-xs text-gray-500 font-medium">Analysis</div>
            </div>
          </div>
        </div>
      </div>

      {/* Preview Cards */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h3 className="text-2xl font-semibold text-gray-900 mb-2">Live Player Analysis</h3>
          <p className="text-gray-600">See how our AI grades your players in real-time</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* START Card */}
          <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-all group shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-700 font-bold text-sm">A+</span>
              </div>
              <div className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                START
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-gray-900">P. Mahomes</h4>
              <p className="text-sm text-gray-500">QB • Kansas City</p>
              <div className="text-2xl font-bold text-gray-900">24.8 pts</div>
            </div>
          </div>

          {/* CONSIDER Card */}
          <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-all group shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-yellow-700 font-bold text-sm">B+</span>
              </div>
              <div className="px-3 py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded-full">
                CONSIDER
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-gray-900">S. Barkley</h4>
              <p className="text-sm text-gray-500">RB • New York</p>
              <div className="text-2xl font-bold text-gray-900">18.3 pts</div>
            </div>
          </div>

          {/* BENCH Card */}
          <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-all group shadow-sm opacity-60">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                <span className="text-gray-600 font-bold text-sm">C</span>
              </div>
              <div className="px-3 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded-full">
                BENCH
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-gray-700">D. Hopkins</h4>
              <p className="text-sm text-gray-400">WR • Tennessee</p>
              <div className="text-2xl font-bold text-gray-700">12.1 pts</div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10">
        <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 shadow-sm">
          <div className="flex flex-col items-center gap-2 text-gray-500">
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
