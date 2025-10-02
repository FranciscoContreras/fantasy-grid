import { Button } from '../ui/button';

interface HeroProps {
  onGetStarted: () => void;
  onSignIn: () => void;
}

export function Hero({ onGetStarted, onSignIn }: HeroProps) {
  return (
    <div className="relative min-h-screen bg-white text-black overflow-hidden">
      {/* Navigation */}
      <nav className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-black rounded-sm"></div>
            <span className="text-2xl font-black tracking-tight">FANTASY GRID</span>
          </div>
          <Button
            variant="ghost"
            onClick={onSignIn}
            className="text-black hover:bg-gray-100 font-semibold"
          >
            Sign In
          </Button>
        </div>
      </nav>

      {/* Hero Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="max-w-4xl">
          {/* Label */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-full mb-8">
            <span className="text-xs font-bold text-gray-900 uppercase tracking-wider">
              Powered by Next Gen Stats + AI
            </span>
          </div>

          {/* Main headline */}
          <h1 className="text-6xl sm:text-7xl md:text-8xl lg:text-9xl font-black tracking-tighter mb-8 leading-none">
            DOMINATE
            <br />
            YOUR LEAGUE
          </h1>

          {/* Subheadline */}
          <p className="text-xl sm:text-2xl md:text-3xl text-gray-600 font-light mb-12 max-w-2xl leading-relaxed">
            AI-powered start/sit decisions.
            <br />
            Real-time analytics.
            <br />
            <span className="text-black font-medium">Zero guesswork.</span>
          </p>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row gap-4 mb-16">
            <Button
              size="lg"
              onClick={onGetStarted}
              className="px-10 py-8 bg-black text-white hover:bg-gray-900 text-lg font-bold rounded-full"
            >
              START WINNING
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={onSignIn}
              className="px-10 py-8 border-2 border-black text-black hover:bg-gray-100 text-lg font-bold rounded-full"
            >
              WATCH DEMO
            </Button>
          </div>

          {/* Stats */}
          <div className="flex flex-wrap gap-12 text-sm border-t border-gray-200 pt-8">
            <div>
              <div className="text-4xl font-black text-black mb-1">10K+</div>
              <div className="text-gray-500 uppercase tracking-wider font-semibold text-xs">Active Users</div>
            </div>
            <div>
              <div className="text-4xl font-black text-black mb-1">73%</div>
              <div className="text-gray-500 uppercase tracking-wider font-semibold text-xs">Win Rate</div>
            </div>
            <div>
              <div className="text-4xl font-black text-black mb-1">4.9★</div>
              <div className="text-gray-500 uppercase tracking-wider font-semibold text-xs">Rating</div>
            </div>
          </div>
        </div>

        {/* Preview Cards - Monochromatic */}
        <div className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl">
          {/* START Card */}
          <div className="group relative bg-black text-white rounded-2xl p-8 hover:scale-105 transition-transform">
            <div className="flex items-center justify-between mb-6">
              <div className="w-16 h-16 bg-white rounded-xl"></div>
              <div className="text-5xl font-black">A+</div>
            </div>
            <div className="text-2xl font-bold mb-1">P. MAHOMES</div>
            <div className="text-sm text-gray-400 mb-6 uppercase tracking-wider">QB · Kansas City</div>
            <div className="inline-flex items-center gap-2 px-5 py-2 bg-white text-black rounded-full font-bold text-sm uppercase tracking-wider">
              START
            </div>
          </div>

          {/* CONSIDER Card */}
          <div className="group relative bg-gray-200 text-black rounded-2xl p-8 hover:scale-105 transition-transform">
            <div className="flex items-center justify-between mb-6">
              <div className="w-16 h-16 bg-gray-400 rounded-xl"></div>
              <div className="text-5xl font-black text-gray-600">B+</div>
            </div>
            <div className="text-2xl font-bold mb-1">S. BARKLEY</div>
            <div className="text-sm text-gray-600 mb-6 uppercase tracking-wider">RB · New York</div>
            <div className="inline-flex items-center gap-2 px-5 py-2 bg-gray-400 text-white rounded-full font-bold text-sm uppercase tracking-wider">
              CONSIDER
            </div>
          </div>

          {/* BENCH Card */}
          <div className="group relative bg-gray-100 text-gray-400 rounded-2xl p-8 hover:scale-105 transition-transform opacity-60">
            <div className="flex items-center justify-between mb-6">
              <div className="w-16 h-16 bg-gray-300 rounded-xl"></div>
              <div className="text-5xl font-black">C</div>
            </div>
            <div className="text-2xl font-bold mb-1">D. HOPKINS</div>
            <div className="text-sm text-gray-500 mb-6 uppercase tracking-wider">WR · Tennessee</div>
            <div className="inline-flex items-center gap-2 px-5 py-2 bg-gray-300 text-gray-600 rounded-full font-bold text-sm uppercase tracking-wider">
              BENCH
            </div>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10">
        <div className="flex flex-col items-center gap-2 text-gray-400">
          <span className="text-xs uppercase tracking-wider font-semibold">Scroll</span>
          <svg className="w-6 h-6 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </div>
    </div>
  );
}
